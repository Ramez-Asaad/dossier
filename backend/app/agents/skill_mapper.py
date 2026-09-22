"""Skill Mapper agent: does a student's concept provide evidence for one of
the target role's actually-required skills.

This is a closed-set decision, not a free translation. Gap Analyst only
credits a demonstrated skill when its mapped industry_skill exactly equals
one of `industry_requirements.skills`' literal names (see gap_analyst.py). An
earlier version translated concepts into free-form industry phrasing
("Computer Vision" -> "computer vision / real-time inference"), which could
never exactly match a job posting's literal skill name ("Docker", "Python"),
so a real, evidenced skill graph could score 0% against every requirement,
because none of its mapped names could ever equal any of them. Constraining
the model's output to the actual candidate list for this role fixes that.

Three tiers, cheapest first: taxonomy identity lookup (deterministic, zero
LLM calls, only counts if it lands inside this role's closed set), the
on-disk inference cache keyed by (role, concept) since the closed set is
role-dependent, then a single batched LLM call for whatever's left.
See docs/agents.md#3-skill-mapper.
"""

from app import llm
from app.state import PipelineState, SkillMapping
from app.tools import skill_mapping_cache
from app.tools.skill_taxonomy import lookup

SYSTEM_PROMPT_TEMPLATE = """You are the Skill Mapper agent in a career-engineering pipeline.
You are given a list of things a student has demonstrated (courses, skills, or
project topics) and the closed list of skills a target job role actually requires.
For each student concept, decide whether it provides genuine, direct evidence the
student can do ONE of the required skills. Only match a concept to a required
skill if there's a real, direct connection: a Computer Vision course is not
evidence of Docker, and a Statistics course is not evidence of SQL. If a concept
doesn't provide direct evidence for any required skill, leave it out of your
response entirely rather than guessing the closest one.

Required skills for this role:
{skills}

Respond with JSON:
{{"mappings": [{{"academic_concept": str, "industry_skill": str}}]}}

Every "industry_skill" value must be copied exactly, character for character,
from the required skills list above. Never invent a name that isn't in that list.
"""


def run(state: PipelineState) -> dict:
    role = state["industry_requirements"].role
    required_skills = [s.name for s in state["industry_requirements"].skills]
    required_by_lower = {s.lower(): s for s in required_skills}

    concepts = {entry.name for entry in state.get("skill_graph", [])}
    concepts.update(required_skills)  # identity fast-path for the requirements themselves

    mappings: list[SkillMapping] = []
    unmapped: list[str] = []
    for concept in sorted(concepts):
        taxonomy_hit = lookup(concept)
        if taxonomy_hit and taxonomy_hit.lower() in required_by_lower:
            mappings.append(
                SkillMapping(academic_concept=concept, industry_skill=required_by_lower[taxonomy_hit.lower()], source="taxonomy")
            )
            continue
        cache_hit = skill_mapping_cache.get(role, concept)
        if cache_hit:
            mappings.append(SkillMapping(academic_concept=concept, industry_skill=cache_hit, source="inferred"))
        else:
            unmapped.append(concept)

    if unmapped and required_skills:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(skills="\n".join(f"- {s}" for s in required_skills))
        user_prompt = "Student concepts:\n" + "\n".join(f"- {concept}" for concept in unmapped)
        result = llm.call_json(system_prompt, user_prompt, agent_name="skill_mapper", max_tokens=1024)

        newly_inferred: dict[str, str] = {}
        for item in result.get("mappings", []):
            concept = item["academic_concept"]
            industry_skill = item["industry_skill"]
            canonical = required_by_lower.get(industry_skill.lower())
            if canonical is None:
                continue  # guard: model invented a name outside the closed set, drop it
            mappings.append(SkillMapping(academic_concept=concept, industry_skill=canonical, source="inferred"))
            newly_inferred[concept] = canonical
        skill_mapping_cache.put_many(role, newly_inferred)

    return {"skill_map": mappings}
