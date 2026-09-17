import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.schemas.mailing_schema import (
    MailingDraftUpdate,
    MailingGenerateRequest,
    MailingInput,
)
from app.services.mailing_data_builder import MailingDataBuilder
from app.services.mailing_service import MailingService


@pytest.mark.asyncio
async def test_mailing_draft_requires_analyzed_job():
    job_repo = MagicMock()
    profile_repo = MagicMock()
    # Unanalyzed job
    job_repo.get_by_id = AsyncMock(return_value={
        "_id": "job_123",
        "user_id": "user_1",
        "company_name": "OpenAI",
        "role_title": "AI Engineer",
        "is_analyzed": False,
        "requirements": None,
    })
    profile_repo.get_by_user_id = AsyncMock(return_value={
        "personal_details": {"full_name": "Test Candidate"}
    })

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo)
    req = MailingGenerateRequest(job_id="job_123")

    with pytest.raises(HTTPException) as excinfo:
        await service.generate_draft("user_1", req)

    assert excinfo.value.status_code == 422
    assert "JD Intelligence unavailable" in excinfo.value.detail


@pytest.mark.asyncio
async def test_mailing_draft_requires_optimized_resume():
    job_repo = MagicMock()
    profile_repo = MagicMock()
    # Analyzed job but unoptimized
    job_repo.get_by_id = AsyncMock(return_value={
        "_id": "job_123",
        "user_id": "user_1",
        "company_name": "OpenAI",
        "role_title": "AI Engineer",
        "is_analyzed": True,
        "requirements": {"required_skills": ["Python"]},
        "is_optimized": False,
        "optimization": None,
    })
    profile_repo.get_by_user_id = AsyncMock(return_value={
        "personal_details": {"full_name": "Test Candidate"}
    })

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo)
    req = MailingGenerateRequest(job_id="job_123")

    with pytest.raises(HTTPException) as excinfo:
        await service.generate_draft("user_1", req)

    assert excinfo.value.status_code == 422
    assert "Optimized Resume unavailable" in excinfo.value.detail


@pytest.mark.asyncio
async def test_mailing_data_builder_constructs_clean_json_input():
    job_doc = {
        "_id": "job_abc",
        "company_name": "PaperFOX AI",
        "role_title": "Junior AI Engineer",
        "is_analyzed": True,
        "is_optimized": True,
        "requirements": {
            "required_skills": ["Python", "FastAPI", "LLMs"],
            "responsibilities": ["Build scalable agent workflows"],
            "preferred_skills": ["Docker"],
            "important_keywords": ["RAG", "Agentic Workflows"],
        },
        "optimization": {
            "personal_details": {"full_name": "Pushkar Chhokar"},
            "summary": "AI Engineer specializing in RAG architectures.",
            "skills": [
                {"category": "AI/ML", "skills": ["Python", "FastAPI", "LangChain"]}
            ],
            "projects": [
                {
                    "project_name": "AutoDoc AI",
                    "technologies": ["Python", "FastAPI", "Qdrant"],
                    "bullets": ["Engineered vector retrieval pipeline with sub-100ms response time."],
                }
            ],
        },
    }
    profile_doc = {
        "personal_details": {"full_name": "Pushkar Chhokar"},
    }

    mailing_input = MailingDataBuilder.build_input(
        job_doc=job_doc,
        profile_doc=profile_doc,
        recipient_name="Alex",
        recipient_role="Engineering Director",
    )

    assert isinstance(mailing_input, MailingInput)
    assert mailing_input.job.company == "PaperFOX AI"
    assert mailing_input.job.role == "Junior AI Engineer"
    assert mailing_input.candidate.name == "Pushkar Chhokar"
    assert len(mailing_input.relevant_projects) == 1
    assert mailing_input.relevant_projects[0].name == "AutoDoc AI"
    assert mailing_input.recipient.name == "Alex"
    assert mailing_input.recipient.role == "Engineering Director"


@pytest.mark.asyncio
async def test_mailing_draft_generation_with_ai():
    job_repo = MagicMock()
    profile_repo = MagicMock()
    router = MagicMock()

    job_repo.get_by_id = AsyncMock(return_value={
        "_id": "job_123",
        "user_id": "user_1",
        "company_name": "Anthropic",
        "role_title": "Senior AI Platform Engineer",
        "is_analyzed": True,
        "is_optimized": True,
        "requirements": {
            "required_skills": ["Python", "FastAPI", "RAG", "FAISS"],
            "responsibilities": ["Scale vector search and model serving pipelines"]
        },
        "optimization": {
            "personal_details": {"full_name": "Pushkar Chhokar"},
            "summary": "AI Engineer specializing in RAG systems.",
            "skills": [{"category": "AI", "skills": ["Python", "FastAPI", "FAISS"]}],
            "projects": [
                {
                    "project_name": "DevMind",
                    "technologies": ["Python", "FastAPI", "FAISS"],
                    "bullets": ["RAG-driven engineering platform with sub-150ms query latency."]
                }
            ]
        }
    })
    job_repo.update_job = AsyncMock(return_value={})

    profile_repo.get_by_user_id = AsyncMock(return_value={
        "personal_details": {"full_name": "Pushkar Chhokar"},
    })

    router.generate_structured_json = AsyncMock(return_value={
        "data": {
            "subject_options": [
                "Senior AI Platform Engineer — Pushkar Chhokar",
                "Re: AI Platform Engineer role / RAG & FAISS background",
                "Pushkar Chhokar <> Anthropic Engineering"
            ],
            "subject": "Senior AI Platform Engineer — Pushkar Chhokar",
            "body": (
                "Hi Alex,\n\n"
                "I'm reaching out regarding the Senior AI Platform Engineer opening at Anthropic. "
                "My recent work centers on scalable RAG architecture and high-throughput vector retrieval.\n\n"
                "Most recently, I engineered DevMind using FastAPI and FAISS, optimizing query pipelines to achieve "
                "sub-150ms latency across 500k documents. This aligns closely with Anthropic's focus on reliable retrieval infrastructure.\n\n"
                "I'd be glad to share my resume and discuss whether my background is a fit for what the team is building.\n\n"
                "Best,\nPushkar Chhokar"
            ),
            "short_body": (
                "Hi Alex,\n\n"
                "I'm reaching out regarding the Senior AI Platform Engineer role at Anthropic. "
                "I recently built DevMind, a RAG platform using FastAPI and FAISS that delivered sub-150ms query latency.\n\n"
                "I'd welcome the chance to share my resume and chat briefly.\n\n"
                "Best,\nPushkar Chhokar"
            ),
            "selected_evidence": ["DevMind RAG platform (FastAPI, FAISS, sub-150ms latency)"]
        }
    })

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo, router=router)

    req = MailingGenerateRequest(
        job_id="job_123",
        recipient_name="Alex",
        recipient_email="alex@anthropic.com",
        recipient_role="Engineering Manager"
    )
    draft = await service.generate_draft("user_1", req)

    assert draft.job_id == "job_123"
    assert draft.recipient_name == "Alex"
    assert draft.recipient_email == "alex@anthropic.com"
    assert draft.recipient_role == "Engineering Manager"
    assert "Senior AI Platform Engineer" in draft.subject
    assert len(draft.subject_options) == 3
    assert "DevMind" in draft.body
    assert "FAISS" in draft.body
    assert "Pushkar Chhokar" in draft.body
    assert draft.status == "ready"

    # Verifies draft was persisted to job doc
    job_repo.update_job.assert_called_once()
    args, kwargs = job_repo.update_job.call_args
    assert args[0] == "job_123"
    assert args[1] == "user_1"
    assert "mailing_draft" in args[2]


@pytest.mark.asyncio
async def test_mailing_draft_sanitization_removes_banned_phrases_and_bolding():
    job_repo = MagicMock()
    profile_repo = MagicMock()
    router = MagicMock()

    job_repo.get_by_id = AsyncMock(return_value={
        "_id": "job_123",
        "user_id": "user_1",
        "company_name": "Google",
        "role_title": "Software Engineer",
        "is_analyzed": True,
        "is_optimized": True,
        "requirements": {"required_skills": ["Python"]},
        "optimization": {
            "personal_details": {"full_name": "Jane Doe"},
            "skills": [{"category": "Languages", "skills": ["Python"]}],
            "projects": [{"project_name": "SearchApp", "technologies": ["Python"], "bullets": ["Built app"]}]
        }
    })
    job_repo.update_job = AsyncMock(return_value={})
    profile_repo.get_by_user_id = AsyncMock(return_value={
        "personal_details": {"full_name": "Jane Doe"},
    })

    # AI returns banned phrases and markdown bolding
    router.generate_structured_json = AsyncMock(return_value={
        "data": {
            "subject_options": ["Software Engineer — Jane Doe"],
            "subject": "**Software Engineer** — Jane Doe",
            "body": (
                "Hi Hiring Team,\n\n"
                "I hope this email finds you well! I am thrilled to apply for this **cutting-edge** role. "
                "I built a **robust** system using Python.\n\n"
                "Best,\nJane Doe"
            ),
            "short_body": "I hope this email finds you well! Short note.",
            "selected_evidence": []
        }
    })

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo, router=router)
    req = MailingGenerateRequest(job_id="job_123")
    draft = await service.generate_draft("user_1", req)

    # Bolding removed
    assert "**" not in draft.subject
    assert "**" not in draft.body
    # Banned phrases stripped
    assert "I hope this email finds you well" not in draft.body
    assert "cutting-edge" not in draft.body
    assert "robust" not in draft.body


@pytest.mark.asyncio
async def test_mailing_draft_update_and_get():
    job_repo = MagicMock()
    profile_repo = MagicMock()

    existing_draft_dict = {
        "job_id": "job_123",
        "recipient_name": "Sarah",
        "recipient_email": "sarah@tech.com",
        "recipient_role": "Recruiter",
        "subject": "Initial Subject",
        "subject_options": ["Initial Subject", "Alt Subject"],
        "body": "Initial body text",
        "short_body": "Short text",
        "selected_evidence": [],
        "status": "ready"
    }

    job_repo.get_by_id = AsyncMock(return_value={
        "_id": "job_123",
        "user_id": "user_1",
        "mailing_draft": existing_draft_dict
    })
    job_repo.update_job = AsyncMock(return_value={})

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo)

    # 1. Test get
    draft = await service.get_draft("user_1", "job_123")
    assert draft is not None
    assert draft.subject == "Initial Subject"
    assert draft.recipient_name == "Sarah"

    # 2. Test update
    update_data = MailingDraftUpdate(
        subject="Updated Subject Line",
        body="Updated refined email body.",
        status="ready"
    )
    updated = await service.update_draft("user_1", "job_123", update_data)
    assert updated.subject == "Updated Subject Line"
    assert updated.body == "Updated refined email body."
    assert updated.status == "ready"
    assert updated.recipient_name == "Sarah"  # Preserved
    assert updated.updated_at is not None


@pytest.mark.asyncio
async def test_mailing_cross_user_forbidden():
    job_repo = MagicMock()
    profile_repo = MagicMock()

    job_repo.get_by_id = AsyncMock(return_value=None)
    job_repo.get_by_id_unscoped = AsyncMock(return_value={
        "_id": "job_123",
        "user_id": "user_2",
        "company_name": "Target Corp",
        "role_title": "Backend Engineer",
    })

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo)
    req = MailingGenerateRequest(job_id="job_123")

    with pytest.raises(HTTPException) as excinfo:
        await service.generate_draft("user_1", req)

    assert excinfo.value.status_code == 403
    assert "You don't have access to this job." in excinfo.value.detail


@pytest.mark.asyncio
async def test_mailing_job_not_found():
    job_repo = MagicMock()
    profile_repo = MagicMock()

    job_repo.get_by_id = AsyncMock(return_value=None)
    job_repo.get_by_id_unscoped = AsyncMock(return_value=None)

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo)
    req = MailingGenerateRequest(job_id="job_does_not_exist")

    with pytest.raises(HTTPException) as excinfo:
        await service.generate_draft("user_1", req)

    assert excinfo.value.status_code == 404
    assert "Job application not found." in excinfo.value.detail
