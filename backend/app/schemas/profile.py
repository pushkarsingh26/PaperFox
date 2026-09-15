from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

SUPPORTED_RESUME_SECTIONS = [
    "summary",
    "education",
    "experience",
    "projects",
    "skills",
    "certifications",
]

DEFAULT_SECTION_ORDER = [
    "summary",
    "education",
    "experience",
    "projects",
    "skills",
    "certifications",
]


def normalize_technologies(v: Any) -> List[str]:
    """
    Normalizes technology input from string (comma-separated) or list of strings.
    Strips whitespace, filters empty values, and deduplicates case-insensitively
    while preserving the original casing of the first appearance.
    """
    if v is None:
        return []
    if isinstance(v, str):
        parts = v.split(",")
    elif isinstance(v, (list, tuple)):
        parts = []
        for item in v:
            if isinstance(item, str) and "," in item:
                parts.extend(item.split(","))
            elif isinstance(item, str):
                parts.append(item)
    else:
        return []

    cleaned: List[str] = []
    seen: set = set()
    for item in parts:
        if isinstance(item, str):
            t = item.strip()
            if t and t.lower() not in seen:
                seen.add(t.lower())
                cleaned.append(t)
    return cleaned


def validate_section_order_list(v: Any) -> Optional[List[str]]:
    if v is None:
        return None
    if isinstance(v, str):
        v = [s.strip() for s in v.split(",") if s.strip()]
    if not isinstance(v, (list, tuple)):
        raise ValueError("section_order must be a list of section identifiers")

    valid_sections = set(SUPPORTED_RESUME_SECTIONS)
    valid_sections.add("internships")
    cleaned: List[str] = []
    seen: set = set()
    for sec in v:
        if not isinstance(sec, str):
            raise ValueError("Section identifier must be a string")
        s = sec.strip().lower()
        if not s:
            raise ValueError("Section identifier cannot be empty")
        if s not in valid_sections:
            raise ValueError(
                f"Unknown section '{sec}'. Supported sections: {SUPPORTED_RESUME_SECTIONS}"
            )
        if s in seen:
            raise ValueError(f"Duplicate section '{sec}' is not allowed in section_order")
        seen.add(s)
        cleaned.append(s)
    return cleaned


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

    @field_validator("technologies", mode="before")
    def clean_technologies(cls, v):
        return normalize_technologies(v)

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

    @field_validator("technologies", mode="before")
    def clean_technologies(cls, v):
        return normalize_technologies(v)

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
    """
    Structured project evidence extracted from ai_analysis_text.
    Aligns with StructuredProjectEvidence in optimization_schema.
    Provenance: 'self' facts come from the user; 'ai_analysis' facts are AI-extracted.
    """
    status: Optional[str] = "unverified"         # unverified | current | stale
    source: Optional[str] = "ai_analysis"        # self | ai_analysis
    architecture: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    apis: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    deployment: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    technical_details: List[str] = Field(default_factory=list)
    engineering_decisions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    verified_at: Optional[datetime] = None


class ProjectSchema(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = ""
    technologies: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    project_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    repository_url: Optional[HttpUrl] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description_source: str = Field(default="self", description="'self' or 'ai'")
    ai_analysis_text: Optional[str] = Field(default=None, description="Raw plain-text analysis response pasted by candidate")
    evidence: Optional[EvidenceSchema] = None
    # Phase 7: evidence lifecycle tracking
    evidence_status: Optional[str] = Field(default=None, description="unverified | current | stale")
    evidence_updated_at: Optional[datetime] = Field(default=None, description="When evidence was last extracted")
    evidence_version: Optional[int] = Field(default=0, description="Increments on each extraction")

    @field_validator("technologies", mode="before")
    def clean_technologies(cls, v):
        return normalize_technologies(v)

    @field_validator("description_source", mode="before")
    def validate_description_source(cls, v):
        if not v or not isinstance(v, str):
            return "self"
        v_clean = v.strip().lower()
        if v_clean not in ("self", "ai"):
            raise ValueError("description_source must be 'self' or 'ai'")
        return v_clean

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

    @field_validator("category")
    def category_not_empty(cls, v):
        if not v or not v.strip():
            return "Other"
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
    section_order: Optional[List[str]] = None

    @field_validator("section_order", mode="before")
    def validate_section_order(cls, v):
        return validate_section_order_list(v)

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
    section_order: Optional[List[str]] = None

    @field_validator("section_order", mode="before")
    def validate_section_order(cls, v):
        return validate_section_order_list(v)

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
    section_order: Optional[List[str]] = None
    completion_percentage: int
    created_at: datetime
    updated_at: datetime
