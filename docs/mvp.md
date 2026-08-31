# MVP Scope (Hackathon Build)

## What ships

- Phase 1 pipeline end to end: Profiler, Industry Analyst, Skill Mapper, Gap Analyst, Project Architect, Validator, with a bounded revision loop (max 2 revisions).
- Static datasets for job postings and skill taxonomy covering the 5 roles in the evaluation dataset (ML Engineer, Computer Vision Engineer, AI Engineer, NLP Engineer, and whatever roles the remaining 5 synthetic profiles need).
- Next.js intake form (courses, projects, GitHub links, target role or job description) and a results view (readiness percentage, demonstrated skills, prioritized gaps, mission brief, requirement-to-gap mapping table).
- The baseline system (single LLM call) implemented alongside the agent pipeline, so the demo can show both outputs side by side.
- The evaluation harness and the 10-profile dataset, with the primary metric (skill-gap-to-project coverage) computed for both systems.

## What's cut for v1 (explicitly out of scope)

- Phase 2 work simulation (Sprint Manager, sprint submission and evaluation). Build only if Phase 1 and the demo are solid with time remaining.
- Live job-board scraping or any live external data source. Static datasets only.
- Authentication, multi-tenant data isolation, persistent long-term storage.
- File upload parsing beyond plain text or pasted content (no PDF parsing pipeline unless time allows; pasted text is an acceptable substitute for the demo).

## Build order

1. `PipelineState` schema and the LangGraph `StateGraph` skeleton (nodes stubbed, edges wired, revision loop and its bound in place) so the orchestration shape exists before any agent has real logic.
2. Skill taxonomy and job postings static datasets for the 5 target roles, authored by hand.
3. Profiler and Industry Analyst (the two agents with no dependency on other agent output).
4. Skill Mapper, then Gap Analyst.
5. Project Architect and Validator together, since the revision loop only makes sense once both exist; test the loop with a deliberately weak mission to confirm it actually revises.
6. Baseline system (single prompt, same input schema) so evaluation can start as soon as the agent pipeline is functional. Done: `backend/app/baseline.py`.
7. FastAPI routes wrapping the graph. Done: `backend/app/api/routes.py`, includes `/generate-plan` and `/generate-baseline`.
8. Next.js intake form and results view. Done: `frontend/app/page.tsx` and `frontend/app/results/[id]/page.tsx`.
9. Evaluation dataset (10 profiles, ground-truth rubrics) and the scoring script for the primary metric. Done: `backend/app/data/eval_profiles/`, `backend/scripts/run_evaluation.py`. Not yet run against a real API key, only against mocked LLM calls in `backend/tests/test_evaluation.py`.
10. Phase 2 (Sprint Manager) only if time remains after steps 1-9 are solid. `backend/app/agents/sprint_manager.py` exists and is reachable via `/sessions/{id}/sprints/{n}/submit`, but nothing splits a mission into sprints yet, so this is still a stretch item.

Remaining before demo day: get a real `ANTHROPIC_API_KEY`, run `python -m scripts.run_evaluation` for real numbers, and spot-check that the frontend renders a real end-to-end run (it has only been exercised against `next build`, not a live backend).

## Demo script (draft)

1. Open on a student profile: courses, one or two real-looking projects, a GitHub link, and a target role.
2. Show the baseline output first: generic, learn-more-courses advice.
3. Run the same input through the agent pipeline. Walk through the skill graph (with evidence), the prioritized gap list, and land on the line "your highest-value gap is X, not Y."
4. Show the generated mission and the requirement-to-gap mapping table, explaining how it extends the student's existing project.
5. Show the coverage report and, if a revision happened, point out that the system caught its own gap and fixed it, not a human catching it after the fact.
6. Close with the evaluation number: baseline vs agent skill-gap-to-project coverage across the 10-profile dataset.
7. If Phase 2 shipped: show one sprint submission and the Sprint Manager's feedback, framing it as "learn, build, prove" rather than "learn, learn, learn."
