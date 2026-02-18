"""Test fixtures for authorization and security testing."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.main import app
from src.database import get_session
from src.models.user import User
from src.models.task import Task


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# Create test session maker
test_async_session_maker = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_test_session():
    """Override database session for testing."""
    async with test_async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with test database."""
    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def alice_credentials():
    """Alice's test credentials."""
    return {
        "email": "alice@example.com",
        "password": "alicepassword123"
    }


@pytest.fixture
def bob_credentials():
    """Bob's test credentials."""
    return {
        "email": "bob@example.com",
        "password": "bobpassword456"
    }


@pytest.fixture
def alice_user(client, alice_credentials):
    """Register Alice and return user data with token."""
    response = client.post("/auth/register", json=alice_credentials)
    assert response.status_code == 201
    data = response.json()
    return {
        "user_id": data["user"]["id"],
        "email": data["user"]["email"],
        "token": data["access_token"],
        "credentials": alice_credentials
    }


@pytest.fixture
def bob_user(client, bob_credentials):
    """Register Bob and return user data with token."""
    response = client.post("/auth/register", json=bob_credentials)
    assert response.status_code == 201
    data = response.json()
    return {
        "user_id": data["user"]["id"],
        "email": data["user"]["email"],
        "token": data["access_token"],
        "credentials": bob_credentials
    }


@pytest.fixture
def alice_task(client, alice_user):
    """Create a task for Alice and return task data."""
    headers = {"Authorization": f"Bearer {alice_user['token']}"}
    task_data = {
        "title": "Alice's private task",
        "description": "Only Alice should see this"
    }
    response = client.post("/tasks", json=task_data, headers=headers)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def bob_task(client, bob_user):
    """Create a task for Bob and return task data."""
    headers = {"Authorization": f"Bearer {bob_user['token']}"}
    task_data = {
        "title": "Bob's private task",
        "description": "Only Bob should see this"
    }
    response = client.post("/tasks", json=task_data, headers=headers)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def multi_user_scenario(client, alice_user, bob_user, alice_task, bob_task):
    """Complete multi-user scenario with two users and their tasks."""
    return {
        "alice": alice_user,
        "bob": bob_user,
        "alice_task": alice_task,
        "bob_task": bob_task,
        "client": client
    }
