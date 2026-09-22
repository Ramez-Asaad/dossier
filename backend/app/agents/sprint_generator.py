"""Sprint Generator: splits a finalized mission into structured sprints.

See FR-17 in docs/requirements.md.
"""

from app.state import Mission, SprintSpec


def generate_sprints(mission: Mission) -> list[SprintSpec]:
    sprints: list[SprintSpec] = []
    for idx, req in enumerate(mission.requirements, start=1):
        sprint = SprintSpec(
            index=idx,
            title=f"Sprint {idx}: {req.addresses_gap} Implementation",
            objective=f"Implement and demonstrate proficiency in {req.addresses_gap} as required by the mission.",
            requirements=[req.description],
            deliverables=[
                f"Source code implementation addressing {req.addresses_gap}",
                "Verification log, documentation, or test output proving functionality",
            ],
            addresses_gap=req.addresses_gap,
        )
        sprints.append(sprint)
    return sprints
