"""Turns a raw graph state-delta into a short, human-readable trace line.

Used by the streaming `/generate-plan/stream` route so a caller can watch
each agent as it finishes, not just wait for the final plan. Deliberately a
one-line summary per agent, not the raw payload: the raw payload still rides
along in the same event for anyone who wants it (see routes.py), this is
just what a human glances at while the pipeline runs.
"""

from typing import Any


def summarize(node_name: str, delta: dict[str, Any]) -> str:
    handler = _HANDLERS.get(node_name)
    if handler is None:
        return f"{node_name} finished."
    return handler(delta)


def _summarize_profiler(delta: dict[str, Any]) -> str:
    skills = delta.get("skill_graph", [])
    high_confidence = sum(1 for s in skills if s.confidence == "high")
    issues = delta.get("github_fetch_issues", [])
    line = f"Extracted {len(skills)} skill(s) from your background, {high_confidence} at high confidence."
    if issues:
        line += f" Could not fetch {len(issues)} GitHub repo(s)."
    return line


def _summarize_industry_analyst(delta: dict[str, Any]) -> str:
    req = delta.get("industry_requirements")
    if req is None:
        return "Loaded industry requirements."
    return f"Loaded requirements for {req.role}: {len(req.skills)} skills, {len(req.responsibilities)} responsibilities."


def _summarize_skill_mapper(delta: dict[str, Any]) -> str:
    mappings = delta.get("skill_map", [])
    inferred = sum(1 for m in mappings if m.source == "inferred")
    return f"Mapped {len(mappings)} concept(s) to required skills ({inferred} needed judgment, the rest were direct matches)."


def _summarize_gap_analyst(delta: dict[str, Any]) -> str:
    gaps = delta.get("gaps", [])
    if not gaps:
        return "No priority gaps found, you're covered."
    top = gaps[0]
    return f"Found {len(gaps)} priority gap(s). Highest-value: {top.skill} ({top.priority})."


def _summarize_project_architect(delta: dict[str, Any]) -> str:
    mission = delta.get("mission")
    if mission is None:
        return "Designing your mission."
    return f'Designed "{mission.title}" with {len(mission.requirements)} requirement(s).'


def _summarize_validator(delta: dict[str, Any]) -> str:
    coverage = delta.get("coverage")
    if coverage is None:
        return "Validating mission coverage."
    total = len(coverage.covered_gaps) + len(coverage.uncovered_gaps)
    line = f"Coverage check: {len(coverage.covered_gaps)}/{total} priority gaps covered."
    if coverage.uncovered_gaps:
        line += " Sending back for revision."
    return line


def _summarize_finalize(delta: dict[str, Any]) -> str:
    plan = delta.get("final_plan")
    if plan is None:
        return "Assembling your plan."
    return f"Plan ready: {plan['readiness_percent']}% readiness."


_HANDLERS = {
    "profiler": _summarize_profiler,
    "industry_analyst": _summarize_industry_analyst,
    "skill_mapper": _summarize_skill_mapper,
    "gap_analyst": _summarize_gap_analyst,
    "project_architect": _summarize_project_architect,
    "validator": _summarize_validator,
    "finalize": _summarize_finalize,
}
