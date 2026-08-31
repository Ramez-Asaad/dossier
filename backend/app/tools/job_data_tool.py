"""Loads the static, curated job postings dataset.

Deliberately static, not a live scraper: see NFR-5 in docs/requirements.md.
Add a new role by dropping a JSON file in app/data/job_postings/, no code
change needed.
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "job_postings"


def _slugify(role: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", role.strip().lower()).strip("_")


def available_roles() -> list[str]:
    return sorted(p.stem for p in DATA_DIR.glob("*.json"))


def load_postings(role: str) -> dict:
    slug = _slugify(role)
    path = DATA_DIR / f"{slug}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No job postings dataset for role '{role}' (looked for {path.name}). "
            f"Available roles: {', '.join(available_roles())}"
        )
    return json.loads(path.read_text(encoding="utf-8"))
