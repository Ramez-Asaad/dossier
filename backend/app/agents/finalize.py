"""Finalize node: assembles the final plan the student sees.

Not an LLM agent, just an assembly step over already-computed state. See
docs/architecture.md for the fields this produces.
"""

from app.state import PipelineState


def run(state: PipelineState) -> dict:
    gaps = state["gaps"]
    coverage = state["coverage"]
    total_gaps = len(gaps)
    covered = len(coverage.covered_gaps)
    readiness = round(100 * covered / total_gaps) if total_gaps else 100

    final_plan = {
        "target_role": state["industry_requirements"].role,
        "readiness_percent": readiness,
        "demonstrated_skills": [s.model_dump() for s in state.get("skill_graph", [])],
        "priority_gaps": [g.model_dump() for g in gaps],
        "mission": state["mission"].model_dump(),
        "coverage": coverage.model_dump(),
        "revisions_used": state.get("revision_count", 0),
        "fully_covered": not coverage.uncovered_gaps,
        "github_fetch_issues": state.get("github_fetch_issues", []),
    }
    return {"final_plan": final_plan}
