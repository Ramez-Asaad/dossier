# Evaluation Results

Real run, not a projection. Produced by `backend/scripts/run_evaluation.py` against Groq
(`openai/gpt-oss-120b`) on 2026-08-31. See `docs/evaluation.md` for the design and the scoring
method this table reports against.

## Primary metric: skill-gap-to-project coverage

| Profile | Persona | Baseline | Agent |
|---|---|---:|---:|
| profile-01 | Computer Science student -> ML Engineer | 0.60 | 0.80 |
| profile-02 | AI student -> Computer Vision Engineer | 0.00 | 0.80 |
| profile-03 | Software Engineering student -> AI Engineer | 0.00 | 0.50 |
| profile-04 | Data Science student -> ML Engineer | 0.40 | 1.00 |
| profile-05 | AI student -> NLP Engineer | 0.20 | 0.40 |
| profile-06 | CS student, already deployed a project -> ML Engineer | 0.50 | 0.75 |
| profile-07 | AI student, early and weak profile -> Computer Vision Engineer | 0.17 | 0.67 |
| profile-08 | SWE student, API-heavy background -> AI Engineer | 0.00 | 0.50 |
| profile-09 | Data Science student, cross-applying -> NLP Engineer | 0.33 | 0.67 |
| profile-10 | AI student, broad unspecialized coursework -> ML Engineer | 0.33 | 0.67 |
| **Average** | | **0.25** | **0.68** |

**Baseline 25% -> Agent 68%, roughly 2.7x.** The agent beat the baseline on every one of the 10
profiles, and on 3 of them (profile-02, profile-03, profile-08) the baseline named zero of the
priority gaps in its recommended project at all.

| Metric | Simple baseline | Agent solution | Change |
|---|---:|---:|---:|
| Primary outcome (avg. coverage) | 0.25 | 0.68 | +0.43 (2.7x) |
| LLM calls per case | 1 | 4-6 | see cost note below |
| Approx. cost per case (Groq) | ~$0.00 (free tier) | ~$0.00 (free tier) | negligible on Groq; see reproduction guide for Anthropic pricing if that provider is used instead |
| Approx. runtime per case | ~3s | ~10s | +7s |

## The challenging case

**profile-05 (AI student -> NLP Engineer) is the weakest agent result, 0.40.** Worth explaining
why, since it reveals a real limitation rather than a bug.

The rubric's hand-authored priority gaps for this profile are `Docker, REST APIs, Automated
testing, LLM integration, Information retrieval`. The pipeline's own Gap Analyst, working only from
this student's actual demonstrated skills and the role's job-posting frequencies, independently
computed a different top-6: `REST APIs, Docker, Model evaluation, PyTorch, Python, Text pipelines`.
Only 2 of the 5 rubric gaps survive that computation, so the mission (which correctly covers all 6
of the gaps the system itself identified) only overlaps the rubric on 2.

This is not the system failing to act on gaps it found. It's the system's independent priority
ranking legitimately disagreeing with the rubric author's (my) manual pick, because `MAX_GAPS = 6`
(see `backend/app/agents/gap_analyst.py`) caps the surfaced list, and for this student's specific
skill profile, other real gaps outranked three of the ones the rubric happened to name. The lesson:
a fixed-cap top-N gap list is only as fair to the ground truth as the ground truth's own priority
ordering. A rubric built independently of the code (as this one was) can diverge from the pipeline's
priority function even when both are individually reasonable. Widening `MAX_GAPS` or scoring against
the union of rubric and computed gaps would change this number without changing whether the mission
itself is any good.

## Secondary observation

The 3 profiles where baseline scored exactly 0.00 (profile-02, 03, 08) share a pattern: the baseline
system's single-shot project recommendation used generic phrasing ("productionize your model," "add
testing") that never named the specific gap skill as text, so the substring-match scorer (see
`docs/evaluation.md`'s note on this being a fast proxy, not the human/LLM-judge standard) found
nothing to credit. That's a real weakness of a single unstructured prompt: it doesn't consistently
name the specific skill it's supposedly targeting, which is exactly the gap-to-evidence traceability
this project's agent pipeline enforces structurally via `MissionRequirement.addresses_gap`.
