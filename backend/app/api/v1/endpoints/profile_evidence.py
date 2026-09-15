"""
profile_evidence.py — Phase 7 Project Evidence API endpoints.

Routes:
  POST /api/v1/profile/projects/{project_id}/extract-evidence
    Triggers evidence extraction from the project's ai_analysis_text.
    Uses the free-model AI router (ProjectEvidenceParser).
    Idempotent: skips re-extraction if evidence is already current (unless ?force=true).

  GET /api/v1/profile/projects/{project_id}/evidence
    Returns stored evidence for a project (no AI call).
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_project_evidence_service
from app.services.project_evidence_service import ProjectEvidenceService

router = APIRouter(prefix="/profile/projects", tags=["Project Evidence"])


@router.post(
    "/{project_id}/extract-evidence",
    summary="Extract structured evidence from project AI analysis",
    response_model=Dict[str, Any],
)
async def extract_project_evidence(
    project_id: str,
    force: bool = Query(
        default=False,
        description="Force re-extraction even if evidence is already current",
    ),
    current_user: dict = Depends(get_current_user),
    evidence_service: ProjectEvidenceService = Depends(get_project_evidence_service),
) -> Dict[str, Any]:
    """
    Extracts structured evidence from the project's stored ai_analysis_text.

    Idempotent: if evidence_status == 'current' and force=False, returns cached evidence.
    Set ?force=true to re-extract after updating ai_analysis_text.

    The raw ai_analysis_text is NEVER modified by this endpoint.
    """
    user_id = current_user.get("id") or str(current_user.get("_id", ""))
    return await evidence_service.extract_and_store(
        user_id=user_id,
        project_id=project_id,
        force_reextract=force,
    )


@router.get(
    "/{project_id}/evidence",
    summary="Get stored evidence for a project",
    response_model=Dict[str, Any],
)
async def get_project_evidence(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    evidence_service: ProjectEvidenceService = Depends(get_project_evidence_service),
) -> Dict[str, Any]:
    """
    Returns the stored structured evidence for a project (no AI call).
    Returns 404 if evidence has not been extracted yet.
    """
    user_id = current_user.get("id") or str(current_user.get("_id", ""))
    return await evidence_service.get_stored_evidence(
        user_id=user_id,
        project_id=project_id,
    )
