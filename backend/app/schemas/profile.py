from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class PersonalDetails(BaseModel):
    full_name: str = Field(..., min_length=1, description="Full candidate name")
    phone: Optional[str] = None
    portfolio_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None

    @field_validator("portfolio_url", "linkedin_url", "github_url", mode="before")
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v


class InternshipSchema(BaseModel):
    id: Optional[str] = None
    company: str
    role: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_dates(self):
        if not self.is_current and self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot be earlier than start_date")
        return self


class WorkExperienceSchema(BaseModel):
    id: Optional[str] = None
    company: str
    role: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_dates(self):
        if not self.is_current and self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot be earlier than start_date")
        return self


class EducationSchema(BaseModel):
    id: Optional[str] = None
    institution: str
    degree: str
    field_of_study: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    grade: Optional[str] = None
    grade_type: Optional[str] = None
    description: Optional[str] = None


class EvidenceSchema(BaseModel):
    status: Optional[str] = "unverified"
    source: Optional[str] = None
    architecture: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    APIs: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    deployment: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    technical_details: List[str] = Field(default_factory=list)
    verified_at: Optional[datetime] = None


class ProjectSchema(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    project_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    repository_url: Optional[HttpUrl] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    evidence: Optional[EvidenceSchema] = None

    @field_validator("project_url", "github_url", "repository_url", mode="before")
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v


class SkillSchema(BaseModel):
    id: Optional[str] = None
    name: str
    category: str = "Other"

    @field_validator("name")
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Skill name cannot be empty")
        return v.strip()


class CertificationSchema(BaseModel):
    id: Optional[str] = None
    name: str
    issuer: str
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[HttpUrl] = None
    description: Optional[str] = None

    @field_validator("credential_url", mode="before")
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v


class ProfileCreate(BaseModel):
    personal_details: PersonalDetails
    candidate_type: str = Field("fresher", description="fresher or experienced")
    profile_status: str = Field("draft", description="draft or complete")
    internships: List[InternshipSchema] = Field(default_factory=list)
    experience: List[WorkExperienceSchema] = Field(default_factory=list)
    education: List[EducationSchema] = Field(default_factory=list)
    projects: List[ProjectSchema] = Field(default_factory=list)
    skills: List[SkillSchema] = Field(default_factory=list)
    certifications: List[CertificationSchema] = Field(default_factory=list)

    @field_validator("skills")
    def prevent_duplicate_skills(cls, skills: List[SkillSchema]):
        seen = set()
        for skill in skills:
            normalized_name = skill.name.strip().lower()
            if normalized_name in seen:
                raise ValueError(f"Duplicate skill '{skill.name}' is not allowed")
            seen.add(normalized_name)
        return skills


class ProfileUpdate(BaseModel):
    personal_details: Optional[PersonalDetails] = None
    candidate_type: Optional[str] = None
    profile_status: Optional[str] = None
    internships: Optional[List[InternshipSchema]] = None
    experience: Optional[List[WorkExperienceSchema]] = None
    education: Optional[List[EducationSchema]] = None
    projects: Optional[List[ProjectSchema]] = None
    skills: Optional[List[SkillSchema]] = None
    certifications: Optional[List[CertificationSchema]] = None

    @field_validator("skills")
    def prevent_duplicate_skills(cls, skills: Optional[List[SkillSchema]]):
        if skills is None:
            return skills
        seen = set()
        for skill in skills:
            normalized_name = skill.name.strip().lower()
            if normalized_name in seen:
                raise ValueError(f"Duplicate skill '{skill.name}' is not allowed")
            seen.add(normalized_name)
        return skills


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    profile_status: str
    personal_details: Dict[str, Any]
    candidate_type: str
    internships: List[Dict[str, Any]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    completion_percentage: int
    created_at: datetime
    updated_at: datetime
