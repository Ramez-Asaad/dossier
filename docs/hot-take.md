# Hot Take

**A closed-vocabulary boundary is worth more than a clever translation step, anywhere two agents
have to agree on the same word.**

## The failure mode we actually observed

Real user test, real profile, 3 real GitHub projects, unmistakably a working Python/ML developer.
The result: every single required skill showed 0% current level, including Python. Not a subtle
miss, a maximally implausible one.

The cause wasn't the extraction agent (Profiler) or the comparison agent (Gap Analyst), both were
working correctly. It was the translation step between them. The Skill Mapper took a student's
skill ("Computer Vision") and asked an LLM to translate it into "the closest industry skill or
responsibility a hiring manager would recognize," producing something like "computer vision /
real-time inference." That's a perfectly reasonable sentence. It is also not, character for
character, equal to "Docker" or "Real-time inference" or any other literal string the Gap Analyst
was comparing against. Every translation the LLM produced was fluent and none of them could ever
match, because nothing downstream told the translator what the finite target vocabulary actually
was.

Two agents were individually correct and the pipeline was still wrong, because the contract between
them was "translate this well" instead of "pick one of these exact N things or say none apply."

## The fix

Give the Skill Mapper the literal, finite list of skill names the Gap Analyst will compare against,
and instruct it to either copy one of those strings exactly or skip the concept. Verified with a
before/after real run: the same profile went from Python and Docker at 0% to both at 60%, with only
the genuinely uncovered gaps left. See `backend/app/agents/skill_mapper.py`'s module docstring and
`docs/changelog.md` iteration 4 for the full before/after.

## The practical lesson

**Whenever one agent's output becomes another component's lookup key, constrain that output to the
receiving side's actual vocabulary, don't let a model translate freely across a boundary that a
downstream string comparison depends on.** "Translate this concept into industry language" sounds
like the right instruction and produces good-looking individual outputs. It is the wrong instruction
whenever something later does `if mapped_name == target_name`. The fix is almost free once you see
it (pass the candidate list into the prompt, validate the response against it, drop anything that
doesn't match), but it's invisible until you actually run the system on input you didn't author
yourself. Every hand-crafted eval profile in this project used vocabulary that happened to already
line up with the taxonomy, which is exactly why this bug survived the mocked tests and the
eval dataset and only showed up the moment a real person typed in their own project descriptions.
The lesson generalizes past this project: a synthetic eval set built by the same person who built
the system will systematically fail to catch exactly this class of bug, because both were authored
with the same implicit vocabulary in mind.

## Runner-up, same shape

A second, smaller instance of the identical failure pattern: Groq's `openai/gpt-oss-120b` spends
hidden reasoning tokens before emitting its answer, and that reasoning length is invisible and
non-deterministic. A `max_tokens` budget sized for the visible answer alone silently produced empty
output on some calls and not others. Same root cause as above: an assumption ("this budget is
enough") that was true often enough to pass every test I wrote myself, and false exactly when a real
call happened to reason longer than expected. Fixed the same way conceptually, by not trusting a
fixed constant and instead detecting the specific failure and escalating (see `backend/app/llm.py`).
