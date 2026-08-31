"""FastAPI routes. In-memory session store, sufficient for the hackathon MVP
per NFR-6 in docs/requirements.md (no persistence required beyond a session).
"""

import json
import uuid
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app import trace as trace_module
from app.agents.sprint_manager import evaluate_submission
from app.baseline import run_baseline
from app.graph import get_graph
from app.state import StudentProfile

router = APIRouter()

_sessions: dict[str, dict] = {}


class ProfileIn(BaseModel):
    raw_courses: list[str] = []
    raw_projects: list[str] = []
    github_urls: list[str] = []
    target_role: str | None = None
    target_job_description: str | None = None


class SprintSubmission(BaseModel):
    requirements: list[str]
    submission_description: str


@router.post("/profile")
def create_profile(profile_in: ProfileIn) -> dict:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"profile": StudentProfile(**profile_in.model_dump()), "plan": None, "baseline": None}
    return {"session_id": session_id}


@router.post("/sessions/{session_id}/generate-plan")
def generate_plan(session_id: str) -> dict:
    session = _get_session(session_id)
    graph = get_graph()
    result = graph.invoke({"student_profile": session["profile"]})
    session["plan"] = result["final_plan"]
    return session["plan"]


@router.post("/sessions/{session_id}/generate-plan/stream")
def generate_plan_stream(session_id: str) -> StreamingResponse:
    """Same pipeline as /generate-plan, but emits one NDJSON line per agent
    as it finishes instead of waiting silently for the whole run. Each line
    carries a short human-readable `summary` (see app/trace.py) plus the
    agent's raw state delta in `data`, so this doubles as a live trace for
    debugging and as the event feed the frontend's generating screen renders.
    """
    session = _get_session(session_id)
    graph = get_graph()

    def event_stream():
        attempt_counts: dict[str, int] = {}
        try:
            for chunk in graph.stream({"student_profile": session["profile"]}, stream_mode="updates"):
                for node_name, delta in chunk.items():
                    attempt_counts[node_name] = attempt_counts.get(node_name, 0) + 1
                    event = {
                        "type": "agent_update",
                        "agent": node_name,
                        "attempt": attempt_counts[node_name],
                        "summary": trace_module.summarize(node_name, delta),
                        "data": _to_jsonable(delta),
                    }
                    yield json.dumps(event) + "\n"
                    if node_name == "finalize":
                        session["plan"] = delta["final_plan"]
            yield json.dumps({"type": "done"}) + "\n"
        except Exception as exc:  # surfaced to the client as a trace event, not a dropped connection
            yield json.dumps({"type": "error", "message": str(exc)}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


@router.post("/sessions/{session_id}/generate-baseline")
def generate_baseline(session_id: str) -> dict:
    """The single-LLM-call comparison system. See docs/evaluation.md."""
    session = _get_session(session_id)
    session["baseline"] = run_baseline(session["profile"])
    return session["baseline"]


@router.get("/sessions/{session_id}/plan")
def get_plan(session_id: str) -> dict:
    session = _get_session(session_id)
    if session["plan"] is None:
        raise HTTPException(status_code=404, detail="No plan generated yet for this session.")
    return session["plan"]


@router.post("/sessions/{session_id}/sprints/{sprint_index}/submit")
def submit_sprint(session_id: str, sprint_index: int, submission: SprintSubmission) -> dict:
    _get_session(session_id)  # validates the session exists
    return evaluate_submission(submission.requirements, submission.submission_description)


def _get_session(session_id: str) -> dict:
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session id.")
    return session


def create_app() -> FastAPI:
    app = FastAPI(title="Evidence Engine API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app
