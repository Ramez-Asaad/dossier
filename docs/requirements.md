# Requirements

## Functional requirements

### Intake
- FR-1: The system accepts academic input as free text or file upload: courses, projects, grades or experience level, skills, certifications.
- FR-2: The system accepts existing work as GitHub repository URLs and optional project descriptions.
- FR-3: The system accepts a target as either a named role (for example "ML Engineer") or a pasted job description.

### Profiling
- FR-4: The system produces a student skill graph where every skill entry has an evidence source and a confidence level of low, medium, or high.
- FR-5: The system does not assert a skill as demonstrated solely because a course title mentions it; course-only evidence caps confidence at low.

### Industry analysis
- FR-6: The system produces a set of industry requirements (skills, responsibilities, tools) for the target role, drawn from the static job postings dataset.
- FR-7: Each industry requirement is annotated with its frequency across the dataset.

### Skill mapping
- FR-8: The system translates academic concepts into their corresponding industry skills and responsibilities using the skill taxonomy dataset, falling back to inferred mapping (flagged as such) when the taxonomy has no entry.

### Gap analysis
- FR-9: The system compares the mapped student skill graph against industry requirements and produces a prioritized gap list, not an exhaustive one.
- FR-10: Gap priority accounts for market importance, gap size, skill dependencies, and project feasibility, not frequency alone.

### Mission generation
- FR-11: The system generates a single mission (project spec) with a title, brief, and a list of requirements, each explicitly tied to the gap it addresses.
- FR-12: The system prefers extending an existing student project over proposing an unrelated one when a suitable existing project exists.

### Validation loop
- FR-13: The system checks the generated mission against the priority gap list and produces a coverage report naming covered and uncovered gaps.
- FR-14: When gaps remain uncovered and the revision count is under the configured maximum, the system revises the mission rather than finalizing it.
- FR-15: The revision loop is bounded by a configurable maximum revision count; the system finalizes at that bound even with uncovered gaps, and states remaining gaps honestly in the output.

### Output
- FR-16: The final output includes a readiness percentage, a list of demonstrated skills, the prioritized gap list, the mission brief, and a table mapping each mission requirement to the skill or gap it demonstrates.

### Phase 2 (work simulation, stretch)
- FR-17: The system splits a finalized mission into sprints.
- FR-18: The system accepts a student's submission for the current sprint and evaluates it per requirement (pass, fail, or partial) with specific feedback.
- FR-19: The next sprint unlocks only after the current sprint's requirements are evaluated.

## Non-functional requirements

- NFR-1 (Latency): A full Phase 1 run, including up to the configured max revisions, completes within a time budget suitable for a live demo (target: under 60 seconds end to end).
- NFR-2 (Cost predictability): The revision loop is hard-bounded so a single run has a known maximum number of LLM calls; unbounded loops are not acceptable.
- NFR-3 (Reproducibility): The evaluation dataset (10 synthetic student profiles) is fixed and version-controlled so baseline-vs-agent comparisons are repeatable across runs.
- NFR-4 (Explainability): Every skill, gap, and requirement surfaced to the student traces back to a stated evidence source; unattributed claims are treated as defects.
- NFR-5 (Demo reliability): Job market data and the skill taxonomy are static local datasets, not live external calls, so a network hiccup or rate limit cannot break a live demo.
- NFR-6 (Privacy): Uploaded academic and project data is only retained for the duration of a session unless the user explicitly requests persistence; no data is shared outside the session context.
- NFR-7 (Portability): The skill taxonomy and job postings datasets are plain JSON files with no proprietary format, so new roles can be added by editing data, not code.
- NFR-8 (Testability): Each agent node is a pure function over the shared state object, so any node can be tested in isolation with a fixed input state.
- NFR-9 (Call and token economy): No agent makes one LLM call per item in a list it's processing; concepts, gaps, or requirements that need LLM judgment are batched into a single call. A translation that has been inferred once (concept to industry skill) is cached and never re-inferred. Each agent's `max_tokens` is sized to its actual output, not a shared generous default. A rate-limit response is retried with exponential backoff before the run fails.
