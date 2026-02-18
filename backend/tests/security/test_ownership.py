"""Security tests for task ownership enforcement."""
import pytest
from fastapi.testclient import TestClient


class TestCrossUserAccess:
    """Test that users cannot access other users' tasks."""

    def test_cross_user_get_attempt(self, multi_user_scenario):
        """Test that Bob cannot GET Alice's task (T015)."""
        scenario = multi_user_scenario
        client = scenario["client"]
        alice_task = scenario["alice_task"]
        bob = scenario["bob"]

        # Bob attempts to access Alice's task
        headers = {"Authorization": f"Bearer {bob['token']}"}
        response = client.get(f"/tasks/{alice_task['id']}", headers=headers)

        # Should return 403 Forbidden
        assert response.status_code == 403
        assert "Not authorized to access this task" in response.json()["detail"]

    def test_cross_user_update_attempt(self, multi_user_scenario):
        """Test that Bob cannot UPDATE Alice's task (T016)."""
        scenario = multi_user_scenario
        client = scenario["client"]
        alice_task = scenario["alice_task"]
        bob = scenario["bob"]

        # Bob attempts to update Alice's task
        headers = {"Authorization": f"Bearer {bob['token']}"}
        update_data = {"title": "Hacked by Bob!", "is_completed": True}
        response = client.put(
            f"/tasks/{alice_task['id']}",
            json=update_data,
            headers=headers
        )

        # Should return 403 Forbidden
        assert response.status_code == 403
        assert "Not authorized to update this task" in response.json()["detail"]

        # Verify Alice's task is unchanged
        alice = scenario["alice"]
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        verify_response = client.get(f"/tasks/{alice_task['id']}", headers=alice_headers)
        assert verify_response.status_code == 200
        assert verify_response.json()["title"] == alice_task["title"]
        assert verify_response.json()["is_completed"] == False

    def test_cross_user_delete_attempt(self, multi_user_scenario):
        """Test that Bob cannot DELETE Alice's task (T017)."""
        scenario = multi_user_scenario
        client = scenario["client"]
        alice_task = scenario["alice_task"]
        bob = scenario["bob"]

        # Bob attempts to delete Alice's task
        headers = {"Authorization": f"Bearer {bob['token']}"}
        response = client.delete(f"/tasks/{alice_task['id']}", headers=headers)

        # Should return 403 Forbidden
        assert response.status_code == 403
        assert "Not authorized to delete this task" in response.json()["detail"]

        # Verify Alice's task still exists
        alice = scenario["alice"]
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        verify_response = client.get(f"/tasks/{alice_task['id']}", headers=alice_headers)
        assert verify_response.status_code == 200
        assert verify_response.json()["id"] == alice_task["id"]


class TestTaskListIsolation:
    """Test that task lists are properly isolated per user."""

    def test_task_list_isolation(self, multi_user_scenario):
        """Test that users only see their own tasks in GET /tasks (T018)."""
        scenario = multi_user_scenario
        client = scenario["client"]
        alice = scenario["alice"]
        bob = scenario["bob"]
        alice_task = scenario["alice_task"]
        bob_task = scenario["bob_task"]

        # Alice gets her task list
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        alice_response = client.get("/tasks", headers=alice_headers)
        assert alice_response.status_code == 200
        alice_tasks = alice_response.json()["tasks"]

        # Alice should see only her task
        assert len(alice_tasks) == 1
        assert alice_tasks[0]["id"] == alice_task["id"]
        assert alice_tasks[0]["user_id"] == alice["user_id"]

        # Verify Bob's task is NOT in Alice's list
        alice_task_ids = [task["id"] for task in alice_tasks]
        assert bob_task["id"] not in alice_task_ids

        # Bob gets his task list
        bob_headers = {"Authorization": f"Bearer {bob['token']}"}
        bob_response = client.get("/tasks", headers=bob_headers)
        assert bob_response.status_code == 200
        bob_tasks = bob_response.json()["tasks"]

        # Bob should see only his task
        assert len(bob_tasks) == 1
        assert bob_tasks[0]["id"] == bob_task["id"]
        assert bob_tasks[0]["user_id"] == bob["user_id"]

        # Verify Alice's task is NOT in Bob's list
        bob_task_ids = [task["id"] for task in bob_tasks]
        assert alice_task["id"] not in bob_task_ids

    def test_empty_task_list_for_new_user(self, client, alice_user):
        """Test that new users see empty task list."""
        # Register a new user (Charlie)
        charlie_credentials = {"email": "charlie@example.com", "password": "charlie123"}
        register_response = client.post("/auth/register", json=charlie_credentials)
        assert register_response.status_code == 201
        charlie_token = register_response.json()["access_token"]

        # Charlie should see empty task list
        headers = {"Authorization": f"Bearer {charlie_token}"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert len(response.json()["tasks"]) == 0


class TestParameterManipulation:
    """Test that parameter manipulation is prevented."""

    def test_parameter_manipulation_prevention(self, client, alice_user, bob_user):
        """Test that user_id in request body is ignored (T019)."""
        alice = alice_user
        bob = bob_user

        # Alice attempts to create a task with Bob's user_id in request body
        alice_headers = {"Authorization": f"Bearer {alice['token']}"}
        malicious_data = {
            "title": "Malicious task",
            "description": "Trying to create task for Bob",
            "user_id": bob["user_id"]  # Attempting to manipulate user_id
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
        bob_tasks_response = client.get("/tasks", headers=bob_headers)
        bob_task_ids = [task["id"] for task in bob_tasks_response.json()["tasks"]]
        assert created_task["id"] not in bob_task_ids

        # Verify Alice can see this task
        alice_tasks_response = client.get("/tasks", headers=alice_headers)
        alice_task_ids = [task["id"] for task in alice_tasks_response.json()["tasks"]]
        assert created_task["id"] in alice_task_ids


class TestOwnershipVerification:
    """Test ownership verification on all operations."""

    def test_owner_can_access_own_task(self, client, alice_user, alice_task):
        """Test that owner can perform all operations on their own task."""
        alice = alice_user
        headers = {"Authorization": f"Bearer {alice['token']}"}

        # GET - should succeed
        get_response = client.get(f"/tasks/{alice_task['id']}", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["id"] == alice_task["id"]

        # PUT - should succeed
        update_data = {"title": "Updated by Alice", "is_completed": True}
        put_response = client.put(
            f"/tasks/{alice_task['id']}",
            json=update_data,
            headers=headers
        )
        assert put_response.status_code == 200
        assert put_response.json()["title"] == "Updated by Alice"
        assert put_response.json()["is_completed"] == True

        # DELETE - should succeed
        delete_response = client.delete(f"/tasks/{alice_task['id']}", headers=headers)
        assert delete_response.status_code == 204

        # Verify task is deleted
        verify_response = client.get(f"/tasks/{alice_task['id']}", headers=headers)
        assert verify_response.status_code == 404

    def test_non_existent_task_returns_404(self, client, alice_user):
        """Test that accessing non-existent task returns 404."""
        alice = alice_user
        headers = {"Authorization": f"Bearer {alice['token']}"}
        non_existent_id = 99999

        # GET non-existent task
        response = client.get(f"/tasks/{non_existent_id}", headers=headers)
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]

    def test_multiple_users_multiple_tasks(self, client):
        """Test isolation with multiple users and multiple tasks each."""
        # Create two users
        alice_creds = {"email": "alice_multi@example.com", "password": "alice123"}
        bob_creds = {"email": "bob_multi@example.com", "password": "bob123"}

        alice_reg = client.post("/auth/register", json=alice_creds)
        bob_reg = client.post("/auth/register", json=bob_creds)

        alice_token = alice_reg.json()["access_token"]
        bob_token = bob_reg.json()["access_token"]

        alice_headers = {"Authorization": f"Bearer {alice_token}"}
        bob_headers = {"Authorization": f"Bearer {bob_token}"}

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

        # Verify Alice sees only her 3 tasks
        alice_list = client.get("/tasks", headers=alice_headers)
        assert alice_list.json()["total"] == 3
        alice_ids = [task["id"] for task in alice_list.json()["tasks"]]
        assert set(alice_ids) == set(alice_task_ids)

        # Verify Bob sees only his 2 tasks
        bob_list = client.get("/tasks", headers=bob_headers)
        assert bob_list.json()["total"] == 2
        bob_ids = [task["id"] for task in bob_list.json()["tasks"]]
        assert set(bob_ids) == set(bob_task_ids)

        # Verify Bob cannot access any of Alice's tasks
        for alice_task_id in alice_task_ids:
            response = client.get(f"/tasks/{alice_task_id}", headers=bob_headers)
            assert response.status_code == 403
