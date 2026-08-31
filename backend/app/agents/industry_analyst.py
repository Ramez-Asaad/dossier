"""Industry Analyst agent: what does the target role actually require.

Deterministic aggregation over the static job postings dataset, no LLM call.
Frequency is a signal the Gap Analyst weighs, not a ranking this agent
produces itself; see docs/agents.md#2-industry-analyst.
"""

from collections import Counter

from app.state import IndustryRequirements, PipelineState, RequirementSkill
from app.tools.job_data_tool import load_postings


def run(state: PipelineState) -> dict:
    role = state["student_profile"].target_role
    if not role:
        role = _infer_role_from_job_description(state["student_profile"].target_job_description)

    dataset = load_postings(role)
    postings = dataset["postings"]
    total = len(postings)

    skill_counts = Counter()
    tool_counts = Counter()
    responsibilities: set[str] = set()

    for posting in postings:
        skill_counts.update(set(posting.get("skills", [])))
        tool_counts.update(set(posting.get("tools", [])))
        responsibilities.update(posting.get("responsibilities", []))

    requirements = IndustryRequirements(
        role=dataset["role"],
        skills=[
            RequirementSkill(name=name, frequency=round(count / total, 2))
            for name, count in skill_counts.most_common()
        ],
        tools=[
            RequirementSkill(name=name, frequency=round(count / total, 2))
            for name, count in tool_counts.most_common()
        ],
        responsibilities=sorted(responsibilities),
    )
    return {"industry_requirements": requirements}


def _infer_role_from_job_description(description: str | None) -> str:
    if not description:
        raise ValueError("Student profile has neither target_role nor target_job_description set.")
    # For the MVP dataset (4 curated roles) a keyword match is enough; a live
    # deployment with a broader role dataset would use the LLM here instead.
    lowered = description.lower()
    for role in ["computer vision engineer", "nlp engineer", "ai engineer", "ml engineer", "machine learning engineer"]:
        if role in lowered:
            return "ML Engineer" if "machine learning" in role else role
    raise ValueError("Could not infer a known role from the job description; pass target_role explicitly.")
