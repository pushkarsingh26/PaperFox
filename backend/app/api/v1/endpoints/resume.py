from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.api.deps import get_current_user, get_resume_service
from app.schemas.resume import ResumeArtifactResponse, ResumeGenerateResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resume", tags=["LaTeX Resume Engine"])


@router.post("/generate", response_model=ResumeGenerateResponse)
async def generate_base_resume(
    current_user: dict = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
):
    """Generate or regenerate the base LaTeX resume for the authenticated user."""
    user_id = current_user["id"]
    user_email = current_user["email"]
    return await resume_service.generate_base_resume(user_id, user_email)


@router.get("/base", response_model=ResumeArtifactResponse)
async def get_base_resume_metadata(
    current_user: dict = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
):
    """Fetch base resume artifact metadata for the authenticated user."""
    user_id = current_user["id"]
    artifact = await resume_service.get_base_artifact(user_id)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base resume artifact not found. Please generate a base resume first.",
        )
    return artifact


@router.get("/base/pdf")
async def get_base_resume_pdf(
    current_user: dict = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
):
    """Serve the compiled base resume PDF binary for the authenticated user."""
    user_id = current_user["id"]
    pdf_bytes = await resume_service.get_base_pdf_bytes(user_id)
    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base resume PDF file not found or not compiled.",
        )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="base_resume.pdf"'},
    )
