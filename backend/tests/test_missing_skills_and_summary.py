import pytest
from unittest.mock import AsyncMock, MagicMock
from app.schemas.job import JobRequirements, SuggestedMissingSkill
from app.schemas.optimization_schema import (
    KeywordAlignment,
    OptimizationMetadata,
    OptimizedProject,
    OptimizedResumeData,
    OptimizedSkillGroup,
    StructuredProjectEvidence,
)
from app.services.ai.optimizer_service import OptimizerService
from app.utils.optimization_validator import validate_optimized_data
from app.resume.job_resume_renderer import render_certifications


@pytest.mark.asyncio
async def test_professional_summary_sanitization_and_no_name():
    router_mock = MagicMock()
    # Mock LLM returning third-person and candidate name
    router_mock.generate_structured_json = AsyncMock(return_value={
        "data": {
            "summary": "Pushkar Chhokar is a fresh Junior AI Engineer specializing in FastAPI and PyTorch. He has built scalable RAG pipelines."
        }
    })

    optimizer = OptimizerService(router=router_mock)
    profile = {
        "personal_details": {"full_name": "Pushkar Chhokar"},
        "skills": [{"name": "FastAPI"}, {"name": "PyTorch"}],
        "projects": [{"name": "DevMind", "technologies": ["FastAPI", "PyTorch"], "description": "AI Platform"}]
    }
    reqs = JobRequirements(
        title="AI Engineer",
        required_skills=["FastAPI", "PyTorch"],
        preferred_skills=[],
        programming_languages=["Python"],
        technologies_frameworks=["FastAPI"],
        ai_ml_requirements=["PyTorch"],
        responsibilities=[],
        important_keywords=[]
    )

    summary = await optimizer.optimize_summary(profile, reqs, approved_additional_skills=["Docker"])

    # 1. Candidate name must never appear
    assert "Pushkar" not in summary
    assert "Chhokar" not in summary
    # 2. Third person "is a" / "He has" preamble stripped
    assert not summary.startswith("Pushkar")
    assert not summary.startswith("He is")
    # 3. Awkward phrase "fresh Junior" sanitized
    assert "fresh Junior" not in summary


@pytest.mark.asyncio
async def test_missing_skills_diff_and_dynamic_categorization():
    router_mock = MagicMock()
    # Mock AI categorizing the missing skills into candidate profile's existing categories
    router_mock.generate_structured_json = AsyncMock(return_value={
        "data": {
            "categorized_skills": [
                {
                    "skill": "Docker",
                    "category": "Developer Tools"
                },
                {
                    "skill": "AWS",
                    "category": "Cloud & Infrastructure"
                },
                {
                    "skill": "Kubernetes",
                    "category": "Developer Tools"
                }
            ]
        }
    })

    optimizer = OptimizerService(router=router_mock)
    profile = {
        "skills": [
            {"category": "Programming Languages", "name": "Python"},
            {"category": "Frameworks & Libraries", "name": "FastAPI"},
            {"category": "AI & Machine Learning", "name": "Scikit-learn"}
        ],
        "projects": [],
        "experience": []
    }
    reqs = JobRequirements(
        title="Senior AI Engineer",
        required_skills=["Docker", "AWS", "k8s", "Sckit-Learn", "Python"],
        preferred_skills=[],
        programming_languages=["Python"],
        technologies_frameworks=["FastAPI"],
        ai_ml_requirements=[],
        responsibilities=[],
        important_keywords=[]
    )

    results = await optimizer.analyze_critical_missing_skills(profile, reqs)

    # 1. Normalized diff: Python and Scikit-learn (synonym Sckit-Learn) are already in profile.
    # Docker, AWS, and Kubernetes (normalized from k8s) must be in results.
    skill_names = [r.skill for r in results]
    assert "Docker" in skill_names
    assert "AWS" in skill_names
    assert "Kubernetes" in skill_names
    assert "Python" not in skill_names
    assert "Scikit-learn" not in skill_names
    assert "Sckit-Learn" not in skill_names

    # 2. All missing skills from diff are returned with assigned categories; no skills dropped by importance
    for r in results:
        assert r.category in ("Developer Tools", "Cloud & Infrastructure", "Other Relevant Skills")


def test_project_bullet_sanitization_no_bolding_no_buzzwords():
    from app.services.ai.optimizer_service import sanitize_project_bullets

    raw_bullets = [
        "Architected an **AI-powered** search engine using FastAPI and LangChain for real-time document search.",
        "Engineered RAG retrieval pipelines with LangChain and FAISS vector index, improving lookup speed.",
        "Built robust background processing workers with FastAPI for batch embedding generation."
    ]

    sanitized = sanitize_project_bullets(
        raw_bullets,
        tech_stack=["FastAPI", "LangChain", "FAISS"]
    )

    assert len(sanitized) == 3
    # 1. No markdown bolding
    for b in sanitized:
        assert "**" not in b
        assert not b.endswith("..")

    # 2. Banned buzzwords stripped / replaced
    assert "AI-powered" not in sanitized[0]
    assert "robust" not in sanitized[2]

    # 3. Repeated technologies across multiple bullets sanitized
    # "LangChain" in bullet 1; bullet 2 should not unnecessarily repeat LangChain
    # "FastAPI" in bullet 1; bullet 3 should not unnecessarily repeat FastAPI
    assert "FastAPI" in sanitized[0]
    assert "FastAPI" not in sanitized[2]



def test_factual_validation_confirmed_skills_allowed_in_technical_skills():
    profile = {
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        "education": [{"institution": "Tech Univ", "degree": "BS CS"}],
        "experience": [],
        "internships": [],
        "projects": [],
        "certifications": []
    }

    opt_data = OptimizedResumeData(
        job_id="job_123",
        personal_details={},
        summary="Software Engineer specializing in Python and FastAPI.",
        education=[{"institution": "Tech Univ", "degree": "BS CS"}],
        experience=[],
        internships=[],
        projects=[],
        skills=[
            OptimizedSkillGroup(category="Languages", skills=["Python"]),
            OptimizedSkillGroup(category="Developer Tools", skills=["Docker"])  # Confirmed skill
        ],
        certifications=[],
        keyword_alignment=KeywordAlignment(
            matched_keywords=["Python"],
            missing_keywords=["Docker"],
            safely_usable_keywords=["Python"],
            unsupported_jd_keywords=["Docker"]
        ),
        optimization_metadata=OptimizationMetadata(status="completed", generated_at="2026-09-16T12:00:00Z")
    )

    # Should pass without error when Docker is in approved_additional_skills
    validate_optimized_data(
        original_profile=profile,
        structured_evidence_map=None,
        optimized_data=opt_data,
        approved_additional_skills=["Docker"]
    )


def test_factual_validation_confirmed_skills_cannot_fabricate_project_technologies():
    profile = {
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        "education": [{"institution": "Tech Univ", "degree": "BS CS"}],
        "experience": [],
        "internships": [],
        "projects": [{"name": "DevMind", "technologies": ["Python", "FastAPI"]}],
        "certifications": []
    }

    opt_data = OptimizedResumeData(
        job_id="job_123",
        personal_details={},
        summary="Software Engineer.",
        education=[{"institution": "Tech Univ", "degree": "BS CS"}],
        experience=[],
        internships=[],
        projects=[
            OptimizedProject(
                project_name="DevMind",
                relevance_score=0.9,
                relevance_reasons=[],
                matched_requirements=[],
                technologies=["Python", "FastAPI", "Docker"],  # Docker NOT in project profile/evidence!
                bullets=["Engineered backend using FastAPI."]
            )
        ],
        skills=[
            OptimizedSkillGroup(category="Languages", skills=["Python", "FastAPI", "Docker"])
        ],
        certifications=[],
        keyword_alignment=KeywordAlignment(
            matched_keywords=["Python"],
            missing_keywords=[],
            safely_usable_keywords=["Python"],
            unsupported_jd_keywords=[]
        ),
        optimization_metadata=OptimizationMetadata(status="completed", generated_at="2026-09-16T12:00:00Z")
    )

    with pytest.raises(ValueError) as excinfo:
        validate_optimized_data(
            original_profile=profile,
            structured_evidence_map=None,
            optimized_data=opt_data,
            approved_additional_skills=["Docker"]
        )

    assert "Project technology 'Docker' in project 'DevMind' was not found" in str(excinfo.value)


def test_factual_validation_confirmed_skills_cannot_fabricate_project_bullets():
    profile = {
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        "education": [{"institution": "Tech Univ", "degree": "BS CS"}],
        "experience": [],
        "internships": [],
        "projects": [{"name": "DevMind", "technologies": ["Python", "FastAPI"]}],
        "certifications": []
    }

    opt_data = OptimizedResumeData(
        job_id="job_123",
        personal_details={},
        summary="Software Engineer.",
        education=[{"institution": "Tech Univ", "degree": "BS CS"}],
        experience=[],
        internships=[],
        projects=[
            OptimizedProject(
                project_name="DevMind",
                relevance_score=0.9,
                relevance_reasons=[],
                matched_requirements=[],
                technologies=["Python", "FastAPI"],
                bullets=["Containerized DevMind using Docker for production deployment."]  # Docker fabricated!
            )
        ],
        skills=[
            OptimizedSkillGroup(category="Languages", skills=["Python", "FastAPI", "Docker"])
        ],
        certifications=[],
        keyword_alignment=KeywordAlignment(
            matched_keywords=["Python"],
            missing_keywords=[],
            safely_usable_keywords=["Python"],
            unsupported_jd_keywords=[]
        ),
        optimization_metadata=OptimizationMetadata(status="completed", generated_at="2026-09-16T12:00:00Z")
    )

    with pytest.raises(ValueError) as excinfo:
        validate_optimized_data(
            original_profile=profile,
            structured_evidence_map=None,
            optimized_data=opt_data,
            approved_additional_skills=["Docker"]
        )

    assert "Confirmed skill 'Docker' cannot be used in project bullet without evidence" in str(excinfo.value)


def test_factual_validation_unconfirmed_missing_skills_rejected():
    profile = {
        "skills": [{"name": "Python"}],
        "education": [{"institution": "Tech Univ", "degree": "BS CS"}],
        "experience": [],
        "internships": [],
        "projects": [],
        "certifications": []
    }

    opt_data = OptimizedResumeData(
        job_id="job_123",
        personal_details={},
        summary="Software Engineer.",
        education=[{"institution": "Tech Univ", "degree": "BS CS"}],
        experience=[],
        internships=[],
        projects=[],
        skills=[
            OptimizedSkillGroup(category="Languages", skills=["Python", "Kubernetes"])  # Kubernetes NOT confirmed!
        ],
        certifications=[],
        keyword_alignment=KeywordAlignment(
            matched_keywords=["Python"],
            missing_keywords=["Kubernetes"],
            safely_usable_keywords=["Python"],
            unsupported_jd_keywords=["Kubernetes"]
        ),
        optimization_metadata=OptimizationMetadata(status="completed", generated_at="2026-09-16T12:00:00Z")
    )

    with pytest.raises(ValueError) as excinfo:
        validate_optimized_data(
            original_profile=profile,
            structured_evidence_map=None,
            optimized_data=opt_data,
            approved_additional_skills=["Docker"]  # Docker is confirmed, but Kubernetes is NOT
        )

    assert "Kubernetes" in str(excinfo.value)


def test_certification_rendering_removes_credentials():
    certifications = [
        {
            "name": "Foundations of AI and Machine Learning",
            "issuer": "Microsoft",
            "issue_date": "2026-04-15",
            "credential_id": "MS-998822",
            "credential_url": "https://learn.microsoft.com/cert/998822"
        },
        {
            "name": "Gen AI – Beyond the Chatbot",
            "issuer": "Google Cloud",
            "issue_date": "2026",
            "verification_url": "https://cloud.google.com/verify/12345"
        }
    ]

    rendered = render_certifications(certifications)

    # Must include Issuer, Name, and Year
    assert "\\textbf{Microsoft:} Foundations of AI and Machine Learning (2026)" in rendered
    assert "\\textbf{Google Cloud:} Gen AI - Beyond the Chatbot (2026)" in rendered

    # Must NOT render credential URLs, IDs, or "Credential"
    assert "credential" not in rendered.lower()
    assert "MS-998822" not in rendered
    assert "learn.microsoft.com" not in rendered
    assert "cloud.google.com/verify" not in rendered
