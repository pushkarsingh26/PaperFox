from typing import List
from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user, get_job_service
from app.schemas.auth import MessageResponse
from app.schemas.job import (
    JobApplicationCreate,
    JobApplicationListResponse,
    JobApplicationResponse
)
from app.services.job_service import JobService

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
