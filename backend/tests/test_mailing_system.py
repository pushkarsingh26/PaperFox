import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.schemas.job import MailingDraftUpdate, MailingGenerateRequest
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
        "requirements": None
    })

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo)

    with pytest.raises(HTTPException) as excinfo:
        await service.generate_mailing_draft("user_1", "job_123")

    assert excinfo.value.status_code == 400
    assert "must be analyzed with JD Intelligence" in excinfo.value.detail


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
        "requirements": {
            "required_skills": ["Python", "FastAPI", "RAG", "FAISS"],
            "responsibilities": ["Scale vector search and model serving pipelines"]
        },
        "approved_additional_skills": ["Docker"]
    })
    job_repo.update_job = AsyncMock(return_value={})

    profile_repo.get_by_user_id = AsyncMock(return_value={
        "personal_details": {"full_name": "Pushkar Chhokar"},
        "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "FAISS"}],
        "projects": [
            {
                "name": "DevMind",
                "technologies": ["Python", "FastAPI", "FAISS"],
                "description": "RAG-driven engineering platform",
                "evidence": {"measurable_outcomes": ["Sub-150ms vector query latency across 500k documents"]}
            }
        ]
    })

    router.generate_structured_json = AsyncMock(return_value={
        "data": {
            "subject_options": [
                "Senior AI Platform Engineer — Pushkar Chhokar",
                "Re: AI Platform Engineer role / RAG & FAISS background",
                "Pushkar Chhokar <> Anthropic Engineering"
            ],
            "chosen_subject": "Senior AI Platform Engineer — Pushkar Chhokar",
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
        recipient_name="Alex",
        recipient_email="alex@anthropic.com",
        recipient_role="Engineering Manager"
    )
    draft = await service.generate_mailing_draft("user_1", "job_123", req)

    assert draft.job_id == "job_123"
    assert draft.recipient_name == "Alex"
    assert draft.recipient_email == "alex@anthropic.com"
    assert draft.recipient_role == "Engineering Manager"
    assert "Senior AI Platform Engineer" in draft.subject
    assert len(draft.subject_options) == 3
    assert "DevMind" in draft.body
    assert "FAISS" in draft.body
    assert "Pushkar Chhokar" in draft.body
    assert draft.status == "draft"

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
        "requirements": {"required_skills": ["Python"]}
    })
    job_repo.update_job = AsyncMock(return_value={})
    profile_repo.get_by_user_id = AsyncMock(return_value={
        "personal_details": {"full_name": "Jane Doe"},
        "skills": [{"name": "Python"}]
    })

    # AI returns banned phrases and markdown bolding
    router.generate_structured_json = AsyncMock(return_value={
        "data": {
            "subject_options": ["Software Engineer — Jane Doe"],
            "chosen_subject": "**Software Engineer** — Jane Doe",
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
    draft = await service.generate_mailing_draft("user_1", "job_123")

    # Bolding removed
    assert "**" not in draft.subject
    assert "**" not in draft.body
    # Banned phrases stripped
    assert "I hope this email finds you well" not in draft.body
    assert "thrilled to apply" not in draft.body
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
        "status": "draft"
    }

    job_repo.get_by_id = AsyncMock(return_value={
        "_id": "job_123",
        "user_id": "user_1",
        "mailing_draft": existing_draft_dict
    })
    job_repo.update_job = AsyncMock(return_value={})

    service = MailingService(job_repository=job_repo, profile_repository=profile_repo)

    # 1. Test get
    draft = await service.get_mailing_draft("user_1", "job_123")
    assert draft is not None
    assert draft.subject == "Initial Subject"
    assert draft.recipient_name == "Sarah"

    # 2. Test update
    update_data = MailingDraftUpdate(
        subject="Updated Subject Line",
        body="Updated refined email body.",
        status="ready"
    )
    updated = await service.update_mailing_draft("user_1", "job_123", update_data)
    assert updated.subject == "Updated Subject Line"
    assert updated.body == "Updated refined email body."
    assert updated.status == "ready"
    assert updated.recipient_name == "Sarah"  # Preserved
    assert updated.updated_at is not None
