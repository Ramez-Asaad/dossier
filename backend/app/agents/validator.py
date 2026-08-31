"""Validator agent: does the mission actually cover the priority gaps.

Coverage itself is a deterministic set comparison against the explicit
addresses_gap field each mission requirement carries (see
project_architect.py); the LLM is only asked for a concrete recommendation
when gaps remain uncovered. This agent never rewrites the mission itself,
per docs/agents.md#6-validator: keeping assessment and generation separate
is what makes the revision loop meaningful.
"""

from app import llm
from app.state import CoverageReport, PipelineState

SYSTEM_PROMPT = """You are the Validator agent in a career-engineering pipeline.
A mission failed to cover one or more priority skill gaps. Given the uncovered
gap and the existing mission, propose one concrete, specific addition to the
mission that would demonstrate that gap. Do not rewrite the whole mission.

Respond with JSON: {"recommendation": str}
"""


def run(state: PipelineState) -> dict:
    gap_skills = {g.skill for g in state["gaps"]}
    addressed_skills = {r.addresses_gap for r in state["mission"].requirements}

    covered = sorted(gap_skills & addressed_skills)
    uncovered = sorted(gap_skills - addressed_skills)

    recommendation = None
    if uncovered:
        user_prompt = (
            f"Mission title: {state['mission'].title}\n"
            f"Mission brief: {state['mission'].brief}\n"
            f"Uncovered gap (highest priority first): {uncovered[0]}"
        )
        result = llm.call_json(SYSTEM_PROMPT, user_prompt, max_tokens=256)
        recommendation = result["recommendation"]

    coverage = CoverageReport(covered_gaps=covered, uncovered_gaps=uncovered, recommendation=recommendation)
    return {"coverage": coverage, "revision_count": state.get("revision_count", 0) + 1}
