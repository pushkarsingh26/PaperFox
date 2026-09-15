import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.job import JobRequirements
from app.schemas.optimization_schema import (
    KeywordAlignment,
    OptimizationMetadata,
    OptimizedProject,
    OptimizedResumeData,
    OptimizedSkillGroup,
    StructuredProjectEvidence,
)
from app.services.ai.optimizer_service import OptimizerService
from app.services.ai.project_evidence_parser import ProjectEvidenceParser
from app.utils.optimization_validator import validate_optimized_data


def test_optimization_validator_valid_data():
    original_profile = {
        "personal_details": {"full_name": "Pushkar Singh"},
        "skills": [{"name": "Python", "category": "Programming"}, {"name": "FastAPI", "category": "Frameworks"}],
        "education": [{"institution": "IIT Bombay", "degree": "B.Tech", "field_of_study": "Computer Science"}],
        "experience": [{"company": "Tech Corp", "role": "Backend Engineer", "technologies": ["Python", "FastAPI"]}],
        "internships": [],
        "projects": [{"name": "PaperFox", "technologies": ["Python", "FastAPI", "MongoDB"]}],
        "certifications": []
    }

    opt_data = OptimizedResumeData(
        job_id="job-123",
        personal_details={"full_name": "Pushkar Singh"},
        summary="Experienced engineer with Python and FastAPI background.",
        education=[{"institution": "IIT Bombay", "degree": "B.Tech", "field_of_study": "Computer Science"}],
        experience=[
            {
                "company": "Tech Corp",
                "role": "Backend Engineer",
                "bullets": ["Developed scalable APIs using FastAPI."],
                "technologies": ["Python", "FastAPI"]
            }
        ],
        internships=[],
        projects=[
            OptimizedProject(
                project_name="PaperFox",
                relevance_score=0.95,
                relevance_reasons=["Relevant tech stack"],
                technologies=["Python", "FastAPI"],
                bullets=["Built resume optimization engine."]
            )
        ],
        skills=[OptimizedSkillGroup(category="Programming", skills=["Python", "FastAPI"])],
        certifications=[],
        keyword_alignment=KeywordAlignment(
            matched_keywords=["Python", "FastAPI"],
            missing_keywords=["Kubernetes"],
            safely_usable_keywords=["Python", "FastAPI"],
            unsupported_jd_keywords=["Kubernetes"]
        ),
        optimization_metadata=OptimizationMetadata(status="completed", provider="test", model="test_model")
    )

    # Should pass without raising ValueError
    validate_optimized_data(original_profile, None, opt_data)


def test_optimization_validator_rejects_hallucinated_skill():
    original_profile = {
        "personal_details": {"full_name": "Pushkar Singh"},
        "skills": [{"name": "Python", "category": "Programming"}],
        "education": [],
        "experience": [],
        "projects": []
    }

    opt_data = OptimizedResumeData(
        job_id="job-123",
        personal_details={"full_name": "Pushkar Singh"},
        summary="Python engineer.",
        education=[],
        experience=[],
        internships=[],
        projects=[],
        skills=[OptimizedSkillGroup(category="Cloud", skills=["Kubernetes"])],  # Hallucinated skill!
        certifications=[],
        keyword_alignment=KeywordAlignment(),
        optimization_metadata=OptimizationMetadata(status="completed")
    )

    with pytest.raises(ValueError, match="Skill 'Kubernetes' is not present in candidate profile"):
        validate_optimized_data(original_profile, None, opt_data)


def test_optimization_validator_rejects_modified_education():
    original_profile = {
        "personal_details": {"full_name": "Pushkar Singh"},
        "skills": [],
        "education": [{"institution": "IIT Bombay", "degree": "B.Tech", "field_of_study": "Computer Science"}],
        "experience": [],
        "projects": []
    }

    opt_data = OptimizedResumeData(
        job_id="job-123",
        personal_details={"full_name": "Pushkar Singh"},
        summary="Computer Science graduate.",
        education=[{"institution": "Stanford University", "degree": "B.Tech", "field_of_study": "Computer Science"}],  # Altered institution!
        experience=[],
        internships=[],
        projects=[],
        skills=[],
        certifications=[],
        keyword_alignment=KeywordAlignment(),
        optimization_metadata=OptimizationMetadata(status="completed")
    )

    with pytest.raises(ValueError, match="Education institution modified"):
        validate_optimized_data(original_profile, None, opt_data)


@pytest.mark.asyncio
async def test_project_evidence_parser():
    raw_text = """
    PROJECT OVERVIEW: Multi-provider AI resume platform.
    ARCHITECTURE: FastAPI microservice with Next.js frontend.
    TECHNOLOGIES: Python, TypeScript, MongoDB, Docker.
    APIs: REST API.
    LIMITATIONS: Kubernetes deployment could not be verified.
    """
    mock_router = AsyncMock()
    mock_router.generate_structured_json.return_value = {
        "data": {
            "architecture": ["microservices"],
            "technologies": ["Python", "TypeScript"],
            "frameworks": ["FastAPI", "Next.js"],
            "apis": ["REST"],
            "databases": ["MongoDB"],
            "deployment": ["Docker"],
            "limitations": ["Kubernetes deployment unverified"]
        }
    }

    parser = ProjectEvidenceParser(mock_router)
    evidence = await parser.parse_analysis_text("PaperFox", raw_text)

    assert "Python" in evidence.technologies
    assert "FastAPI" in evidence.frameworks
    assert "MongoDB" in evidence.databases
    assert "Kubernetes deployment unverified" in evidence.limitations


@pytest.mark.asyncio
async def test_optimizer_service_keyword_alignment():
    cand_profile = {
        "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "Docker"}],
        "experience": [],
        "projects": []
    }
    job_reqs = JobRequirements(
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker", "Kubernetes"]
    )

    optimizer = OptimizerService()
    alignment = optimizer.compute_keyword_alignment(cand_profile, job_reqs)

    assert "Python" in alignment.matched_keywords
    assert "FastAPI" in alignment.matched_keywords
    assert "Docker" in alignment.matched_keywords
    assert "Kubernetes" in alignment.unsupported_jd_keywords
    assert "Kubernetes" not in alignment.matched_keywords
