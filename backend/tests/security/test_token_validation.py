"""Security tests for JWT token validation."""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from src.config import settings


class TestMissingAuthentication:
    """Test that missing authentication is properly rejected."""

    def test_missing_authorization_header(self, client):
        """Test that requests without Authorization header are rejected (T025)."""
        # Attempt to access protected endpoint without token
        response = client.get("/tasks")

        # Should return 403 Forbidden (FastAPI HTTPBearer default)
        assert response.status_code == 403
        assert "detail" in response.json()


class TestExpiredToken:
    """Test that expired tokens are rejected."""

    def test_expired_token_rejection(self, client, alice_credentials):
        """Test that expired tokens are rejected with specific error (T026)."""
        # Register user first
        register_response = client.post("/auth/register", json=alice_credentials)
        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]

        # Create an expired token (expired 1 hour ago)
        expired_payload = {
            "sub": user_id,
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        # Attempt to use expired token
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/tasks", headers=headers)

        # Should return 401 Unauthorized with specific message
        assert response.status_code == 401
        assert "Token has expired" in response.json()["detail"]

    def test_expired_token_on_task_access(self, client, alice_user, alice_task):
        """Test that expired tokens are rejected on specific task access."""
        alice = alice_user
        task = alice_task

        # Create an expired token for Alice
        expired_payload = {
            "sub": alice["user_id"],
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        # Attempt to access task with expired token
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get(f"/tasks/{task['id']}", headers=headers)

        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert "Token has expired" in response.json()["detail"]


class TestTamperedToken:
    """Test that tampered tokens are rejected."""

    def test_tampered_payload_rejection(self, client, alice_user, bob_user):
        """Test that tokens with tampered payload are rejected (T027)."""
        alice = alice_user
        bob = bob_user

        # Decode Alice's token to get payload
        alice_payload = jwt.decode(
            alice["token"],
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Tamper with payload: change user_id to Bob's
        tampered_payload = alice_payload.copy()
        tampered_payload["sub"] = bob["user_id"]

        # Re-encode with correct secret (simulating payload tampering)
        # Note: This will fail signature verification because we're changing the payload
        # We need to encode WITHOUT the secret to simulate tampering
        tampered_token = jwt.encode(
            tampered_payload,
            "wrong_secret",  # Use wrong secret to simulate tampering
            algorithm=settings.JWT_ALGORITHM
        )

        # Attempt to use tampered token
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = client.get("/tasks", headers=headers)

        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert response.json()["detail"] in ["Invalid token", "Could not validate credentials"]

    def test_malformed_token_rejection(self, client):
        """Test that malformed tokens are rejected."""
        # Use a completely invalid token format
        headers = {"Authorization": "Bearer not.a.valid.jwt.token.format"}
        response = client.get("/tasks", headers=headers)

        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert "detail" in response.json()


class TestInvalidSignature:
    """Test that tokens with invalid signatures are rejected."""

    def test_invalid_signature_rejection(self, client, alice_credentials):
        """Test that tokens signed with wrong secret are rejected (T028)."""
        # Register user first
        register_response = client.post("/auth/register", json=alice_credentials)
        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]

        # Create token with WRONG secret
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        invalid_token = jwt.encode(
            payload,
            "wrong_secret_key_12345",  # Wrong secret
            algorithm=settings.JWT_ALGORITHM
        )

        # Attempt to use token with invalid signature
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = client.get("/tasks", headers=headers)

        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_token_with_different_algorithm(self, client, alice_credentials):
        """Test that tokens signed with different algorithm are rejected."""
        # Register user first
        register_response = client.post("/auth/register", json=alice_credentials)
        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]

        # Create token with different algorithm (HS512 instead of HS256)
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        invalid_token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm="HS512"  # Different algorithm
        )

        # Attempt to use token with wrong algorithm
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = client.get("/tasks", headers=headers)

        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert "detail" in response.json()


class TestValidToken:
    """Test that valid tokens are accepted."""

    def test_valid_token_acceptance(self, client, alice_user):
        """Test that valid tokens grant access to protected endpoints (T029)."""
        alice = alice_user

        # Use valid token to access protected endpoint
        headers = {"Authorization": f"Bearer {alice['token']}"}
        response = client.get("/tasks", headers=headers)

        # Should return 200 OK
        assert response.status_code == 200
        assert "tasks" in response.json()
        assert "total" in response.json()

    def test_valid_token_on_all_operations(self, client, alice_user):
        """Test that valid tokens work for all CRUD operations."""
        alice = alice_user
        headers = {"Authorization": f"Bearer {alice['token']}"}

        # CREATE - should succeed
        create_response = client.post(
            "/tasks",
            json={"title": "Test task", "description": "Test description"},
            headers=headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # READ - should succeed
        read_response = client.get(f"/tasks/{task_id}", headers=headers)
        assert read_response.status_code == 200
        assert read_response.json()["id"] == task_id

        # UPDATE - should succeed
        update_response = client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated task", "is_completed": True},
            headers=headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated task"

        # DELETE - should succeed
        delete_response = client.delete(f"/tasks/{task_id}", headers=headers)
        assert delete_response.status_code == 204

    def test_token_user_extraction(self, client, alice_user, bob_user):
        """Test that tokens correctly identify different users."""
        alice = alice_user
        bob = bob_user

        # Alice creates a task
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        alice_task_response = client.post(
            "/tasks",
            json={"title": "Alice's task"},
            headers=alice_headers
        )
        assert alice_task_response.status_code == 201
        alice_task_id = alice_task_response.json()["id"]

        # Bob creates a task
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}
        bob_task_response = client.post(
            "/tasks",
            json={"title": "Bob's task"},
            headers=bob_headers
        )
        assert bob_task_response.status_code == 201
        bob_task_id = bob_task_response.json()["id"]

        # Verify Alice sees only her task
        alice_list = client.get("/tasks", headers=alice_headers)
        alice_task_ids = [task["id"] for task in alice_list.json()["tasks"]]
        assert alice_task_id in alice_task_ids
        assert bob_task_id not in alice_task_ids

        # Verify Bob sees only his task
        bob_list = client.get("/tasks", headers=bob_headers)
        bob_task_ids = [task["id"] for task in bob_list.json()["tasks"]]
        assert bob_task_id in bob_task_ids
        assert alice_task_id not in bob_task_ids
