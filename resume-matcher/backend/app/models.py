from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("JobDescription", back_populates="owner", cascade="all, delete-orphan")
    matches = relationship("MatchResult", back_populates="owner", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    owner = relationship("User", back_populates="resumes")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    owner = relationship("User", back_populates="jobs")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)

    status = Column(String, default="pending")  # pending | processing | done | failed
    score = Column(Float, nullable=True)
    strengths = Column(JSON, nullable=True)
    gaps = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    matched_chunks = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    feedback = Column(String, nullable=True)  # helpful | not_helpful | null

    created_at = Column(DateTime, default=utcnow)

    owner = relationship("User", back_populates="matches")
    resume = relationship("Resume")
    job = relationship("JobDescription")
