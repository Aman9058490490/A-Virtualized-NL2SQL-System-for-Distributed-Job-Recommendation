"""Utility helpers for the federated NL-to-SQL project."""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Set

from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)

CODE_FENCE_PATTERN = re.compile(r"```(json)?(.*?)```", re.IGNORECASE | re.DOTALL)
JSON_OBJECT_PATTERN = re.compile(r"\{.*\}", re.DOTALL)
MULTI_SPACE_PATTERN = re.compile(r"\s+")
FORBIDDEN_SQL_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|REPLACE)\b",
    re.IGNORECASE,
)
SELECT_PREFIX = re.compile(r"^\s*SELECT\b", re.IGNORECASE)
SKILL_SPLIT_PATTERN = re.compile(r"[,/;\|]+")


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger if not already set."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    else:
        logging.getLogger().setLevel(level)


def strip_code_fences(text: str) -> str:
    match = CODE_FENCE_PATTERN.search(text)
    if match:
        return match.group(2).strip()
    return text.strip()


def _replace_single_quotes(json_text: str) -> str:
    # Replace single quotes surrounding keys/values when double quotes are absent.
    return re.sub(r"'([^']*)'", lambda m: '"' + m.group(1) + '"', json_text)


def load_json_response(raw_text: str) -> Dict[str, Any]:
    """Parse JSON text emitted by the LLM with common cleanup heuristics."""
    text = strip_code_fences(raw_text)
    for candidate in (text, _replace_single_quotes(text)):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    match = JSON_OBJECT_PATTERN.search(text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    raise ValueError("LLM response is not valid JSON: %s" % raw_text[:200])


def normalize_sql_whitespace(sql: str) -> str:
    return MULTI_SPACE_PATTERN.sub(" ", sql or "").strip()


def is_safe_sql(sql: str) -> bool:
    if not sql:
        return True
    sanitized = sql.strip()
    if not SELECT_PREFIX.match(sanitized):
        return False
    if ";" in sanitized[:-1]:
        # Reject multiple statements; allow optional trailing semicolon.
        return False
    return FORBIDDEN_SQL_PATTERN.search(sanitized) is None


def ensure_safe_sql(sql: str) -> str:
    if not is_safe_sql(sql):
        raise ValueError("Only read-only SELECT statements are permitted.")
    return sql


def tokenize_skills(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        for token in SKILL_SPLIT_PATTERN.split(value):
            token = token.strip()
            if token:
                yield token
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            if item is None:
                continue
            token = str(item).strip()
            if token:
                yield token


def collect_skill_set(records: Sequence[Dict[str, Any]], columns: Iterable[str] | None = None) -> Set[str]:
    skill_set: Set[str] = set()
    normalized_columns = None if columns is None else {col.lower() for col in columns}
    for record in records:
        for key, value in record.items():
            if normalized_columns is not None and key.lower() not in normalized_columns:
                continue
            if "skill" not in key.lower():
                continue
            for token in tokenize_skills(value):
                skill_set.add(token.lower())
    return skill_set


def collect_course_skill_map(
    records: Sequence[Dict[str, Any]],
    course_id_key: str = "course_id",
    alias_keys: Iterable[str] | None = ("course_name",),
) -> Dict[str, Set[str]]:
    mapping: Dict[str, Set[str]] = {}
    normalized_alias = None if alias_keys is None else [alias for alias in alias_keys]
    for record in records:
        keys: List[str] = []
        primary = record.get(course_id_key)
        if primary:
            keys.append(str(primary))
        if normalized_alias:
            for alias in normalized_alias:
                alias_value = record.get(alias)
                if alias_value:
                    keys.append(str(alias_value))
        if not keys:
            continue

        skill_tokens: Set[str] = set()
        for key, value in record.items():
            if "skill" not in key.lower():
                continue
            for token in tokenize_skills(value):
                skill_tokens.add(token.lower())

        if not skill_tokens:
            continue

        for identifier in keys:
            mapping.setdefault(identifier, set()).update(skill_tokens)
    return mapping


def load_database_config(prefix: str) -> DatabaseConfig:
    """Load database credentials from environment variables using a prefix."""
    load_dotenv()
    host = os.getenv(f"{prefix}_HOST", "localhost")
    port = int(os.getenv(f"{prefix}_PORT", "3306"))
    user = os.getenv(f"{prefix}_USER", "root")
    password = os.getenv(f"{prefix}_PASSWORD", "")
    database = os.getenv(f"{prefix}_NAME")
    if not database:
        raise ValueError(
            f"Missing environment variable {prefix}_NAME specifying the database name"
        )
    return DatabaseConfig(host=host, port=port, user=user, password=password, database=database)


def extract_text_columns(rows: Sequence[Dict[str, Any]], columns: Iterable[str]) -> str:
    """Combine text fields for summarization prompts."""
    collected: list[str] = []
    for row in rows:
        for column in columns:
            value = row.get(column)
            if value:
                collected.append(str(value))
    return "\n".join(collected)


# ------------------------------------------------------------------
# Qualification normalization helpers
# ------------------------------------------------------------------
def _normalize_degree_text(text: str) -> str:
    """Lowercase and strip punctuation/spaces from degree text for matching."""
    if text is None:
        return ""
    s = str(text).lower()
    # replace common punctuation with space then remove extra spaces
    s = re.sub(r"[\.\-_,]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def qualification_like_patterns(qual: str) -> List[str]:
    """Return a list of SQL LIKE patterns (lowercase) to match common variants.

    Example: 'M.Tech' -> ["%mtech%","%m.tech%","%m tech%","%m tech%"]
    """
    if not qual:
        return []
    base = _normalize_degree_text(qual)
    patterns = set()

    # bare letters/digits
    compact = re.sub(r"\s+", "", base)
    patterns.add(f"%{compact}%")

    # dotted and spaced variants
    dotted = base.replace(" ", ".")
    spaced = base.replace(".", " ")
    patterns.add(f"%{dotted}%")
    patterns.add(f"%{spaced}%")

    # also include the original lowercased form
    patterns.add(f"%{base}%")

    # return sorted list for determinism
    return sorted(patterns)


def qualification_variants(term: str) -> list:
    """Return common LIKE variants for a qualification term.

    Example: 'M.Tech' -> ['mtech', 'm.tech', 'm tech']
    All variants are lower-cased and suitable for use inside SQL LIKE.
    """
    if not term:
        return []
    t = term.strip().lower()
    variants = set()

    # remove dots and spaces
    compact = re.sub(r"[\.\s]", "", t)
    variants.add(compact)

    # with dot between letter and tech (m.tech)
    variants.add(re.sub(r"\s+", " ", t))

    # spaced form (m tech)
    spaced = re.sub(r"\.", " ", t)
    variants.add(spaced)

    # also include raw letters only (e.g., mtech)
    variants.add(compact)

    # include versions without dots or spaces
    variants.add(compact.replace(" ", ""))

    # return sorted list for deterministic ordering
    return sorted(list(variants))
