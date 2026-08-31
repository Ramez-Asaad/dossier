"""Profiler agent: what can this student actually do, with evidence.

See docs/agents.md#1-profiler.
"""

from app import llm
from app.state import PipelineState, SkillEntry
from app.tools.github_tool import fetch_repo_summaries

SYSTEM_PROMPT = """You are the Profiler agent in a career-engineering pipeline.
Given a student's courses, project descriptions, and GitHub repo evidence, extract
the skills they can actually demonstrate, not just what they've been exposed to.

Rules:
- Every skill must cite specific evidence: the exact course, project, or repo it
  came from.
- A course title mentioning a topic, with no corroborating project, is "low"
  confidence. A described project that clearly uses the skill is "medium". A
  GitHub repo that corroborates the skill (language, dependencies, README) is
  "high".
- Never invent a skill with no evidence trail.

Respond with JSON: {"skills": [{"name": str, "evidence": str, "confidence": "low"|"medium"|"high"}]}
"""


def run(state: PipelineState) -> dict:
    profile = state["student_profile"]
    repo_context, github_fetch_issues = fetch_repo_summaries(profile.github_urls)

    user_prompt = (
        f"Courses:\n{_bulleted(profile.raw_courses)}\n\n"
        f"Projects:\n{_bulleted(profile.raw_projects)}\n\n"
        f"GitHub evidence:\n{repo_context}"
    )

    result = llm.call_json(SYSTEM_PROMPT, user_prompt, max_tokens=768)
    skills = [SkillEntry(**entry) for entry in result.get("skills", [])]
    return {"skill_graph": skills, "github_fetch_issues": github_fetch_issues}


def _bulleted(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "(none provided)"
