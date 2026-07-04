from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResumeOut(BaseModel):
    id: int
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    raw_text: str


class JobOut(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    resume_id: int
    job_id: int


class MatchOut(BaseModel):
    id: int
    resume_id: int
    job_id: int
    status: str
    score: Optional[float] = None
    strengths: Optional[List[str]] = None
    gaps: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    matched_chunks: Optional[List[Any]] = None
    error: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackIn(BaseModel):
    feedback: str  # "helpful" | "not_helpful"
