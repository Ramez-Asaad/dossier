"""The baseline system for the hackathon comparison: a single LLM call,
no pipeline. See docs/evaluation.md for why this exists and how it's scored
against the agent.
"""

from app import llm
from app.state import StudentProfile

SYSTEM_PROMPT = """You are a career advice assistant. A student gives you their
courses, projects, GitHub links, and a target role or job description.
Analyze the student's skills and recommend what they should learn or build to
become qualified for the role.

Respond with JSON:
{"demonstrated_skills": [str],
 "priority_gaps": [str],
 "recommended_project": {"title": str, "description": str}}
"""


def run_baseline(profile: StudentProfile) -> dict:
    target = profile.target_role or profile.target_job_description or "(no target given)"
    user_prompt = (
        f"Courses:\n{_bulleted(profile.raw_courses)}\n\n"
        f"Projects:\n{_bulleted(profile.raw_projects)}\n\n"
        f"GitHub links:\n{_bulleted(profile.github_urls)}\n\n"
        f"Target: {target}"
    )
    return llm.call_json(SYSTEM_PROMPT, user_prompt, max_tokens=1024)


def _bulleted(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "(none provided)"
