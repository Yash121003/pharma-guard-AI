# AI Complaint Management System -- Backend

FastAPI backend for an AI-powered customer complaint management system for
pharmaceutical manufacturing (AIVOA Round 1 assessment).

## Stack

Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, LangGraph, Groq
(`gemma2-9b-it` default, `llama-3.3-70b-versatile` optional).

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env, see below
```

You'll need a running PostgreSQL instance. Create the database:

```bash
psql -c "CREATE DATABASE complaint_mgmt;"
```

Then run migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger docs, or
`http://localhost:8000/health` for a quick status check.

## Environment Variables

See `.env.example` for the full list with inline documentation. The
important ones:

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | Yes | Postgres connection string |
| `SECRET_KEY` | Yes | JWT signing secret -- generate a real random value for anything beyond local dev |
| `GROQ_API_KEY` | Only if `AI_MOCK_MODE=false` | Get one free at https://console.groq.com/keys |
| `AI_MOCK_MODE` | No (defaults to `true`) | See "AI Modes" below |

## AI Modes

This project has two ways to run the AI features (document extraction,
chat assistant, summarize, root cause, CAPA, risk prediction, duplicate
detection, completeness check). Both are controlled by `AI_MOCK_MODE` in
`.env`, independent of whether `GROQ_API_KEY` is set.

### Mock mode (`AI_MOCK_MODE=true`) -- the default

- No calls are made to Groq at all, and no API key is required.
- Every AI endpoint returns a realistic, clearly-labeled mock response
  (prefixed `[MOCK RESPONSE]` / `[MOCK EXTRACTION]`) instead.
- The mock responses are deterministic enough to exercise the full
  workflow end-to-end: extract populates a form, chat answers questions,
  summarize/root-cause/capa/risk write to the complaint record, etc.
- Useful for: frontend development, demos, offline environments, CI, or
  any situation where you don't have (or don't want to spend) Groq quota.

### Live mode (`AI_MOCK_MODE=false`)

- Requires a valid `GROQ_API_KEY` and network access to `api.groq.com`.
- Every AI endpoint calls the real Groq API using the configured model
  (`GROQ_MODEL_DEFAULT`, currently `gemma2-9b-it`).
- If `GROQ_API_KEY` is missing in this mode, **the app still starts
  normally** -- it logs a clear warning at startup, exposes
  `"ai_status": "unconfigured"` on `GET /health`, and every AI endpoint
  returns a clean `502` with a descriptive error message until you set
  the key. No other part of the app (auth, complaints CRUD, etc.) is
  affected.

### Checking current AI status

```bash
curl http://localhost:8000/health
# {"status": "healthy", "environment": "development", "ai_status": "mock"}
#   ai_status is one of: "mock" | "live" | "unconfigured"
```

## Running Tests

```bash
# Verifies all SQLAlchemy models, relationships, and constraints against a real DB
python -m tests.smoke_test_models

# Verifies the LangGraph workflow routes and executes all 8 AI tasks correctly
# (LLM calls are mocked at the call_llm/call_llm_json boundary in this specific
# test, regardless of your AI_MOCK_MODE setting, to keep it fast and offline)
python -m tests.smoke_test_ai_graph
```

To exercise the AI endpoints for real against mock responses (no Groq
needed), just make sure `AI_MOCK_MODE=true` in `.env` and hit the running
server with curl or the Swagger UI at `/docs`.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── core/                 # config, security, logging
│   ├── db/                   # SQLAlchemy engine/session/init
│   ├── models/                # ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── api/v1/                  # route handlers (auth, complaints, uploads, ai)
│   ├── services/                # business logic
│   └── ai/                       # LangGraph workflow, nodes, Groq client, mock responses
├── alembic/                        # DB migrations
├── tests/                           # smoke tests + sample complaint files
├── requirements.txt
├── requirements-dev.txt              # ruff, reportlab (for regenerating test fixtures)
└── .env.example
```

## Sample Complaint Files

`tests/sample_files/` contains realistic mock pharmaceutical complaints in
all 4 supported formats (PDF, DOCX, TXT, EML) for testing the upload +
extraction flow.
