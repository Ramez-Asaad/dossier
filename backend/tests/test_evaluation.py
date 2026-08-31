"""Offline, mocked sanity check of the evaluation harness itself: does the
scoring plumbing in scripts/run_evaluation.py run cleanly over the real
10-profile dataset and produce bounded, well-formed numbers.

This does not exercise real model quality (llm.call_json is mocked, same
approach as tests/test_graph.py), so it is not a substitute for
`python -m scripts.run_evaluation` with a real API key.
"""

import re

import pytest

from app import llm
from app.graph import build_graph
from app.tools import skill_mapping_cache
from scripts.run_evaluation import evaluate_profile, load_profiles


def _parse_gap_skills(user_prompt: str) -> list[str]:
    return re.findall(r"^- (.+?) \(priority: \w+\)$", user_prompt, flags=re.MULTILINE)


@pytest.fixture(autouse=True)
def isolated_skill_mapping_cache(tmp_path, monkeypatch):
    # Defensive: nothing in the current fixtures should trigger a Skill Mapper
    # LLM call (see the note on the Skill Mapper branch below), but if a
    # future profile or dataset change does, this keeps the write out of the
    # real backend/app/data/ directory.
    monkeypatch.setattr(skill_mapping_cache, "CACHE_PATH", tmp_path / "skill_mapping_cache.json")
    monkeypatch.setattr(skill_mapping_cache, "_cache", None)


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    def fake_call_json(system: str, user: str, **kwargs) -> dict:
        if "Profiler agent" in system:
            return {"skills": [{"name": "Python", "evidence": "student projects", "confidence": "medium"}]}
        if "Skill Mapper agent" in system:
            # Not expected to be hit today: the taxonomy already covers every
            # concept these fixtures produce (see test_graph.py's note).
            concepts = re.findall(r"^- (.+)$", user, flags=re.MULTILINE)
            return {"mappings": [{"academic_concept": c, "industry_skill": c} for c in concepts]}
        if "Project Architect agent" in system:
            gap_skills = _parse_gap_skills(user)
            return {
                "title": "Generated mission",
                "brief": "Covers the computed priority gaps.",
                "requirements": [{"description": f"Demonstrate {skill}", "addresses_gap": skill} for skill in gap_skills],
            }
        if "Validator agent" in system:
            return {"recommendation": "add a requirement covering the named gap"}
        if "career advice assistant" in system:
            return {
                "demonstrated_skills": ["Python"],
                "priority_gaps": ["productionization"],
                "recommended_project": {
                    "title": "Build something with your existing skills",
                    "description": "A generic follow-on project using the student's current tools.",
                },
            }
        raise AssertionError(f"Unexpected system prompt: {system[:60]}")

    monkeypatch.setattr(llm, "call_json", fake_call_json)


def test_all_ten_profiles_present():
    profiles = load_profiles()
    assert len(profiles) == 10
    assert len({p["id"] for p in profiles}) == 10


def test_evaluate_profile_produces_bounded_coverage():
    graph = build_graph()
    for profile in load_profiles():
        result = evaluate_profile(profile, graph)
        assert 0.0 <= result["baseline_coverage"] <= 1.0
        assert 0.0 <= result["agent_coverage"] <= 1.0
        assert result["id"] == profile["id"]
