"""Interactive CLI demo for the federated NL-to-SQL system."""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

import pandas as pd

from executor import DatabaseExecutor
from groq_client import GroqClient, GroqClientError
from query_analyzer import QueryAnalyzer
from utils import configure_logging

LOGGER = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Federated NL-to-SQL demo")
    parser.add_argument("query", nargs="?", help="Natural language query to execute")
    parser.add_argument("--fallback-batch", action="store_true", help="Run a preset batch of difficult fallback queries (deterministic fallback path)")
    parser.add_argument("--rows", type=int, default=10, help="Rows to preview per table")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    return parser.parse_args()


def _print_dataframe(title: str, df: pd.DataFrame, max_rows: int) -> None:
    print(f"\n--- {title} (showing up to {max_rows} rows) ---")
    if df.empty:
        print("<empty>")
    else:
        print(df.head(max_rows).to_string(index=False))


def run_demo(query: str, max_rows: int) -> None:
    configure_logging()

    client = GroqClient()
    analyzer = QueryAnalyzer(client)
    executor = DatabaseExecutor()

    print("\n=== Natural language query ===\n", query)

    decomposition = analyzer.generate_decomposition(query)

    print("\n=== Generated SQL ===")
    print("CourseDB SQL:\n", decomposition.course_sql or "<none>")
    print("\nJobDB SQL:\n", decomposition.job_sql or "<none>")
    print("\nNatural Query:\n", decomposition.natural_query or "<none>")

    if not decomposition.course_sql and not decomposition.job_sql:
        print("\nNo executable SQL was produced. Please refine the query and try again.")
        return

    # Run SQL against both DBs and merge
    results = executor.execute(decomposition.course_sql, decomposition.job_sql)

    # Show all intermediate data
    _print_dataframe("CourseDB results", results["course"], max_rows)
    _print_dataframe("JobDB results", results["job"], max_rows)
    # _print_dataframe("Merged results", results["merged"], max_rows)

    # # Optional: ranked course recommendations (unchanged)
    # ranked_courses = DatabaseExecutor.rank_courses(results["course"], results["job"])
    # if not ranked_courses.empty:
    #     _print_dataframe("Ranked course recommendations", ranked_courses, max_rows)

    # ----------------------------------------------------------------------
    # NEW: Use Innovation #1 ETL-based merging instead of simple prefix-merge
    # ----------------------------------------------------------------------
    from innovation1 import auto_merge_dataframes

    # OLD:
    # merged_df = results["merged"]

    merged_df = auto_merge_dataframes(
        results["course"],
        results["job"],
    )

    _print_dataframe("Merged results (AI-ETL unified)", merged_df, max_rows)

    # ----------------------------------------------------------------------
    # FINAL ANSWER GENERATION (THIS REPLACES THE OLD SUMMARY SYSTEM)
    # ----------------------------------------------------------------------
    # final_answer = executor.generate_final_answer(
    #     results["merged"],
    #     decomposition.natural_query
    # )
    final_answer = executor.generate_final_answer(
        merged_df,
        decomposition.natural_query
    )


    print("\n=== Final Answer ===\n", final_answer)


def main() -> None:
    args = _parse_args()

    # If requested, run a preset batch of difficult queries using the deterministic fallback.
    if args.fallback_batch:
        configure_logging()
        # Use a client=None since we will call the deterministic fallback directly
        analyzer = QueryAnalyzer(client=None)
        executor = DatabaseExecutor()

        batch_queries = [
            "courses that teach React and frontend jobs requiring React",
            "compare software engineering courses that teach cloud skills with frontend jobs requiring cloud integrations",
            "which courses map to frontend jobs requiring TypeScript and 3 to 5 years experience",
            "list courses for BTech graduates and frontend roles that accept BTech",
            "compare salaries between backend software roles and frontend roles for candidates with 5 years experience",
            "find frontend jobs that prefer female candidates and software courses that support leadership skills",
            "which courses help frontend developers become full stack engineers and what job openings match that transition",
            "top skills taught in software courses that match frontend job postings requiring Vue.js or React",
            "frontend jobs with remote work and software courses offering online delivery",
            "courses that teach UX design and frontend jobs seeking UX skills with 2-4 years experience",
        ]

        from innovation1 import auto_merge_dataframes

        for q in batch_queries:
            print("\n=== QUERY ===\n", q)
            res = analyzer._fallback_decomposition(q)
            print("\n-- CourseDB SQL --\n", res.course_sql or "<none>")
            print("\n-- JobDB SQL --\n", res.job_sql or "<none>")

            try:
                outputs = executor.execute(res.course_sql or "", res.job_sql or "")
            except Exception as exc:
                print("Execution failed (DB may be offline or misconfigured):", exc)
                continue

            course_df = outputs.get("course")
            job_df = outputs.get("job")
            merged = auto_merge_dataframes(course_df, job_df)

            course_rows = int(course_df.shape[0]) if course_df is not None and hasattr(course_df, "shape") else 0
            job_rows = int(job_df.shape[0]) if job_df is not None and hasattr(job_df, "shape") else 0
            merged_rows = int(merged.shape[0]) if merged is not None and hasattr(merged, "shape") else 0
            print(f"\nRows: course={course_rows}, job={job_rows}, merged={merged_rows}")

            if merged is not None and hasattr(merged, "empty") and not merged.empty:
                print("\n-- Merged top 5 --")
                print(merged.head(5).to_markdown(index=False))

            print("\n-- Final answer --")
            try:
                print(executor.generate_final_answer(merged, res.natural_query))
            except Exception as exc:
                print("Final answer generation failed (LLM may be misconfigured):", exc)

        sys.exit(0)

    try:
        query = args.query or input("Enter a natural language query: ")
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)

    if not query.strip():
        print("A query is required.")
        sys.exit(1)

    try:
        run_demo(query, max_rows=args.rows)
    except GroqClientError as exc:
        LOGGER.error("LLM failure: %s", exc)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Unexpected error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
