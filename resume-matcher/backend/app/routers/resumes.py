from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user
from ..parsing import extract_text

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload", response_model=schemas.ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File is too large (max 5MB).")

    try:
        text = extract_text(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Couldn't extract any text from that file. If it's a scanned PDF, try a text-based export instead.",
        )

    resume = models.Resume(owner_id=current_user.id, filename=file.filename, raw_text=text)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=List[schemas.ResumeOut])
def list_resumes(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.Resume)
        .filter(models.Resume.owner_id == current_user.id)
        .order_by(models.Resume.created_at.desc())
        .all()
    )


@router.delete("/{resume_id}", status_code=204)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.id == resume_id, models.Resume.owner_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    db.delete(resume)
    db.commit()
