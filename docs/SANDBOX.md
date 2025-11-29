ETL exec sandbox (innovation1)

This file documents the safe execution sandbox used by `innovation1.execute_etl_code`.

Allowed builtins and objects

- print: Allowed for debugging and safe output within generated ETL code.
- len, range, min, max, sum, abs, sorted: standard safe builtins for data processing.
- int, str, float, tuple, list, dict, set, map: basic types and collections.

Globals provided to executed code

- `pd`: the pandas module
- `re`: the regular expressions module
- `np`: the numpy module
- `df_course`: a copy of the course dataframe provided as input
- `df_job`: a copy of the job dataframe provided as input

Rationale

- The sandbox intentionally exposes a minimal set of builtins to reduce risk while allowing common
  ETL operations and comprehensions.
- Dataframes are provided in `globals()` (not `locals()`) to ensure nested functions and comprehensions
  inside generated code can access them.

Security notes

- The sandbox is not a full security boundary. It prevents file / network / subprocess calls by omitting
  those capabilities from builtins and not exposing `os`, `sys`, or similar modules.
- Never execute untrusted code in a production environment without a proper sandboxing mechanism (e.g., separate process with OS-level restrictions).

If you need additional helpers (e.g., `datetime` parsing), add them explicitly here and justify why they are safe.