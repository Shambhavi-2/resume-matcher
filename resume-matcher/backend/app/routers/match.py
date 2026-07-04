from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db, SessionLocal
from ..auth import get_current_user
from ..parsing import chunk_text
from ..embeddings import score_resume_against_job
from ..llm import generate_explanation

router = APIRouter(prefix="/matches", tags=["matches"])


def run_match_pipeline(match_id: int):
    """
    Runs in a FastAPI BackgroundTask (out of the request/response cycle) so
    uploads and match requests return instantly while the heavier embedding +
    LLM work happens after the response is sent. Uses its own DB session
    since the request-scoped session is closed by the time this runs.

    For higher-throughput production use, swap this for a Celery task backed
    by Redis/RabbitMQ - the function body below would move into the task
    almost unchanged.
    """
    db = SessionLocal()
    try:
        match = db.query(models.MatchResult).filter(models.MatchResult.id == match_id).first()
        if not match:
            return

        match.status = "processing"
        db.commit()

        resume = db.query(models.Resume).filter(models.Resume.id == match.resume_id).first()
        job = db.query(models.JobDescription).filter(models.JobDescription.id == match.job_id).first()

        resume_chunks = chunk_text(resume.raw_text)
        job_chunks = chunk_text(job.raw_text)

        result = score_resume_against_job(resume_chunks, job_chunks)
        explanation = generate_explanation(result["matches"])

        match.score = result["score"]
        match.matched_chunks = result["matches"]
        match.strengths = explanation["strengths"]
        match.gaps = explanation["gaps"]
        match.suggestions = explanation["suggestions"]
        match.status = "done"
        db.commit()
    except Exception as e:
        match = db.query(models.MatchResult).filter(models.MatchResult.id == match_id).first()
        if match:
            match.status = "failed"
            match.error = str(e)
            db.commit()
    finally:
        db.close()


@router.post("", response_model=schemas.MatchOut, status_code=202)
def create_match(
    match_in: schemas.MatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.id == match_in.resume_id, models.Resume.owner_id == current_user.id)
        .first()
    )
    job = (
        db.query(models.JobDescription)
        .filter(
            models.JobDescription.id == match_in.job_id,
            models.JobDescription.owner_id == current_user.id,
        )
        .first()
    )
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job description not found.")

    match = models.MatchResult(
        owner_id=current_user.id,
        resume_id=resume.id,
        job_id=job.id,
        status="pending",
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    background_tasks.add_task(run_match_pipeline, match.id)
    return match


@router.get("/{match_id}", response_model=schemas.MatchOut)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    match = (
        db.query(models.MatchResult)
        .filter(models.MatchResult.id == match_id, models.MatchResult.owner_id == current_user.id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found.")
    return match


@router.get("", response_model=List[schemas.MatchOut])
def list_matches(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.MatchResult)
        .filter(models.MatchResult.owner_id == current_user.id)
        .order_by(models.MatchResult.created_at.desc())
        .all()
    )


@router.post("/{match_id}/feedback", response_model=schemas.MatchOut)
def submit_feedback(
    match_id: int,
    feedback_in: schemas.FeedbackIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if feedback_in.feedback not in ("helpful", "not_helpful"):
        raise HTTPException(status_code=400, detail="Feedback must be 'helpful' or 'not_helpful'.")

    match = (
        db.query(models.MatchResult)
        .filter(models.MatchResult.id == match_id, models.MatchResult.owner_id == current_user.id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found.")

    match.feedback = feedback_in.feedback
    db.commit()
    db.refresh(match)
    return match
