"""Run several queries through the deterministic fallback and show results.

This script calls `QueryAnalyzer._fallback_decomposition` directly (bypassing
the LLM) so you can inspect the SQL produced by the fallback and see how the
executor handles it end-to-end.
"""
from __future__ import annotations

from query_analyzer import QueryAnalyzer
from executor import DatabaseExecutor

def run_example(query: str, analyzer: QueryAnalyzer, executor: DatabaseExecutor):
    print("\n=== QUERY ===")
    print(query)
    print("--- Fallback decomposition (SQL) ---")
    result = analyzer._fallback_decomposition(query)
    print("Course DB SQL:\n", result.course_sql or "<none>")
    print("Job DB SQL:\n", result.job_sql or "<none>")

    print("--- Executing SQL ---")
    try:
        outputs = executor.execute(result.course_sql or "", result.job_sql or "")
    except Exception as exc:
        print("Execution failed (DB may be offline or misconfigured):", exc)
        return

    course_df = outputs.get("course")
    job_df = outputs.get("job")
    merged = outputs.get("merged")

    print(f"Course rows: {len(course_df) if course_df is not None else 0}")
    print(f"Job rows: {len(job_df) if job_df is not None else 0}")
    print(f"Merged rows: {len(merged) if merged is not None else 0}")

    if not merged.empty:
        print("\n--- Merged (top 5) ---")
        print(merged.head(5).to_markdown(index=False))

    print("\n--- Final answer (LLM) ---")
    try:
        answer = executor.generate_final_answer(merged, result.natural_query)
        print(answer)
    except Exception as exc:
        print("Final answer generation failed (LLM may be misconfigured):", exc)


def main():
    # Instantiate analyzer and executor. We don't need a working LLM client
    # because we'll call the deterministic fallback directly.
    analyzer = QueryAnalyzer(client=None)
    executor = DatabaseExecutor()

    queries = [
        # Qualification-focused (should produce multiple LIKE variants)
        "frontend jobs for MTech candidates with 2 to 3 years experience",

        # Experience range-focused
        "frontend roles with 4-6 years experience",

        # Generic role that should match both DBs when relevant
        "courses to become a data scientist",

        # Preference / filter example
        "jobs that prefer female candidates",
    ]

    for q in queries:
        run_example(q, analyzer, executor)


if __name__ == "__main__":
    main()
