"""Focused tests for the Skill Mapper's closed-set matching, batching, and
caching behavior.

Closed-set matching exists because Gap Analyst only credits a demonstrated
skill when it exactly equals one of the target role's literal requirement
names. An earlier version let the LLM translate concepts into free-form
industry phrasing, which could never exactly match, so a real, evidenced
skill graph could score 0% against every requirement. See skill_mapper.py's
module docstring for the full story; these tests guard against regressing
back to that.

Batching and caching are asserted here directly via a call counter, rather
than indirectly through the full graph, since the full graph's fixtures
don't naturally produce an unmapped concept (see the note in test_graph.py).
"""

import pytest

from app import llm
from app.agents import skill_mapper
from app.state import IndustryRequirements, RequirementSkill, SkillEntry
from app.tools import skill_mapping_cache


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(skill_mapping_cache, "CACHE_PATH", tmp_path / "skill_mapping_cache.json")
    monkeypatch.setattr(skill_mapping_cache, "_cache", None)


def build_state() -> dict:
    return {
        "skill_graph": [
            SkillEntry(name="Computer Vision", evidence="course, no project evidence", confidence="low"),
            SkillEntry(name="Python", evidence="capstone project", confidence="high"),
        ],
        "industry_requirements": IndustryRequirements(
            role="ML Engineer",
            skills=[RequirementSkill(name="Python", frequency=1.0), RequirementSkill(name="Docker", frequency=0.8)],
            tools=[],
            responsibilities=[],
        ),
    }


def test_unmapped_concepts_are_batched_into_a_single_call(monkeypatch):
    call_count = {"n": 0}

    def fake_call_json(system: str, user: str, **kwargs) -> dict:
        call_count["n"] += 1
        assert "Computer Vision" in user
        assert "Python" in system and "Docker" in system  # closed set is in the prompt
        return {"mappings": []}  # a CV course alone doesn't evidence Python or Docker

    monkeypatch.setattr(llm, "call_json", fake_call_json)

    result = skill_mapper.run(build_state())

    assert call_count["n"] == 1
    taxonomy_hits = {m.academic_concept for m in result["skill_map"] if m.source == "taxonomy"}
    assert "Python" in taxonomy_hits  # Python is in the closed set and matches itself for free
    inferred = {m.academic_concept for m in result["skill_map"] if m.source == "inferred"}
    assert "Computer Vision" not in inferred  # correctly not credited toward anything


def test_model_cannot_invent_a_name_outside_the_closed_set(monkeypatch):
    def fake_call_json(system: str, user: str, **kwargs) -> dict:
        return {"mappings": [{"academic_concept": "Computer Vision", "industry_skill": "computer vision / real-time inference"}]}

    monkeypatch.setattr(llm, "call_json", fake_call_json)

    result = skill_mapper.run(build_state())

    # "computer vision / real-time inference" isn't one of the two required
    # skills (Python, Docker), so it must be dropped, not passed through.
    assert all(m.industry_skill in {"Python", "Docker"} for m in result["skill_map"])
    assert not any(m.academic_concept == "Computer Vision" for m in result["skill_map"])


def test_second_run_reuses_the_cache_and_makes_no_new_call(monkeypatch):
    call_count = {"n": 0}

    def fake_call_json(system: str, user: str, **kwargs) -> dict:
        call_count["n"] += 1
        return {"mappings": [{"academic_concept": "Computer Vision", "industry_skill": "Docker"}]}

    monkeypatch.setattr(llm, "call_json", fake_call_json)

    skill_mapper.run(build_state())
    assert call_count["n"] == 1

    second_result = skill_mapper.run(build_state())
    assert call_count["n"] == 1  # served from cache, no second LLM call

    inferred = {m.academic_concept: m.industry_skill for m in second_result["skill_map"] if m.source == "inferred"}
    assert inferred["Computer Vision"] == "Docker"
