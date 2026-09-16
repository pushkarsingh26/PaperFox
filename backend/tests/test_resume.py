from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import AsyncClient
from app.resume.escaping import escape_latex, format_latex_url
from app.resume.transformer import transform_profile_to_resume_data


async def get_auth_headers(async_client: AsyncClient, email: str = "res_user@example.com") -> dict:
    res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "SecurePassword123!"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_1_latex_escaping():
    raw_text = "R&D % 100$ #1 _test_ {foo} ~ ^ \\"
    escaped = escape_latex(raw_text)
    assert r"\&" in escaped
    assert r"\%" in escaped
    assert r"\$" in escaped
    assert r"\#" in escaped
    assert r"\_" in escaped
    assert r"\{" in escaped
    assert r"\}" in escaped
    assert r"\textasciitilde{}" in escaped
    assert r"\textasciicircum{}" in escaped
    assert r"\textbackslash{}" in escaped


def test_2_latex_url_formatting():
    url = "https://github.com/myuser/project_name"
    formatted = format_latex_url(url, "GitHub Repo")
    assert r"\href{https://github.com/myuser/project_name}{GitHub Repo}" == formatted


def test_3_transformer():
    profile_dict = {
        "personal_details": {"full_name": "Alice Smith", "phone": "123-456-7890"},
        "candidate_type": "fresher",
        "education": [{"institution": "MIT", "degree": "B.S."}],
        "projects": [{"name": "PaperFox", "repository_url": "https://repo.com"}],
        "skills": [{"name": "Python", "category": "Programming"}],
    }
    user_email = "alice@example.com"
    data = transform_profile_to_resume_data(profile_dict, user_email)

    assert data["header"]["full_name"] == "Alice Smith"
    assert data["header"]["email"] == "alice@example.com"
    assert len(data["education"]) == 1
    assert len(data["projects"]) == 1
    assert data["projects"][0]["repository_url"] == "https://repo.com"


@pytest.mark.asyncio
async def test_4_generate_resume_missing_profile(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "noprofile@example.com")
    res = await async_client.post("/api/v1/resume/generate", headers=headers)
    assert res.status_code == 400
    assert "not found" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_5_compiler_unavailable_status(async_client: AsyncClient, mock_mongo_db, monkeypatch):
    headers = await get_auth_headers(async_client, "no_compiler@example.com")

    # Create profile
    await async_client.post(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "Bob Vance"}, "candidate_type": "fresher"},
        headers=headers,
    )

    # Force compiler worker to return unavailable
    from app.providers.pdf.latex_worker import LaTeXCompilerWorker
    monkeypatch.setattr(
        LaTeXCompilerWorker,
        "compile_with_status",
        AsyncMock(return_value=(None, 0, "COMPILER_UNAVAILABLE: pdflatex not found")),
    )

    res = await async_client.post("/api/v1/resume/generate", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "compiler_unavailable"
    assert data["pdf_storage_reference"] is None
    assert "pdflatex or xelatex" in data["message"]


@pytest.mark.asyncio
async def test_6_successful_mocked_compilation_and_immutability(
    async_client: AsyncClient, mock_mongo_db, monkeypatch
):
    headers = await get_auth_headers(async_client, "mock_success@example.com")

    # 1. Create candidate profile
    profile_payload = {
        "personal_details": {
            "full_name": "Charlie Day",
            "portfolio_url": "https://charlie.dev",
        },
        "candidate_type": "experienced",
        "experience": [
            {
                "company": "Paddy's",
                "role": "Janitor",
                "start_date": "2018-01",
                "is_current": True,
            }
        ],
        "education": [
            {"institution": "Philly High", "degree": "Diploma", "field_of_study": "General", "start_date": "2010"}
        ],
    }
    await async_client.post("/api/v1/profile", json=profile_payload, headers=headers)

    # Fetch initial profile snapshot to verify immutability
    initial_profile = (await async_client.get("/api/v1/profile", headers=headers)).json()

    # Mock compiler worker to simulate successful 1-page PDF generation
    fake_pdf = b"%PDF-1.4 Mock PDF Content"
    from app.providers.pdf.latex_worker import LaTeXCompilerWorker

    monkeypatch.setattr(
        LaTeXCompilerWorker,
        "compile_with_status",
        AsyncMock(return_value=(fake_pdf, 1, "success")),
    )

    # 2. Trigger generation
    gen_res = await async_client.post("/api/v1/resume/generate", headers=headers)
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert gen_data["status"] == "success"
    assert gen_data["page_count"] == 1
    assert gen_data["pdf_storage_reference"].startswith("storage://")

    # 3. Verify Candidate Profile was NOT mutated
    post_gen_profile = (await async_client.get("/api/v1/profile", headers=headers)).json()
    assert initial_profile == post_gen_profile

    # 4. Fetch Base Artifact Metadata
    meta_res = await async_client.get("/api/v1/resume/base", headers=headers)
    assert meta_res.status_code == 200
    assert meta_res.json()["status"] == "success"

    # 5. Fetch PDF Binary
    pdf_res = await async_client.get("/api/v1/resume/base/pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content == fake_pdf


@pytest.mark.asyncio
async def test_7_overflow_mocked_compilation(
    async_client: AsyncClient, mock_mongo_db, monkeypatch
):
    headers = await get_auth_headers(async_client, "overflow@example.com")
    await async_client.post(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "Multi Page User"}, "candidate_type": "fresher"},
        headers=headers,
    )

    fake_pdf = b"%PDF-1.4 Multi-page PDF"
    from app.providers.pdf.latex_worker import LaTeXCompilerWorker

    monkeypatch.setattr(
        LaTeXCompilerWorker,
        "compile_with_status",
        AsyncMock(return_value=(fake_pdf, 2, "success")),
    )

    gen_res = await async_client.post("/api/v1/resume/generate", headers=headers)
    assert gen_res.status_code == 200
    assert gen_res.json()["status"] == "overflow"
    assert gen_res.json()["page_count"] == 2


@pytest.mark.asyncio
async def test_8_cross_user_resume_isolation(async_client: AsyncClient, mock_mongo_db, monkeypatch):
    headers_a = await get_auth_headers(async_client, "res_a@example.com")
    headers_b = await get_auth_headers(async_client, "res_b@example.com")

    # User A creates profile and generates resume
    await async_client.post(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "User A"}, "candidate_type": "fresher"},
        headers=headers_a,
    )
    fake_pdf = b"%PDF-1.4 User A PDF"
    from app.providers.pdf.latex_worker import LaTeXCompilerWorker

    monkeypatch.setattr(
        LaTeXCompilerWorker,
        "compile_with_status",
        AsyncMock(return_value=(fake_pdf, 1, "success")),
    )

    await async_client.post("/api/v1/resume/generate", headers=headers_a)

    # User B attempting to fetch User A's resume gets 404
    meta_b = await async_client.get("/api/v1/resume/base", headers=headers_b)
    assert meta_b.status_code == 404

    pdf_b = await async_client.get("/api/v1/resume/base/pdf", headers=headers_b)
    assert pdf_b.status_code == 404


def test_9_latex_compiler_worker_resolution():
    from app.providers.pdf.latex_worker import LaTeXCompilerWorker
    # Test worker initialization with default/configured setting
    worker = LaTeXCompilerWorker()
    assert hasattr(worker, "compiler")
    assert isinstance(worker.is_available(), bool)

    # Test explicit compiler resolution
    worker_custom = LaTeXCompilerWorker(compiler_binary="non_existent_compiler_xyz")
    assert worker_custom.compiler is None or worker_custom.is_available() is False

