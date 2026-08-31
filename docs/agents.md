# Agent Specifications

Each agent is a single LangGraph node: it reads the shared `PipelineState`, does one job, and writes its output back into state. See `docs/architecture.md` for the schema and the graph wiring.

## 1. Profiler

**Goal:** determine what the student can actually do, with evidence, not what they claim to know.

**Inputs:** `student_profile.raw_courses`, `raw_projects`, `github_urls`.

**Output:** `skill_graph: list[SkillEntry]`, each with a `name`, an `evidence` string pointing at the specific course, project, or repo it came from, and a `confidence` of low, medium, or high.

**Tools:** GitHub tool (repo metadata, README, language breakdown) to corroborate claimed skills.

**Prompting notes:** a course mention alone is low confidence. A project that demonstrably uses a skill (visible in a repo's dependencies, README, or described implementation) is medium to high confidence depending on depth. Never infer a skill from a course title alone if there's no project evidence; downgrade confidence instead of dropping the skill.

**Guardrail:** every entry must have non-empty evidence. An entry with no evidence is a bug, not a valid output.

## 2. Industry Analyst

**Goal:** determine what the target role actually requires.

**Inputs:** `student_profile.target_role` or `target_job_description`, the static job postings dataset for that role.

**Output:** `industry_requirements`: technical skills, responsibilities, and tools, each annotated with frequency across the dataset (how many postings mention it) as a signal, not a ranking.

**Tools:** job data tool (reads `backend/app/data/job_postings/`).

**Prompting notes:** frequency is one input, not the output. Do not rank by frequency alone; that judgment belongs to the Gap Analyst, which also weighs the student's existing knowledge and skill dependencies.

## 3. Skill Mapper

**Goal:** translate between academic language and industry language so the Gap Analyst is comparing like with like.

**Inputs:** `skill_graph`, `industry_requirements`, the skill taxonomy dataset.

**Output:** `skill_map`: a dictionary linking academic concepts to the industry skills and responsibilities they correspond to (for example, "Neural Network Optimization" maps to "model training and optimization").

**Tools:** skill taxonomy tool (reads `backend/app/data/skill_taxonomy.json`), skill mapping cache (reads/writes `backend/app/data/skill_mapping_cache.json`).

**Prompting notes:** this is a lookup-and-reconcile step, not open-ended reasoning. Where the taxonomy has no entry for a concept, fall back to LLM judgment but flag the mapping as inferred rather than sourced, so the Gap Analyst can weigh it accordingly.

**Cost note:** resolve concepts in three tiers, cheapest first: taxonomy lookup (deterministic, zero calls), then the on-disk cache (a concept already inferred once is never re-inferred), and only then a single LLM call batching every remaining unmapped concept together. An earlier version called the LLM once per unmapped concept; since the taxonomy originally covered only academic-side terms, every industry-side skill name fell through, meaning 15-20 calls for one pipeline run. The taxonomy now also carries identity entries for the industry vocabulary itself (Docker, REST APIs, SQL, ...), so in practice most runs need zero Skill Mapper LLM calls at all. Do not reintroduce a per-concept call loop here.

## 4. Gap Analyst

**Goal:** compare the student's mapped skill graph against industry requirements and produce a prioritized, not exhaustive, gap list.

**Inputs:** `skill_map`, `industry_requirements`, `skill_graph`.

**Output:** `gaps: list[GapEntry]`, each with `current_level` (0 to 1), `market_importance`, and `priority`. Priority accounts for market importance, current gap size, skill dependencies (a prerequisite gap ranks above a downstream one), and project feasibility (can this realistically be demonstrated in one project).

**Guardrail:** cap the surfaced list to the highest-value gaps (a handful, not seventeen). The product goal is "your highest-value gap is X," not a checklist that overwhelms the student.

## 5. Project Architect

**Goal:** design a single real-world mission (project spec) that demonstrably closes as many high-priority gaps as possible, reusing the student's existing work where feasible.

**Inputs:** `gaps`, `skill_graph` (to find an existing project worth extending), on revision passes also `coverage` (the prior Validator report).

**Output:** `mission`: a title, a one-paragraph brief, and a list of `MissionRequirement`, each explicitly tied to the gap it addresses via `addresses_gap`.

**Prompting notes:** prefer extending an existing student project over inventing one from scratch; this is what makes the mission feel achievable rather than like another tutorial. On a revision pass, read the Validator's `recommendation` and add or adjust requirements to cover the named uncovered gap, don't regenerate the whole mission from zero.

## 6. Validator

**Goal:** check whether the proposed mission actually covers the priority gaps, and produce a revision signal if it doesn't.

**Inputs:** `mission`, `gaps`.

**Output:** `coverage: CoverageReport` with `covered_gaps`, `uncovered_gaps`, and a `recommendation` (a concrete addition, such as "add a prediction logging database to demonstrate SQL/data persistence").

**Guardrail:** this agent must not rewrite the mission itself, only assess it and hand back a recommendation. Keeping assessment and generation in separate agents is what makes the revision loop meaningful instead of one agent grading its own homework.

**Loop control:** the graph, not this agent, enforces the max revision count. At max revisions the graph routes to Finalize regardless of remaining uncovered gaps, and the final output should say so plainly (partial coverage is an honest result, not a bug to hide).

## 7. Sprint Manager (Phase 2, stretch)

**Goal:** act as an engineering manager reviewing the student's actual submitted work per sprint.

**Inputs:** the finalized `mission`, the current sprint's requirements, the student's submission (code, files, or a description of what they built).

**Output:** a per-requirement pass/fail/partial evaluation with specific feedback (for example, "missing input validation"), and a decision on whether the next sprint unlocks.

**Prompting notes:** evaluate against the mission's own stated requirements, not generic code-quality opinions. Feedback should name the specific missing piece, mirroring the Validator's style of concrete, actionable gaps rather than vague criticism.
