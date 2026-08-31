# Evidence Engine

Working name for this project. Rename freely once a final name is picked; update this file and the README if you do.

## What this is

An agentic system that takes a student's academic background and existing project work, compares it against what a target industry role actually requires, finds the highest-value skill gaps, and generates a real-world project (a "mission") that closes those gaps. A second phase turns the mission into a sprint-based work simulation where an agent reviews the student's submissions like an engineering manager.

Pitch: "Stop taking courses. Start turning what you know into evidence that you can do the job."

Full product thinking lives in `docs/`. Read `docs/architecture.md` and `docs/agents.md` before touching the pipeline.

## Tech stack

- Backend: Python 3.11+, LangGraph for orchestration, FastAPI for the HTTP API, Pydantic for state/schema models.
- LLM: Anthropic Claude models via the Anthropic API. `llm.call_json` takes a `model` override per call, but every agent currently uses the same `DEFAULT_MODEL`; a multi-provider abstraction (to add a free/fast option like Groq per agent) is planned but not yet built.
- Frontend: Next.js (App Router), TypeScript, Tailwind.
- Storage for MVP: SQLite (or in-memory) is enough. No auth, no multi-tenant concerns for the hackathon build.

## Directory structure (target)

```
hackathon/
  .claude/
    CLAUDE.md
  docs/
    architecture.md
    agents.md
    requirements.md
    user-stories.md
    evaluation.md
    mvp.md
  backend/
    app/
      state.py          # LangGraph state schema (Pydantic)
      graph.py           # StateGraph wiring, conditional edges, revision loop
      llm.py              # Anthropic call wrapper: retry/backoff, per-call max_tokens
      baseline.py         # single-LLM-call comparison system, see docs/evaluation.md
      agents/
        profiler.py
        industry_analyst.py
        skill_mapper.py
        gap_analyst.py
        project_architect.py
        validator.py
        finalize.py
        sprint_manager.py   # phase 2
      tools/
        github_tool.py
        job_data_tool.py
        skill_taxonomy.py
        skill_mapping_cache.py
      api/
        routes.py
      data/
        skill_taxonomy.json
        skill_mapping_cache.json   # generated at runtime, not hand-authored
        job_postings/       # static synthetic dataset for demo reliability
        eval_profiles/       # 10 synthetic student profiles for evaluation
    scripts/
      run_evaluation.py    # baseline-vs-agent coverage scoring, see docs/evaluation.md
    tests/
  frontend/
    app/
    components/
  README.md
```

Backend and frontend are scaffolded and both build/test clean (see README.md for run commands). The eval dataset (10 profiles) and the baseline system are done. Remaining work is Phase 2 (Sprint Manager is written but not wired into any route besides the raw `/sessions/{id}/sprints/{n}/submit` endpoint, since missions aren't split into sprints yet) and a multi-provider LLM layer (currently Anthropic-only, see chat history for the accepted plan to add Groq/OpenAI-compatible providers with per-agent model routing).

## Conventions

- One agent per file under `backend/app/agents/`. Every agent function takes and returns the shared Pydantic state object, nothing else, so the graph stays composable.
- Every skill or gap the pipeline surfaces must carry an evidence field (which course, project, or repo it came from) and a confidence level. Never assert a skill without evidence, per the product thesis: a course mention is not proficiency.
- The Validator to Project Architect revise loop is bounded (default max 2 revisions) to keep latency and cost predictable in a demo setting. Bound lives in graph.py, not hardcoded inside an agent.
- Job market data and the academic-to-industry skill taxonomy are static, curated datasets for the hackathon (`backend/app/data/`), not live scraping. Live search is a stated future upgrade, not an MVP dependency. Do not add a live scraping dependency without discussing it first, it makes demo day fragile.
- Never call the LLM once per item in a loop. If an agent needs a judgment call for N items (skills, concepts, gaps), batch them into one call. Skill Mapper batches every unmapped concept into a single call and caches the result in `skill_mapping_cache.json`; an earlier version called once per concept and cost 15-20 calls per run. Follow that pattern for any new per-item LLM step.
- Size `max_tokens` per call to what that agent actually produces (see the per-agent values in each agent module), don't reuse `llm.call_json`'s default for everything.

## Key docs

- `docs/architecture.md`: pipeline, state schema, orchestration, data sources, API surface.
- `docs/agents.md`: per-agent spec (inputs, outputs, tools, guardrails).
- `docs/requirements.md`: functional and non-functional requirements.
- `docs/user-stories.md`: personas and stories with acceptance criteria.
- `docs/evaluation.md`: baseline-vs-agent comparison design, dataset, metrics.
- `docs/mvp.md`: exact hackathon scope, cut list, build order, demo script.
