# Evidence Engine

Working name, rename freely. Built entirely during the micro1 Agentic Workflows Hackathon; nothing
in this repository predates the event.

## Who has this problem, and why it's worth solving

**Students preparing for a specific technical role** (ML Engineer, Computer Vision Engineer, AI
Engineer, NLP Engineer here), who have real coursework and real side projects but no reliable way to
know which of those actually count as evidence for the job they want, and what single project would
close the gap fastest. The bottleneck: translating "I took Neural Networks and built an image
classifier" into "here's what an ML Engineer job actually requires, here's what you're missing, and
here's the one project that proves you can do it" is not something a student can do accurately on
their own, academic and industry vocabulary genuinely differ, and a generic AI chat answer
("learn Docker, brush up on APIs") gives no evidence trail and no way to verify it actually closes
the right gaps.

Pitch: stop taking courses, start turning what you know into evidence that you can do the job.

## What it does

Six agents (Profiler, Industry Analyst, Skill Mapper, Gap Analyst, Project Architect, Validator)
plus a bounded verification/revision loop turn a student's background and a target role into one
real project, each requirement explicitly tied to the specific skill gap it closes. A second phase
(Sprint Manager) turns that project into a sprint-by-sprint work simulation: submit what you built,
get evaluated against the actual requirement, unlock the next sprint.

## Results

Real evaluation, 10 synthetic profiles, baseline (single LLM call) vs. the full agent pipeline,
scored on skill-gap-to-project coverage:

**Baseline: 0.25 average coverage. Agent: 0.68. Roughly 2.7x.**

Full numbers, per-profile breakdown, and the one case that came out weakest (and why) are in
[`docs/evaluation-results.md`](docs/evaluation-results.md).

## Docs

- [`docs/changelog.md`](docs/changelog.md): the improvement changelog, baseline through final, with real evidence at every stage.
- [`docs/reproduction.md`](docs/reproduction.md): clean-environment setup, exact commands, expected output, versions, runtime and cost.
- [`docs/evaluation-results.md`](docs/evaluation-results.md): the real baseline-vs-agent numbers and the challenging case.
- [`docs/hot-take.md`](docs/hot-take.md): the main failure mode this project actually hit, and the general lesson from it.
- [`docs/trajectories/`](docs/trajectories/): real captured runs for every agent, not fabricated examples.
- [`docs/architecture.md`](docs/architecture.md): pipeline, state schema, orchestration, data sources, API surface.
- [`docs/agents.md`](docs/agents.md): per-agent spec (inputs, outputs, tools, guardrails).
- [`docs/requirements.md`](docs/requirements.md): functional and non-functional requirements.
- [`docs/user-stories.md`](docs/user-stories.md): personas and stories with acceptance criteria.
- [`docs/evaluation.md`](docs/evaluation.md): baseline-vs-agent comparison design, dataset, metrics.
- [`docs/mvp.md`](docs/mvp.md): exact hackathon scope, cut list, build order, demo script.

## Running it

See [`docs/reproduction.md`](docs/reproduction.md) for the full clean-environment walkthrough with
expected output at each step. Short version:

Backend (from `backend/`):
```
python -m venv .venv
.venv/Scripts/activate        # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # fill in GROQ_API_KEY or ANTHROPIC_API_KEY
uvicorn main:app --port 8001
```

Frontend (from `frontend/`):
```
npm install
cp .env.local.example .env.local   # point NEXT_PUBLIC_API_BASE_URL at the backend port above
npm run dev
```

Backend tests (no API key needed, LLM calls are mocked):
```
cd backend && pytest
```

Real evaluation (needs a real API key, makes real LLM calls):
```
cd backend && python -m scripts.run_evaluation
```

## Stack

Backend: Python 3.11+, LangGraph, FastAPI, Pydantic. LLM: Groq (`openai/gpt-oss-120b`) or Anthropic
Claude, selectable via `LLM_PROVIDER`, see `backend/app/llm.py`.
Frontend: Next.js, TypeScript, Tailwind.

## Scope and disclaimers

Job postings and the skill taxonomy are a small, hand-authored, synthetic dataset covering 4 roles,
not a live market scan, see `docs/requirements.md` NFR-5. The 10 evaluation profiles and their
ground-truth rubrics were authored by the same person who built the system; that's a known
limitation of the evaluation, not hidden, see `docs/evaluation-results.md`. Every plan and sprint
evaluation this system produces is advisory: it's meant to guide a student's own next step, not to
replace a real mentor, instructor, or hiring decision.
