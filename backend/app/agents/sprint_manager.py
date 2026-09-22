"""Sprint Manager agent: Phase 2, stretch goal. See docs/agents.md#7-sprint-manager.

Not wired into the Phase 1 graph. Called directly from the sprint-submit API
route once a mission has been split into sprints.
"""

from app import llm

SYSTEM_PROMPT = """You are the Sprint Manager agent, acting as an engineering manager
reviewing a student's actual submitted work for one sprint of their mission.

Evaluate the submission against the sprint's own stated requirements only, not
generic code-quality opinions. For each requirement, decide pass, fail, or
partial, and give specific, actionable feedback naming the exact missing piece
(for example "missing input validation"), not vague criticism.

Respond with JSON:
{"results": [{"requirement": str, "status": "pass"|"fail"|"partial", "feedback": str}],
 "next_sprint_unlocked": bool}
"""


def evaluate_submission(sprint_requirements: list[str], submission_description: str) -> dict:
    user_prompt = (
        f"Sprint requirements:\n" + "\n".join(f"- {r}" for r in sprint_requirements) + "\n\n"
        f"Student submission:\n{submission_description}"
    )
    return llm.call_json(SYSTEM_PROMPT, user_prompt, agent_name="sprint_manager", max_tokens=768)
