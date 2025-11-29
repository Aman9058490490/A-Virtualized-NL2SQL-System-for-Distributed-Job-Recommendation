"""Execution layer for running SQL against CourseDB and JobDB."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Dict, List, Optional, Set

import pandas as pd
import pymysql
from pymysql import MySQLError
from pymysql.cursors import DictCursor
# --- Prevent Gemini gRPC shutdown warnings ---
import atexit
import google.generativeai as genai

def shutdown_gemini():
    try:
        genai._genai_service = None
    except:
        pass

atexit.register(shutdown_gemini)
# ---------------------------------------------

from utils import (
    DatabaseConfig,
    collect_course_skill_map,
    collect_skill_set,
    ensure_safe_sql,
    extract_text_columns,
    load_database_config,
)

LOGGER = logging.getLogger(__name__)


class DatabaseExecutor:
    """Execute read-only SQL against federated databases."""

    def __init__(
        self,
        course_config: Optional[DatabaseConfig] = None,
        job_config: Optional[DatabaseConfig] = None,
    ) -> None:

        self.course_config = course_config or load_database_config("COURSE_DB")
        self.job_config = job_config or load_database_config("JOB_DB")

    # ------------------------------------------------------------------------------------
    # SCHEMA MAPPING (CURRENTLY UNUSED BUT LEFT FOR FUTURE EXPANSION)
    # ------------------------------------------------------------------------------------
    def _apply_schema_mapping(self, df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        if not mapping:
            return df
        rename_dict = {col: mapping[col] for col in mapping if mapping[col]}
        return df.rename(columns=rename_dict)

    # ------------------------------------------------------------------------------------
    # MERGE RESULTS (UNIFY PREFIXES)
    # ------------------------------------------------------------------------------------
    def _merge_results(self, course_df: pd.DataFrame, job_df: pd.DataFrame) -> pd.DataFrame:

        if course_df.empty and job_df.empty:
            return pd.DataFrame()

        def normalize(df, prefix):
            new = df.copy()
            new.columns = [c.replace(prefix, "") for c in df.columns]
            return new

        software = normalize(course_df, "se_")
        frontend = normalize(job_df, "fe_")

        if not software.empty:
            software["__source"] = "software"
        if not frontend.empty:
            frontend["__source"] = "frontend"

        return pd.concat([software, frontend], ignore_index=True, sort=True)

    # ------------------------------------------------------------------------------------
    # DB CONNECTION + SQL EXECUTION
    # ------------------------------------------------------------------------------------
    @contextmanager
    def _connection(self, config: DatabaseConfig):
        try:
            conn = pymysql.connect(
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.database,
                cursorclass=DictCursor,
                autocommit=True,
            )
        except MySQLError as exc:
            LOGGER.error(
                "Failed to connect to %s:%s/%s: %s",
                config.host, config.port, config.database, exc
            )
            raise
        try:
            yield conn
        finally:
            conn.close()

    def _run_query(self, sql: str, config: DatabaseConfig) -> pd.DataFrame:
        sql = ensure_safe_sql(sql)
        if not sql:
            return pd.DataFrame()

        with self._connection(config) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                except MySQLError as exc:
                    LOGGER.error("SQL execution failed: %s", exc)
                    raise

        return pd.DataFrame(rows)

    def execute(self, course_sql: str, job_sql: str) -> Dict[str, pd.DataFrame]:
        course_df = self._run_query(course_sql, self.course_config) if course_sql else pd.DataFrame()
        job_df = self._run_query(job_sql, self.job_config) if job_sql else pd.DataFrame()

        merged_df = self._merge_results(course_df, job_df)

        return {
            "course": course_df,
            "job": job_df,
            "merged": merged_df,
        }

    # ------------------------------------------------------------------------------------
    # RANK COURSES (UNCHANGED)
    # ------------------------------------------------------------------------------------
    @staticmethod
    def collect_text_for_summary(results: Dict[str, pd.DataFrame]) -> str:
        text_payload = []
        if not results["course"].empty:
            course_columns = DatabaseExecutor._select_available_columns(
                results["course"],
                ["course_description", "prerequisites", "skill_name", "offered_mode"],
            )
            text_payload.append(
                extract_text_columns(
                    results["course"].to_dict(orient="records"),
                    course_columns,
                )
            )
        if not results["job"].empty:
            job_columns = DatabaseExecutor._select_available_columns(
                results["job"],
                ["job_description", "education_requirement", "skill_name", "location"],
            )
            text_payload.append(
                extract_text_columns(
                    results["job"].to_dict(orient="records"),
                    job_columns,
                )
            )
        return "\n\n".join(part for part in text_payload if part)

    @staticmethod
    def _select_available_columns(df: pd.DataFrame, candidates: List[str]) -> List[str]:
        return [column for column in candidates if column in df.columns]

    @staticmethod
    def rank_courses(course_df: pd.DataFrame, job_df: pd.DataFrame) -> pd.DataFrame:
        if course_df.empty:
            return course_df

        job_records = job_df.to_dict(orient="records") if not job_df.empty else []
        job_skills = collect_skill_set(job_records)
        if not job_skills:
            return course_df

        course_records = course_df.to_dict(orient="records")
        course_skill_map = collect_course_skill_map(course_records)
        if not course_skill_map:
            return course_df

        subset_cols = [col for col in ["course_id", "course_name"] if col in course_df.columns]
        ranked_df = (
            course_df.drop_duplicates(subset=subset_cols).copy()
            if subset_cols else course_df.copy()
        )

        matched_counts = []
        coverage_scores = []
        matching_skill_strings = []
        job_skill_count = len(job_skills)

        for idx, row in ranked_df.iterrows():
            keys = []
            if "course_id" in row:
                keys.append(str(row["course_id"]))
            if "course_name" in row:
                keys.append(str(row["course_name"]))
            if not keys:
                keys.append(str(idx))

            course_skills = set()
            for identifier in keys:
                course_skills.update(course_skill_map.get(identifier, set()))

            matched = course_skills.intersection(job_skills)
            matched_counts.append(len(matched))
            coverage_scores.append(len(matched) / job_skill_count if job_skill_count else 0)
            matching_skill_strings.append(", ".join(sorted(skill.title() for skill in matched)))

        ranked_df = ranked_df.assign(
            matched_skill_count=matched_counts,
            coverage_score=coverage_scores,
            matching_skills=matching_skill_strings,
        )

        ranked_df = ranked_df[ranked_df["matched_skill_count"] > 0]
        if ranked_df.empty:
            return course_df

        sort_columns = ["matched_skill_count", "coverage_score"]
        ascending = [False, False]
        ranked_df = ranked_df.sort_values(sort_columns, ascending=ascending).reset_index(drop=True)
        return ranked_df

    # ------------------------------------------------------------------------------------
    # FINAL ANSWER GENERATION (TOP 5 ROWS → COMPACT BULLET LIST → LLM)
    # ------------------------------------------------------------------------------------
    # def generate_final_answer(self, merged_df: pd.DataFrame, natural_query: str):
    #     """
    #     Final answer generation: send the FULL merged dataframe to the LLM
    #     in markdown table format, along with the natural query.
    #     """

    #     if merged_df.empty:
    #         return "No matching results were found in either database."

    #     # Convert FULL dataframe to markdown (LLM reads this extremely well)
    #     table_text = merged_df.to_markdown(index=False)
    #     print(table_text)
    #     prompt = (
    #         "You are an expert job-market analyst.\n"
    #         "You are given a natural language question and a complete merged dataset.\n\n"
    #         "DATASET (FULL):\n"
    #         f"{table_text}\n\n"
    #         "USER QUESTION:\n"
    #         f"{natural_query}\n\n"
    #         "Your job:\n"
    #         "- Understand the dataset\n"
    #         "- Answer the user's question clearly\n"
    #         "- DO NOT repeat the dataset\n"
    #         "- DO NOT mention SQL or databases\n"
    #         "- Provide a concise, helpful interpretation"
    #     )

    #     # LLM call
    #     from groq_client import GroqClient
    #     client = GroqClient()

    #     response = client.chat(
    #         [
    #             {"role": "system", "content": "You provide concise, helpful answers."},
    #             {"role": "user", "content": prompt}
    #         ],
    #         temperature=0.1
    #     )

    #     # Extract best-effort answer
    #     try:
    #         if isinstance(response, str):
    #             return response
    #         if "choices" in response:
    #             choice = response["choices"][0]
    #             if "message" in choice and "content" in choice["message"]:
    #                 return choice["message"]["content"]
    #             if "text" in choice:
    #                 return choice["text"]
    #         return str(response)
    #     except Exception:
    #         return "The LLM failed to produce an answer."
    def generate_final_answer(self, merged_df: pd.DataFrame, natural_query: str, original_user_query: str = ""):
        """
        Final answer generation: send the FULL merged dataframe to the LLM
        in markdown table format, along with the natural query.
        The LLM is permitted to answer using its own knowledge if the dataset
        is incomplete or insufficient.
        """

        if merged_df.empty:
            # When no results, ask LLM to provide helpful suggestions
            prompt = (
                "The user asked: '{}'\\n\\n"
                "Our database contains ONLY:\\n"
                "- Software Engineering jobs (backend, full-stack, cloud, DevOps roles)\\n"
                "- Frontend Engineering jobs (React, Angular, Vue, UI/UX roles)\\n\\n"
                "No matching results were found for this query.\\n\\n"
                "Please:\\n"
                "1. Politely explain that the query is not available in our database\\n"
                "2. Suggest 3 relevant alternative queries that WOULD work with our database\\n"
                "3. Make suggestions based on what's actually available (software or frontend engineering jobs)\\n\\n"
                "Format your response in a friendly, helpful manner.\\n"
                "Additional context: {}"
            ).format(original_user_query or natural_query, natural_query)
            
            from groq_client import GroqClient
            client = GroqClient()
            
            response = client.chat(
                [
                    {"role": "system", "content": "You are a helpful assistant that guides users to ask better queries based on available data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            try:
                if isinstance(response, str):
                    return response
                if "choices" in response:
                    choice = response["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                    if "text" in choice:
                        return choice["text"]
                return "This query doesn't match our database. Our database contains software engineering and frontend engineering jobs. Please try queries related to these domains."
            except Exception:
                return "This query doesn't match our database. Our database contains software engineering and frontend engineering jobs. Please try queries related to these domains."

        # Convert FULL dataframe to markdown (LLM reads this extremely well)
        table_text = merged_df.to_markdown(index=False)

        prompt = (
            "You are an expert job-market analyst.\n\n"
            "DATABASE CONTAINS: Software engineering jobs and frontend engineering jobs ONLY.\n\n"
            "DATASET:\n"
            f"{table_text}\n\n"
            "TASK:\n"
            f"{natural_query}\n\n"
            "Instructions:\n"
            "- Answer the user's question using the dataset\n"
            "- If the user asked about something NOT in our database scope, acknowledge this\n"
            "  and suggest what they COULD ask about instead (software or frontend jobs)\n"
            "- If dataset has limited results, mention that and provide suggestions\n"
            "- Be conversational and helpful\n"
            "- DO NOT mention SQL or technical database details\n"
            "- Provide clear, actionable insights"
        )


        # LLM call
        from groq_client import GroqClient
        #from gemeni_client import GeminiClient
        client = GroqClient()
        #client = GeminiClient()

        response = client.chat(
            [
                {"role": "system", "content": "You are a helpful job-market analyst who provides clear insights and helpful suggestions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        # Extract best-effort answer
        try:
            if isinstance(response, str):
                return response
            if "choices" in response:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
                if "text" in choice:
                    return choice["text"]
            return str(response)
        except Exception:
            return "The LLM failed to produce an answer."




