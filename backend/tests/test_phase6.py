"""
test_phase6.py — Unit tests for Phase 6 resume rendering, compression, and ATS validation.

Tests cover:
- Compression level config correctness
- Transformer bullet/project limiting
- Renderer LaTeX output validity
- ATS validation logic
- JobResumeService guard (optimization required)
- Compiler unavailable path
- Overwrite idempotency (via mock)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.resume.compression import (
    get_compression_level,
    MAX_COMPRESSION_LEVEL,
    CompressionLevel,
)
from app.resume.optimized_resume_transformer import (
    transform_optimized_to_render_data,
    _apply_bullet_limit,
    _truncate_summary,
)
from app.resume.job_resume_renderer import (
    render_job_latex_resume,
    render_summary,
    render_education,
    render_skills,
    render_certifications,
)
from app.schemas.optimization_schema import (
    OptimizedResumeData,
    OptimizedProject,
    OptimizedExperience,
    OptimizedSkillGroup,
    KeywordAlignment,
    OptimizationMetadata,
)
from app.schemas.job import ATSValidation
from app.services.job_resume_service import _run_ats_validation


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

def _make_optimized(**kwargs) -> OptimizedResumeData:
    defaults = dict(
        job_id="job-001",
        personal_details={"full_name": "Test User", "phone": "555-1234", "linkedin_url": "https://linkedin.com/in/test"},
        summary="Experienced engineer building scalable distributed systems.",
        education=[{"institution": "State University", "degree": "B.S.", "field_of_study": "Computer Science", "start_date": "2018", "end_date": "2022"}],
        experience=[
            OptimizedExperience(
                company="TechCorp",
                role="Software Engineer",
                start_date="2022-01",
                is_current=True,
                bullets=["Led API redesign", "Improved throughput by 40%", "Managed 3 engineers", "Deployed to GKE"],
                technologies=["Python", "FastAPI", "GKE"],
            )
        ],
        internships=[],
        projects=[
            OptimizedProject(
                project_name="Smart Search",
                relevance_score=0.90,
                technologies=["Python", "Elasticsearch"],
                bullets=["Indexed 10M documents", "Sub-100ms P99 latency", "Deployed on AWS ECS", "Integrated ML reranking"],
            ),
            OptimizedProject(
                project_name="Auth Service",
                relevance_score=0.75,
                technologies=["Go", "JWT"],
                bullets=["Zero-downtime token rotation", "Rate limiting", "Audit logging"],
            ),
            OptimizedProject(
                project_name="CI Pipeline",
                relevance_score=0.55,
                technologies=["GitHub Actions", "Docker"],
                bullets=["Automated testing", "Multi-environment deploy"],
            ),
        ],
        skills=[
            OptimizedSkillGroup(category="Languages", skills=["Python", "Go", "TypeScript"]),
            OptimizedSkillGroup(category="Databases", skills=["PostgreSQL", "Redis"]),
        ],
        certifications=[{"name": "AWS SAA", "issuer": "Amazon", "issue_date": "2023-01"}],
        keyword_alignment=KeywordAlignment(
            matched_keywords=["Python", "FastAPI"],
            missing_keywords=["Rust"],
        ),
        optimization_metadata=OptimizationMetadata(status="completed", provider="gemini", model="gemini-2.5-flash"),
    )
    defaults.update(kwargs)
    return OptimizedResumeData(**defaults)


# ──────────────────────────────────────────────────────────────────────────────
# Compression level tests
# ──────────────────────────────────────────────────────────────────────────────

def test_compression_level_count():
    """All levels 0..MAX_COMPRESSION_LEVEL must be accessible."""
    for i in range(MAX_COMPRESSION_LEVEL + 1):
        lvl = get_compression_level(i)
        assert lvl.level == i


def test_compression_level_clamps():
    """Out-of-range levels clamp to MAX_COMPRESSION_LEVEL."""
    lvl = get_compression_level(999)
    assert lvl.level == MAX_COMPRESSION_LEVEL


def test_compression_level_0_no_limits():
    """Level 0 must apply zero restrictions."""
    lvl = get_compression_level(0)
    assert lvl.max_project_bullets == 0
    assert lvl.max_exp_bullets == 0
    assert lvl.max_projects == 0
    assert lvl.include_certifications is True
    assert lvl.summary_max_chars == 0


def test_compression_level_5_max():
    """Level 5 must apply maximum restrictions."""
    lvl = get_compression_level(5)
    assert lvl.max_projects == 2
    assert lvl.max_project_bullets == 2
    assert lvl.include_certifications is False
    assert lvl.summary_max_chars > 0


def test_compression_progressively_tighter():
    """Margins must become progressively tighter from level 0 → 5."""
    margins = [get_compression_level(i).margin_top for i in range(MAX_COMPRESSION_LEVEL + 1)]
    for i in range(1, len(margins)):
        assert margins[i] <= margins[i - 1], f"Level {i} margin not <= level {i-1}"


# ──────────────────────────────────────────────────────────────────────────────
# Transformer tests
# ──────────────────────────────────────────────────────────────────────────────

def test_apply_bullet_limit_unlimited():
    """max_bullets=0 means no limit."""
    bullets = ["a", "b", "c", "d", "e"]
    assert _apply_bullet_limit(bullets, 0) == bullets


def test_apply_bullet_limit_capped():
    bullets = ["a", "b", "c", "d", "e"]
    assert _apply_bullet_limit(bullets, 3) == ["a", "b", "c"]


def test_truncate_summary_no_limit():
    long = "x " * 300
    assert _truncate_summary(long, 0) == long


def test_truncate_summary_preserves_word_boundary():
    text = "This is a long sentence for testing purposes and we want word boundaries."
    result = _truncate_summary(text, 30)
    assert len(result) <= 30 + 5  # Allow for trailing punctuation
    assert " " not in result[-1:] or result.endswith(".")


def test_transformer_projects_sorted_by_relevance():
    """Projects must be sorted by relevance_score descending."""
    optimized = _make_optimized()
    comp = get_compression_level(0)
    rd = transform_optimized_to_render_data(optimized, "test@example.com", comp)
    scores = [p.get("relevance_score", 0) for p in rd["projects"]]
    # relevance is not directly in render dict, but projects are sorted
    names = [p["name"] for p in rd["projects"]]
    assert names[0] == "Smart Search"  # Highest relevance (0.90)
    assert names[-1] == "CI Pipeline"  # Lowest relevance (0.55)


def test_transformer_level4_limits_projects():
    """Level 4 must limit to top 3 projects."""
    optimized = _make_optimized()
    comp = get_compression_level(4)
    rd = transform_optimized_to_render_data(optimized, "test@example.com", comp)
    assert len(rd["projects"]) == 3


def test_transformer_level5_limits_projects_and_drops_certs():
    """Level 5 must limit to top 2 projects and exclude certifications."""
    optimized = _make_optimized()
    comp = get_compression_level(5)
    rd = transform_optimized_to_render_data(optimized, "test@example.com", comp)
    assert len(rd["projects"]) == 2
    assert len(rd["certifications"]) == 0


def test_transformer_level2_caps_project_bullets():
    """Level 2 must cap project bullets at 3."""
    optimized = _make_optimized()
    comp = get_compression_level(2)
    rd = transform_optimized_to_render_data(optimized, "test@example.com", comp)
    for proj in rd["projects"]:
        assert len(proj["features"]) <= 3


def test_transformer_never_mutates_input():
    """Transform must not mutate the original OptimizedResumeData."""
    optimized = _make_optimized()
    original_projects = len(optimized.projects)
    original_bullets = list(optimized.projects[0].bullets)
    comp = get_compression_level(5)
    transform_optimized_to_render_data(optimized, "test@example.com", comp)
    assert len(optimized.projects) == original_projects, "Projects list was mutated"
    assert optimized.projects[0].bullets == original_bullets, "Bullets list was mutated"


def test_transformer_education_always_included():
    """Education must never be compressed away regardless of level."""
    optimized = _make_optimized()
    for level in range(MAX_COMPRESSION_LEVEL + 1):
        comp = get_compression_level(level)
        rd = transform_optimized_to_render_data(optimized, "t@t.com", comp)
        assert len(rd["education"]) == 1, f"Education removed at level {level}"


# ──────────────────────────────────────────────────────────────────────────────
# Renderer tests
# ──────────────────────────────────────────────────────────────────────────────

def test_renderer_produces_valid_latex():
    """render_job_latex_resume must produce a complete LaTeX document."""
    optimized = _make_optimized()
    comp = get_compression_level(0)
    rd = transform_optimized_to_render_data(optimized, "user@example.com", comp)
    latex = render_job_latex_resume(rd)
    assert "\\documentclass" in latex
    assert "\\begin{document}" in latex
    assert "\\end{document}" in latex
    assert "inputenc" in latex  # Must use fixed encoding package
    assert "utf8" in latex


def test_renderer_contains_candidate_name():
    optimized = _make_optimized()
    comp = get_compression_level(0)
    rd = transform_optimized_to_render_data(optimized, "user@example.com", comp)
    latex = render_job_latex_resume(rd)
    assert "Test User" in latex


def test_renderer_summary_section():
    latex = render_summary("Expert Python developer with 10 years of experience.")
    assert "\\section{Professional Summary}" in latex
    assert "Expert Python" in latex


def test_renderer_empty_summary_returns_empty():
    assert render_summary("") == ""
    assert render_summary("   ") == ""


def test_renderer_education_section():
    edu = [{"institution": "MIT", "degree": "B.S.", "field_of_study": "CS", "start_date": "2018", "end_date": "2022"}]
    latex = render_education(edu)
    assert "\\section{Education}" in latex
    assert "MIT" in latex
    assert "2018" in latex


def test_renderer_skills_grouped():
    skills = [
        {"category": "Languages", "name": "Python"},
        {"category": "Languages", "name": "Go"},
        {"category": "Databases", "name": "PostgreSQL"},
    ]
    latex = render_skills(skills)
    assert "\\section{Technical Skills}" in latex
    assert "Languages" in latex
    assert "Python" in latex


def test_renderer_no_certifications_when_empty():
    assert render_certifications([]) == ""


def test_renderer_latex_escaping():
    """Special LaTeX characters must be escaped in user content."""
    optimized = _make_optimized(
        summary="Increased revenue by 50% using C++ & Rust (not $AMZN).",
        personal_details={"full_name": "A & B User"},
    )
    comp = get_compression_level(0)
    rd = transform_optimized_to_render_data(optimized, "test@x.com", comp)
    latex = render_job_latex_resume(rd)
    assert "50\\%" in latex or "\\%" in latex
    assert "\\&" in latex


def test_renderer_margin_injection():
    """Margin values from compression config must appear in LaTeX output."""
    optimized = _make_optimized()
    comp = get_compression_level(5)
    rd = transform_optimized_to_render_data(optimized, "test@x.com", comp)
    latex = render_job_latex_resume(rd)
    # Level 5 margin is 0.30in
    assert "0.30" in latex


# ──────────────────────────────────────────────────────────────────────────────
# ATS Validation tests
# ──────────────────────────────────────────────────────────────────────────────

def test_ats_validation_single_page():
    render_data = {"summary": "Hello", "skills": [{"name": "Python"}], "education": [{}], "experience": [], "internships": [], "projects": [{}]}
    ats = _run_ats_validation(b"fake-pdf-bytes", 1, render_data)
    assert ats.is_single_page is True
    assert ats.page_count == 1


def test_ats_validation_overflow():
    render_data = {"summary": "Hello", "skills": [], "education": [], "experience": [], "internships": [], "projects": []}
    ats = _run_ats_validation(b"x", 3, render_data)
    assert ats.is_single_page is False
    assert ats.page_count == 3


def test_ats_validation_no_pdf():
    render_data = {"summary": "", "skills": [], "education": [{}], "experience": [], "internships": [], "projects": []}
    ats = _run_ats_validation(None, 0, render_data)
    assert ats.is_single_page is False
    assert ats.text_extractable is True
    assert ats.has_education is True
    assert ats.has_summary is False


def test_ats_validation_all_sections():
    render_data = {
        "summary": "Summary text",
        "skills": [{"name": "Python"}],
        "education": [{"institution": "X"}],
        "experience": [{"company": "Y"}],
        "internships": [],
        "projects": [],
    }
    ats = _run_ats_validation(b"x", 1, render_data)
    assert ats.has_summary is True
    assert ats.has_skills is True
    assert ats.has_education is True
    assert ats.has_experience_or_projects is True


# ──────────────────────────────────────────────────────────────────────────────
# JobResumeService guard tests
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_service_requires_optimization():
    """Service must reject generate_job_resume when is_optimized is False."""
    from fastapi import HTTPException
    from app.services.job_resume_service import JobResumeService

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value={
        "_id": "job-001",
        "user_id": "user-001",
        "is_optimized": False,
        "optimization": None,
    })

    service = JobResumeService(job_repository=mock_repo)
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_job_resume("user-001", "job-001", "user@example.com")
    assert exc_info.value.status_code == 400
    assert "optimization" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_service_404_on_missing_job():
    """Service must return 404 when job application is not found."""
    from fastapi import HTTPException
    from app.services.job_resume_service import JobResumeService

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=None)

    service = JobResumeService(job_repository=mock_repo)
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_job_resume("user-001", "missing-job", "user@example.com")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_service_compiler_unavailable():
    """Service must save LaTeX source and return compiler_unavailable status when no compiler."""
    from app.services.job_resume_service import JobResumeService
    from app.schemas.optimization_schema import (
        OptimizedResumeData, KeywordAlignment, OptimizationMetadata, OptimizedSkillGroup
    )

    optimized = _make_optimized()

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value={
        "_id": "job-001",
        "user_id": "user-001",
        "is_optimized": True,
        "optimization": optimized.model_dump(),
    })
    mock_repo.upsert_job_resume_artifact = AsyncMock(return_value={
        "_id": "job-001",
        "user_id": "user-001",
        "is_optimized": True,
        "optimization": optimized.model_dump(),
        "job_resume_artifact": {"status": "compiler_unavailable"},
    })

    # Compiler that reports unavailable
    mock_compiler = MagicMock()
    mock_compiler.is_available = MagicMock(return_value=False)

    service = JobResumeService(job_repository=mock_repo, compiler_worker=mock_compiler)
    result = await service.generate_job_resume("user-001", "job-001", "user@example.com")

    assert result["status"] == "compiler_unavailable"
    assert result["pdf_storage_reference"] is None
    assert result["page_count"] == 0
    # Must have called upsert (saving LaTeX source)
    mock_repo.upsert_job_resume_artifact.assert_called_once()
    artifact_saved = mock_repo.upsert_job_resume_artifact.call_args[0][2]
    assert artifact_saved["status"] == "compiler_unavailable"
    assert len(artifact_saved["latex_source"]) > 0


@pytest.mark.asyncio
async def test_service_success_no_compression():
    """Service must succeed and stop at level 0 when PDF fits in one page."""
    from app.services.job_resume_service import JobResumeService

    optimized = _make_optimized()

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value={
        "_id": "job-001",
        "user_id": "user-001",
        "is_optimized": True,
        "optimization": optimized.model_dump(),
    })
    mock_repo.upsert_job_resume_artifact = AsyncMock(return_value={
        "_id": "job-001",
        "job_resume_artifact": {"status": "success", "page_count": 1},
    })

    mock_compiler = MagicMock()
    mock_compiler.is_available = MagicMock(return_value=True)
    # Always returns 1-page PDF on first attempt
    mock_compiler.compile_with_status = AsyncMock(return_value=(b"%PDF-1.4 fake", 1, "success"))

    mock_storage = MagicMock()
    mock_storage.save_pdf = MagicMock(return_value="storage://user-001/job_job-001/job_resume.pdf")

    service = JobResumeService(
        job_repository=mock_repo,
        compiler_worker=mock_compiler,
        pdf_storage=mock_storage,
    )
    result = await service.generate_job_resume("user-001", "job-001", "user@example.com")

    assert result["status"] == "success"
    assert result["page_count"] == 1
    assert result["compression_level_used"] == 0
    assert result["pdf_storage_reference"] is not None
    # Compiler must have been called exactly once (stopped after first 1-page result)
    mock_compiler.compile_with_status.assert_called_once()


@pytest.mark.asyncio
async def test_service_compression_reduces_calls():
    """Service must iterate through compression levels on overflow until 1-page."""
    from app.services.job_resume_service import JobResumeService

    optimized = _make_optimized()

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value={
        "_id": "job-001",
        "user_id": "user-001",
        "is_optimized": True,
        "optimization": optimized.model_dump(),
    })
    mock_repo.upsert_job_resume_artifact = AsyncMock(return_value={
        "_id": "job-001",
        "job_resume_artifact": {"status": "success"},
    })

    call_count = 0
    async def fake_compile(latex):
        nonlocal call_count
        call_count += 1
        # Returns 2 pages for first 2 calls, then 1 page on 3rd
        if call_count < 3:
            return (b"%PDF-1.4", 2, "success")
        return (b"%PDF-1.4", 1, "success")

    mock_compiler = MagicMock()
    mock_compiler.is_available = MagicMock(return_value=True)
    mock_compiler.compile_with_status = fake_compile

    mock_storage = MagicMock()
    mock_storage.save_pdf = MagicMock(return_value="storage://user-001/job_job-001/job_resume.pdf")

    service = JobResumeService(
        job_repository=mock_repo,
        compiler_worker=mock_compiler,
        pdf_storage=mock_storage,
    )
    result = await service.generate_job_resume("user-001", "job-001", "user@example.com")

    assert result["status"] == "success"
    assert result["compression_level_used"] == 2
    assert call_count == 3


@pytest.mark.asyncio
async def test_service_overwrite_idempotent():
    """Re-running generate_job_resume must call upsert again (overwrite)."""
    from app.services.job_resume_service import JobResumeService

    optimized = _make_optimized()
    artifact_stub = {"status": "success", "page_count": 1}

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value={
        "_id": "job-001",
        "user_id": "user-001",
        "is_optimized": True,
        "optimization": optimized.model_dump(),
        "job_resume_artifact": artifact_stub,   # Already has an artifact
    })
    mock_repo.upsert_job_resume_artifact = AsyncMock(return_value={
        "_id": "job-001",
        "job_resume_artifact": artifact_stub,
    })

    mock_compiler = MagicMock()
    mock_compiler.is_available = MagicMock(return_value=True)
    mock_compiler.compile_with_status = AsyncMock(return_value=(b"%PDF-1.4", 1, "success"))

    mock_storage = MagicMock()
    mock_storage.save_pdf = MagicMock(return_value="storage://x")

    service = JobResumeService(
        job_repository=mock_repo,
        compiler_worker=mock_compiler,
        pdf_storage=mock_storage,
    )

    # Run twice
    await service.generate_job_resume("user-001", "job-001", "user@example.com")
    await service.generate_job_resume("user-001", "job-001", "user@example.com")

    # upsert should have been called twice — overwriting the previous artifact
    assert mock_repo.upsert_job_resume_artifact.call_count == 2
