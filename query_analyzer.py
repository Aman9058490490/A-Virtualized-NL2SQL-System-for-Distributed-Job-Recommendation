"""Natural language query analyzer that orchestrates LLM decomposition."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from groq_client import GroqClient, GroqClientError
from utils import load_json_response, normalize_sql_whitespace, qualification_like_patterns

LOGGER = logging.getLogger(__name__)

COURSE_SCHEMA_SUMMARY = """
coursedb (port 3306) - INDEPENDENT DATABASE
Tables:
  software_engineer_jobs (
    se_Job_Id bigint PK,
    se_Job_Title varchar(255),
    se_Role varchar(255),
    se_skills text,
    se_Company varchar(255),
    se_Experience varchar(50),
    se_Qualifications varchar(100),
    se_Salary_Range varchar(50),
    se_location varchar(100),
    se_Work_Type varchar(50)
  )
IMPORTANT: Can only query job_data table. No cross-database references allowed.
""".strip()

JOB_SCHEMA_SUMMARY = """
fe_database (port 3307) - INDEPENDENT DATABASE
Tables:
  frontend_engineer_jobs (
    fe_Job_Id bigint PK,
    fe_Job_Title varchar(255),
    fe_Role varchar(255),
    fe_skills text,
    fe_Company varchar(255),
    fe_Experience varchar(50),
    fe_Qualifications varchar(100),
    fe_Salary_Range varchar(50),
    fe_location varchar(100),
    fe_Work_Type varchar(50),
    fe_Company_Size int,
    fe_Preference varchar(20),
    fe_Contact_Person varchar(255),
    fe_Job_Description text,
    fe_Benefits text,
    fe_Responsibilities text,
    fe_Company_Profile text
  )
IMPORTANT: Use LOWER() for case-insensitive text matches. Search fe_Job_Title, fe_Role, and fe_skills for relevant keywords.
""".strip()

SYSTEM_PROMPT = """
You are an expert federated SQL planner. Your task is to convert the user's
natural language question into THREE outputs:

1. "course_sql"    – SQL for the SOFTWARE ENGINEERING database
2. "job_sql"       – SQL for the FRONTEND ENGINEERING database
3. "natural_query" – A reasoning prompt for a second LLM that MUST answer all
                     parts of the user's question that CANNOT be answered
                     directly from SQL results.

Your output MUST be a JSON object with exactly these 3 keys.

==============================================================================
DATABASE SCHEMA SUMMARIES WITH REAL SAMPLE ROWS
==============================================================================

SOFTWARE DATABASE (CourseDB)
Table: software_engineer_jobs
Prefix: se_

Example row:
{
  "se_Job_Id": "SE001",
  "se_Experience": "3 years",
  "se_Qualifications": "MTech",
  "se_Salary_Range": "$127k - $146k",
  "se_location": "Shermanland",
  "se_Country": "San Marino",
  "se_Work_Type": "On-site",
  "se_Company_Size": "1000+",
  "se_Preference": "Any",
  "se_Job_Title": "Backend Developer",
  "se_Role": "Software Development",
  "se_skills": "Serverless, AWS Lambda",
  "se_Company": "Levy and Sons"
}

FRONTEND DATABASE (JobDB)
Table: frontend_engineer_jobs
Prefix: fe_

Example row:
{
  "fe_Job_Id": "FE001",
  "fe_Experience": "7 years",
  "fe_Qualifications": "BTech",
  "fe_Salary_Range": "$62k - $164k",
  "fe_location": "Smithstad",
  "fe_Country": "Saint Martin",
  "fe_Work_Type": "Remote",
  "fe_Company_Size": "1000+",
  "fe_Preference": "Any",
  "fe_Job_Title": "React Developer",
  "fe_Role": "Frontend Development",
  "fe_skills": "Angular, RxJS",
  "fe_Company": "Stevenson, Patel and Gould"
}

==============================================================================
MANDATORY DB ROUTING RULES
==============================================================================

You MUST generate SQL for the correct database:

● course_sql is required when the query involves:
  "software engineer", "software developer", "backend", "cloud", "full-stack",
  "software jobs", or any general "software roles".

● job_sql is required when the query involves:
  "frontend", "front end", "UI", "UX", "web developer", "javascript developer",
  "react", "typescript", "frontend jobs".

● If BOTH domains appear → you MUST generate BOTH SQL queries.

● Only leave SQL empty ("") when a domain is clearly irrelevant.

==============================================================================
HANDLING OUT-OF-SCOPE QUERIES
==============================================================================

If the user's query asks about information NOT available in either database
(e.g., medical jobs, teaching positions, non-tech roles, information not in the schema):

1. Generate the BEST POSSIBLE SQL queries that retrieve the most relevant data
   (even if not perfect matches)
2. In the "natural_query", CLEARLY explain:
   - What information is NOT available in the database
   - Suggest 2-3 similar queries that WOULD work with the available data
   - Ask the second LLM to acknowledge limitations and provide alternative suggestions

Example natural_query for out-of-scope request:
"The user asked about [X] which is not available in our database. Our database only
contains software engineering jobs and frontend engineering jobs. Please:
1. Explain that we don't have data for [X]
2. Suggest these alternative queries that match our database:
   - [Similar query 1]
   - [Similar query 2]
   - [Similar query 3]
3. If the SQL returned any results, briefly mention them as 'closest matches'"

==============================================================================
STRICT SQL RULES
==============================================================================

- SQL must be valid MySQL and must start with SELECT.
- Use ONLY table names (no database prefixes like db.table).
- Use correct prefixes:
      se_ for software_engineer_jobs
      fe_ for frontend_engineer_jobs
- Use LOWER(column) LIKE '%text%' for case-insensitive text matching.
- Always include LIMIT 25 for broad queries.
- Only use columns that appear in the schema examples.

QUALIFICATION MATCHING GUIDANCE:
- When generating SQL that filters on qualifications (e.g. BTech, M.Tech, MSc, PhD),
  produce multiple case-insensitive LIKE variants to cover common punctuation and spacing
  variants (for example: "%mtech%", "%m.tech%", "%m tech%") so that records with
  slightly different formatting still match. The deterministic fallback will also
  generate multiple LIKE patterns when qualifications are detected.

==============================================================================
NATURAL_QUERY RULES (IMPORTANT)
==============================================================================

The "natural_query" MUST:

✔ Restate the user's true intent  
✔ Explicitly describe what the second LLM must figure out  
✔ Include ANY part of the question that CANNOT be answered by SQL  
✔ If query is out-of-scope, suggest relevant alternative queries

Examples of things SQL CANNOT answer (but natural_query MUST include):
  – career guidance  
  – job comparison  
  – recommendations  
  – analysis, reasoning, explanations  
  – ranking logic  
  – anything requiring outside knowledge  
  – judgments or opinions  
  – combining results across both databases  
  – queries about data not in the schema

The second LLM will receive BOTH:
  1. the SQL results
  2. your natural_query

So natural_query should tell the LLM **how to use the SQL results PLUS extra reasoning**
to fully answer the user's question.

For out-of-scope queries, natural_query should instruct the second LLM to:
- Politely explain what information is NOT available
- Suggest 2-3 alternative queries that WOULD work with the database
- Provide any partial matches if the SQL returned relevant data

==============================================================================
OUTPUT FORMAT (STRICT)
==============================================================================

Return ONLY a JSON object with EXACTLY these keys:

{
  "course_sql": "<sql or empty string>",
  "job_sql": "<sql or empty string>",
  "natural_query": "<string>"
}

NO explanations.  
NO commentary.  
Return pure JSON ONLY.
"""


COURSE_KEYWORDS = [
    "all",
    "course",
    "courses",
    "software",
    "sd_database",
    "sd_jobs",
    "skills",
    "salary",
    "experience",
    "qualifications",
    "work type",
    "benefits"
]

JOB_KEYWORDS = [
    "all",
    "job",
    "jobs",
    "front",
    "front end",
    "front-end",
    "frontend",
    "developer",
    "engineer",
    "programming",
    "software",
    "web",
    "ui",
    "ux",
    "javascript"
]

ROLE_EXTRACTION_PATTERN = re.compile(
    r"(?:for|as|to become|towards|about)\s+([^?.!,]+)",
    re.IGNORECASE,
)
ROLE_SANITIZE_PATTERN = re.compile(r"[^a-zA-Z0-9\s]")
ROLE_STOPWORDS = {
    "courses",
    "course",
    "job",
    "jobs",
    "role",
    "roles",
    "position",
    "positions",
    "career",
    "careers",
    "me",
    "for",
    "a",
    "an",
    "the",
    "suggest",
    "suggestion",
    "suggestions",
    "recommend",
    "recommendations",
    "list",
    "find",
    "with",
    "in",
    "of",
    "to",
    "become",
}


@dataclass
class AnalyzerResult:
    course_sql: str
    job_sql: str
    natural_query: str


class QueryAnalyzer:
    """Generate SQL decomposition for natural language queries."""

    def __init__(
        self,
        client: GroqClient,
        *,
        max_attempts: int = 2,
        enable_fallback: bool = True,
        fallback_default_role: str = "Data Scientist",
    ) -> None:
        self._client = client
        self._max_attempts = max(1, max_attempts)
        self._enable_fallback = enable_fallback
        self._fallback_default_role = fallback_default_role

    def _needs_course_db(self, query: str) -> bool:
        return any(keyword in query.lower() for keyword in COURSE_KEYWORDS)

    def _needs_job_db(self, query: str) -> bool:
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in JOB_KEYWORDS) or 'developer' in query_lower or 'engineer' in query_lower

    def _build_user_prompt(self, query: str) -> str:
        target_parts: List[str] = []
        if self._needs_course_db(query):
            target_parts.append("CourseDB")
        if self._needs_job_db(query):
            target_parts.append("JobDB")
        targets = ", ".join(target_parts) if target_parts else "(model must decide)"

        return (
            f"User question: {query}\n\n"
            f"Potential target databases: {targets}\n\n"
            "CourseDB schema summary:\n"
            f"{COURSE_SCHEMA_SUMMARY}\n\n"
            "JobDB schema summary:\n"
            f"{JOB_SCHEMA_SUMMARY}\n\n"
            "Respond with JSON and ensure SQL strings are escaped properly."
        )

    def generate_decomposition(self, query: str) -> AnalyzerResult:
        """Generate SQL for both databases plus optional unstructured prompt."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self._build_user_prompt(query)},
        ]

        last_error: Optional[Exception] = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                raw_response = self._client.chat(messages, temperature=0.05)
                payload = load_json_response(raw_response)
            except (GroqClientError, ValueError) as exc:
                last_error = exc
                LOGGER.warning("LLM decomposition attempt %s failed: %s", attempt, exc)
                if attempt >= self._max_attempts:
                    break  # Don't raise, let fallback handle it
                continue

            course_sql = normalize_sql_whitespace(payload.get("course_sql", ""))
            job_sql = normalize_sql_whitespace(payload.get("job_sql", ""))
            natural_query = (payload.get("natural_query", "") or "").strip()


            missing_course = not course_sql and self._needs_course_db(query)
            missing_job = not job_sql and self._needs_job_db(query)

            if (course_sql or job_sql) and not (missing_course or missing_job):
                return AnalyzerResult(
                    course_sql=course_sql,
                    job_sql=job_sql,
                    natural_query=natural_query
                )


            LOGGER.warning(
                "LLM returned incomplete SQL payload on attempt %s (course_sql=%s, job_sql=%s)",
                attempt,
                bool(course_sql),
                bool(job_sql),
            )
            last_error = ValueError("LLM returned incomplete SQL payload")

        if self._enable_fallback:
            LOGGER.info("Falling back to deterministic SQL templates for query: %s", query)
            return self._fallback_decomposition(query)

        raise last_error or RuntimeError("LLM decomposition failed")

    def _fallback_decomposition(self, query: str) -> AnalyzerResult:
        role, sanitized_like = self._extract_role(query)
        # Build a safer search term token list (avoid literal multi-word phrase matching)
        tokens = [t for t in re.findall(r"\w+", sanitized_like.lower()) if t and t not in ROLE_STOPWORDS]
        if not tokens:
            tokens = [sanitized_like.lower()] if sanitized_like else []
        
        # Extract experience range if present
        exp_pattern = re.compile(r'(\d+)\s*(?:to|-)\s*(\d+)\s*years?', re.IGNORECASE)
        exp_match = exp_pattern.search(query)
        exp_min = exp_match.group(1) if exp_match else None
        exp_max = exp_match.group(2) if exp_match else None
        
        query_lower = query.lower()

        # If the user asked specifically about qualifications (degrees), build
        # qualification-focused SQL using multiple LIKE variants for robustness
        qual_pattern = re.compile(r"\b(m\.?tech|mtech|b\.?tech|btech|b\.?sc|bsc|m\.?sc|msc|phd|ph\.?d)\b", re.IGNORECASE)
        qual_match = qual_pattern.search(query_lower)
        if qual_match:
            qual_term = qual_match.group(1)
            variants = qualification_like_patterns(qual_term)
            # build qualification conditions for both DBs (patterns are already lowercase/with %)
            course_qual_conds = [f"LOWER(se_Qualifications) LIKE '{v}'" for v in variants]
            job_qual_conds = [f"LOWER(fe_Qualifications) LIKE '{v}'" for v in variants]

            experience_condition_course = ""
            experience_condition_job = ""
            if exp_min and exp_max:
                try:
                    start = int(exp_min)
                    end = int(exp_max)
                    years_list = ", ".join(f"'{y} years'" for y in range(start, end + 1))
                    experience_condition_course = f" AND se_Experience IN ({years_list})"
                    experience_condition_job = f" AND fe_Experience IN ({years_list})"
                except Exception:
                    pass

            course_sql = (
                "SELECT * FROM software_engineer_jobs "
                f"WHERE ({' OR '.join(course_qual_conds)})"
                f"{experience_condition_course} "
                "LIMIT 25"
            )

            job_sql = (
                "SELECT * FROM frontend_engineer_jobs "
                f"WHERE ({' OR '.join(job_qual_conds)})"
                f"{experience_condition_job} "
                "LIMIT 25"
            )

            return AnalyzerResult(course_sql=normalize_sql_whitespace(course_sql), job_sql=normalize_sql_whitespace(job_sql), natural_query=f"Using the results of both SQL queries, answer the user query: '{query}'.")

        # Generate independent fe_database query with proper experience filtering
        # Start with generic frontend conditions and extend with role tokens when available
        role_conditions = [
            "LOWER(fe_Job_Title) LIKE '%front%'",
            "LOWER(fe_Role) LIKE '%front%'",
            "LOWER(fe_skills) LIKE '%frontend%'"
        ]
        if tokens:
            # Add token-based matching to increase recall while avoiding full-phrase literal matches
            for t in tokens[:3]:
                role_conditions.append(f"LOWER(fe_Job_Title) LIKE '%{t}%'")
                role_conditions.append(f"LOWER(fe_Role) LIKE '%{t}%'")
                role_conditions.append(f"LOWER(fe_skills) LIKE '%{t}%'")

        # Add experience filter if specified — build a simple IN list of years
        experience_condition_job = ""
        if exp_min and exp_max:
            try:
                start = int(exp_min)
                end = int(exp_max)
                years_list = ", ".join(f"'{y} years'" for y in range(start, end + 1))
                experience_condition_job = f" AND fe_Experience IN ({years_list})"
            except Exception:
                experience_condition_job = ""

        job_sql = (
            "SELECT * FROM frontend_engineer_jobs "
            f"WHERE ({' OR '.join(role_conditions)})"
            f"{experience_condition_job} "
            "LIMIT 25"
        )

        # Generate independent software database query with proper experience filtering
        # Build course search conditions from tokens for more robust matching
        search_conditions = []
        if tokens:
            token_conds = []
            for t in tokens[:3]:
                token_conds.append(f"LOWER(se_Job_Title) LIKE '%{t}%'")
                token_conds.append(f"LOWER(se_skills) LIKE '%{t}%'")
                token_conds.append(f"LOWER(se_Role) LIKE '%{t}%'")
            search_conditions = token_conds
        else:
            # fallback to whole phrase if tokens missing
            search_term = sanitized_like.lower()
            search_conditions = [
                f"LOWER(se_Job_Title) LIKE '%{search_term}%'",
                f"LOWER(se_skills) LIKE '%{search_term}%'",
                f"LOWER(se_Role) LIKE '%{search_term}%'",
            ]

        experience_condition_course = ""
        if exp_min and exp_max:
            try:
                start = int(exp_min)
                end = int(exp_max)
                years_list = ", ".join(f"'{y} years'" for y in range(start, end + 1))
                experience_condition_course = f" AND se_Experience IN ({years_list})"
            except Exception:
                experience_condition_course = ""

        course_sql = (
            "SELECT * FROM software_engineer_jobs "
            f"WHERE ({' OR '.join(search_conditions)})"
            f"{experience_condition_course} "
            "LIMIT 25"
        )

        prompt = (
            f"Summarize how the listed courses support the '{role}' role, "
            "highlighting overlap with job skills and any remaining gaps."
        )

        return AnalyzerResult(course_sql=course_sql, job_sql=job_sql, natural_query=f"Using the results of both SQL queries, answer the user query: '{query}'.")

    def _get_common_skills_for_role(self, role: str) -> List[str]:
        """Get common skills for a given role based on predefined mappings."""
        role_lower = role.lower()
        
        # Predefined skill mappings for common roles
        skill_mappings = {
            'data scientist': ['Python', 'Machine Learning', 'Statistics', 'Data Analysis', 'Pandas', 'NumPy'],
            'ai engineer': ['Python', 'Machine Learning', 'TensorFlow', 'Deep Learning', 'NLP'],
            'machine learning engineer': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Deep Learning'],
            'software engineer': ['Python', 'Java', 'C++', 'OOP', 'Git'],
            'web developer': ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js'],
            'frontend developer': ['JavaScript', 'HTML', 'CSS', 'React'],
            'backend developer': ['Python', 'Java', 'SQL', 'REST APIs'],
            'full stack developer': ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js', 'Python'],
            'devops engineer': ['Docker', 'Kubernetes', 'AWS', 'Cloud Computing', 'Linux'],
            'cloud engineer': ['AWS', 'Azure', 'Cloud Computing', 'Docker', 'Kubernetes'],
            'security engineer': ['Cybersecurity', 'Ethical Hacking', 'Security', 'Networking'],
            'data analyst': ['Python', 'SQL', 'Data Analysis', 'Statistics', 'Excel', 'Power BI'],
            'big data engineer': ['Python', 'Big Data', 'SQL', 'Data Analysis']
        }
        
        # Find matching skills
        for role_key, skills in skill_mappings.items():
            if role_key in role_lower:
                return skills
        
        # Default skills for unknown roles
        return ['Python', 'Java', 'JavaScript', 'SQL']

    def _extract_role(self, query: str) -> Tuple[str, str]:
        candidate = ""
        match = ROLE_EXTRACTION_PATTERN.search(query)
        if match:
            candidate = match.group(1)
        if not candidate:
            candidate = query

        candidate = ROLE_SANITIZE_PATTERN.sub(" ", candidate)
        tokens = [token for token in candidate.split() if token.lower() not in ROLE_STOPWORDS]
        if not tokens:
            tokens = self._fallback_default_role.split()

        role = " ".join(tokens[:5]).strip() or self._fallback_default_role
        sanitized_like = ROLE_SANITIZE_PATTERN.sub(" ", role)
        sanitized_like = re.sub(r"\s+", " ", sanitized_like).strip()
        sanitized_like = sanitized_like.replace("'", "")
        return role, sanitized_like


__all__ = ["QueryAnalyzer", "AnalyzerResult"]
