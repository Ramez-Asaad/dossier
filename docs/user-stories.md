# User Stories

## Personas (also the basis for the evaluation dataset in `docs/evaluation.md`)

1. Computer Science student targeting ML Engineer.
2. AI student targeting Computer Vision Engineer.
3. Software Engineering student targeting AI Engineer.
4. Data Science student targeting ML Engineer.
5. AI student targeting NLP Engineer.

## Core pipeline stories

**US-1.** As a student, I want to submit my courses, projects, and GitHub links, so that the system can build an accurate picture of what I actually know rather than what I've merely been exposed to.
- Acceptance: submission accepts free text and file upload; the resulting skill graph cites a specific course, project, or repo for every entry.

**US-2.** As a student, I want to specify a target role or paste a job description, so that the analysis is relevant to the job I actually want.
- Acceptance: both a named role and a pasted job description are accepted as valid targets.

**US-3.** As a student, I want to see which of my skills are already strong, so that I don't waste time relearning things I've already demonstrated.
- Acceptance: the output lists demonstrated skills separately from gaps, each with its evidence.

**US-4.** As a student, I want to see a short, prioritized list of my highest-value gaps instead of an overwhelming list of everything I'm missing, so that I know what to focus on first.
- Acceptance: the gap list surfaces a handful of items, each with a stated priority and the reasoning behind it (market importance, dependency, feasibility).

**US-5.** As a student, I want a single concrete project to build, tied explicitly to my gaps, so that I have one clear next action instead of a vague roadmap.
- Acceptance: every mission requirement states which gap it addresses; the mission brief explains why this project was chosen for this student.

**US-6.** As a student, I want the system to prefer extending a project I've already built over proposing something unrelated, so that the recommended work feels achievable and builds on what I already have.
- Acceptance: when a suitable existing project exists in the student's input, the mission explicitly extends it rather than proposing a new one from scratch.

**US-7.** As a student, I want to trust that the recommended project actually closes my gaps, so that finishing it is worth my time.
- Acceptance: the output shows a coverage report (which gaps are covered, which aren't) rather than asserting coverage without evidence.

**US-8.** As a student, if my highest-value gaps can't all be covered by one project, I want to know that honestly, so that I'm not misled into thinking I'm more job-ready than I am.
- Acceptance: when the revision loop hits its maximum and gaps remain uncovered, the final output states this explicitly rather than silently presenting partial coverage as complete.

## Phase 2 stories (stretch)

**US-9.** As a student, I want my mission broken into sprints, so that I can make progress incrementally instead of facing one large undifferentiated project.
- Acceptance: the mission is split into an ordered sequence of sprints, each with its own subset of requirements.

**US-10.** As a student, I want feedback on my actual submitted work per sprint, specific enough to act on, so that I know exactly what to fix before moving on.
- Acceptance: evaluation feedback names the specific missing or incomplete requirement (for example, "missing input validation"), not a generic quality judgment.

**US-11.** As a student, I want the next sprint to unlock only once I've addressed the current one, so that the simulation reflects real engineering accountability rather than letting me skip ahead.
- Acceptance: sprint N+1 is inaccessible until sprint N's requirements are evaluated.

## Internal (evaluation) stories

**US-12.** As the team building this system, I want a fixed baseline (a single LLM call with the same input) to compare against, so that we can measure whether the multi-agent pipeline actually adds value.
- Acceptance: the baseline and the agent pipeline run on the same 10 synthetic profiles and are scored with the same rubric.

**US-13.** As the team building this system, I want a quantifiable primary metric (skill-gap-to-project coverage), so that "our agent is better" is a measured claim, not an assertion.
- Acceptance: for every evaluation profile, the percentage of high-priority gaps demonstrably covered by the generated project is computed for both baseline and agent.
