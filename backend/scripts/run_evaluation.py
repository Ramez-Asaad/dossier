"""Runs the baseline and agent pipeline over the eval dataset and computes
the primary metric from docs/evaluation.md: skill-gap-to-project coverage.

Usage (from backend/, with ANTHROPIC_API_KEY set in .env or the environment):
    python -m scripts.run_evaluation

Both systems make real LLM calls; this is not a mocked run. For an offline,
mocked sanity check of the scoring logic itself, see tests/test_evaluation.py.
"""

import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app.baseline import run_baseline  # noqa: E402 (must load .env first)
from app.graph import build_graph  # noqa: E402
from app.state import StudentProfile  # noqa: E402

PROFILES_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "eval_profiles"


def load_profiles() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(PROFILES_DIR.glob("*.json"))]


def coverage_against_rubric(priority_gaps: list[str], covered_gaps: set[str]) -> float:
    if not priority_gaps:
        return 1.0
    hits = sum(1 for gap in priority_gaps if gap in covered_gaps)
    return round(hits / len(priority_gaps), 2)


def baseline_covered_gaps(priority_gaps: list[str], baseline_result: dict) -> set[str]:
    # Crude proxy for the "human scorer, or human-reviewed LLM judge" standard
    # docs/evaluation.md actually calls for: a rubric gap counts as covered if
    # its name shows up anywhere in the baseline's free-form project text.
    haystack = json.dumps(baseline_result.get("recommended_project", {})).lower()
    return {gap for gap in priority_gaps if gap.lower() in haystack}


def agent_covered_gaps(agent_final_plan: dict) -> set[str]:
    return {req["addresses_gap"] for req in agent_final_plan["mission"]["requirements"]}


def evaluate_profile(profile: dict, graph) -> dict:
    student_profile = StudentProfile(**profile["input"])
    priority_gaps = profile["rubric"]["priority_gaps"]

    baseline_result = run_baseline(student_profile)
    baseline_coverage = coverage_against_rubric(priority_gaps, baseline_covered_gaps(priority_gaps, baseline_result))

    agent_result = graph.invoke({"student_profile": student_profile})
    agent_coverage = coverage_against_rubric(priority_gaps, agent_covered_gaps(agent_result["final_plan"]))

    return {
        "id": profile["id"],
        "persona": profile["persona"],
        "baseline_coverage": baseline_coverage,
        "agent_coverage": agent_coverage,
    }


def main() -> None:
    graph = build_graph()
    results = [evaluate_profile(profile, graph) for profile in load_profiles()]

    for r in results:
        print(f"{r['id']:12s} {r['persona']:55s} baseline={r['baseline_coverage']:.2f}  agent={r['agent_coverage']:.2f}")

    avg_baseline = round(sum(r["baseline_coverage"] for r in results) / len(results), 2)
    avg_agent = round(sum(r["agent_coverage"] for r in results) / len(results), 2)
    print()
    print(f"Average skill-gap-to-project coverage: baseline={avg_baseline:.2f}  agent={avg_agent:.2f}")


if __name__ == "__main__":
    main()
