import pytest
from httpx import AsyncClient
from app.core.security import verify_password


@pytest.mark.asyncio
async def test_1_signup_success(async_client: AsyncClient, mock_mongo_db):
    response = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "candidate@example.com", "password": "SecurePassword123!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_2_duplicate_email_rejection(async_client: AsyncClient, mock_mongo_db):
    # First signup
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "duplicate@example.com", "password": "SecurePassword123!"},
    )
    # Duplicate signup with same email (case insensitive)
    response = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "DUPLICATE@example.com", "password": "AnotherPassword123!"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_3_password_hashing(async_client: AsyncClient, mock_mongo_db):
    raw_password = "MySecretPassword123"
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "hashcheck@example.com", "password": raw_password},
    )
    user_doc = await mock_mongo_db["users"].find_one({"email": "hashcheck@example.com"})
    assert user_doc is not None
    assert user_doc["password_hash"] != raw_password
    assert verify_password(raw_password, user_doc["password_hash"]) is True


@pytest.mark.asyncio
async def test_4_login_success(async_client: AsyncClient, mock_mongo_db):
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "loginuser@example.com", "password": "Password123!"},
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "loginuser@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_5_invalid_credentials(async_client: AsyncClient, mock_mongo_db):
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "wrongpass@example.com", "password": "Password123!"},
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_6_protected_endpoint_without_token(async_client: AsyncClient):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_7_protected_endpoint_with_invalid_token(async_client: AsyncClient):
    headers = {"Authorization": "Bearer invalid_garbage_token_str"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_8_protected_endpoint_with_valid_token(async_client: AsyncClient, mock_mongo_db):
    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "validuser@example.com", "password": "Password123!"},
    )
    access_token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "validuser@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_9_refresh_token_success(async_client: AsyncClient, mock_mongo_db):
    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "refreshuser@example.com", "password": "Password123!"},
    )
    refresh_token = signup_res.json()["refresh_token"]

    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_10_invalid_expired_refresh_token(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "bogus_refresh_token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_11_logout(async_client: AsyncClient, mock_mongo_db):
    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "logoutuser@example.com", "password": "Password123!"},
    )
    refresh_token = signup_res.json()["refresh_token"]

    response = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "logged out" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_12_refresh_token_cannot_be_reused_after_logout(
    async_client: AsyncClient, mock_mongo_db
):
    signup_res = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "reusecheck@example.com", "password": "Password123!"},
    )
    refresh_token = signup_res.json()["refresh_token"]

    # Logout to revoke token
    await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )

    # Attempt to refresh using revoked token
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 401
