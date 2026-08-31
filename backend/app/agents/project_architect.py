"""Project Architect agent: one mission, each requirement tied to a gap.

See docs/agents.md#5-project-architect. On a revision pass, reads the prior
Validator recommendation and adjusts rather than regenerating from zero.
"""

from app import llm
from app.state import Mission, MissionRequirement, PipelineState

SYSTEM_PROMPT = """You are the Project Architect agent in a career-engineering pipeline.
Design a single real-world project (a "mission") that closes as many of the
student's priority skill gaps as possible.

Rules:
- Prefer extending an existing student project over inventing an unrelated one,
  if a suitable existing project is described in their skill graph evidence.
- Every requirement must explicitly state which gap skill it addresses, using the
  exact skill name given in the gap list.
- Keep the mission achievable as a single project, not a multi-month program.

Respond with JSON:
{"title": str, "brief": str, "requirements": [{"description": str, "addresses_gap": str}]}
"""

REVISION_SYSTEM_PROMPT = SYSTEM_PROMPT + """

This is a revision pass. You will be given the previous mission and a coverage
report naming which gaps remain uncovered, plus a recommendation. Adjust or add
requirements to cover the named gaps. Do not discard requirements that already
cover a gap.
"""


def run(state: PipelineState) -> dict:
    gaps = state["gaps"]
    skill_graph = state.get("skill_graph", [])
    coverage = state.get("coverage")

    gap_lines = "\n".join(f"- {g.skill} (priority: {g.priority})" for g in gaps)
    evidence_lines = "\n".join(f"- {s.name}: {s.evidence}" for s in skill_graph)

    if coverage is None:
        user_prompt = (
            f"Priority gaps:\n{gap_lines}\n\n"
            f"Student's existing skills and evidence:\n{evidence_lines}"
        )
        result = llm.call_json(SYSTEM_PROMPT, user_prompt, max_tokens=1536)
    else:
        previous_mission = state["mission"]
        user_prompt = (
            f"Priority gaps:\n{gap_lines}\n\n"
            f"Student's existing skills and evidence:\n{evidence_lines}\n\n"
            f"Previous mission title: {previous_mission.title}\n"
            f"Previous mission brief: {previous_mission.brief}\n"
            f"Previous requirements: {[r.model_dump() for r in previous_mission.requirements]}\n\n"
            f"Uncovered gaps: {coverage.uncovered_gaps}\n"
            f"Validator recommendation: {coverage.recommendation}"
        )
        result = llm.call_json(REVISION_SYSTEM_PROMPT, user_prompt, max_tokens=1536)

    mission = Mission(
        title=result["title"],
        brief=result["brief"],
        requirements=[MissionRequirement(**r) for r in result["requirements"]],
    )
    return {"mission": mission}
