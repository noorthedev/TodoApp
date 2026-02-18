# Quickstart Guide: Authorization & User Isolation Layer

**Feature**: 003-auth-isolation
**Date**: 2026-02-16
**Prerequisites**: Backend API from 002-backend-api-db must be running

## Overview

This guide provides step-by-step instructions for testing the authorization and user isolation features of the Task Management API. It covers both manual testing with cURL and automated security testing scenarios.

## Prerequisites

1. **Backend API Running**:
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uvicorn src.main:app --reload
   ```

2. **API Available**: http://localhost:8000

3. **Tools Required**:
   - cURL (command-line HTTP client)
   - jq (JSON processor, optional but recommended)
   - Postman (optional, for organized test collections)

## Quick Start: 5-Minute Authorization Test

### Step 1: Create Two Test Users

```bash
# Create User A (Alice)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }' | jq

# Save Alice's token
TOKEN_A=$(curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

# Create User B (Bob)
TOKEN_B=$(curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "password456"
  }' | jq -r '.access_token')

echo "Alice Token: $TOKEN_A"
echo "Bob Token: $TOKEN_B"
```

### Step 2: Alice Creates a Task

```bash
# Alice creates a task
TASK_ID=$(curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Alice private task",
    "description": "Only Alice should see this"
  }' | jq -r '.id')

echo "Task ID: $TASK_ID"
```

### Step 3: Test Cross-User Access (Should Fail)

```bash
# Bob tries to access Alice's task (should return 403 Forbidden)
curl -X GET http://localhost:8000/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN_B"

# Expected output:
# {
#   "error": {
#     "type": "http_error",
#     "status_code": 403,
#     "message": "Not authorized to access this task"
#   }
# }
```

### Step 4: Verify Alice Can Access Her Own Task

```bash
# Alice accesses her own task (should succeed)
curl -X GET http://localhost:8000/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN_A" | jq

# Expected: Full task details returned
```

### Step 5: Verify Task List Isolation

```bash
# Alice sees her task
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN_A" | jq

# Bob sees empty list (Alice's task not visible)
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN_B" | jq
```

**✅ If all tests pass, authorization is working correctly!**

---

## Comprehensive Security Test Suite

### Test 1: Horizontal Privilege Escalation Prevention

**Objective**: Verify users cannot access other users' resources

**Steps**:

1. Alice creates a task:
   ```bash
   ALICE_TASK=$(curl -X POST http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN_A" \
     -H "Content-Type: application/json" \
     -d '{"title": "Alice task"}' | jq -r '.id')
   ```

2. Bob attempts to GET Alice's task:
   ```bash
   curl -X GET http://localhost:8000/tasks/$ALICE_TASK \
     -H "Authorization: Bearer $TOKEN_B"
   # Expected: 403 Forbidden
   ```

3. Bob attempts to UPDATE Alice's task:
   ```bash
   curl -X PUT http://localhost:8000/tasks/$ALICE_TASK \
     -H "Authorization: Bearer $TOKEN_B" \
     -H "Content-Type: application/json" \
     -d '{"title": "Hacked!"}'
   # Expected: 403 Forbidden
   ```

4. Bob attempts to DELETE Alice's task:
   ```bash
   curl -X DELETE http://localhost:8000/tasks/$ALICE_TASK \
     -H "Authorization: Bearer $TOKEN_B"
   # Expected: 403 Forbidden
   ```

5. Verify Alice's task is unchanged:
   ```bash
   curl -X GET http://localhost:8000/tasks/$ALICE_TASK \
     -H "Authorization: Bearer $TOKEN_A" | jq
   # Expected: Original task data intact
   ```

**Pass Criteria**: All Bob's attempts return 403 Forbidden, Alice's task remains unchanged

---

### Test 2: Token Tampering Detection

**Objective**: Verify modified tokens are rejected

**Steps**:

1. Get a valid token:
   ```bash
   TOKEN=$(curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "alice@example.com",
       "password": "password123"
     }' | jq -r '.access_token')
   ```

2. Decode token to see structure (using jwt.io or base64):
   ```bash
   echo $TOKEN | cut -d. -f2 | base64 -d | jq
   # Shows: {"sub": 1, "exp": 1234567890, ...}
   ```

3. Attempt to use a token with modified payload:
   ```bash
   # Manually create a token with modified user_id
   # (This will have invalid signature)
   TAMPERED_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjk5OX0.invalid"

   curl -X GET http://localhost:8000/tasks \
     -H "Authorization: Bearer $TAMPERED_TOKEN"
   # Expected: 401 Unauthorized
   ```

**Pass Criteria**: Tampered token is rejected with 401 Unauthorized

---

### Test 3: Expired Token Rejection

**Objective**: Verify expired tokens are rejected

**Note**: This test requires waiting 24 hours or manually creating an expired token for testing.

**Steps**:

1. Create a token with short expiration (requires backend modification for testing):
   ```python
   # In backend/src/utils/jwt.py, temporarily set:
   # expire = datetime.utcnow() + timedelta(seconds=5)
   ```

2. Get token and wait for expiration:
   ```bash
   TOKEN=$(curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "alice@example.com", "password": "password123"}' \
     | jq -r '.access_token')

   sleep 10  # Wait for token to expire
   ```

3. Attempt to use expired token:
   ```bash
   curl -X GET http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN"
   # Expected: 401 Unauthorized with "Token expired" message
   ```

**Pass Criteria**: Expired token is rejected with 401 Unauthorized

---

### Test 4: Missing Authentication

**Objective**: Verify protected endpoints require authentication

**Steps**:

1. Attempt to access protected endpoints without token:
   ```bash
   # GET /tasks
   curl -X GET http://localhost:8000/tasks
   # Expected: 401 Unauthorized

   # POST /tasks
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Test"}'
   # Expected: 401 Unauthorized

   # GET /tasks/{id}
   curl -X GET http://localhost:8000/tasks/1
   # Expected: 401 Unauthorized

   # PUT /tasks/{id}
   curl -X PUT http://localhost:8000/tasks/1 \
     -H "Content-Type: application/json" \
     -d '{"title": "Test"}'
   # Expected: 401 Unauthorized

   # DELETE /tasks/{id}
   curl -X DELETE http://localhost:8000/tasks/1
   # Expected: 401 Unauthorized
   ```

**Pass Criteria**: All requests return 401 Unauthorized

---

### Test 5: Parameter Manipulation Prevention

**Objective**: Verify user_id in request body is ignored

**Steps**:

1. Alice attempts to create task with different user_id:
   ```bash
   curl -X POST http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN_A" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test task",
       "user_id": 999
     }' | jq
   ```

2. Verify task belongs to Alice (not user_id 999):
   ```bash
   curl -X GET http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN_A" | jq
   # Expected: Task has user_id matching Alice's ID (from token)
   ```

**Pass Criteria**: Task is created with authenticated user's ID, not the ID from request body

---

### Test 6: Task List Isolation

**Objective**: Verify users only see their own tasks

**Steps**:

1. Alice creates 3 tasks:
   ```bash
   for i in {1..3}; do
     curl -X POST http://localhost:8000/tasks \
       -H "Authorization: Bearer $TOKEN_A" \
       -H "Content-Type: application/json" \
       -d "{\"title\": \"Alice task $i\"}"
   done
   ```

2. Bob creates 2 tasks:
   ```bash
   for i in {1..2}; do
     curl -X POST http://localhost:8000/tasks \
       -H "Authorization: Bearer $TOKEN_B" \
       -H "Content-Type: application/json" \
       -d "{\"title\": \"Bob task $i\"}"
   done
   ```

3. Verify Alice sees only her 3 tasks:
   ```bash
   curl -X GET http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN_A" | jq '.total'
   # Expected: 3
   ```

4. Verify Bob sees only his 2 tasks:
   ```bash
   curl -X GET http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN_B" | jq '.total'
   # Expected: 2
   ```

**Pass Criteria**: Each user sees only their own tasks

---

## Postman Collection

For easier testing, import this Postman collection:

### Collection Structure

```
Authorization Tests
├── Setup
│   ├── Register Alice
│   ├── Register Bob
│   └── Health Check
├── Positive Tests
│   ├── Alice Creates Task
│   ├── Alice Views Task
│   ├── Alice Updates Task
│   └── Alice Deletes Task
└── Security Tests
    ├── Bob Accesses Alice Task (403)
    ├── Bob Updates Alice Task (403)
    ├── Bob Deletes Alice Task (403)
    ├── No Token Access (401)
    └── Task List Isolation
```

### Environment Variables

Set these in Postman environment:

- `base_url`: http://localhost:8000
- `token_alice`: (set after registration)
- `token_bob`: (set after registration)
- `alice_task_id`: (set after task creation)

---

## Troubleshooting

### Issue: All requests return 401 Unauthorized

**Possible Causes**:
- Backend not running
- JWT_SECRET not configured in .env
- Token expired

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/
# Should return: {"status": "healthy", ...}

# Check .env file has JWT_SECRET
cat backend/.env | grep JWT_SECRET

# Get fresh token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "password123"}' \
  | jq -r '.access_token')
```

---

### Issue: 403 Forbidden when accessing own tasks

**Possible Causes**:
- Using wrong token
- Task belongs to different user

**Solution**:
```bash
# Verify token belongs to correct user
echo $TOKEN | cut -d. -f2 | base64 -d | jq '.sub'

# Check task ownership
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

### Issue: Bob can access Alice's tasks

**This is a critical security vulnerability!**

**Investigation Steps**:
1. Check ownership verification in `backend/src/api/tasks.py`
2. Verify `get_current_user` dependency is applied to all endpoints
3. Check database query filtering includes `user_id` WHERE clause
4. Review logs for authorization failures

---

## Performance Testing

### Authorization Overhead Test

Measure authorization performance:

```bash
# Time 100 authorized requests
time for i in {1..100}; do
  curl -s -X GET http://localhost:8000/tasks \
    -H "Authorization: Bearer $TOKEN" > /dev/null
done

# Expected: <5 seconds total (50ms per request)
```

---

## Security Checklist

After completing all tests, verify:

- ✅ Users cannot access other users' tasks (403 Forbidden)
- ✅ Tampered tokens are rejected (401 Unauthorized)
- ✅ Expired tokens are rejected (401 Unauthorized)
- ✅ Missing authentication is rejected (401 Unauthorized)
- ✅ Request body user_id is ignored (uses token user_id)
- ✅ Task lists show only user's own tasks
- ✅ Authorization checks complete in <50ms
- ✅ All authorization failures are logged

**If all items are checked, authorization is production-ready!**

---

## Next Steps

1. **Automated Testing**: Convert manual tests to pytest test suite
2. **Load Testing**: Test authorization under concurrent load
3. **Penetration Testing**: Run automated security scanner
4. **Monitoring**: Set up alerts for authorization failures
5. **Documentation**: Update API documentation with authorization requirements
