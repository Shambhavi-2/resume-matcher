# Fieldnotes — AI Resume-to-Job Matcher

An explainable resume-matching tool: upload a resume and a job description, and get back a
score plus a breakdown of *which* requirements are covered, which are missing, and specific
rewrites to close the gaps — not just a black-box percentage.

**Stack**
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, JWT auth
- **AI:** `sentence-transformers` embeddings for retrieval (stage 1) + an LLM for explanation
  generation (stage 2), with a heuristic fallback if no LLM key is set
- **Frontend:** React + Vite, plain CSS (no framework), custom "editor's desk" design
- **Infra:** Docker Compose (Postgres + FastAPI + Nginx-served React build)

## How the matching pipeline works

1. **Parse** — the resume (PDF/DOCX/TXT) and job description are split into chunks
   (`backend/app/parsing.py`).
2. **Retrieve** — each job-requirement chunk is embedded and compared via cosine similarity
   against every resume chunk to find its best match (`backend/app/embeddings.py`). This is
   the retrieval stage: cheap, fast, fully local, no API cost.
3. **Explain** — the matched (requirement, resume-snippet, similarity) triples are handed to
   an LLM, which writes the strengths/gaps/suggestions in plain language
   (`backend/app/llm.py`). If `OPENAI_API_KEY` isn't set, a rule-based fallback still produces
   a usable (if blunter) explanation — the app never hard-fails just because no LLM key is
   configured.
4. **Serve async** — matching runs as a FastAPI `BackgroundTask` so the upload/match endpoints
   return immediately; the frontend polls `/matches/{id}` until it's done. This is the same
   pattern you'd extend into an actual Celery/Redis queue for production load — the task body
   would move over almost unchanged (see the docstring in `backend/app/routers/match.py`).

## Project structure

```
resume-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + CORS + router registration
│   │   ├── config.py          # env-based settings
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # User, Resume, JobDescription, MatchResult
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── auth.py            # JWT + password hashing
│   │   ├── parsing.py         # PDF/DOCX/TXT extraction + chunking
│   │   ├── embeddings.py      # sentence-transformers + cosine similarity
│   │   ├── llm.py             # LLM explanation layer + heuristic fallback
│   │   └── routers/           # auth, resumes, jobs, matches
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api.js             # fetch wrapper for the backend
│   │   ├── components/        # Navbar, UploadForm, ScoreStamp, MatchResult
│   │   └── pages/             # Home, Login, Register, Dashboard
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── .gitignore
```

## Running locally with Docker (recommended)

```bash
git clone <your-repo-url>
cd resume-matcher

# 1. Configure the backend
cp backend/.env.example backend/.env
# Edit backend/.env: set a real SECRET_KEY, optionally add OPENAI_API_KEY

# 2. Build and start everything (Postgres + API + frontend)
docker compose up --build
```

Then open:
- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

## Running locally without Docker (dev mode)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# For local dev without Postgres, set DATABASE_URL=sqlite:///./matcher.db in .env
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Pushing this to GitHub

```bash
cd resume-matcher
git init
git add .
git commit -m "Initial commit: AI resume-to-job matcher"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

`.env` files are already excluded via `.gitignore` — only `.env.example` files are committed,
so no secrets end up in the repo.

## Deploying

- **Backend + Postgres:** any host that runs Docker Compose (a small VPS, Railway, Render,
  Fly.io). Point `DATABASE_URL` at a managed Postgres instance if you don't want to run it
  in a container in production.
- **Frontend:** the built static files in `frontend/dist` can also be deployed standalone to
  Vercel/Netlify/Cloudflare Pages — just set `VITE_API_URL` to your deployed backend URL at
  build time.
- Set `ALLOWED_ORIGINS` in `backend/.env` to your deployed frontend's URL so CORS allows it.

## Notes on scope / what's intentionally simplified

- **No Celery/Redis queue** — FastAPI's `BackgroundTasks` is used instead to keep the compose
  stack to 3 services. Swapping in Celery is a natural next step if you need retries, task
  monitoring, or to run matching on a separate worker fleet.
- **No FAISS/pgvector index** — since a match only compares one resume against one job
  description at a time (not a search over thousands of documents), plain in-memory cosine
  similarity is enough. Add a vector index if you extend this to "search many resumes for the
  best candidates for a job."

## Stretch ideas

- Swap `BackgroundTasks` for Celery + Redis for production-grade async processing
- Add a browser extension that scrapes a LinkedIn/Indeed posting into the job description field
- Fine-tune the scoring rubric/prompt so repeated runs on the same inputs are more consistent
- Track feedback (`helpful` / `not_helpful`) over time to evaluate prompt changes
