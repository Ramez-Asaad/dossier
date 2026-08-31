"""Gap Analyst agent: prioritized, not exhaustive, gap list.

Deterministic scoring, no LLM call. Priority weighs market importance,
current level, and gap size; frequency alone never decides priority.
See docs/agents.md#4-gap-analyst.
"""

from app.state import GapEntry, PipelineState

MAX_GAPS = 6

_CONFIDENCE_SCORE = {"low": 0.3, "medium": 0.6, "high": 0.9}

_PRIORITY_RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0}


def run(state: PipelineState) -> dict:
    demonstrated = _demonstrated_industry_skills(state)

    gaps: list[GapEntry] = []
    for requirement in state["industry_requirements"].skills:
        current_level = demonstrated.get(requirement.name, 0.0)
        market_importance = _bucket_importance(requirement.frequency)
        priority = _score_priority(current_level, market_importance)
        gaps.append(
            GapEntry(
                skill=requirement.name,
                current_level=current_level,
                market_importance=market_importance,
                priority=priority,
                frequency=requirement.frequency,
            )
        )

    gaps.sort(key=lambda g: (_PRIORITY_RANK[g.priority], 1 - g.current_level), reverse=True)
    return {"gaps": gaps[:MAX_GAPS]}


def _demonstrated_industry_skills(state: PipelineState) -> dict[str, float]:
    concept_to_industry = {m.academic_concept: m.industry_skill for m in state.get("skill_map", [])}
    demonstrated: dict[str, float] = {}
    for entry in state.get("skill_graph", []):
        industry_name = concept_to_industry.get(entry.name, entry.name)
        score = _CONFIDENCE_SCORE[entry.confidence]
        demonstrated[industry_name] = max(demonstrated.get(industry_name, 0.0), score)
    return demonstrated


def _bucket_importance(frequency: float) -> str:
    if frequency >= 0.6:
        return "high"
    if frequency >= 0.3:
        return "medium"
    return "low"


def _score_priority(current_level: float, market_importance: str) -> str:
    gap_size = 1 - current_level
    if market_importance == "high" and gap_size >= 0.7:
        return "critical"
    if market_importance == "high" and gap_size >= 0.4:
        return "high"
    if market_importance == "medium" and gap_size >= 0.7:
        return "high"
    if market_importance == "medium" and gap_size >= 0.4:
        return "medium"
    if market_importance == "low" and gap_size >= 0.7:
        return "medium"
    return "low"
