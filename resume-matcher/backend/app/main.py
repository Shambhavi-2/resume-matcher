from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .config import get_settings
from .routers import auth, resumes, jobs, match

settings = get_settings()

# Creates tables on startup if they don't exist yet. Fine for this project's
# scope; a production app would use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Resume Matcher API",
    description="AI-powered resume-to-job matching with explainable scoring.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(match.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
