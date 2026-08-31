# Agent Trajectories

Real captured runs against Groq (`openai/gpt-oss-120b`), not fabricated examples. Each file is the
actual response from the running system on 2026-08-31. Commands to reproduce any of these are in
`docs/reproduction.md`.

## `raw_run_1.ndjson`: full pipeline, weak profile

Input: a student with only "Introduction to Programming" and "Neural Networks" courses and one
tutorial-following PyTorch project, targeting Computer Vision Engineer (a deliberately sparse case,
similar in spirit to `profile-07` in the eval dataset).

Each line is one agent finishing, in the order the LangGraph pipeline actually executed them:

1. **Profiler** (instructions: `backend/app/agents/profiler.py`) extracted 5 skills, all low or
   medium confidence, explicitly refusing to assert anything the tutorial-based project didn't
   evidence.
2. **Industry Analyst** (tool: `job_data_tool.py` reading `computer_vision_engineer.json`) loaded
   11 required skills and their real posting frequencies.
3. **Skill Mapper** (tool: `skill_taxonomy.py`, cache: `skill_mapping_cache.json`) mapped 12
   concepts, 11 resolved via the static taxonomy for free, 1 needed a live LLM judgment call.
4. **Gap Analyst** (deterministic, no LLM call) computed 6 priority gaps, ranked by market
   importance and gap size, not frequency alone.
5. **Project Architect** designed a mission with one requirement per gap, explicit
   `addresses_gap` field per requirement.
6. **Validator** (the verification step) checked the mission's `addresses_gap` set against the 6
   gaps by exact match and found full coverage. No revision needed this run, see the note below on
   when it does trigger.
7. **Finalize** assembled the plan the student actually sees.

## `raw_run_2.ndjson`: full pipeline, empty profile

Input: one course, zero projects, targeting AI Engineer, the sparsest input the system reasonably
accepts. Same 7-step shape as above. Included specifically because it's the harder case: with zero
demonstrated skills, every one of the 6 computed gaps starts at 0% current level, so the Project
Architect has to design a mission that covers all 6 with no reusable existing work to extend, unlike
the usual case where at least one project gives it something to build on.

## On the revision loop specifically

The Validator-to-Project-Architect loop (`backend/app/graph.py`, bounded at `MAX_REVISIONS = 2`) is
the verification mechanism this project leans on hardest. Both real trajectories above resolved on
the first pass, `openai/gpt-oss-120b` reliably follows the "use the exact skill name" instruction
closely enough that a real revision didn't fire in either attempt captured here.

That doesn't mean the loop is unexercised. `backend/tests/test_graph.py::test_revision_loop_fills_remaining_gap`
deterministically forces the failure case (a mocked Project Architect deliberately drops one gap on
its first response) and asserts the graph correctly routes back, the Architect gets a second attempt
with the Validator's specific uncovered-gap and recommendation in its prompt, and the second attempt
succeeds. That test is the proof the mechanism works; these trajectories are the proof it's rarely
*needed* with a capable model, which is itself worth knowing rather than hiding.

## `baseline_run_1.json`: the comparison system

Same kind of input as the two runs above (the real profile from early manual testing: 3 GitHub
projects, no explicit tech stack named in the course/project text), through the single-call baseline
(`backend/app/baseline.py`) instead of the pipeline. One call, no tool use, no verification. Compare
its `priority_gaps` (generic category names like "MLOps," "Software Engineering Practices") against
the pipeline's gap list in the other two files (specific, job-posting-literal names like "Docker,"
"Kubernetes"): this difference in specificity is exactly what the closed-set Skill Mapper fix
(`docs/changelog.md`, iteration 4) exists to guarantee downstream.

## `sprint_manager_run_1.json`: Phase 2 evaluation

A submission for the first mission requirement from `raw_run_1.ndjson` ("build a real-time video
detection pipeline"), submitted as a genuinely incomplete implementation (frames captured and
inferred, but no visual overlay and no verified frame rate). The Sprint Manager
(`backend/app/agents/sprint_manager.py`) correctly returned `"partial"`, not a lazy pass, and named
the two specific missing pieces plus a concrete frame-rate threshold to hit, matching the engineering
manager framing from the original product brief rather than generic praise.
