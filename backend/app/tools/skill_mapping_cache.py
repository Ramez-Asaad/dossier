"""On-disk memoization for Skill Mapper's LLM-inferred concept mappings.

Keyed by (role, concept), not concept alone: whether a concept maps to a
required skill depends on the closed set of skills that role requires (see
skill_mapper.py), so the same concept can have a different, or no, mapping
for a different target role.

Not for taxonomy hits, those are already free (see skill_taxonomy.py); this
cache only holds concepts the taxonomy didn't cover for this role.
"""

import json
from pathlib import Path

CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "skill_mapping_cache.json"

_cache: dict[str, str] | None = None


def _key(role: str, concept: str) -> str:
    return f"{role.strip().lower()}::{concept.strip().lower()}"


def _load() -> dict[str, str]:
    global _cache
    if _cache is None:
        if CACHE_PATH.exists():
            _cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        else:
            _cache = {}
    return _cache


def get(role: str, concept: str) -> str | None:
    return _load().get(_key(role, concept))


def put_many(role: str, mappings: dict[str, str]) -> None:
    if not mappings:
        return
    cache = _load()
    cache.update({_key(role, concept): industry_skill for concept, industry_skill in mappings.items()})
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
