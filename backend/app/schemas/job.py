from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ApplicationStatus(str, Enum):
    """
    Lifecycle state of a job application.
    Changing status MUST NOT alter master profile, JD, optimization snapshot, or resume.
    """
    DRAFT = "draft"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"
    WITHDRAWN = "withdrawn"


class JobRequirements(BaseModel):
    """
    Structured JD Intelligence extracted by PaperFox AI Provider Router.
    """
    title: Optional[str] = Field(default=None, description="Job title extracted from JD")
    experience_years_required: Optional[float] = Field(default=None, description="Minimum years of experience required")
    education_required: Optional[str] = Field(default=None, description="Education or degree requirement")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have/preferred skills")
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    technologies_frameworks: List[str] = Field(default_factory=list, description="Libraries, frameworks, and databases")
    ai_ml_requirements: List[str] = Field(default_factory=list, description="AI, ML, LLM, or Data Science requirements")
    responsibilities: List[str] = Field(default_factory=list, description="Core job responsibilities")
    important_keywords: List[str] = Field(default_factory=list, description="High-priority keywords for resume ATS optimization")

    @field_validator(
        "required_skills", "preferred_skills", "programming_languages",
        "technologies_frameworks", "ai_ml_requirements", "responsibilities",
        "important_keywords", mode="before"
    )
    def ensure_list_of_strings(cls, v):
        if isinstance(v, list):
            return [str(item).strip() for item in v if item is not None and str(item).strip()]
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return []


class JobApplicationCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200, description="Company name")
    role_title: str = Field(..., min_length=1, max_length=200, description="Target job title")
    job_description: str = Field(..., min_length=10, description="Raw job description text")
    job_url: Optional[str] = Field(default=None, description="Link to job posting")
    location: Optional[str] = Field(default=None, max_length=200, description="Job location")

    @field_validator("company_name", "role_title", "job_description", mode="before")
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class JobApplicationUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    role_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    job_description: Optional[str] = Field(default=None, min_length=10)
    job_url: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)


class ATSValidation(BaseModel):
    """ATS readability and structure validation results."""
    is_single_page: bool = False
    page_count: int = 0
    text_extractable: bool = True
    has_summary: bool = False
    has_skills: bool = False
    has_education: bool = False
    has_experience_or_projects: bool = False


class JobResumeArtifact(BaseModel):
    """
    Phase 6 artifact: a job-specific compiled resume.
    Stored as a subdocument inside the job_applications MongoDB document.
    """
    latex_source: str = Field(..., description="Complete LaTeX source string")
    pdf_storage_reference: Optional[str] = Field(
        default=None,
        description="storage:// URI pointing to the compiled PDF binary"
    )
    page_count: int = Field(default=0, description="Number of pages in the compiled PDF")
    compression_level_used: int = Field(
        default=0,
        description="Compression level applied (0 = no compression, 5 = max)"
    )
    status: str = Field(
        default="pending",
        description="One of: success | overflow | compiler_unavailable | error"
    )
    ats_validation: ATSValidation = Field(default_factory=ATSValidation)
    error_message: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class JobApplicationResponse(BaseModel):
    id: str = Field(..., description="Unique job application ID")
    user_id: str = Field(..., description="Owner user ID")
    company_name: str
    role_title: str
    job_description: str
    job_url: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[JobRequirements] = None
    analysis_provider: Optional[str] = None
    analysis_model: Optional[str] = None
    is_analyzed: bool = False
    optimization: Optional[Dict[str, Any]] = None
    is_optimized: bool = False
    job_resume_artifact: Optional[Dict[str, Any]] = None
    is_resume_generated: bool = False
    # Phase 7: application lifecycle
    application_status: str = Field(default="draft", description="draft|applied|interview|rejected|offer|withdrawn")
    notes: Optional[str] = None
    status_updated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class JobApplicationListResponse(BaseModel):
    items: List[JobApplicationResponse]
    total: int


# ── Phase 7: Application History schemas ──────────────────────────────────────

class JobStatusUpdate(BaseModel):
    """Request body for PATCH /jobs/{job_id}/status"""
    status: ApplicationStatus


class JobNotesUpdate(BaseModel):
    """Request body for PATCH /jobs/{job_id}/notes"""
    notes: str = Field(default="", max_length=5000, description="Free-text notes for this application")


class JobHistoryItem(BaseModel):
    """Lightweight view of a job application for history listing."""
    id: str
    company_name: str
    role_title: str
    job_url: Optional[str] = None
    location: Optional[str] = None
    application_status: str = "draft"
    notes: Optional[str] = None
    is_analyzed: bool = False
    is_optimized: bool = False
    is_resume_generated: bool = False
    status_updated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class JobHistoryResponse(BaseModel):
    items: List[JobHistoryItem]
    total: int
    status_filter: Optional[str] = None


class JobHistoryStats(BaseModel):
    total: int = 0
    by_status: Dict[str, int] = Field(default_factory=dict)
