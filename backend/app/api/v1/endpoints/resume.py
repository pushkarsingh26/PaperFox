from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.api.deps import get_current_user, get_resume_service
from app.providers.pdf.latex_worker import LaTeXCompilerWorker
from app.schemas.resume import ResumeArtifactResponse, ResumeGenerateResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resume", tags=["LaTeX Resume Engine"])


@router.get("/compiler-status")
async def get_compiler_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Return the current LaTeX compiler availability status for the authenticated user.
    Used by the frontend to display actionable setup instructions.
    """
    from app.core.config import settings
    worker = LaTeXCompilerWorker()
    available = worker.is_available()
    compiler_name = getattr(settings, "LATEX_COMPILER", "pdflatex")
    compiler_path_setting = getattr(settings, "LATEX_COMPILER_PATH", "").strip()
    return {
        "compiler_available": available,
        "compiler_binary": worker.compiler if available else None,
        "configured_name": compiler_name,
        "configured_path": compiler_path_setting or None,
        "description": worker.compiler_description(),
        "install_guide": (
            None
            if available
            else {
                "windows": (
                    "Install MiKTeX from https://miktex.org/download "
                    "then restart the backend server. "
                    "If pdflatex.exe is installed but not on PATH, set "
                    "LATEX_COMPILER_PATH=C:\\path\\to\\miktex\\bin\\x64\\pdflatex.exe "
                    "in backend/.env and restart."
                ),
                "linux": (
                    "Run: sudo apt-get install texlive-latex-base texlive-fonts-recommended "
                    "then restart the backend server."
                ),
                "docker": (
                    "Add to Dockerfile: "
                    "RUN apt-get install -y texlive-latex-base texlive-fonts-recommended"
                ),
            }
        ),
    }


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

