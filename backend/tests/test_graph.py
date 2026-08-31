"""Smoke tests for the Phase 1 graph.

Monkeypatches app.llm.call_json (agents call it via the `llm` module, not a
direct import, specifically so this works without a live API key or network
access) and points the job data / skill taxonomy tools at fixture data.

The Skill Mapper branch below is rarely exercised by these two tests: with
the taxonomy expanded to cover the ml_engineer.json vocabulary (see
backend/app/data/skill_taxonomy.json), every concept in play here resolves
via taxonomy lookup with zero LLM calls. It's kept here so the fake still
answers correctly if that stops being true. See tests/test_skill_mapper.py
for a focused test of the batched-call and cache behavior itself.
"""

import re

import pytest

from app import llm
from app.graph import build_graph
from app.state import StudentProfile


def _parse_gap_skills(user_prompt: str) -> list[str]:
    return re.findall(r"^- (.+?) \(priority: \w+\)$", user_prompt, flags=re.MULTILINE)


@pytest.fixture
def student_profile() -> StudentProfile:
    return StudentProfile(
        raw_courses=["Neural Networks", "Database Management"],
        raw_projects=["Image classifier built with PyTorch, trained on a public dataset"],
        github_urls=[],
        target_role="ML Engineer",
    )


def test_full_coverage_on_first_pass(monkeypatch, student_profile):
    def fake_call_json(system: str, user: str, **kwargs) -> dict:
        if "Profiler agent" in system:
            return {
                "skills": [
                    {"name": "Python", "evidence": "Image classifier project", "confidence": "medium"},
                    {"name": "PyTorch", "evidence": "Image classifier project", "confidence": "medium"},
                ]
            }
        if "Skill Mapper agent" in system:
            concepts = re.findall(r"^- (.+)$", user, flags=re.MULTILINE)
            return {"mappings": [{"academic_concept": c, "industry_skill": c} for c in concepts]}
        if "Project Architect agent" in system:
            gap_skills = _parse_gap_skills(user)
            return {
                "title": "Productionize the Image Classifier",
                "brief": "Turn the existing classifier into a monitored inference service.",
                "requirements": [{"description": f"Demonstrate {skill}", "addresses_gap": skill} for skill in gap_skills],
            }
        if "Validator agent" in system:
            return {"recommendation": "add a requirement covering the named gap"}
        raise AssertionError(f"Unexpected system prompt: {system[:60]}")

    monkeypatch.setattr(llm, "call_json", fake_call_json)

    result = build_graph().invoke({"student_profile": student_profile})
    plan = result["final_plan"]

    assert plan["fully_covered"] is True
    assert plan["revisions_used"] == 1
    assert plan["readiness_percent"] == 100
    assert plan["mission"]["title"] == "Productionize the Image Classifier"


def test_revision_loop_fills_remaining_gap(monkeypatch, student_profile):
    call_count = {"architect": 0}

    def fake_call_json(system: str, user: str, **kwargs) -> dict:
        if "Profiler agent" in system:
            return {"skills": [{"name": "Python", "evidence": "Image classifier project", "confidence": "medium"}]}
        if "Skill Mapper agent" in system:
            concepts = re.findall(r"^- (.+)$", user, flags=re.MULTILINE)
            return {"mappings": [{"academic_concept": c, "industry_skill": c} for c in concepts]}
        if "Project Architect agent" in system:
            call_count["architect"] += 1
            gap_skills = _parse_gap_skills(user)
            if call_count["architect"] == 1:
                gap_skills = gap_skills[:-1]  # deliberately drop one gap on the first pass
            return {
                "title": "Productionize the Image Classifier",
                "brief": "Turn the existing classifier into a monitored inference service.",
                "requirements": [{"description": f"Demonstrate {skill}", "addresses_gap": skill} for skill in gap_skills],
            }
        if "Validator agent" in system:
            return {"recommendation": "add a requirement covering the named gap"}
        raise AssertionError(f"Unexpected system prompt: {system[:60]}")

    monkeypatch.setattr(llm, "call_json", fake_call_json)

    result = build_graph().invoke({"student_profile": student_profile})
    plan = result["final_plan"]

    assert call_count["architect"] == 2
    assert plan["fully_covered"] is True
    assert plan["revisions_used"] == 2
