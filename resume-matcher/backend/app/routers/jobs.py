from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=schemas.JobOut, status_code=201)
def create_job(
    job_in: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not job_in.raw_text.strip():
        raise HTTPException(status_code=400, detail="Job description text can't be empty.")

    job = models.JobDescription(
        owner_id=current_user.id, title=job_in.title, raw_text=job_in.raw_text
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=List[schemas.JobOut])
def list_jobs(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.JobDescription)
        .filter(models.JobDescription.owner_id == current_user.id)
        .order_by(models.JobDescription.created_at.desc())
        .all()
    )


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    job = (
        db.query(models.JobDescription)
        .filter(models.JobDescription.id == job_id, models.JobDescription.owner_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
    db.delete(job)
    db.commit()
