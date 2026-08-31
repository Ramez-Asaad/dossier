# Reproduction Guide

Written for someone starting from a clean clone with nothing installed. Every command below is
exact, copy-pasteable, and was run to produce this doc.

## Versions this was built and tested against

- Python 3.11.15
- Node.js v24.11.1, npm 10.8.2
- Key Python packages (see `backend/requirements.txt` for the full pinned list): `anthropic==1.2.0`,
  `openai==3.6.0` (used for Groq's OpenAI-compatible endpoint, not OpenAI itself), `langgraph==1.2.11`,
  `fastapi==0.141.1`
- LLM: this run used Groq's `openai/gpt-oss-120b`. Anthropic Claude models work too, see the
  provider note below; results and cost differ by provider and are not claimed to be identical.

## 1. Get an API key

Free option: a Groq API key at <https://console.groq.com>, no payment method required for the free
tier used here. Anthropic works too if you'd rather use Claude, see `backend/app/llm.py` for how
provider selection works.

## 2. Backend setup

```
cd backend
python -m venv .venv
.venv/Scripts/activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set one of:
```
GROQ_API_KEY=your-key-here
```
or
```
ANTHROPIC_API_KEY=your-key-here
```
If both are set, Groq is used unless you set `LLM_PROVIDER=anthropic` explicitly.

Run the backend test suite. This needs no API key at all, every LLM call is mocked:
```
pytest
```
Expected output: `7 passed` in under 10 seconds.

Start the API:
```
uvicorn main:app --port 8001
```
`--reload` is intentionally omitted here: in this environment, `uvicorn --reload`'s file watcher
was observed to silently miss code changes. Restart manually after backend edits. Expected output:
`Application startup complete.` and the server listening on `http://127.0.0.1:8001`.

## 3. Frontend setup

```
cd frontend
npm install
cp .env.local.example .env.local
```
Edit `.env.local` so `NEXT_PUBLIC_API_BASE_URL` matches whatever port the backend is actually
running on (`http://localhost:8001` if you followed step 2 exactly).

```
npm run dev
```
Expected output: `Ready` with the server on `http://localhost:3000`. Open it, fill in the intake
form, and you should land on an animated agent trace followed by a results page.

## 4. Run the baseline vs. agent evaluation for real

From `backend/`, with the venv active and a real API key set:
```
python -m scripts.run_evaluation
```
Expected output: a line per profile (`profile-01` through `profile-10`) showing `baseline=` and
`agent=` coverage, followed by an average line. This is a real run against the live LLM, not
mocked, expect roughly 2-3 minutes total and negligible cost on Groq's free tier (10 profiles x
roughly 5-7 calls each). The numbers in `docs/evaluation-results.md` came from exactly this
command.

## 5. Try one realistic case end to end

Through the UI (`http://localhost:3000`), or directly:
```
curl -s -X POST http://127.0.0.1:8001/profile \
  -H "Content-Type: application/json" \
  -d '{"raw_courses":["Neural Networks"],"raw_projects":["Image classifier in Python with PyTorch, deployed with FastAPI and Docker"],"target_role":"ML Engineer"}'
```
Take the returned `session_id` and:
```
curl -s -X POST http://127.0.0.1:8001/sessions/<session_id>/generate-plan
```
Expected output: a JSON plan with `readiness_percent`, `demonstrated_skills`, `priority_gaps` (each
with a real `frequency` from the job-postings dataset), a `mission`, and `coverage`. Takes roughly
10 seconds on Groq.

## Cost and runtime summary

| Task | Approx. runtime | Approx. cost (Groq free tier) |
|---|---|---|
| One full plan generation | ~10s | effectively $0 |
| One baseline call | ~3s | effectively $0 |
| Full 10-profile evaluation | ~2-3 min | effectively $0 |
| Backend test suite (mocked) | <10s | $0, no API calls |

Anthropic pricing would apply per its published rates if `ANTHROPIC_API_KEY` is used instead;
see `docs/architecture.md`'s LLM call budget note for the approximate call count per run
(4-6 calls) to estimate cost under that provider.

## Known environment quirk

In the sandbox this was developed in, a killed process occasionally left a phantom TCP listener on
a port with no owning process (`netstat` showed it, `taskkill` reported "process not found"). If a
backend port refuses new connections for no visible reason, this is why, pick a different port
rather than debugging the ghost socket.
