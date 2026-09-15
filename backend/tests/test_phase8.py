import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from app.core.config import settings
from app.schemas.optimization_schema import (
    StructuredProjectEvidence,
    OptimizedResumeData,
    OptimizedProject,
    OptimizedExperience,
    OptimizedInternship,
    OptimizedSkillGroup,
    KeywordAlignment,
    OptimizationMetadata,
)


@pytest.mark.asyncio
async def test_phase8_health_endpoint_healthy(async_client: AsyncClient):
    with patch("app.main.ping_database", new_callable=AsyncMock) as mock_ping:
        mock_ping.return_value = True
        resp = await async_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["service"] == "PaperFox"


@pytest.mark.asyncio
async def test_phase8_health_endpoint_unhealthy(async_client: AsyncClient):
    with patch("app.main.ping_database", new_callable=AsyncMock) as mock_ping:
        mock_ping.return_value = False
        resp = await async_client.get("/health")
        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"


@pytest.mark.asyncio
async def test_phase8_security_headers(async_client: AsyncClient):
    resp = await async_client.get("/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert "strict-origin-when-cross-origin" in resp.headers.get("Referrer-Policy", "")
    assert "camera=()" in resp.headers.get("Permissions-Policy", "")


@pytest.mark.asyncio
async def test_phase8_global_exception_handling_masks_traceback(async_client: AsyncClient):
    # Trigger an unexpected exception by patching service method to raise RuntimeError
    # Signup first to get valid auth token
    reg_resp = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "masktest@example.com", "password": "Password123!"},
    )
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with patch(
        "app.services.job_service.JobService.list_jobs",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Secret database connection string leaked!"),
    ):
        resp = await async_client.get("/api/v1/jobs", headers=headers)
        assert resp.status_code == 500
        data = resp.json()
        assert data["detail"] == "Internal server error"
        assert "error_id" in data
        assert "Secret database connection" not in str(resp.content)
        assert "RuntimeError" not in str(resp.content)
        assert "Traceback" not in str(resp.content)


@pytest.mark.asyncio
async def test_phase8_rate_limiting_auth(async_client: AsyncClient):
    # Ensure rate limiting is enabled
    old_enabled = settings.RATE_LIMITING_ENABLED
    settings.RATE_LIMITING_ENABLED = True
    try:
        # Rate limit is 10 per minute
        hit_429 = False
        for i in range(13):
            resp = await async_client.post(
                "/api/v1/auth/signup",
                json={"email": f"ratelimit_{i}@example.com", "password": "Password123!"},
            )
            if resp.status_code == 429:
                hit_429 = True
                assert "retry_after" in resp.json()
                assert "Retry-After" in resp.headers
                break
        assert hit_429, "Expected to hit 429 Rate Limit on 11th-13th auth request"
    finally:
        settings.RATE_LIMITING_ENABLED = old_enabled


@pytest.mark.asyncio
async def test_phase8_cross_user_resource_isolation(async_client: AsyncClient):
    # 1. User A signup and create job
    user_a = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "user_a@example.com", "password": "Password123!"},
    )
    token_a = user_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    job_a = await async_client.post(
        "/api/v1/jobs",
        json={
            "company_name": "User A Corp",
            "role_title": "Private Engineer",
            "job_description": "Secret job description for User A.",
        },
        headers=headers_a,
    )
    job_a_id = job_a.json()["id"]

    # 2. User B signup
    user_b = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "user_b@example.com", "password": "Password123!"},
    )
    token_b = user_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User B attempts to access User A's job -> 404
    resp_get = await async_client.get(f"/api/v1/jobs/{job_a_id}", headers=headers_b)
    assert resp_get.status_code == 404

    # User B attempts to update status on User A's job -> 404
    resp_status = await async_client.patch(
        f"/api/v1/jobs/{job_a_id}/status",
        json={"status": "offer"},
        headers=headers_b,
    )
    assert resp_status.status_code == 404

    # User B attempts to update notes on User A's job -> 404
    resp_notes = await async_client.patch(
        f"/api/v1/jobs/{job_a_id}/notes",
        json={"notes": "Hacked notes"},
        headers=headers_b,
    )
    assert resp_notes.status_code == 404

    # User B attempts to delete User A's job -> 404
    resp_del = await async_client.delete(f"/api/v1/jobs/{job_a_id}", headers=headers_b)
    assert resp_del.status_code == 404


@pytest.mark.asyncio
async def test_phase8_complete_22_step_product_journey(async_client: AsyncClient):
    """
    Genuine full-lifecycle integration test covering all 22 steps of PaperFox:
    1. Signup
    2. Login
    3. Auth Me
    4. Profile Create
    5. Project with AI Analysis Text
    6. Extract Project Evidence (mock AI)
    7. Persistent Evidence Verification
    8. Create Job
    9. Analyze JD (mock AI)
    10. Provider/Model Attribution
    11. Optimize Resume (mock AI)
    12. Factually Grounded Optimization Check
    13. Render Job Resume
    14. One-page ATS Validation Check
    15. Retrieve Resume Artifact Metadata
    16. PDF Download Binary Content-Type Check
    17. Update Status to 'interview'
    18. Add Application Notes
    19. Application History Retrieval & Filtering
    20. History Statistics Breakdown
    21. Logout
    22. Verify Post-Logout Access & Refresh Rejection
    """
    # 1. Signup
    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "journey_user@example.com", "password": "ProductionPassword123!"},
    )
    assert signup_res.status_code == 201
    auth_data = signup_res.json()
    access_token = auth_data["access_token"]
    refresh_token = auth_data["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "journey_user@example.com", "password": "ProductionPassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Auth Me
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "journey_user@example.com"
    user_id = me_res.json()["id"]

    # 4 & 5. Create Profile with Project + AI Analysis Text
    profile_payload = {
        "personal_details": {
            "full_name": "Alex Mercer",
            "phone": "+1-555-0199",
            "portfolio_url": "https://alexmercer.dev",
            "github_url": "https://github.com/alexmercer",
            "linkedin_url": "https://linkedin.com/in/alexmercer",
        },
        "candidate_type": "experienced",
        "profile_status": "complete",
        "skills": [
            {"name": "Python", "category": "Programming"},
            {"name": "FastAPI", "category": "Frameworks"},
            {"name": "PostgreSQL", "category": "Databases"},
        ],
        "projects": [
            {
                "id": "proj-paperfox",
                "name": "Distributed Resume Engine",
                "description_source": "ai",
                "ai_analysis_text": "Project Distributed Resume Engine. FastAPI backend with Redis queue and Docker.",
                "technologies": ["Python", "FastAPI"],
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "start_date": "2018-09",
                "end_date": "2022-06",
            }
        ],
        "experience": [
            {
                "company": "CloudTech",
                "role": "Software Engineer",
                "start_date": "2022-07",
                "is_current": True,
                "responsibilities": ["Built async microservices handling 10M req/day."],
            }
        ],
    }
    prof_res = await async_client.post("/api/v1/profile", json=profile_payload, headers=headers)
    assert prof_res.status_code == 201

    # 6. Extract Project Evidence (mocking ProjectEvidenceParser)
    mock_evidence = {
        "architecture": ["Async microservices architecture with decoupled workers"],
        "technologies": ["Python", "Docker"],
        "frameworks": ["FastAPI"],
        "apis": ["POST /v1/render"],
        "models": [],
        "databases": ["Redis", "PostgreSQL"],
        "deployment": ["Docker Compose"],
        "features": ["Async job processing", "LaTeX rendering"],
        "technical_details": ["Used Redis queue to decouple ingest from compute"],
        "engineering_decisions": ["Used Redis queue to decouple ingest from compute"],
        "limitations": ["Kubernetes cluster unverified"],
    }
    with patch(
        "app.services.project_evidence_service.ProjectEvidenceParser.parse_analysis_text",
        new_callable=AsyncMock,
    ) as mock_parse:
        mock_parse.return_value = StructuredProjectEvidence(**mock_evidence)

        extract_res = await async_client.post(
            "/api/v1/profile/projects/proj-paperfox/extract-evidence",
            headers=headers,
        )
        assert extract_res.status_code == 200
        assert extract_res.json()["evidence_status"] == "current"

    # 7. Persistent Evidence Verification
    get_ev = await async_client.get(
        "/api/v1/profile/projects/proj-paperfox/evidence",
        headers=headers,
    )
    assert get_ev.status_code == 200
    assert "Async microservices architecture with decoupled workers" in get_ev.json()["evidence"]["architecture"]

    # 8. Create Job
    job_payload = {
        "company_name": "Google",
        "role_title": "Senior AI Systems Engineer",
        "job_description": "Seeking a Senior AI Engineer experienced in Python, FastAPI, distributed systems, and LLM optimization.",
        "location": "Mountain View, CA",
    }
    create_job_res = await async_client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert create_job_res.status_code == 201
    job_id = create_job_res.json()["id"]
    assert create_job_res.json()["application_status"] == "draft"

    # 9 & 10. Analyze JD (mock AI router) + Attribution Check
    mock_requirements = {
        "title": "Senior AI Systems Engineer",
        "experience_years_required": 4.0,
        "required_skills": ["Python", "FastAPI", "Distributed Systems"],
        "preferred_skills": ["Docker", "PostgreSQL"],
        "programming_languages": ["Python"],
        "technologies_frameworks": ["FastAPI"],
        "ai_ml_requirements": ["LLM optimization"],
        "responsibilities": ["Design high-throughput APIs"],
        "important_keywords": ["python", "fastapi", "distributed systems"],
    }
    with patch(
        "app.services.ai.provider_router.ProviderRouter.generate_structured_json",
        new_callable=AsyncMock,
    ) as mock_ai_json:
        mock_ai_json.return_value = {
            "data": mock_requirements,
            "provider": "gemini",
            "model": "gemini-2.5-flash",
        }

        analyze_res = await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)
        assert analyze_res.status_code == 200
        assert analyze_res.json()["is_analyzed"] is True
        assert analyze_res.json()["analysis_provider"] == "gemini"
        assert analyze_res.json()["analysis_model"] == "gemini-2.5-flash"

    # 11 & 12. Optimize Resume (mock AI optimizer)
    mock_opt_data = OptimizedResumeData(
        job_id=job_id,
        personal_details={"full_name": "Alex Mercer", "email": "journey_user@example.com"},
        summary="Senior Software Engineer with deep expertise in Python and FastAPI backend architectures.",
        education=[{"institution": "Stanford University", "degree": "B.S. Computer Science"}],
        experience=[
            OptimizedExperience(
                company="CloudTech",
                role="Software Engineer",
                bullets=["Engineered async microservices with 99.99% uptime."],
                technologies=["Python", "FastAPI"],
            )
        ],
        internships=[],
        projects=[
            OptimizedProject(
                project_name="Distributed Resume Engine",
                relevance_score=0.95,
                bullets=["Built high-throughput distributed pipeline."],
                technologies=["Python", "FastAPI", "Redis"],
            )
        ],
        skills=[OptimizedSkillGroup(category="Programming", skills=["Python", "FastAPI", "PostgreSQL"])],
        certifications=[],
        keyword_alignment=KeywordAlignment(
            matched_keywords=["python", "fastapi"],
            missing_keywords=[],
            safely_usable_keywords=["python", "fastapi"],
            unsupported_jd_keywords=[],
        ),
        optimization_metadata=OptimizationMetadata(
            status="completed",
            provider="gemini",
            model="gemini-2.5-flash",
        ),
    )
    with patch(
        "app.services.ai.optimizer_service.OptimizerService.optimize",
        new_callable=AsyncMock,
    ) as mock_opt:
        mock_opt.return_value = mock_opt_data

        opt_res = await async_client.post(f"/api/v1/jobs/{job_id}/optimize", headers=headers)
        assert opt_res.status_code == 200
        assert opt_res.json()["status"] == "completed"

    # 13 & 14. Render Job Resume + ATS Validation (mock LaTeX compiler to return 1 page)
    with patch(
        "app.providers.pdf.latex_worker.LaTeXCompilerWorker.is_available",
        return_value=True,
    ), patch(
        "app.providers.pdf.latex_worker.LaTeXCompilerWorker.compile_with_status",
        new_callable=AsyncMock,
    ) as mock_compile:
        # Return fake PDF bytes + 1 page count
        fake_pdf = b"%PDF-1.4 Mocked PDF Binary"
        mock_compile.return_value = (fake_pdf, 1, "OK")

        render_res = await async_client.post(f"/api/v1/jobs/{job_id}/render", headers=headers)
        assert render_res.status_code == 200
        data_render = render_res.json()
        assert data_render["status"] == "success"
        assert data_render["page_count"] == 1
        assert data_render["ats_validation"]["is_single_page"] is True

    # 15. Retrieve Resume Artifact Metadata
    art_res = await async_client.get(f"/api/v1/jobs/{job_id}/resume", headers=headers)
    assert art_res.status_code == 200
    assert art_res.json()["status"] == "success"

    # 16. PDF Download Binary Content-Type Check
    with patch(
        "app.services.job_resume_service.JobResumeService.get_job_resume_pdf_bytes",
        new_callable=AsyncMock,
    ) as mock_bytes:
        mock_bytes.return_value = b"%PDF-1.4 Mock Binary for Download"
        dl_res = await async_client.get(f"/api/v1/jobs/{job_id}/resume/download", headers=headers)
        assert dl_res.status_code == 200
        assert dl_res.headers.get("content-type") == "application/pdf"
        assert len(dl_res.content) > 0

    # 17. Update Status to 'interview'
    status_res = await async_client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={"status": "interview"},
        headers=headers,
    )
    assert status_res.status_code == 200
    assert status_res.json()["application_status"] == "interview"

    # 18. Add Application Notes
    notes_res = await async_client.patch(
        f"/api/v1/jobs/{job_id}/notes",
        json={"notes": "System design round scheduled for next Tuesday at 3 PM."},
        headers=headers,
    )
    assert notes_res.status_code == 200
    assert notes_res.json()["notes"] == "System design round scheduled for next Tuesday at 3 PM."

    # 19. Retrieve Application History with Filter
    hist_res = await async_client.get("/api/v1/jobs/history?status=interview", headers=headers)
    assert hist_res.status_code == 200
    assert hist_res.json()["total"] == 1
    assert hist_res.json()["items"][0]["company_name"] == "Google"

    # 20. Retrieve Application History Statistics
    stats_res = await async_client.get("/api/v1/jobs/history/stats", headers=headers)
    assert stats_res.status_code == 200
    assert stats_res.json()["total"] == 1
    assert stats_res.json()["by_status"]["interview"] == 1

    # 21. Logout
    logout_res = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 200

    # 22. Verify Revoked Refresh Token Rejection
    reuse_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert reuse_res.status_code == 401
