from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.job import JobRequirements


class JobApplicationModel(BaseModel):
    """
    MongoDB Document schema for `job_applications` collection.
    """
    id: str = Field(..., alias="_id")
    user_id: str = Field(...)
    company_name: str
    role_title: str
    job_description: str
    job_url: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    analysis_provider: Optional[str] = None
    analysis_model: Optional[str] = None
    is_analyzed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
