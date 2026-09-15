from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


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
    created_at: datetime
    updated_at: datetime


class JobApplicationListResponse(BaseModel):
    items: List[JobApplicationResponse]
    total: int
