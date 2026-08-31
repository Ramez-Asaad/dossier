# Solution Video Script (5 minutes)

Structure follows the hackathon brief exactly: problem and baseline, one full realistic execution,
the comparison, the changelog highlight, one removed experiment. Timestamps are targets, not
rigid, adjust pacing to what actually reads well on screen.

---

## 0:00-0:30 — The problem and the baseline

**Screen:** README.md open, or a title card.

**Say:**
"A student who's taken real courses and built real projects still can't answer one question:
what's the highest-value thing I should build next to prove I can do this job. Academic and
industry language don't match, and a generic AI answer doesn't give you evidence, just advice.

Here's the baseline: one LLM call, same input, straightforward prompt: 'analyze this student and
recommend what to learn and build.'"

**Screen:** show `backend/app/baseline.py`'s system prompt briefly, or the actual baseline output
from `docs/trajectories/baseline_run_1.json`, specifically its `priority_gaps` list ("MLOps,"
"Software Engineering Practices," generic categories).

"Notice these gaps are generic categories, not specific skills you could go verify. Keep that in
mind, we'll come back to it."

---

## 0:30-3:00 — One real execution, start to finish

**Screen:** the actual running app at `localhost:3000`.

1. **Intake form (~15s).** Fill in real courses and projects (use the same example from testing:
   Neural Networks, Deep Learning course list; the Emotion Detection / Stock Prediction / Finals
   Buddy projects, or a fresh one). Target role: ML Engineer. Submit.

2. **Generating screen (~60s).** Let the live trace actually play. Narrate over it as each agent
   lands:
   "Profiler just extracted skills with an evidence source and a confidence level for each, it
   won't assert something it can't point to. Industry Analyst loaded real job-posting frequency
   data for this role. Skill Mapper is deciding which of the student's skills actually count as
   evidence for one of the role's required skills, not just translating freely. Gap Analyst ranked
   the priority gaps. Project Architect just designed a mission where every requirement is tied to
   one specific gap. And Validator just checked that mission against the gap list, that's the
   verification step, if it didn't cover everything, it would send it back for a revision right
   here."

   Click **"View your results"** once it's ready, don't let it auto-navigate, call out that this
   button exists specifically because an earlier version yanked you to the next screen before you
   could read anything.

3. **Results page (~45s).** Show the readiness gauge, the demonstrated skills with real evidence
   strings, the gap table with real job-posting frequency percentages, and the mission with every
   requirement's `addresses_gap` tag visible.

4. **Trace page (~30s).** Click "View full trace." Expand one agent's configuration, show the real
   model, max_tokens, and system prompt that produced that specific output. "This isn't a
   simulation of tracing, it's the actual config and the actual state, input and output, for every
   step, persisted so you can come back to it."

5. **Mission / work simulation (~30s).** Click "Start your mission," submit a real (or deliberately
   partial) answer to sprint 1, show the Sprint Manager's specific, non-generic feedback.

---

## 3:00-3:45 — The comparison

**Screen:** `docs/evaluation-results.md`.

"Ran this for real against 10 synthetic student profiles, baseline vs. the full pipeline, scored on
what percentage of the priority gaps the recommended project actually covers.

Baseline: 25% average. Agent: 68%. Roughly two point seven times.

And it's not close on the easy cases either, three of the ten profiles, the baseline named zero of
the real gaps in its own recommendation."

Point out the one honest miss: "profile-05 is the weakest agent result, 40%, and it's worth showing
why: the system's own gap-priority ranking legitimately disagreed with my hand-picked rubric on
three of five gaps. Not a bug, a real methodology limitation, documented, not hidden."

---

## 3:45-4:30 — The changelog: the change that mattered most, and the one that got thrown out

**Screen:** `docs/changelog.md`.

"The single highest-impact fix: a real user test came back with zero percent on every required
skill for a student with three actual GitHub projects. Traced it to the Skill Mapper translating
skills into free-form industry phrasing that could never exactly match the job posting's literal
skill name. Constrained it to a closed set, pick one of the role's actual skill names or skip it.
Before: Python and Docker at 0% for someone who clearly used both. After: 60%, correctly showing
partial, real credit."

"And one thing I threw out entirely: the first visual redesign. Dark background, rounded shadowed
cards, warm accent color. Every individual choice was reasonable and it still read as generic
AI-generated template the moment a real person looked at it. Replaced the whole direction: light
paper background, a color pair you won't find in a default AI palette, flat hairline borders instead
of cards. The lesson wasn't about taste, it was that 'professional and elegant' by default converges
on one narrow look, and avoiding it takes an active different reference point, not more polish on
the same one."

---

## 4:30-5:00 — Close

**Screen:** `docs/hot-take.md`, or back to the results page.

"The real hot take: whenever one agent's output becomes another component's lookup key, constrain
that output to the receiving side's actual vocabulary. A model that translates freely across that
boundary will produce fluent, individually-reasonable output that silently never matches anything
downstream. It's invisible in every test you write yourself, because you wrote the eval data with
the same vocabulary in mind. It only shows up the moment a real person uses the system.

That's the lesson this whole project is actually about: stop teaching what to learn next, build the
thing that proves what you can already do."

**End card:** repo link / zip contents reference, `docs/reproduction.md` for anyone who wants to run
it themselves.
