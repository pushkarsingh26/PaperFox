import pytest
from httpx import AsyncClient


async def get_auth_headers(async_client: AsyncClient, email: str = "user@example.com") -> dict:
    res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "SecurePassword123!"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_1_create_profile(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "create_prof@example.com")
    payload = {
        "personal_details": {
            "full_name": "Jane Doe",
            "phone": "+1234567890",
            "portfolio_url": "https://janedoe.dev",
            "linkedin_url": "https://linkedin.com/in/janedoe",
            "github_url": "https://github.com/janedoe",
        },
        "candidate_type": "fresher",
        "profile_status": "draft",
        "education": [
            {
                "institution": "Tech University",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "start_date": "2020-09",
                "end_date": "2024-05",
            }
        ],
    }
    response = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["personal_details"]["full_name"] == "Jane Doe"
    assert data["completion_percentage"] > 0
    assert data["profile_status"] == "draft"


@pytest.mark.asyncio
async def test_2_get_own_profile(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "get_prof@example.com")
    # Post profile
    await async_client.post(
        "/api/v1/profile",
        json={
            "personal_details": {"full_name": "John Smith"},
            "candidate_type": "fresher",
        },
        headers=headers,
    )
    # Get profile
    res = await async_client.get("/api/v1/profile", headers=headers)
    assert res.status_code == 200
    assert res.json()["personal_details"]["full_name"] == "John Smith"


@pytest.mark.asyncio
async def test_3_update_profile(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "update_prof@example.com")
    await async_client.post(
        "/api/v1/profile",
        json={
            "personal_details": {"full_name": "Initial Name"},
            "candidate_type": "fresher",
        },
        headers=headers,
    )
    update_res = await async_client.put(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "Updated Name"}},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["personal_details"]["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_4_delete_profile(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "del_prof@example.com")
    await async_client.post(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "To Delete"}},
        headers=headers,
    )
    del_res = await async_client.delete("/api/v1/profile", headers=headers)
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"].lower()

    # Verify subsequent GET returns 404
    get_res = await async_client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_5_unauthorized_access(async_client: AsyncClient):
    res = await async_client.get("/api/v1/profile")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_6_cross_user_ownership_isolation(async_client: AsyncClient, mock_mongo_db):
    headers_a = await get_auth_headers(async_client, "usera@example.com")
    headers_b = await get_auth_headers(async_client, "userb@example.com")

    await async_client.post(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "User A Profile"}},
        headers=headers_a,
    )

    # User B fetching profile before creating one gets 404
    res_b = await async_client.get("/api/v1/profile", headers=headers_b)
    assert res_b.status_code == 404

    # User B creates own profile
    await async_client.post(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "User B Profile"}},
        headers=headers_b,
    )

    # Fetch User B profile -> gets User B data
    res_b2 = await async_client.get("/api/v1/profile", headers=headers_b)
    assert res_b2.json()["personal_details"]["full_name"] == "User B Profile"


@pytest.mark.asyncio
async def test_7_fresher_without_internship_completion(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "fresher_no_int@example.com")
    payload = {
        "personal_details": {"full_name": "Fresher Candidate"},
        "candidate_type": "fresher",
        "internships": [],
        "education": [
            {
                "institution": "University A",
                "degree": "B.Tech",
                "field_of_study": "CS",
                "start_date": "2020",
            }
        ],
        "projects": [
            {"name": "Proj 1", "description": "Desc 1", "technologies": ["Python"]}
        ],
        "skills": [{"name": "Python", "category": "Programming"}],
        "certifications": [
            {"name": "Cert 1", "issuer": "AWS", "issue_date": "2023"}
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 201
    assert res.json()["completion_percentage"] == 100


@pytest.mark.asyncio
async def test_8_fresher_with_internship(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "fresher_with_int@example.com")
    payload = {
        "personal_details": {"full_name": "Fresher Intern"},
        "candidate_type": "fresher",
        "internships": [
            {
                "company": "Company X",
                "role": "Software Intern",
                "start_date": "2023-05",
                "end_date": "2023-08",
            }
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 201
    assert res.json()["completion_percentage"] > 0


@pytest.mark.asyncio
async def test_9_experienced_candidate(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "experienced@example.com")
    payload = {
        "personal_details": {"full_name": "Senior Eng"},
        "candidate_type": "experienced",
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Senior Engineer",
                "start_date": "2020-01",
                "is_current": True,
            }
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 201
    assert res.json()["completion_percentage"] > 0


@pytest.mark.asyncio
async def test_10_multiple_projects_repository_url(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "projects@example.com")
    payload = {
        "personal_details": {"full_name": "Project Lead"},
        "candidate_type": "fresher",
        "projects": [
            {
                "name": "PaperFox",
                "description": "Resume Platform",
                "technologies": ["FastAPI", "Next.js"],
                "repository_url": "https://github.com/myorg/paperfox",
                "github_url": "https://github.com/myorg/paperfox-public",
            },
            {
                "name": "Project Two",
                "description": "Analytics tool",
                "technologies": ["Python"],
            },
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 201
    projects = res.json()["projects"]
    assert len(projects) == 2
    assert projects[0]["repository_url"] == "https://github.com/myorg/paperfox"


@pytest.mark.asyncio
async def test_11_multiple_education_entries(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "edu@example.com")
    payload = {
        "personal_details": {"full_name": "Dual Graduate"},
        "candidate_type": "fresher",
        "education": [
            {
                "institution": "Univ 1",
                "degree": "B.S.",
                "field_of_study": "CS",
                "start_date": "2016",
                "end_date": "2020",
            },
            {
                "institution": "Univ 2",
                "degree": "M.S.",
                "field_of_study": "AI",
                "start_date": "2020",
                "end_date": "2022",
            },
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 201
    assert len(res.json()["education"]) == 2


@pytest.mark.asyncio
async def test_12_skill_duplicate_prevention(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "dupskill@example.com")
    payload = {
        "personal_details": {"full_name": "Skill Master"},
        "skills": [
            {"name": "Python", "category": "Programming"},
            {"name": "python", "category": "Programming"},
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 422
    assert "duplicate skill" in str(res.json()).lower()


@pytest.mark.asyncio
async def test_13_url_validation(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "badurl@example.com")
    payload = {
        "personal_details": {
            "full_name": "Invalid URL candidate",
            "portfolio_url": "not-a-valid-url-scheme",
        }
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_14_date_validation(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "baddate@example.com")
    payload = {
        "personal_details": {"full_name": "Bad Date Candidate"},
        "candidate_type": "experienced",
        "experience": [
            {
                "company": "Corp",
                "role": "Eng",
                "start_date": "2023-05",
                "end_date": "2020-01",  # End before start
                "is_current": False,
            }
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_15_completion_percentage_accuracy(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "score@example.com")
    payload = {
        "personal_details": {"full_name": "Partial Profile"},
        "candidate_type": "fresher",
        "education": [
            {
                "institution": "MIT",
                "degree": "B.S.",
                "field_of_study": "CS",
                "start_date": "2020",
            }
        ],
    }
    res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert res.status_code == 201
    percentage = res.json()["completion_percentage"]
    assert 40 <= percentage <= 65


@pytest.mark.asyncio
async def test_16_profile_status_transition(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "status@example.com")
    # Draft initial
    res1 = await async_client.post(
        "/api/v1/profile",
        json={
            "personal_details": {"full_name": "Status User"},
            "profile_status": "draft",
        },
        headers=headers,
    )
    assert res1.json()["profile_status"] == "draft"

    # Save & Complete transition
    res2 = await async_client.put(
        "/api/v1/profile",
        json={"profile_status": "complete"},
        headers=headers,
    )
    assert res2.json()["profile_status"] == "complete"


@pytest.mark.asyncio
async def test_17_persistence_after_update(async_client: AsyncClient, mock_mongo_db):
    headers = await get_auth_headers(async_client, "persist@example.com")
    await async_client.post(
        "/api/v1/profile",
        json={
            "personal_details": {"full_name": "Original Name", "phone": "111-222-3333"},
            "candidate_type": "fresher",
        },
        headers=headers,
    )

    # Partial update
    await async_client.put(
        "/api/v1/profile",
        json={"personal_details": {"full_name": "Persisted Updated Name"}},
        headers=headers,
    )

    # Re-fetch profile
    fetch_res = await async_client.get("/api/v1/profile", headers=headers)
    assert fetch_res.status_code == 200
    assert fetch_res.json()["personal_details"]["full_name"] == "Persisted Updated Name"
