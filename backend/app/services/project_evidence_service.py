"""
project_evidence_service.py — Phase 7 Evidence Extraction Orchestrator.

Responsibilities:
- Accept user_id + project_id
- Load project from profile
- Validate ai_analysis_text is present
- Skip re-extraction if evidence is already current (no wasted AI calls)
- Call ProjectEvidenceParser (free-model AI router)
- Validate the structured evidence returned
- Store evidence persistently in the project subdocument
- Preserve raw ai_analysis_text untouched
- Return structured evidence with provenance metadata

Invariants:
- NEVER mutates ai_analysis_text
- NEVER mutates master profile fields (name, description, technologies, etc.)
- NEVER invents facts not present in the ai_analysis_text
- Only updates evidence, evidence_status, evidence_updated_at, evidence_version
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.repositories.profile_repository import ProfileRepository
from app.schemas.optimization_schema import StructuredProjectEvidence
from app.services.ai.project_evidence_parser import ProjectEvidenceParser
from app.services.ai.provider_router import ProviderRouter

logger = logging.getLogger(__name__)

# Evidence statuses
EVIDENCE_STATUS_CURRENT = "current"
EVIDENCE_STATUS_STALE = "stale"
EVIDENCE_STATUS_UNVERIFIED = "unverified"


class ProjectEvidenceService:
    """
    Orchestrates the extraction and persistent storage of structured project evidence.

    Designed to be injected via FastAPI dependency system.
    """

    def __init__(
        self,
        profile_repository: ProfileRepository,
        router: Optional[ProviderRouter] = None,
    ):
        self.profile_repository = profile_repository
        self.router = router or ProviderRouter()

    def _find_project(
        self, profile_doc: Dict[str, Any], project_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find a project by ID within a profile document."""
        for proj in profile_doc.get("projects", []):
            if proj.get("id") == project_id:
                return proj
        return None

    def _evidence_to_dict(self, ev: StructuredProjectEvidence) -> Dict[str, Any]:
        """Convert StructuredProjectEvidence → dict suitable for MongoDB storage."""
        return {
            "status": EVIDENCE_STATUS_CURRENT,
            "source": "ai_analysis",
            "architecture": ev.architecture,
            "technologies": ev.technologies,
            "frameworks": ev.frameworks,
            "apis": ev.apis,
            "models": ev.models,
            "databases": ev.databases,
            "deployment": ev.deployment,
            "features": ev.features,
            "technical_details": ev.technical_details,
            "engineering_decisions": ev.engineering_decisions,
            "limitations": ev.limitations,
            "verified_at": ev.verified_at or datetime.now(timezone.utc).isoformat(),
        }

    async def extract_and_store(
        self,
        user_id: str,
        project_id: str,
        force_reextract: bool = False,
    ) -> Dict[str, Any]:
        """
        Main extraction pipeline.

        Args:
            user_id: Authenticated user (owner).
            project_id: Target project ID within the user's profile.
            force_reextract: If True, re-extracts even when evidence is current.

        Returns:
            Dict with keys: evidence, evidence_status, project_name, was_cached, extracted_at
        """
        # 1. Load profile
        profile_doc = await self.profile_repository.get_by_user_id(user_id)
        if not profile_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found. Complete your master profile first.",
            )

        # 2. Find project
        project = self._find_project(profile_doc, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_id}' not found in your profile.",
            )

        project_name = project.get("name", "Project")

        # 3. Validate ai_analysis_text
        ai_text = project.get("ai_analysis_text")
        if not ai_text or not ai_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Project '{project_name}' has no AI analysis text. "
                    "Set description_source to 'ai', generate the universal prompt, "
                    "run your coding AI, and paste the result before extracting evidence."
                ),
            )

        # 4. Check if evidence is already current — skip if not forced
        current_evidence_status = project.get("evidence_status")
        if current_evidence_status == EVIDENCE_STATUS_CURRENT and not force_reextract:
            existing_evidence = project.get("evidence", {})
            logger.info(
                f"Evidence for project '{project_name}' is already current — returning cached."
            )
            return {
                "evidence": existing_evidence,
                "evidence_status": EVIDENCE_STATUS_CURRENT,
                "project_name": project_name,
                "was_cached": True,
                "extracted_at": project.get("evidence_updated_at"),
                "evidence_version": project.get("evidence_version", 0),
            }

        # 5. Extract structured evidence via AI
        parser = ProjectEvidenceParser(self.router)
        try:
            structured_ev: StructuredProjectEvidence = await parser.parse_analysis_text(
                project_name=project_name,
                ai_analysis_text=ai_text,
            )
        except Exception as e:
            logger.error(f"Evidence extraction failed for '{project_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Evidence extraction AI call failed: {str(e)}",
            )

        # 6. Convert to dict for storage
        evidence_dict = self._evidence_to_dict(structured_ev)

        # 7. Increment version counter
        new_version = (project.get("evidence_version") or 0) + 1

        # 8. Persist evidence on project subdocument (never touches ai_analysis_text)
        updated_profile = await self.profile_repository.update_project_evidence(
            user_id=user_id,
            project_id=project_id,
            evidence_dict=evidence_dict,
            evidence_status=EVIDENCE_STATUS_CURRENT,
            evidence_version=new_version,
        )
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist evidence to profile. The project may have been deleted.",
            )

        extracted_at = datetime.now(timezone.utc).isoformat()
        return {
            "evidence": evidence_dict,
            "evidence_status": EVIDENCE_STATUS_CURRENT,
            "project_name": project_name,
            "was_cached": False,
            "extracted_at": extracted_at,
            "evidence_version": new_version,
        }

    async def get_stored_evidence(
        self, user_id: str, project_id: str
    ) -> Dict[str, Any]:
        """Return the stored evidence for a project (no AI call)."""
        profile_doc = await self.profile_repository.get_by_user_id(user_id)
        if not profile_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found.",
            )

        project = self._find_project(profile_doc, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_id}' not found.",
            )

        evidence = project.get("evidence")
        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"No evidence extracted for project '{project.get('name', project_id)}' yet. "
                    "Run evidence extraction first."
                ),
            )

        return {
            "evidence": evidence,
            "evidence_status": project.get("evidence_status", EVIDENCE_STATUS_UNVERIFIED),
            "evidence_version": project.get("evidence_version", 0),
            "extracted_at": project.get("evidence_updated_at"),
            "project_name": project.get("name", project_id),
            "ai_analysis_text_length": len(project.get("ai_analysis_text") or ""),
        }
