from typing import Optional
from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user, get_mailing_service
from app.schemas.mailing_schema import (
    MailingDraftResponse,
    MailingDraftUpdate,
    MailingGenerateRequest,
)
from app.services.mailing_service import MailingService

router = APIRouter(prefix="/mailing", tags=["Mailing System"])


@router.post("/generate", response_model=MailingDraftResponse, status_code=status.HTTP_200_OK)
async def generate_outreach_email(
    req: MailingGenerateRequest,
    current_user: dict = Depends(get_current_user),
    mailing_service: MailingService = Depends(get_mailing_service),
):
    """
    Independent endpoint to generate a personalized cold outreach email
    consuming pre-existing JD Intelligence and Optimized Resume snapshots.
    """
    user_id = current_user["id"]
    return await mailing_service.generate_draft(user_id=user_id, req=req)


@router.get("/{job_id}", response_model=Optional[MailingDraftResponse])
async def get_outreach_draft(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    mailing_service: MailingService = Depends(get_mailing_service),
):
    """Retrieve saved outreach draft for a job application."""
    user_id = current_user["id"]
    return await mailing_service.get_draft(user_id=user_id, job_id=job_id)


@router.put("/{job_id}", response_model=MailingDraftResponse)
async def update_outreach_draft(
    job_id: str,
    body: MailingDraftUpdate,
    current_user: dict = Depends(get_current_user),
    mailing_service: MailingService = Depends(get_mailing_service),
):
    """Save user edits to the outreach draft for a job application."""
    user_id = current_user["id"]
    return await mailing_service.update_draft(user_id=user_id, job_id=job_id, update_in=body)
