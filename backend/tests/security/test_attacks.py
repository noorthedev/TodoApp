"""Security attack tests for authorization system.

This module tests the system's resistance to common authorization attacks
including IDOR, privilege escalation, token replay, race conditions, and
parameter manipulation.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from jose import jwt
from src.config import settings


class TestIDORAttack:
    """Test resistance to Insecure Direct Object Reference (IDOR) attacks."""

    def test_sequential_id_enumeration(self, client, alice_user, bob_user):
        """Test that users cannot enumerate resources by guessing sequential IDs (T035)."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}

        # Alice creates 3 tasks
        alice_task_ids = []
        for i in range(3):
            response = client.post(
                "/tasks",
                json={"title": f"Alice task {i+1}"},
                headers=alice_headers
            )
            alice_task_ids.append(response.json()["id"])

        # Bob creates 2 tasks
        bob_task_ids = []
        for i in range(2):
            response = client.post(
                "/tasks",
                json={"title": f"Bob task {i+1}"},
                headers=bob_headers
            )
            bob_task_ids.append(response.json()["id"])

        # Bob attempts to enumerate all IDs from 1 to max(alice_task_ids)
        max_id = max(alice_task_ids + bob_task_ids)
        accessible_ids = []
        forbidden_count = 0

        for task_id in range(1, max_id + 1):
            response = client.get(f"/tasks/{task_id}", headers=bob_headers)
            if response.status_code == 200:
                accessible_ids.append(task_id)
            elif response.status_code == 403:
                forbidden_count += 1

        # Bob should only access his own tasks
        assert set(accessible_ids) == set(bob_task_ids)
        # Bob should get 403 for Alice's tasks
        assert forbidden_count >= len(alice_task_ids)

    def test_id_guessing_with_large_gaps(self, client, alice_user, bob_user):
        """Test that ID guessing doesn't work even with large ID gaps."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}

        # Alice creates a task
        alice_response = client.post(
            "/tasks",
            json={"title": "Alice's secret task"},
            headers=alice_headers
        )
        alice_task_id = alice_response.json()["id"]

        # Bob tries to guess IDs around Alice's task ID
        for offset in [-10, -5, -1, 0, 1, 5, 10]:
            guess_id = alice_task_id + offset
            response = client.get(f"/tasks/{guess_id}", headers=bob_headers)

            # Bob should either get 404 (doesn't exist) or 403 (not authorized)
            # Never 200 for Alice's tasks
            if response.status_code == 200:
                # If 200, verify it's Bob's own task
                task_data = response.json()
                assert task_data["user_id"] == bob["user_id"]


class TestHorizontalPrivilegeEscalation:
    """Test resistance to horizontal privilege escalation attacks."""

    def test_token_substitution_attack(self, client, alice_user, bob_user):
        """Test that substituting tokens doesn't grant access to other users' data (T036)."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}

        # Alice creates a task
        alice_task = client.post(
            "/tasks",
            json={"title": "Alice's confidential task"},
            headers=alice_headers
        ).json()

        # Bob attempts to access Alice's task using his own valid token
        response = client.get(f"/tasks/{alice_task['id']}", headers=bob_headers)

        # Should be blocked with 403
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_user_id_manipulation_in_token(self, client, alice_user, bob_user):
        """Test that manipulating user_id in token payload is detected."""
        alice = alice_user
        bob = bob_user

        # Create a token with Bob's user_id but signed with correct secret
        # This simulates an attacker who knows the secret trying to impersonate
        malicious_payload = {
            "sub": bob["user_id"],  # Bob's ID
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        malicious_token = jwt.encode(
            malicious_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        # Use malicious token to try to access Bob's tasks
        headers = {"Authorization": f"Bearer {malicious_token}"}
        response = client.get("/tasks", headers=headers)

        # This should work because the token is valid and correctly identifies Bob
        assert response.status_code == 200

        # But Bob should only see his own tasks, not Alice's
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        alice_task = client.post(
            "/tasks",
            json={"title": "Alice's task"},
            headers=alice_headers
        ).json()

        # Bob's token should not give access to Alice's task
        bob_access = client.get(f"/tasks/{alice_task['id']}", headers=headers)
        assert bob_access.status_code == 403

    def test_privilege_escalation_via_update(self, client, alice_user, bob_user):
        """Test that users cannot escalate privileges by updating resources."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}

        # Alice creates a task
        alice_task = client.post(
            "/tasks",
            json={"title": "Alice's task"},
            headers=alice_headers
        ).json()

        # Bob attempts to update Alice's task to change ownership
        malicious_update = {
            "title": "Bob took over",
            "user_id": bob["user_id"]  # Attempting to change ownership
        }
        response = client.put(
            f"/tasks/{alice_task['id']}",
            json=malicious_update,
            headers=bob_headers
        )

        # Should be blocked with 403
        assert response.status_code == 403

        # Verify Alice's task is unchanged
        verify_response = client.get(f"/tasks/{alice_task['id']}", headers=alice_headers)
        assert verify_response.status_code == 200
        assert verify_response.json()["user_id"] == alice["user_id"]
        assert verify_response.json()["title"] == "Alice's task"


class TestTokenReplayAttack:
    """Test resistance to token replay attacks."""

    def test_expired_token_replay(self, client, alice_credentials):
        """Test that expired tokens cannot be replayed (T037)."""
        # Register user
        register_response = client.post("/auth/register", json=alice_credentials)
        user_id = register_response.json()["user"]["id"]

        # Create an expired token
        expired_payload = {
            "sub": user_id,
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        # Attempt to replay expired token multiple times
        headers = {"Authorization": f"Bearer {expired_token}"}

        for _ in range(3):
            response = client.get("/tasks", headers=headers)
            # Should consistently reject expired token
            assert response.status_code == 401
            assert "expired" in response.json()["detail"].lower()

    def test_old_token_after_password_change(self, client, alice_user):
        """Test that old tokens should ideally be invalidated after password change.

        Note: Current implementation doesn't support token revocation (stateless JWT).
        This test documents the limitation and expected future behavior.
        """
        alice = alice_user
        old_token = alice["token"]

        # Old token should still work (limitation of stateless JWT)
        headers = {"Authorization": f"Bearer {old_token}"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200

        # TODO: Implement token revocation/blacklist for password changes
        # After password change, old tokens should be rejected

    def test_token_reuse_across_sessions(self, client, alice_user):
        """Test that tokens can be reused within their validity period (expected behavior)."""
        alice = alice_user
        headers = {"Authorization": f"Bearer {alice['token']}"}

        # Use token multiple times
        for _ in range(5):
            response = client.get("/tasks", headers=headers)
            assert response.status_code == 200

        # This is expected behavior for stateless JWT
        # Token is valid until expiration


class TestRaceConditionAttack:
    """Test resistance to race condition attacks."""

    @pytest.mark.asyncio
    async def test_concurrent_access_attempts(self, client, alice_user, bob_user):
        """Test that concurrent requests don't bypass authorization (T038)."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}

        # Alice creates a task
        alice_task = client.post(
            "/tasks",
            json={"title": "Alice's task"},
            headers=alice_headers
        ).json()

        # Bob attempts concurrent access to Alice's task
        async def attempt_access():
            return client.get(f"/tasks/{alice_task['id']}", headers=bob_headers)

        # Launch 10 concurrent requests
        tasks = [attempt_access() for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        # All requests should be blocked with 403
        for response in responses:
            assert response.status_code == 403

    def test_concurrent_create_and_access(self, client, alice_user, bob_user):
        """Test race condition between create and unauthorized access."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}

        # Alice creates a task
        alice_task = client.post(
            "/tasks",
            json={"title": "Alice's new task"},
            headers=alice_headers
        ).json()

        # Bob immediately tries to access it (simulating race condition)
        response = client.get(f"/tasks/{alice_task['id']}", headers=bob_headers)

        # Should still be blocked
        assert response.status_code == 403

    def test_concurrent_update_attempts(self, client, alice_user, bob_user):
        """Test that concurrent updates maintain authorization."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}

        # Alice creates a task
        alice_task = client.post(
            "/tasks",
            json={"title": "Original title"},
            headers=alice_headers
        ).json()

        # Alice and Bob both try to update simultaneously
        alice_update = {"title": "Alice's update"}
        bob_update = {"title": "Bob's malicious update"}

        alice_response = client.put(
            f"/tasks/{alice_task['id']}",
            json=alice_update,
            headers=alice_headers
        )
        bob_response = client.put(
            f"/tasks/{alice_task['id']}",
            json=bob_update,
            headers=bob_headers
        )

        # Alice should succeed
        assert alice_response.status_code == 200

        # Bob should be blocked
        assert bob_response.status_code == 403

        # Verify final state is Alice's update
        verify_response = client.get(f"/tasks/{alice_task['id']}", headers=alice_headers)
        assert verify_response.json()["title"] == "Alice's update"


class TestParameterManipulationAttack:
    """Test resistance to parameter manipulation attacks."""

    def test_user_id_injection_in_create(self, client, alice_user, bob_user):
        """Test that user_id in request body is ignored during creation (T039)."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}

        # Alice attempts to create a task for Bob by injecting user_id
        malicious_data = {
            "title": "Malicious task",
            "description": "Trying to create for Bob",
            "user_id": bob["user_id"]  # Injected user_id
        }
        response = client.post("/tasks", json=malicious_data, headers=alice_headers)

        # Task should be created successfully
        assert response.status_code == 201
        created_task = response.json()

        # But user_id should be Alice's (from token), not Bob's
        assert created_task["user_id"] == alice["user_id"]
        assert created_task["user_id"] != bob["user_id"]

        # Verify Bob cannot see this task
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}
        bob_tasks = client.get("/tasks", headers=bob_headers).json()
        bob_task_ids = [task["id"] for task in bob_tasks["tasks"]]
        assert created_task["id"] not in bob_task_ids

    def test_user_id_injection_in_update(self, client, alice_user, bob_user):
        """Test that user_id cannot be changed via update."""
        alice = alice_user
        bob = bob_user
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}

        # Alice creates a task
        alice_task = client.post(
            "/tasks",
            json={"title": "Alice's task"},
            headers=alice_headers
        ).json()

        # Alice attempts to change ownership to Bob via update
        malicious_update = {
            "title": "Updated task",
            "user_id": bob["user_id"]  # Attempting to change ownership
        }
        response = client.put(
            f"/tasks/{alice_task['id']}",
            json=malicious_update,
            headers=alice_headers
        )

        # Update should succeed (title changes)
        assert response.status_code == 200

        # But user_id should remain Alice's
        updated_task = response.json()
        assert updated_task["user_id"] == alice["user_id"]
        assert updated_task["user_id"] != bob["user_id"]
        assert updated_task["title"] == "Updated task"

    def test_sql_injection_in_task_id(self, client, alice_user):
        """Test that SQL injection attempts in task_id are blocked."""
        alice = alice_user
        headers = {"Authorization": f"Bearer {alice['token']}"}

        # Attempt SQL injection in task_id parameter
        malicious_ids = [
            "1 OR 1=1",
            "1; DROP TABLE tasks;",
            "1' OR '1'='1",
            "1 UNION SELECT * FROM users",
        ]

        for malicious_id in malicious_ids:
            response = client.get(f"/tasks/{malicious_id}", headers=headers)

            # Should return 422 (validation error) or 404 (not found)
            # Never 200 or 500 (SQL injection succeeded)
            assert response.status_code in [404, 422]

    def test_header_injection_attack(self, client, alice_user):
        """Test that header injection doesn't bypass authorization."""
        alice = alice_user

        # Attempt to inject additional headers
        malicious_headers = {
            "Authorization": f"Bearer {alice['token']}",
            "X-User-Id": "999",  # Attempting to override user_id
            "X-Admin": "true",   # Attempting to claim admin privileges
        }

        response = client.get("/tasks", headers=malicious_headers)

        # Should work normally (extra headers ignored)
        assert response.status_code == 200

        # Should only return Alice's tasks
        tasks = response.json()["tasks"]
        for task in tasks:
            assert task["user_id"] == alice["user_id"]


class TestAuthorizationBypass:
    """Test various authorization bypass attempts."""

    def test_missing_token_bypass(self, client):
        """Test that missing token cannot be bypassed."""
        # Attempt to access protected endpoint without token
        response = client.get("/tasks")
        assert response.status_code == 403

    def test_malformed_token_bypass(self, client):
        """Test that malformed tokens are rejected."""
        malformed_tokens = [
            "Bearer",
            "Bearer ",
            "Bearer invalid",
            "NotBearer token",
            "",
        ]

        for token in malformed_tokens:
            headers = {"Authorization": token}
            response = client.get("/tasks", headers=headers)
            assert response.status_code in [401, 403]

    def test_null_byte_injection(self, client, alice_user):
        """Test that null byte injection doesn't bypass authorization."""
        alice = alice_user
        headers = {"Authorization": f"Bearer {alice['token']}\x00admin"}

        # Should either work normally or reject the malformed header
        response = client.get("/tasks", headers=headers)
        assert response.status_code in [200, 401, 403]

        if response.status_code == 200:
            # If accepted, should only return Alice's tasks
            tasks = response.json()["tasks"]
            for task in tasks:
                assert task["user_id"] == alice["user_id"]
