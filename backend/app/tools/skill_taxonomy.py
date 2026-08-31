"""Loads the academic-to-industry skill taxonomy used by the Skill Mapper."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "skill_taxonomy.json"

_taxonomy: dict[str, str] | None = None


def load_taxonomy() -> dict[str, str]:
    global _taxonomy
    if _taxonomy is None:
        _taxonomy = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return _taxonomy


def lookup(academic_concept: str) -> str | None:
    """Case-insensitive exact-key lookup. Returns None if the taxonomy has no entry."""
    taxonomy = load_taxonomy()
    target = academic_concept.strip().lower()
    for key, value in taxonomy.items():
        if key.strip().lower() == target:
            return value
    return None
