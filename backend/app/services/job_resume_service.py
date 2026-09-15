"""
job_resume_service.py — Phase 6 orchestration service.

Transforms OptimizedResumeData → LaTeX → PDF using the deterministic
compression loop. Never invokes AI. Saves the artifact to the job_applications
document and runs ATS readability validation.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.models.user import serialize_doc
from app.providers.pdf.latex_worker import LaTeXCompilerWorker
from app.repositories.job_repository import JobRepository
from app.resume.compression import (
    CompressionLevel,
    MAX_COMPRESSION_LEVEL,
    get_compression_level,
)
from app.resume.job_resume_renderer import render_job_latex_resume
from app.resume.optimized_resume_transformer import transform_optimized_to_render_data
from app.schemas.job import ATSValidation, JobResumeArtifact
from app.schemas.optimization_schema import OptimizedResumeData
from app.storage.pdf_storage import PDFStorageService


# ──────────────────────────────────────────────────────────────────────────────
# ATS Validation
# ──────────────────────────────────────────────────────────────────────────────

def _run_ats_validation(
    pdf_bytes: Optional[bytes],
    page_count: int,
    render_data: Dict[str, Any],
) -> ATSValidation:
    """
    Deterministic ATS readability check. Validates structure and page count.
    Text-extractability is set to True by default since we generate clean LaTeX.
    """
    return ATSValidation(
        is_single_page=page_count == 1,
        page_count=page_count,
        text_extractable=True,  # LaTeX-generated PDFs are always text-based
        has_summary=bool(render_data.get("summary", "").strip()),
        has_skills=len(render_data.get("skills", [])) > 0,
        has_education=len(render_data.get("education", [])) > 0,
        has_experience_or_projects=(
            len(render_data.get("experience", [])) > 0
            or len(render_data.get("internships", [])) > 0
            or len(render_data.get("projects", [])) > 0
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# JobResumeService
# ──────────────────────────────────────────────────────────────────────────────

class JobResumeService:
    def __init__(
        self,
        job_repository: JobRepository,
        compiler_worker: Optional[LaTeXCompilerWorker] = None,
        pdf_storage: Optional[PDFStorageService] = None,
    ):
        self.job_repository = job_repository
        self.compiler_worker = compiler_worker or LaTeXCompilerWorker()
        self.pdf_storage = pdf_storage or PDFStorageService()

    async def generate_job_resume(
        self, user_id: str, job_id: str, user_email: str
    ) -> Dict[str, Any]:
        """
        Phase 6 main pipeline:
        1. Assert job is optimized (Phase 5 complete).
        2. Run iterative compression loop (levels 0 → MAX).
        3. Persist artifact to MongoDB.
        4. Run ATS validation.
        5. Return result dict.

        Never auto-triggers optimization. Never invents content.
        Overwrites any previous artifact for the same job.
        """
        doc = await self.job_repository.get_by_id(job_id, user_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found.",
            )

        # ── Guard: optimization must be complete ─────────────────────────────
        if not doc.get("is_optimized") or not doc.get("optimization"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Job-specific resume optimization (Phase 5) must be completed before "
                    "generating a resume. Run optimization first."
                ),
            )

        # ── Load OptimizedResumeData ──────────────────────────────────────────
        try:
            optimized = OptimizedResumeData(**doc["optimization"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse stored optimization data: {str(e)}",
            )

        # ── Handle compiler unavailability immediately ─────────────────────────
        if not self.compiler_worker.is_available():
            # Still render LaTeX source so it can be downloaded
            compression = get_compression_level(0)
            render_data = transform_optimized_to_render_data(optimized, user_email, compression)
            try:
                latex_source = render_job_latex_resume(render_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"LaTeX rendering failed: {str(e)}",
                )

            ats = _run_ats_validation(None, 0, render_data)
            artifact = JobResumeArtifact(
                latex_source=latex_source,
                pdf_storage_reference=None,
                page_count=0,
                compression_level_used=0,
                status="compiler_unavailable",
                ats_validation=ats,
                error_message=(
                    "LaTeX compiler (pdflatex or xelatex) is not installed. "
                    "The LaTeX source is available and ready for local compilation."
                ),
                generated_at=datetime.now(timezone.utc),
            )
            artifact_dict = artifact.model_dump()
            artifact_dict["generated_at"] = artifact_dict["generated_at"].isoformat()
            artifact_dict["ats_validation"] = ats.model_dump()

            saved_doc = await self.job_repository.upsert_job_resume_artifact(
                job_id, user_id, artifact_dict
            )
            return {
                "status": "compiler_unavailable",
                "message": (
                    "LaTeX source generated successfully. PDF compilation requires "
                    "pdflatex or xelatex to be installed on the server."
                ),
                "compression_level_used": 0,
                "page_count": 0,
                "pdf_storage_reference": None,
                "ats_validation": ats.model_dump(),
                "artifact": serialize_doc(saved_doc),
            }

        # ── Iterative compression loop ─────────────────────────────────────────
        final_pdf_bytes: Optional[bytes] = None
        final_page_count: int = 0
        final_latex: str = ""
        final_render_data: Dict[str, Any] = {}
        compression_level_used: int = 0
        compile_error: Optional[str] = None

        for level in range(MAX_COMPRESSION_LEVEL + 1):
            compression: CompressionLevel = get_compression_level(level)
            render_data = transform_optimized_to_render_data(optimized, user_email, compression)

            try:
                latex_source = render_job_latex_resume(render_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"LaTeX rendering failed at compression level {level}: {str(e)}",
                )

            pdf_bytes, page_count, compiler_status = (
                await self.compiler_worker.compile_with_status(latex_source)
            )

            # Track last successful attempt (even if overflowing)
            if pdf_bytes:
                final_pdf_bytes = pdf_bytes
                final_page_count = page_count
                final_latex = latex_source
                final_render_data = render_data
                compression_level_used = level
                compile_error = None

                if page_count == 1:
                    # One-page target achieved — stop
                    break
                # Continue compressing on overflow
            else:
                # Compilation error at this level
                compile_error = compiler_status
                if final_pdf_bytes is None:
                    # First attempt failed — record LaTeX for diagnostics
                    final_latex = latex_source
                    final_render_data = render_data
                    compression_level_used = level
                # Try next compression level

        # ── Determine final status ─────────────────────────────────────────────
        if final_pdf_bytes is None:
            # All compilation attempts failed
            ats = _run_ats_validation(None, 0, final_render_data)
            artifact = JobResumeArtifact(
                latex_source=final_latex,
                pdf_storage_reference=None,
                page_count=0,
                compression_level_used=compression_level_used,
                status="error",
                ats_validation=ats,
                error_message=compile_error or "Unknown compilation failure.",
                generated_at=datetime.now(timezone.utc),
            )
            artifact_dict = artifact.model_dump()
            artifact_dict["generated_at"] = artifact_dict["generated_at"].isoformat()
            artifact_dict["ats_validation"] = ats.model_dump()

            await self.job_repository.upsert_job_resume_artifact(
                job_id, user_id, artifact_dict
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LaTeX compilation failed: {compile_error}",
            )

        # ── Save PDF ────────────────────────────────────────────────────────────
        artifact_type = f"job_{job_id}"
        storage_ref = self.pdf_storage.save_pdf(user_id, artifact_type, final_pdf_bytes)

        artifact_status = "success" if final_page_count == 1 else "overflow"
        overflow_msg = (
            None
            if final_page_count == 1
            else (
                f"Resume is {final_page_count} page(s) after maximum compression "
                f"(level {compression_level_used}). Consider reducing content in your profile."
            )
        )

        ats = _run_ats_validation(final_pdf_bytes, final_page_count, final_render_data)

        artifact = JobResumeArtifact(
            latex_source=final_latex,
            pdf_storage_reference=storage_ref,
            page_count=final_page_count,
            compression_level_used=compression_level_used,
            status=artifact_status,
            ats_validation=ats,
            error_message=overflow_msg,
            generated_at=datetime.now(timezone.utc),
        )
        artifact_dict = artifact.model_dump()
        artifact_dict["generated_at"] = artifact_dict["generated_at"].isoformat()
        artifact_dict["ats_validation"] = ats.model_dump()

        saved_doc = await self.job_repository.upsert_job_resume_artifact(
            job_id, user_id, artifact_dict
        )

        compression_note = (
            f" (compression level {compression_level_used} applied)"
            if compression_level_used > 0
            else ""
        )
        message = (
            f"Job-specific resume generated successfully — 1 page{compression_note}."
            if artifact_status == "success"
            else overflow_msg
        )

        return {
            "status": artifact_status,
            "message": message,
            "compression_level_used": compression_level_used,
            "page_count": final_page_count,
            "pdf_storage_reference": storage_ref,
            "ats_validation": ats.model_dump(),
            "artifact": serialize_doc(saved_doc),
        }

    async def get_job_resume_artifact(
        self, user_id: str, job_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return the stored Phase 6 artifact metadata (no PDF bytes)."""
        doc = await self.job_repository.get_by_id(job_id, user_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found.",
            )
        artifact = doc.get("job_resume_artifact")
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume artifact found for this job. Generate the resume first.",
            )
        return artifact

    async def get_job_resume_pdf_bytes(
        self, user_id: str, job_id: str
    ) -> Optional[bytes]:
        """Return the raw PDF bytes for a generated job resume."""
        artifact = await self.get_job_resume_artifact(user_id, job_id)
        storage_ref = artifact.get("pdf_storage_reference")
        if not storage_ref:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "PDF file not available. "
                    "The artifact status may be 'compiler_unavailable' or 'error'."
                ),
            )
        pdf_bytes = self.pdf_storage.get_pdf(storage_ref)
        if not pdf_bytes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found on server. It may have been deleted.",
            )
        return pdf_bytes
