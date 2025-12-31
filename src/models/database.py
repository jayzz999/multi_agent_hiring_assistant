"""Database models and schemas for HR automation system."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/hr_automation.db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class JobStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"
    FILLED = "filled"
    CANCELLED = "cancelled"


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    SCREENED_IN = "screened_in"
    SCREENED_OUT = "screened_out"
    ASSESSMENT = "assessment"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_PENDING = "offer_pending"
    OFFER_SENT = "offer_sent"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class InterviewType(str, Enum):
    PHONE_SCREEN = "phone_screen"
    VIDEO = "video"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"
    ONSITE = "onsite"
    AI_SCREENING = "ai_screening"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class OfferStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


# SQLAlchemy Models
class Job(Base):
    """Job posting/requisition."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    department = Column(String)
    location = Column(String)
    job_type = Column(String)  # full-time, part-time, contract
    description = Column(Text, nullable=False)
    requirements = Column(JSON)  # structured requirements
    skills_required = Column(JSON)  # list of skills
    experience_min = Column(Integer)  # years
    experience_max = Column(Integer)
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String, default="USD")
    status = Column(SQLEnum(JobStatus), default=JobStatus.DRAFT)
    hiring_manager_id = Column(String)
    recruiter_id = Column(String)
    openings = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    posted_at = Column(DateTime)
    closed_at = Column(DateTime)
    job_metadata = Column(JSON)  # additional metadata

    # Relationships
    applications = relationship("Application", back_populates="job")
    interviews = relationship("Interview", back_populates="job")


class Candidate(Base):
    """Candidate information."""
    __tablename__ = "candidates"

    id = Column(String, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    portfolio_url = Column(String)
    current_title = Column(String)
    current_company = Column(String)
    location = Column(String)
    willing_to_relocate = Column(Boolean, default=False)
    work_authorization = Column(String)
    years_of_experience = Column(Float)
    skills = Column(JSON)  # list of skills
    education = Column(JSON)  # list of education entries
    experience = Column(JSON)  # list of work experience
    resume_url = Column(String)  # S3/storage URL
    resume_text = Column(Text)  # parsed resume text
    resume_vector_id = Column(String)  # ChromaDB ID
    source = Column(String)  # where they came from
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    candidate_metadata = Column(JSON)

    # Relationships
    applications = relationship("Application", back_populates="candidate")
    interviews = relationship("Interview", back_populates="candidate")
    offers = relationship("Offer", back_populates="candidate")


class Application(Base):
    """Job application."""
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, index=True)
    source = Column(String)  # LinkedIn, Indeed, Referral, etc.
    referrer_id = Column(String)  # if referred by employee
    applied_at = Column(DateTime, default=datetime.utcnow)

    # Screening
    screening_score = Column(Float)
    screening_passed = Column(Boolean)
    screening_notes = Column(Text)
    screening_ai_analysis = Column(JSON)

    # Matching
    skills_match_score = Column(Float)
    experience_match_score = Column(Float)
    culture_fit_score = Column(Float)
    overall_match_score = Column(Float)

    # Assessment
    assessment_sent_at = Column(DateTime)
    assessment_completed_at = Column(DateTime)
    assessment_score = Column(Float)
    assessment_results = Column(JSON)

    # Ranking
    final_rank = Column(Integer)
    ranking_notes = Column(Text)

    # Metadata
    resume_file_path = Column(String)
    cover_letter = Column(Text)
    knockout_answers = Column(JSON)
    application_metadata = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")


class Interview(Base):
    """Interview scheduling and feedback."""
    __tablename__ = "interviews"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    interview_type = Column(SQLEnum(InterviewType), nullable=False)
    status = Column(SQLEnum(InterviewStatus), default=InterviewStatus.SCHEDULED)
    round_number = Column(Integer, default=1)

    # Scheduling
    scheduled_at = Column(DateTime)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String)
    meeting_link = Column(String)
    meeting_room = Column(String)
    calendar_event_id = Column(String)

    # Interviewers
    interviewer_ids = Column(JSON)  # list of interviewer IDs
    panel_lead_id = Column(String)

    # Feedback
    completed_at = Column(DateTime)
    feedback = Column(JSON)  # list of feedback from each interviewer
    overall_rating = Column(Float)
    recommendation = Column(String)  # hire, no-hire, maybe
    feedback_notes = Column(Text)

    # AI Analysis (for AI interviews)
    transcript = Column(Text)
    sentiment_analysis = Column(JSON)
    technical_evaluation = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    interview_metadata = Column(JSON)

    # Relationships
    job = relationship("Job", back_populates="interviews")
    candidate = relationship("Candidate", back_populates="interviews")
    application = relationship("Application", back_populates="interviews")


class Offer(Base):
    """Job offer."""
    __tablename__ = "offers"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    status = Column(SQLEnum(OfferStatus), default=OfferStatus.DRAFT)

    # Compensation
    base_salary = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    bonus = Column(Float)
    equity = Column(String)
    benefits = Column(JSON)

    # Details
    start_date = Column(DateTime)
    job_title = Column(String)
    department = Column(String)
    location = Column(String)
    employment_type = Column(String)

    # Offer letter
    offer_letter_url = Column(String)
    offer_letter_template_id = Column(String)
    custom_terms = Column(Text)

    # Workflow
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    sent_at = Column(DateTime)
    expires_at = Column(DateTime)
    accepted_at = Column(DateTime)
    declined_at = Column(DateTime)

    # Approvals
    approvals = Column(JSON)  # list of approvers and status

    # Negotiation
    negotiation_history = Column(JSON)
    final_terms = Column(JSON)

    # Signature
    signature_request_id = Column(String)  # DocuSign/HelloSign ID
    signed_document_url = Column(String)

    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    offer_metadata = Column(JSON)

    # Relationships
    candidate = relationship("Candidate", back_populates="offers")


class CommunicationLog(Base):
    """Communication history with candidates."""
    __tablename__ = "communications"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"))
    channel = Column(String)  # email, sms, whatsapp, call
    direction = Column(String)  # inbound, outbound
    subject = Column(String)
    content = Column(Text)
    template_id = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    replied_at = Column(DateTime)
    status = Column(String)
    comm_metadata = Column(JSON)


class Assessment(Base):
    """Skills assessment/test."""
    __tablename__ = "assessments"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    assessment_type = Column(String)  # coding, behavioral, cognitive
    platform = Column(String)  # HackerRank, Codility, internal
    external_id = Column(String)  # ID in external platform

    # Test details
    test_name = Column(String)
    difficulty = Column(String)
    duration_minutes = Column(Integer)

    # Status
    sent_at = Column(DateTime)
    started_at = Column(DateTime)
    submitted_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Results
    score = Column(Float)
    max_score = Column(Float)
    percentile = Column(Float)
    passed = Column(Boolean)
    results = Column(JSON)
    feedback = Column(Text)

    # Plagiarism
    plagiarism_detected = Column(Boolean, default=False)
    plagiarism_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    assessment_metadata = Column(JSON)


class Referral(Base):
    """Employee referrals."""
    __tablename__ = "referrals"

    id = Column(String, primary_key=True)
    employee_id = Column(String, nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"))

    status = Column(String)
    bonus_amount = Column(Float)
    bonus_paid = Column(Boolean, default=False)
    bonus_paid_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    referral_metadata = Column(JSON)


class JobPosting(Base):
    """Job postings on external boards."""
    __tablename__ = "job_postings"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    board = Column(String, nullable=False)  # LinkedIn, Indeed, etc.
    external_id = Column(String)
    url = Column(String)

    posted_at = Column(DateTime)
    expires_at = Column(DateTime)
    closed_at = Column(DateTime)

    views = Column(Integer, default=0)
    applications = Column(Integer, default=0)
    cost = Column(Float)

    status = Column(String)
    posting_metadata = Column(JSON)


# Pydantic Models for API
class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = "full-time"
    description: str
    requirements: Optional[Dict[str, Any]] = None
    skills_required: Optional[List[str]] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    hiring_manager_id: Optional[str] = None
    openings: int = 1


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    current_title: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None


class ApplicationCreate(BaseModel):
    job_id: str
    candidate_id: Optional[str] = None  # If new candidate, will be created
    candidate_data: Optional[CandidateCreate] = None
    source: Optional[str] = None
    referrer_id: Optional[str] = None
    cover_letter: Optional[str] = None
    knockout_answers: Optional[Dict[str, Any]] = None


class InterviewCreate(BaseModel):
    job_id: str
    candidate_id: str
    application_id: str
    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int = 60
    interviewer_ids: List[str]
    meeting_link: Optional[str] = None


class OfferCreate(BaseModel):
    job_id: str
    candidate_id: str
    base_salary: float
    currency: str = "USD"
    bonus: Optional[float] = None
    equity: Optional[str] = None
    start_date: Optional[datetime] = None
    job_title: str
    employment_type: str = "full-time"


def init_db():
    """Initialize database tables."""
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
