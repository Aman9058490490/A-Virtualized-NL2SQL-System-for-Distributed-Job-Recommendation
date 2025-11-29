# innovation1.py
"""
Innovation Module #1 — AI-driven ETL merging

This module:
1) Takes 2 dataframes: course_df and job_df.
2) Extracts 2 sample rows from each DB.
3) Sends samples to LLM to generate schema-alignment ETL code.
4) Strips markdown fences from LLM output.
5) Executes generated ETL code safely in a sandbox.
6) Returns df_merged (clean unified dataframe).
"""

from __future__ import annotations
import pandas as pd
import json
import traceback
from typing import Dict, Any

from groq_client import GroqClient



# -----------------------------------------------------------------
# UTILITY: Strip Markdown ```python fences from LLM code output
# -----------------------------------------------------------------
def strip_code_fences(code: str) -> str:
    code = code.strip()

    # If starts with ```... remove first fenced block
    if code.startswith("```"):
        parts = code.split("```")
        if len(parts) >= 2:
            code = parts[1]  # inside fenced block

    # Remove ALL remaining backticks
    code = code.replace("```", "").strip()

    # Remove leading 'python' line if present
    lines = code.splitlines()
    if lines:
        first = lines[0].strip().lower()
        if first == "python" or first.startswith("python"):
            code = "\n".join(lines[1:]).strip()

    return code



# -----------------------------------------------------------------
# STEP 1 — Extract 2 sample rows
# -----------------------------------------------------------------
def extract_samples(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    return df.head(2).to_dict(orient="records")



# -----------------------------------------------------------------
# STEP 2 — LLM: Generate ETL code using sample rows ONLY
# -----------------------------------------------------------------
def generate_etl_code(sample_course: list, sample_job: list) -> str:
    client = GroqClient()

    prompt = f"""
You are a senior Python ETL engineer.

You are given two **real** datasets from two different SQL sources.
Each contains **2 rows only** representing the actual schema.

SOFTWARE_DB_SAMPLE = {json.dumps(sample_course, indent=2)}
FRONTEND_DB_SAMPLE = {json.dumps(sample_job, indent=2)}

Your task:
1. Analyze column names and data patterns.
2. Generate Python ETL code that:
   - Uses ONLY existing variables: df_course and df_job
   - DOES NOT recreate, redefine, overwrite, or assign new values to df_course or df_job
   - DOES NOT load SOFTWARE_DB_SAMPLE or FRONTEND_DB_SAMPLE
   - Harmonizes column names based purely on sample rows
   - Removes prefixes (like se_ / fe_) safely
   - Normalizes datatypes ONLY for columns found in samples
   - Does NOT invent new or nonexistent column names
   - Produces: df_merged = <final merged pandas DataFrame>

STRICT RULES:
- df_course and df_job ALREADY exist.
- DO NOT modify df_course or df_job assignment.
- DO NOT declare new variables named df_course or df_job.
- Allowed imports: pandas, re, numpy.
- DO NOT use filesystem, subprocess, OS, or network calls.
- Output ONLY Python code. NO markdown fences. NO explanation.

Your output MUST end with:
df_merged = <pandas DataFrame>
"""

    response = client.chat(
        [
            {"role": "system", "content": "You generate safe Python ETL code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    if "choices" in response:
        return response["choices"][0]["message"]["content"]

    return str(response)



# -----------------------------------------------------------------
# STEP 3 — Safely execute ETL code in restricted sandbox
# -----------------------------------------------------------------
def execute_etl_code(etl_code: str, df_course: pd.DataFrame, df_job: pd.DataFrame) -> pd.DataFrame:
    # Clean out markdown ``` fences + "python" token
    etl_code_clean = strip_code_fences(etl_code)

    # Restrict imports inside the sandbox to a short allowlist.
    def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        allowed = {"re", "numpy", "pandas"}
        if name in allowed:
            return __import__(name, globals, locals, fromlist, level)
        raise ImportError(f"Import of module '{name}' is not allowed in the ETL sandbox")

    safe_globals: Dict[str, Any] = {
        "__builtins__": {
            # safe builtins only
            "len": len,
            "range": range,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "sorted": sorted,
            "__import__": _safe_import,
            "ValueError": ValueError,
            "Exception": Exception,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "any": any,
            "all": all,
            "enumerate": enumerate,
            "zip": zip,
            "bool": bool,
            "int": int,
            "str": str,
            "float": float,
            "tuple": tuple,         # <-- ADD THIS
            "list": list,           # (OPTIONAL but good)
            "dict": dict,           # (OPTIONAL but safe)
            "set": set,
            "map": map,
            "print": print,
        },
        "pd": pd,
        "re": __import__("re"),
        "np": __import__("numpy"),
        # make the input dataframes available as globals so comprehensions
        # and nested scopes inside exec can access them reliably
        "df_course": df_course.copy(),
        "df_job": df_job.copy(),
    }
    # keep locals minimal to avoid scope issues inside comprehensions
    safe_locals: Dict[str, Any] = {}

    try:
        exec(etl_code_clean, safe_globals, safe_locals)
    except Exception as e:
        print("\n❌ ERROR EXECUTING GENERATED ETL CODE:")
        print("RAW CODE RECEIVED:\n", etl_code)
        print("\nCLEAN CODE EXECUTED:\n", etl_code_clean)
        print("\nEXCEPTION:\n", e)
        print(traceback.format_exc())
        # As a robust fallback, attempt a safe merge by normalizing prefixes
        try:
            sc = df_course.copy()
            sj = df_job.copy()

            def _strip_prefixes(df):
                df2 = df.copy()
                df2.columns = [c.replace("se_", "").replace("fe_", "") for c in df2.columns]
                return df2

            scc = _strip_prefixes(sc) if not sc.empty else pd.DataFrame()
            sjj = _strip_prefixes(sj) if not sj.empty else pd.DataFrame()

            # Align columns and concat
            merged_fallback = pd.concat([scc, sjj], ignore_index=True, sort=True)
            return merged_fallback
        except Exception:
            return pd.DataFrame()

    # ETL code may write df_merged into locals or globals depending on how exec ran.
    if "df_merged" in safe_locals:
        output = safe_locals["df_merged"]
    elif "df_merged" in safe_globals:
        output = safe_globals["df_merged"]
    else:
        print("\n❌ ETL code did NOT define df_merged")
        return pd.DataFrame()

    if not isinstance(output, pd.DataFrame):
        print("\n❌ df_merged is not a pandas DataFrame")
        return pd.DataFrame()

    return output



# -----------------------------------------------------------------
# MAIN ENTRY POINT — called from run_demo.py
# -----------------------------------------------------------------
def auto_merge_dataframes(course_df: pd.DataFrame, job_df: pd.DataFrame) -> pd.DataFrame:

    sample_course = extract_samples(course_df)
    sample_job = extract_samples(job_df)

    # If both DBs are empty → no merge possible
    if not sample_course and not sample_job:
        return pd.DataFrame()

    # Generate ETL Python code from LLM
    etl_code = generate_etl_code(sample_course, sample_job)

    print("\n=== GENERATED ETL CODE (Innovation #1) ===\n")
    print(etl_code)
    print("\n==========================================\n")

    # Execute ETL code
    merged_df = execute_etl_code(etl_code, course_df, job_df)

    return merged_df
