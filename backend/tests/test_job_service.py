import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobApplicationCreate
from app.services.job_service import JobService


@pytest.mark.asyncio
async def test_job_service_crud(mock_mongo_db):
    repo = JobRepository(mock_mongo_db["job_applications"])
    service = JobService(repo)
    user_id = "user-test-123"

    # 1. Create Job Application
    job_in = JobApplicationCreate(
        company_name="OpenAI",
        role_title="Member of Technical Staff",
        job_description="Build distributed LLM training systems in Python and C++.",
        location="San Francisco, CA"
    )
    job_res = await service.create_job(user_id, job_in)
    assert job_res.id is not None
    assert job_res.company_name == "OpenAI"
    assert job_res.is_analyzed is False

    # 2. Get Job Application
    fetched = await service.get_job(user_id, job_res.id)
    assert fetched.id == job_res.id
    assert fetched.role_title == "Member of Technical Staff"

    # 3. List Job Applications
    jobs_list = await service.list_jobs(user_id)
    assert len(jobs_list) == 1
    assert jobs_list[0].id == job_res.id

    # 4. Delete Job Application
    deleted = await service.delete_job(user_id, job_res.id)
    assert deleted is True

    # 5. Get Deleted Job returns 404
    with pytest.raises(HTTPException) as exc:
        await service.get_job(user_id, job_res.id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_job_service_analyze_job(mock_mongo_db):
    repo = JobRepository(mock_mongo_db["job_applications"])
    mock_router = MagicMock()
    mock_router.generate_structured_json = AsyncMock(return_value={
        "data": {
            "title": "Senior AI Engineer",
            "experience_years_required": 5,
            "education_required": "Bachelor's degree in CS",
            "required_skills": ["Python", "FastAPI"],
            "preferred_skills": ["Kubernetes"],
            "programming_languages": ["Python"],
            "technologies_frameworks": ["FastAPI", "Docker"],
            "ai_ml_requirements": ["LLMs"],
            "responsibilities": ["Build backend services"],
            "important_keywords": ["FastAPI", "Python"]
        },
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "attempt_history": []
    })

    service = JobService(repo, router=mock_router)
    user_id = "user-test-456"

    job_in = JobApplicationCreate(
        company_name="Google",
        role_title="AI Research Engineer",
        job_description="Develop generative AI foundation models in Python."
    )
    created = await service.create_job(user_id, job_in)

    # Execute analyze_job
    analyzed = await service.analyze_job(user_id, created.id)
    assert analyzed.is_analyzed is True
    assert analyzed.analysis_provider == "gemini"
    assert analyzed.analysis_model == "gemini-2.5-flash"
    assert analyzed.requirements is not None
    assert analyzed.requirements.experience_years_required == 5
    assert "Python" in analyzed.requirements.required_skills
