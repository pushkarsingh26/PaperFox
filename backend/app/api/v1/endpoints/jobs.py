from typing import List
from fastapi import APIRouter, Depends, Response, status
from app.api.deps import get_current_user, get_job_service, get_job_resume_service
from app.schemas.auth import MessageResponse
from app.schemas.job import (
    JobApplicationCreate,
    JobApplicationListResponse,
    JobApplicationResponse,
)
from app.services.job_service import JobService
from app.services.job_resume_service import JobResumeService
from app.schemas.optimization_schema import OptimizationResponse

router = APIRouter(prefix="/jobs", tags=["Job Applications"])


@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_job_application(
    job_in: JobApplicationCreate,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Create a new Job Application record for the authenticated user."""
    user_id = current_user["id"]
    return await job_service.create_job(user_id, job_in)


@router.get("", response_model=JobApplicationListResponse)
async def list_job_applications(
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """List all Job Applications owned by the authenticated user."""
    user_id = current_user["id"]
    jobs = await job_service.list_jobs(user_id)
    return JobApplicationListResponse(items=jobs, total=len(jobs))


@router.get("/{job_id}", response_model=JobApplicationResponse)
async def get_job_application(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Retrieve details of a specific Job Application owned by the user."""
    user_id = current_user["id"]
    return await job_service.get_job(user_id, job_id)


@router.post("/{job_id}/analyze", response_model=JobApplicationResponse)
async def analyze_job_description(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """
    Analyze Job Description using PaperFox AI Provider Router (Gemini primary, Groq/OpenRouter fallbacks).
    Extracts structured requirements (required skills, preferred skills, languages, tech, AI/ML, keywords).
    """
    user_id = current_user["id"]
    return await job_service.analyze_job(user_id, job_id)


@router.post("/{job_id}/optimize", response_model=OptimizationResponse)
async def optimize_resume_for_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """
    Execute Phase 5 job-specific resume optimization pipeline.
    Transforms master candidate profile into an independent OptimizedResumeData snapshot.
    """
    user_id = current_user["id"]
    return await job_service.optimize_job(user_id, job_id)


@router.get("/{job_id}/optimization", response_model=OptimizationResponse)
async def get_job_optimization(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Retrieve the stored job-specific resume optimization snapshot for a job application."""
    user_id = current_user["id"]
    return await job_service.get_job_optimization(user_id, job_id)


# ──────────────────────────────────────────────────────────────────────────────
# Phase 6 — Resume Rendering endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/{job_id}/render")
async def render_job_resume(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_resume_service: JobResumeService = Depends(get_job_resume_service),
):
    """
    Phase 6: Generate the final job-specific resume PDF.

    Requires Phase 5 optimization to be completed first.
    Applies deterministic LaTeX rendering and iterative compression to enforce one-page output.
    Overwrites any previous artifact for this job application.

    If the LaTeX compiler is unavailable, the LaTeX source is saved and status is
    returned as 'compiler_unavailable' — no fake PDF is generated.
    """
    user_id = current_user["id"]
    user_email = current_user.get("email", "")
    return await job_resume_service.generate_job_resume(user_id, job_id, user_email)


@router.get("/{job_id}/resume")
async def get_job_resume_artifact(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_resume_service: JobResumeService = Depends(get_job_resume_service),
):
    """
    Phase 6: Retrieve the stored Phase 6 resume artifact metadata for a job application.
    Returns status, page count, compression level used, ATS validation results.
    Does not return the PDF binary; use /resume/download for the binary.
    """
    user_id = current_user["id"]
    return await job_resume_service.get_job_resume_artifact(user_id, job_id)


@router.get("/{job_id}/resume/download")
async def download_job_resume_pdf(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_resume_service: JobResumeService = Depends(get_job_resume_service),
):
    """
    Phase 6: Download the compiled job-specific resume PDF binary.

    Returns raw PDF as application/pdf.
    Raises 404 if the artifact has status 'compiler_unavailable' or 'error'.
    """
    user_id = current_user["id"]
    pdf_bytes = await job_resume_service.get_job_resume_pdf_bytes(user_id, job_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="resume_{job_id}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.delete("/{job_id}", response_model=MessageResponse)
async def delete_job_application(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Delete a specific Job Application owned by the user."""
    user_id = current_user["id"]
    await job_service.delete_job(user_id, job_id)
    return MessageResponse(message="Job application deleted successfully.")
