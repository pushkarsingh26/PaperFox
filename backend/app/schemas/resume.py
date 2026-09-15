from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ResumeArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    type: str
    latex_source: str
    pdf_storage_reference: Optional[str] = None
    page_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ResumeGenerateResponse(BaseModel):
    status: str
    message: str
    page_count: int
    pdf_storage_reference: Optional[str] = None
    artifact: Optional[ResumeArtifactResponse] = None
