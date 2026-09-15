import pytest
from httpx import AsyncClient


async def get_auth_token(async_client: AsyncClient, email: str, password: str = "TestPassword123!"):
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password, "full_name": f"User {email}"}
    )
    res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_jobs_api_full_flow(async_client: AsyncClient, mock_mongo_db):
    token = await get_auth_token(async_client, "job_user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Job Application
    create_res = await async_client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company_name": "Anthropic",
            "role_title": "Full Stack Infrastructure Engineer",
            "job_description": "Build resilient cloud infrastructure and web dashboards using Python and React.",
            "location": "San Francisco, CA"
        }
    )
    assert create_res.status_code == 201
    job_data = create_res.json()
    job_id = job_data["id"]
    assert job_data["company_name"] == "Anthropic"
    assert job_data["is_analyzed"] is False

    # 2. List Job Applications
    list_res = await async_client.get("/api/v1/jobs", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    assert list_res.json()["items"][0]["id"] == job_id

    # 3. Get Job Application Detail
    get_res = await async_client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["role_title"] == "Full Stack Infrastructure Engineer"

    # 4. Delete Job Application
    del_res = await async_client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"]

    # 5. Get after delete -> 404
    get_after_del = await async_client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_after_del.status_code == 404


@pytest.mark.asyncio
async def test_jobs_api_ownership_isolation(async_client: AsyncClient, mock_mongo_db):
    token_user_a = await get_auth_token(async_client, "usera@example.com")
    token_user_b = await get_auth_token(async_client, "userb@example.com")

    headers_a = {"Authorization": f"Bearer {token_user_a}"}
    headers_b = {"Authorization": f"Bearer {token_user_b}"}

    # User A creates a job
    create_res = await async_client.post(
        "/api/v1/jobs",
        headers=headers_a,
        json={
            "company_name": "Stripe",
            "role_title": "Backend Engineer",
            "job_description": "Build high-reliability payment APIs in Ruby and Go."
        }
    )
    job_id_a = create_res.json()["id"]

    # User B tries to access User A's job -> 404
    get_res_b = await async_client.get(f"/api/v1/jobs/{job_id_a}", headers=headers_b)
    assert get_res_b.status_code == 404

    # User B tries to delete User A's job -> 404
    del_res_b = await async_client.delete(f"/api/v1/jobs/{job_id_a}", headers=headers_b)
    assert del_res_b.status_code == 404

    # User B list shows 0 jobs
    list_res_b = await async_client.get("/api/v1/jobs", headers=headers_b)
    assert list_res_b.json()["total"] == 0


@pytest.mark.asyncio
async def test_candidate_profile_immutability(async_client: AsyncClient, mock_mongo_db):
    token = await get_auth_token(async_client, "profile_owner@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create candidate profile
    profile_data = {
        "personal_details": {
            "full_name": "Pushkar Singh",
            "email": "profile_owner@example.com",
            "phone": "+1234567890"
        },
        "candidate_type": "experienced",
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Senior Engineer",
                "start_date": "2020-01",
                "is_current": True
            }
        ]
    }
    create_prof = await async_client.post("/api/v1/profile", headers=headers, json=profile_data)
    assert create_prof.status_code == 201

    # 2. Create and analyze a job application
    job_res = await async_client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company_name": "Meta",
            "role_title": "Production Engineer",
            "job_description": "Manage distributed systems and Python infrastructure."
        }
    )
    job_id = job_res.json()["id"]

    # 3. Retrieve candidate profile to ensure creating job did NOT alter profile
    get_prof = await async_client.get("/api/v1/profile", headers=headers)
    assert get_prof.status_code == 200
    assert get_prof.json()["personal_details"]["full_name"] == "Pushkar Singh"
    assert len(get_prof.json()["experience"]) == 1
