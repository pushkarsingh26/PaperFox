import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from app.services.ai.project_evidence_parser import ProjectEvidenceParser
from app.schemas.optimization_schema import StructuredProjectEvidence


@pytest.fixture
def mock_evidence_json():
    return {
        "architecture": ["FastAPI async gateway with Redis cache and Celery workers"],
        "technologies": ["Python", "Docker"],
        "frameworks": ["FastAPI", "Celery"],
        "apis": ["POST /v1/infer", "GET /v1/status/{task_id}"],
        "models": ["meta-llama/Llama-3-8b-instruct"],
        "databases": ["Redis"],
        "deployment": ["Docker Compose"],
        "features": ["Async job processing", "Model inference gateway"],
        "technical_details": ["Used Redis queue to decouple ingest from compute"],
        "engineering_decisions": ["Used Redis queue to decouple ingest from compute"],
        "limitations": ["Kubernetes cluster deployment unverified"],
    }


@pytest.mark.asyncio
async def test_phase7_evidence_extraction_and_lifecycle(async_client: AsyncClient, mock_evidence_json):
    # 1. Register and login
    reg_resp = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "evidence_user@example.com", "password": "Password123!"},
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Save profile with project having ai_analysis_text
    profile_data = {
        "personal_details": {"full_name": "Evidence Tester"},
        "candidate_type": "fresher",
        "skills": [{"name": "Python", "category": "Programming"}],
        "projects": [
            {
                "id": "proj-101",
                "name": "LLM Serving Engine",
                "description_source": "ai",
                "ai_analysis_text": "Project LLM Serving Engine. Built FastAPI gateway with Redis cache and Celery workers...",
            },
            {
                "id": "proj-102",
                "name": "Manual Project",
                "description_source": "self",
                "description": "Hand-written description.",
            },
        ],
    }
    save_resp = await async_client.post("/api/v1/profile", json=profile_data, headers=headers)
    assert save_resp.status_code == 201

    # 3. Extract evidence on proj-101 (mocking parser)
    with patch.object(
        ProjectEvidenceParser,
        "parse_analysis_text",
        new_callable=AsyncMock,
    ) as mock_parse:
        mock_parse.return_value = StructuredProjectEvidence(**mock_evidence_json)

        extract_resp = await async_client.post(
            "/api/v1/profile/projects/proj-101/extract-evidence",
            headers=headers,
        )
        assert extract_resp.status_code == 200
        data = extract_resp.json()
        assert data["evidence_status"] == "current"
        assert data["was_cached"] is False
        assert data["evidence"]["architecture"] == ["FastAPI async gateway with Redis cache and Celery workers"]
        assert "Python" in data["evidence"]["technologies"]
        assert mock_parse.call_count == 1

        # 4. Test idempotency: calling again should return cached without AI call
        extract_again = await async_client.post(
            "/api/v1/profile/projects/proj-101/extract-evidence",
            headers=headers,
        )
        assert extract_again.status_code == 200
        assert extract_again.json()["was_cached"] is True
        assert mock_parse.call_count == 1  # No additional AI call!

        # 5. Force re-extraction should call parser again
        force_extract = await async_client.post(
            "/api/v1/profile/projects/proj-101/extract-evidence?force=true",
            headers=headers,
        )
        assert force_extract.status_code == 200
        assert force_extract.json()["was_cached"] is False
        assert mock_parse.call_count == 2

    # 6. GET stored evidence endpoint
    get_ev = await async_client.get(
        "/api/v1/profile/projects/proj-101/evidence",
        headers=headers,
    )
    assert get_ev.status_code == 200
    assert "FastAPI async gateway with Redis cache and Celery workers" in get_ev.json()["evidence"]["architecture"]

    # 7. Extract on project without ai_analysis_text should return 400
    err_ev = await async_client.post(
        "/api/v1/profile/projects/proj-102/extract-evidence",
        headers=headers,
    )
    assert err_ev.status_code == 400


@pytest.mark.asyncio
async def test_phase7_application_history_and_status(async_client: AsyncClient):
    # 1. Register and login
    reg_resp = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "history_user@example.com", "password": "Password123!"},
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create two job applications
    job1_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "company_name": "Acme Corp",
            "role_title": "Senior Python Engineer",
            "job_description": "We are seeking a senior Python developer experienced in FastAPI and Docker.",
            "location": "Remote",
        },
        headers=headers,
    )
    assert job1_resp.status_code == 201
    job1_id = job1_resp.json()["id"]
    assert job1_resp.json()["application_status"] == "draft"

    job2_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "company_name": "Beta Labs",
            "role_title": "AI Platform Engineer",
            "job_description": "Looking for an engineer to build LLM pipelines and RAG workflows.",
            "location": "San Francisco, CA",
        },
        headers=headers,
    )
    assert job2_resp.status_code == 201
    job2_id = job2_resp.json()["id"]

    # 3. Update status of job1 to applied
    stat_resp = await async_client.patch(
        f"/api/v1/jobs/{job1_id}/status",
        json={"status": "applied"},
        headers=headers,
    )
    assert stat_resp.status_code == 200
    assert stat_resp.json()["application_status"] == "applied"
    assert stat_resp.json()["status_updated_at"] is not None

    # 4. Update status with invalid value should return 422
    inv_resp = await async_client.patch(
        f"/api/v1/jobs/{job1_id}/status",
        json={"status": "non_existent_status"},
        headers=headers,
    )
    assert inv_resp.status_code == 422

    # 5. Update notes on job1
    notes_resp = await async_client.patch(
        f"/api/v1/jobs/{job1_id}/notes",
        json={"notes": "Applied via referral on LinkedIn."},
        headers=headers,
    )
    assert notes_resp.status_code == 200
    assert notes_resp.json()["notes"] == "Applied via referral on LinkedIn."
    # Status should remain 'applied'
    assert notes_resp.json()["application_status"] == "applied"

    # 6. Check history listing
    hist_all = await async_client.get("/api/v1/jobs/history", headers=headers)
    assert hist_all.status_code == 200
    assert hist_all.json()["total"] == 2

    # 7. Check history listing filtered by status
    hist_applied = await async_client.get("/api/v1/jobs/history?status=applied", headers=headers)
    assert hist_applied.status_code == 200
    assert hist_applied.json()["total"] == 1
    assert hist_applied.json()["items"][0]["company_name"] == "Acme Corp"

    hist_draft = await async_client.get("/api/v1/jobs/history?status=draft", headers=headers)
    assert hist_draft.status_code == 200
    assert hist_draft.json()["total"] == 1
    assert hist_draft.json()["items"][0]["company_name"] == "Beta Labs"

    # 8. Check stats
    stats_resp = await async_client.get("/api/v1/jobs/history/stats", headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total"] == 2
    assert stats["by_status"].get("applied") == 1
    assert stats["by_status"].get("draft") == 1
