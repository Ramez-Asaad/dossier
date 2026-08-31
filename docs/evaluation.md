# Evaluation Design

## Two systems under comparison

**Baseline:** a single LLM call. Input: student profile plus target role or job description. Prompt: analyze the student's skills and recommend what they should learn or build to become qualified for the role.

**Agent:** the same exact input, run through the full pipeline in `docs/architecture.md` (Profiler, Industry Analyst, Skill Mapper, Gap Analyst, Project Architect, Validator, with revision loop).

Both systems receive identical input per profile. Nothing about the input changes between runs; only the system generating the output changes.

## Dataset

10 synthetic but realistic student profiles, stored under `backend/app/data/eval_profiles/`, version-controlled so results are reproducible. Each profile includes:

- A list of completed courses.
- A list of past projects (with enough description to infer skills, some with a GitHub link).
- A target role or a pasted job description.

Profile set, authored in `backend/app/data/eval_profiles/profile-01.json` through `profile-10.json`:

| # | Background | Target role | Notable variation |
|---|---|---|---|
| 1 | Computer Science student | ML Engineer | baseline case |
| 2 | AI student | Computer Vision Engineer | baseline case |
| 3 | Software Engineering student | AI Engineer | strong engineering, weak AI-specific skills |
| 4 | Data Science student | ML Engineer | notebook-only work, no production experience |
| 5 | AI student | NLP Engineer | baseline case |
| 6 | Computer Science student | ML Engineer | already has a deployed project to extend |
| 7 | AI student | Computer Vision Engineer | early, low-evidence profile, mostly low confidence |
| 8 | Software Engineering student | AI Engineer | API-heavy background plus one LLM-integration project |
| 9 | Data Science student | NLP Engineer | cross-domain: stats/SQL background applied to an NLP target |
| 10 | AI student | ML Engineer | broad, unspecialized coursework, nothing extended past class |

Each profile's `rubric.priority_gaps` uses skill names that appear verbatim in that role's `backend/app/data/job_postings/*.json` file, so the scoring script in `backend/scripts/run_evaluation.py` can check the agent's `addresses_gap` fields against the rubric by exact match rather than fuzzy text matching.

Each profile needs a hand-authored ground-truth rubric: the skills the profile actually demonstrates (with evidence), the priority gaps for the stated target role, and what a genuinely gap-closing project would need to include. This rubric is authored once, by a human, before running either system, so scoring isn't circular.

## Primary metric: Skill-Gap-to-Project Coverage

For each profile: of the gaps in the ground-truth rubric's priority list, what percentage does the generated project actually address?

```
coverage = (priority gaps demonstrably addressed by the project) / (total priority gaps in the rubric)
```

Computed for both baseline and agent, per profile, then averaged across the dataset. This is the headline number for the hackathon comparison (for example, baseline 43% average coverage vs agent 86%).

"Demonstrably addressed" means a human scorer (or a separate LLM-judge pass, cross-checked by a human) can point to a specific requirement in the generated project that maps to the gap, the same evidentiary standard the product itself enforces on students.

## Secondary metrics

- **Skill identification accuracy:** does the generated skill graph (or, for the baseline, its implicit skill assessment) match the rubric's ground-truth demonstrated skills?
- **Gap precision:** of the gaps the system surfaces, how many are real gaps per the rubric (not false positives)?
- **Project relevance:** independent of gap coverage, does the proposed project make sense for this student and this role?
- **Expert usefulness:** human evaluators rate, on a fixed scale, whether the output would actually help this student become more job-ready.
- **Evidence quality:** does every major claim (skill, gap, requirement) in the output cite a specific evidence source, per NFR-4 in `docs/requirements.md`?

## Scoring procedure

1. Author the ground-truth rubric for all 10 profiles before running either system.
2. Run the baseline on all 10 profiles; capture raw output.
3. Run the agent pipeline on all 10 profiles; capture raw output, including intermediate state (skill graph, gaps, coverage report) for the evidence-quality check.
4. Score both systems against the rubric using the same scorer (human, or human-reviewed LLM judge) and the same criteria, blind to which system produced which output where feasible.
5. Report primary metric average plus per-profile breakdown, and secondary metrics as a supporting table.

`backend/scripts/run_evaluation.py` automates steps 2 through 5 for the primary metric only. It scores the agent by exact match against each mission requirement's `addresses_gap` field, and scores the baseline by checking whether a rubric gap's name appears as text in the baseline's free-form project description. The text-match check is a fast proxy, not the human or LLM-judge standard described above; treat its output as a quick sanity signal during development, and fall back to human scoring for the number that goes in front of judges.
