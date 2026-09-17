from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MailingJobContext(BaseModel):
    company: str
    role: str


class MailingJDContext(BaseModel):
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    important_keywords: List[str] = Field(default_factory=list)


class MailingCandidateContext(BaseModel):
    name: str
    summary: str
    skills: List[str] = Field(default_factory=list)


class MailingProjectContext(BaseModel):
    name: str
    technologies: List[str] = Field(default_factory=list)
    description: List[str] = Field(default_factory=list)


class MailingRecipientContext(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class MailingInput(BaseModel):
    """
    Normalized, self-contained JSON input prepared by MailingDataBuilder
    from existing JD Intelligence and Optimized Resume data.
    """
    job: MailingJobContext
    jd_context: MailingJDContext
    candidate: MailingCandidateContext
    relevant_projects: List[MailingProjectContext] = Field(default_factory=list)
    recipient: MailingRecipientContext


class MailingGenerateRequest(BaseModel):
    job_id: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_role: Optional[str] = None
    is_short: bool = False


class MailingDraftUpdate(BaseModel):
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_role: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    short_body: Optional[str] = None
    status: Optional[str] = "ready"


class MailingDraftResponse(BaseModel):
    job_id: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_role: Optional[str] = None
    subject: str
    subject_options: List[str] = Field(default_factory=list)
    body: str
    short_body: Optional[str] = None
    selected_evidence: List[str] = Field(default_factory=list)
    status: str = "draft"
    generated_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MailingAIResponse(BaseModel):
    subject: str = Field(description="The single strongest, professional outreach subject line")
    subject_options: List[str] = Field(default_factory=list, description="2-3 alternative subject line options")
    body: str = Field(description="Full natural, authentic cold outreach email body")
    short_body: Optional[str] = Field(default=None, description="Concise 2-3 paragraph alternative version")
    selected_evidence: List[str] = Field(default_factory=list, description="1-3 short strings noting candidate evidence cited")
