"""
application_history_service.py — Phase 7 Application Lifecycle Service.

Manages:
- Application status transitions (draft → applied → interview → offer/rejected/withdrawn)
- Notes updates
- History retrieval (with optional status filtering)
- Per-status statistics

Invariants:
- Changing status NEVER mutates master profile, JD, optimization snapshot, or generated resume
- All operations enforce strict user_id ownership
- Business logic stays in the service layer, not route handlers
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.repositories.job_repository import JobRepository
from app.schemas.job import (
    ApplicationStatus,
    JobHistoryItem,
    JobHistoryResponse,
    JobHistoryStats,
    JobApplicationResponse,
    JobRequirements,
)

logger = logging.getLogger(__name__)

# All valid status values
VALID_STATUSES = {s.value for s in ApplicationStatus}


class ApplicationHistoryService:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def _doc_to_history_item(self, doc: Dict[str, Any]) -> JobHistoryItem:
        return JobHistoryItem(
            id=str(doc["_id"]),
            company_name=doc["company_name"],
            role_title=doc["role_title"],
            job_url=doc.get("job_url"),
            location=doc.get("location"),
            application_status=doc.get("application_status", "draft"),
            notes=doc.get("notes"),
            is_analyzed=doc.get("is_analyzed", False),
            is_optimized=doc.get("is_optimized", False),
            is_resume_generated=doc.get("is_resume_generated", False),
            status_updated_at=doc.get("status_updated_at"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    async def update_status(
        self, user_id: str, job_id: str, new_status: str
    ) -> JobApplicationResponse:
        """
        Transition application status.

        Validates:
        - job exists and belongs to user
        - new_status is a valid ApplicationStatus value

        Guarantees:
        - Master profile, JD, optimization, and generated resume are NOT touched
        """
        # Validate status value
        if new_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid application status '{new_status}'. "
                    f"Valid values: {sorted(VALID_STATUSES)}"
                ),
            )

        # Ownership guard
        existing = await self.job_repository.get_by_id(job_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found.",
            )

        updated = await self.job_repository.update_status(job_id, user_id, new_status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update application status.",
            )

        return self._doc_to_full_response(updated)

    async def update_notes(
        self, user_id: str, job_id: str, notes: str
    ) -> JobApplicationResponse:
        """Update free-text notes. Never changes status, profile, JD, or resume."""
        existing = await self.job_repository.get_by_id(job_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found.",
            )

        updated = await self.job_repository.update_notes(job_id, user_id, notes)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update notes.",
            )

        return self._doc_to_full_response(updated)

    async def get_history(
        self, user_id: str, status_filter: Optional[str] = None
    ) -> JobHistoryResponse:
        """Return application history, optionally filtered by status."""
        if status_filter and status_filter not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status filter '{status_filter}'. Valid: {sorted(VALID_STATUSES)}",
            )

        docs = await self.job_repository.list_by_status(user_id, status_filter)
        items = [self._doc_to_history_item(d) for d in docs]
        return JobHistoryResponse(
            items=items,
            total=len(items),
            status_filter=status_filter,
        )

    async def get_stats(self, user_id: str) -> JobHistoryStats:
        """Return per-status counts for the user's applications."""
        stats_dict = await self.job_repository.get_stats(user_id)
        total = sum(stats_dict.values())
        return JobHistoryStats(total=total, by_status=stats_dict)

    def _doc_to_full_response(self, doc: Dict[str, Any]) -> JobApplicationResponse:
        """Build a full JobApplicationResponse from a raw MongoDB document."""
        reqs = None
        if doc.get("requirements"):
            try:
                reqs = JobRequirements(**doc["requirements"])
            except Exception:
                reqs = None

        return JobApplicationResponse(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            company_name=doc["company_name"],
            role_title=doc["role_title"],
            job_description=doc["job_description"],
            job_url=doc.get("job_url"),
            location=doc.get("location"),
            requirements=reqs,
            analysis_provider=doc.get("analysis_provider"),
            analysis_model=doc.get("analysis_model"),
            is_analyzed=doc.get("is_analyzed", False),
            optimization=doc.get("optimization"),
            is_optimized=doc.get("is_optimized", False),
            job_resume_artifact=doc.get("job_resume_artifact"),
            is_resume_generated=doc.get("is_resume_generated", False),
            application_status=doc.get("application_status", "draft"),
            notes=doc.get("notes"),
            status_updated_at=doc.get("status_updated_at"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
