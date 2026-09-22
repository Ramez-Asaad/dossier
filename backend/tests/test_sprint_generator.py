from app.agents.sprint_generator import generate_sprints
from app.state import Mission, MissionRequirement


def test_generate_sprints():
    mission = Mission(
        title="Deployable ML Service",
        brief="Build a full ML service with monitoring and REST endpoints.",
        requirements=[
            MissionRequirement(description="Build PyTorch model trainer", addresses_gap="PyTorch"),
            MissionRequirement(description="Expose model via FastAPI and Docker", addresses_gap="Docker"),
        ],
    )
    sprints = generate_sprints(mission)
    assert len(sprints) == 2
    assert sprints[0].index == 1
    assert "PyTorch" in sprints[0].title
    assert len(sprints[0].deliverables) > 0
    assert sprints[1].addresses_gap == "Docker"
