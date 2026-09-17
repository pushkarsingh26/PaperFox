from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.models.user import serialize_doc
from app.providers.pdf.latex_worker import LaTeXCompilerWorker
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.resume.renderer import render_latex_resume
from app.resume.transformer import transform_profile_to_resume_data
from app.storage.pdf_storage import PDFStorageService


class ResumeService:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        profile_repo: ProfileRepository,
        compiler_worker: Optional[LaTeXCompilerWorker] = None,
        pdf_storage: Optional[PDFStorageService] = None,
    ):
        self.resume_repo = resume_repo
        self.profile_repo = profile_repo
        self.compiler_worker = compiler_worker or LaTeXCompilerWorker()
        self.pdf_storage = pdf_storage or PDFStorageService()

    async def generate_base_resume(self, user_id: str, user_email: str) -> Dict[str, Any]:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate profile not found. Please complete your profile first.",
            )

        personal = profile.get("personal_details", {})
        if not personal or not personal.get("full_name", "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate profile is missing required personal details (Full Name).",
            )

        # Transform profile to ResumeData (Immutable profile guarantee)
        resume_data = transform_profile_to_resume_data(profile, user_email)

        # Render LaTeX source string
        try:
            latex_source = render_latex_resume(resume_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to render LaTeX template: {str(e)}",
            )

        # Compile via real system LaTeX compiler worker
        pdf_bytes, page_count, compiler_status = await self.compiler_worker.compile_with_status(
            latex_source
        )

        if compiler_status.startswith("COMPILER_UNAVAILABLE"):
            artifact_dict = {
                "latex_source": latex_source,
                "pdf_storage_reference": None,
                "page_count": 0,
                "status": "compiler_unavailable",
                "error_message": compiler_status,
            }
            saved_doc = await self.resume_repo.upsert_base_artifact(user_id, artifact_dict)
            return {
                "status": "compiler_unavailable",
                "message": (
                    "LaTeX compiler (pdflatex or xelatex) is not installed on the server environment. "
                    "The valid LaTeX source was generated and saved, but binary compilation requires local TeX Live/MiKTeX."
                ),
                "page_count": 0,
                "pdf_storage_reference": None,
                "artifact": serialize_doc(saved_doc),
            }

        if not pdf_bytes:
            artifact_dict = {
                "latex_source": latex_source,
                "pdf_storage_reference": None,
                "page_count": 0,
                "status": "error",
                "error_message": compiler_status,
            }
            saved_doc = await self.resume_repo.upsert_base_artifact(user_id, artifact_dict)
            return {
                "status": "error",
                "message": f"LaTeX compilation failed: {compiler_status}",
                "page_count": 0,
                "pdf_storage_reference": None,
                "artifact": serialize_doc(saved_doc),
            }

        # Save PDF binary securely using storage abstraction
        storage_ref = self.pdf_storage.save_pdf(user_id, "base", pdf_bytes)
        artifact_status = "success" if page_count == 1 else "overflow"

        artifact_dict = {
            "latex_source": latex_source,
            "pdf_storage_reference": storage_ref,
            "page_count": page_count,
            "status": artifact_status,
            "error_message": None if page_count == 1 else "Resume exceeds 1 page length target.",
        }

        saved_doc = await self.resume_repo.upsert_base_artifact(user_id, artifact_dict)

        msg = (
            "Base resume successfully compiled (1-page pass)."
            if page_count == 1
            else f"Base resume compiled with {page_count} pages (overflow state)."
        )

        return {
            "status": artifact_status,
            "message": msg,
            "page_count": page_count,
            "pdf_storage_reference": storage_ref,
            "artifact": serialize_doc(saved_doc),
        }

    async def get_base_artifact(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.resume_repo.get_base_artifact(user_id)
        return serialize_doc(doc)

    async def get_base_pdf_bytes(self, user_id: str) -> Optional[bytes]:
        artifact = await self.get_base_artifact(user_id)
        if not artifact:
            return None

        # Try reading from local filesystem first (fast path for warm containers).
        storage_ref = artifact.get("pdf_storage_reference")
        if storage_ref:
            cached = self.pdf_storage.get_pdf(storage_ref)
            if cached:
                return cached

        # Filesystem miss (ephemeral Cloud Run container or first request after restart).
        # Recompile from the LaTeX source that is durably stored in MongoDB.
        latex_source = artifact.get("latex_source")
        if not latex_source:
            return None

        pdf_bytes, _, status_msg = await self.compiler_worker.compile_with_status(latex_source)
        if not pdf_bytes:
            return None

        # Optionally persist back to the container's local cache for subsequent warm requests.
        if storage_ref:
            try:
                self.pdf_storage.save_pdf(user_id, "base", pdf_bytes)
            except Exception:
                pass  # Non-critical — the bytes are still returned

        return pdf_bytes

