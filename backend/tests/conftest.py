import asyncio
from typing import AsyncGenerator
# pyrefly: ignore [missing-import]
import mongomock_motor
import pytest
# pyrefly: ignore [missing-import]
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.core.database import db_instance
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


from app.core.middleware import reset_rate_limiters


@pytest_asyncio.fixture(autouse=True)
async def mock_mongo_db():
    reset_rate_limiters()
    client = mongomock_motor.AsyncMongoMockClient()
    db = client["paperfox_test_db"]
    
    db_instance.client = client
    db_instance.db = db
    
    # Create indexes in test DB
    await db["users"].create_index("email", unique=True)
    await db["sessions"].create_index("token_hash", unique=True)

    yield db

    # Cleanup collections after each test
    await db["users"].delete_many({})
    await db["sessions"].delete_many({})
    await db["candidate_profiles"].delete_many({})
    await db["job_applications"].delete_many({})
    reset_rate_limiters()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
