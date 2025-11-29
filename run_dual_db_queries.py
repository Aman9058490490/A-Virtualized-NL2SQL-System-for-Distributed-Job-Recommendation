"""Run challenging queries that require both CourseDB and JobDB integration.

This script uses the deterministic fallback (`_fallback_decomposition`) so the
SQL is produced reliably without depending on the LLM. It executes both SQL
against the configured databases and prints merged results and a final answer
from the project's `generate_final_answer` method.
"""
from __future__ import annotations

from query_analyzer import QueryAnalyzer
from executor import DatabaseExecutor


def run_query(q: str, analyzer: QueryAnalyzer, executor: DatabaseExecutor):
    print("\n=== QUERY ===")
    print(q)
    res = analyzer._fallback_decomposition(q)
    print("\n-- CourseDB SQL --\n", res.course_sql or "<none>")
    print("\n-- JobDB SQL --\n", res.job_sql or "<none>")

    try:
        outputs = executor.execute(res.course_sql or "", res.job_sql or "")
    except Exception as exc:
        print("Execution error (DB may be offline):", exc)
        return

    merged = outputs.get("merged")
    course_df = outputs.get("course")
    job_df = outputs.get("job")
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
        print("Final answer generation failed:", exc)


def main():
    analyzer = QueryAnalyzer(client=None)
    executor = DatabaseExecutor()

    queries = [
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

    for q in queries:
        run_query(q, analyzer, executor)


if __name__ == "__main__":
    main()
