# Architecture

## Two phases

**Phase 1: Plan Generation.** Six agents plus a bounded revision loop turn a student profile and a target role into a validated mission (a real-world project spec).

**Phase 2: Work Simulation.** The mission becomes a sequence of sprints. The student submits work per sprint; a Sprint Manager agent evaluates it against the mission's requirements and unlocks the next sprint. Phase 2 is a stretch goal for the hackathon build; see `docs/mvp.md` for what ships first.

## Pipeline (Phase 1)

```
Student input (academic background, existing work, target role or job description)
        |
        v
  [1] Profiler ----------------> student skill graph (with evidence + confidence)
        |
        v
  [2] Industry Analyst ---------> industry requirement set (skills, responsibilities, tools)
        |
        v
  [3] Skill Mapper --------------> academic-to-industry skill map
        |
        v
  [4] Gap Analyst ----------------> prioritized gap list (current level, market importance, priority)
        |
        v
  [5] Project Architect ----------> mission spec (requirements, each tied to a gap)
        |
        v
  [6] Validator -------------------> coverage report
        |
        +--- gaps remain, revisions < max ---> back to [5] Project Architect
        |
        +--- covered, or revisions == max ---> Final Plan
```

The loop-back edge from Validator to Project Architect is the one piece of real agentic behavior in this system: without it, this is six sequential LLM calls. The loop is what makes it iterative.

## Orchestration

LangGraph `StateGraph` with one node per agent. Nodes 1 to 4 are a straight line. Node 5 (Project Architect) and node 6 (Validator) form a cycle with a conditional edge: if the Validator finds uncovered high-priority gaps and the revision count is under the configured max (default 2), route back to Project Architect with the coverage report added to state; otherwise route to a Finalize node that assembles the output described in `docs/mvp.md`.

Each node reads and writes a single shared state object. No node calls another node directly. This keeps every agent independently testable: given a fixed input state, a node's output is deterministic modulo LLM sampling, which is what the evaluation harness in `docs/evaluation.md` depends on.

## State schema (conceptual)

```python
class SkillEntry(BaseModel):
    name: str
    evidence: str          # course, project, or repo this came from
    confidence: Literal["low", "medium", "high"]

class StudentProfile(BaseModel):
    raw_courses: list[str]
    raw_projects: list[str]
    github_urls: list[str]
    target_role: str | None
    target_job_description: str | None

class GapEntry(BaseModel):
    skill: str
    current_level: float        # 0-1
    market_importance: Literal["low", "medium", "high"]
    priority: Literal["low", "medium", "high", "critical"]

class MissionRequirement(BaseModel):
    description: str
    addresses_gap: str           # skill name this requirement targets

class CoverageReport(BaseModel):
    covered_gaps: list[str]
    uncovered_gaps: list[str]
    recommendation: str | None

class PipelineState(BaseModel):
    student_profile: StudentProfile
    skill_graph: list[SkillEntry] = []
    industry_requirements: dict = {}
    skill_map: dict = {}
    gaps: list[GapEntry] = []
    mission: dict | None = None
    coverage: CoverageReport | None = None
    revision_count: int = 0
    final_plan: dict | None = None
```

Phase 2 adds a `SprintState` (current sprint index, submissions, per-sprint evaluation results) attached to the same student session, not a new pipeline.

## Data sources and tools

- **Resume/syllabus/project intake:** file upload (PDF, plain text, or pasted text) parsed by the Profiler agent directly via the LLM. No separate parsing library needed for the hackathon; the LLM extracts structured skills from raw text.
- **GitHub:** a tool that fetches repo metadata, README content, language breakdown, and commit recency for URLs the student supplies. Used as evidence for the Profiler's confidence scoring, not as a code-quality judge.
- **Job market data:** a static, curated dataset of job postings per target role (`backend/app/data/job_postings/`), not live scraping. Reliability on demo day matters more than freshness; live search is a documented future upgrade.
- **Skill taxonomy:** a curated JSON mapping of academic concepts to industry skills and responsibilities (`backend/app/data/skill_taxonomy.json`), used by the Skill Mapper. This is hand-authored for the roles covered by the evaluation dataset, not learned or scraped. It also carries identity entries for the industry-side vocabulary itself (Docker, REST APIs, SQL, and so on), so the Skill Mapper resolves most concepts without an LLM call at all.
- **Skill mapping cache:** `backend/app/data/skill_mapping_cache.json`, a flat concept-to-industry-skill map the Skill Mapper writes to after any LLM-inferred mapping (a taxonomy miss). Concept translation is deterministic, so a concept is never re-inferred once cached, this matters most when the same concepts recur across the 10-profile evaluation dataset.

## LLM call budget and reliability

A single plan-generation run makes roughly 4-6 LLM calls, not one per agent per concept: Profiler (1), Skill Mapper (0-1, batched and usually skipped entirely thanks to taxonomy coverage), Project Architect (1-3, bounded by the revision loop), Validator (0-2, only called when gaps are uncovered). `max_tokens` is set per agent to match actual output size rather than sharing one generous default, so token spend also stays proportional to what each agent actually produces. `app/llm.py` retries on a 429 rate-limit response with exponential backoff (five attempts) before giving up, so a rate limit degrades a run to slower rather than failing it outright.

## API surface (FastAPI)

- `POST /profile`: accept raw academic and project input, return a session id.
- `POST /sessions/{id}/generate-plan`: run the Phase 1 graph, return the final plan (readiness percentage, demonstrated skills, prioritized gaps, mission spec, skill-to-requirement mapping).
- `GET /sessions/{id}/plan`: fetch a previously generated plan.
- `POST /sessions/{id}/sprints/{n}/submit`: Phase 2, submit work for a sprint, get back the Sprint Manager's evaluation and whether the next sprint unlocks.

## Frontend (Next.js)

- Intake form: academic background, project/GitHub links, target role or job description paste.
- Results view: readiness percentage, skill graph, prioritized gap table, mission brief, requirement-to-skill mapping table.
- Phase 2 view (stretch): current sprint description, submission form, evaluation feedback, sprint progress.

## Explicit non-goals for v1

- No live job-board scraping.
- No authentication or multi-tenant data isolation.
- No persistent long-term storage beyond what a session needs; SQLite or in-memory is sufficient.
- No fine-tuned models; all agents use prompted calls to a general Claude model.
