"""LangGraph wiring for Phase 1. See docs/architecture.md for the diagram this mirrors.

The Validator-to-Project-Architect loop is bounded here, not inside either
agent, per the convention in .claude/CLAUDE.md.
"""

from langgraph.graph import END, StateGraph

from app.agents import finalize, gap_analyst, industry_analyst, profiler, project_architect, skill_mapper, validator
from app.state import PipelineState

MAX_REVISIONS = 2


def _route_after_validation(state: PipelineState) -> str:
    coverage = state["coverage"]
    if coverage.uncovered_gaps and state.get("revision_count", 0) < MAX_REVISIONS:
        return "revise"
    return "finalize"


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("profiler", profiler.run)
    graph.add_node("industry_analyst", industry_analyst.run)
    graph.add_node("skill_mapper", skill_mapper.run)
    graph.add_node("gap_analyst", gap_analyst.run)
    graph.add_node("project_architect", project_architect.run)
    graph.add_node("validator", validator.run)
    graph.add_node("finalize", finalize.run)

    graph.set_entry_point("profiler")
    graph.add_edge("profiler", "industry_analyst")
    graph.add_edge("industry_analyst", "skill_mapper")
    graph.add_edge("skill_mapper", "gap_analyst")
    graph.add_edge("gap_analyst", "project_architect")
    graph.add_edge("project_architect", "validator")
    graph.add_conditional_edges(
        "validator",
        _route_after_validation,
        {"revise": "project_architect", "finalize": "finalize"},
    )
    graph.add_edge("finalize", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph
