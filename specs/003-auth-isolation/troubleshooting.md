# Authorization Troubleshooting Guide

**Feature**: 003-auth-isolation
**Date**: 2026-02-16
**Audience**: Developers, DevOps, Support Engineers

## Overview

This guide helps diagnose and resolve common authorization issues in the Task Management API. Use this when users report authentication failures, access denied errors, or unexpected authorization behavior.

---

## Quick Diagnostic Checklist

When troubleshooting authorization issues, check these in order:

1. **Is the token present?** → Check Authorization header
2. **Is the token valid?** → Verify signature and expiration
3. **Does the user exist?** → Check database for user_id
4. **Does the resource exist?** → Check database for resource_id
5. **Does the user own the resource?** → Verify user_id match
6. **Are logs showing the failure?** → Check application logs

---

## Common Issues and Solutions

### Issue 1: "403 Forbidden" - No Authorization Header

**Symptom**: User receives 403 Forbidden immediately without any token validation

**Error Response**:
```json
{
  "detail": "Not authenticated"
}
```

**Root Cause**: No Authorization header in request

**Diagnosis**:
```bash
# Check if Authorization header is present
curl -v http://localhost:8000/tasks
# Look for: Authorization: Bearer <token>
```

**Solution**:
- **Frontend**: Ensure Authorization header is included in all API requests
- **Postman/cURL**: Add header: `Authorization: Bearer <token>`
- **Code Example**:
  ```javascript
  // Correct
  fetch('/tasks', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  // Wrong - missing header
  fetch('/tasks')
  ```

**Prevention**:
- Use API client interceptors to automatically add Authorization header
- Validate token exists before making requests

---

### Issue 2: "401 Unauthorized - Token has expired"

**Symptom**: User was authenticated but now receives 401 with "Token has expired"

**Error Response**:
```json
{
  "error": {
    "type": "http_error",
    "status_code": 401,
    "message": "Token has expired"
  }
}
```

**Root Cause**: JWT token expiration (24-hour TTL exceeded)

**Diagnosis**:
```bash
# Decode token to check expiration (use jwt.io or python-jose)
python -c "from jose import jwt; print(jwt.get_unverified_claims('$TOKEN'))"
# Check 'exp' field (Unix timestamp)
```

**Solution**:
- **User Action**: Log in again to get new token
- **Frontend**: Implement token refresh or automatic re-login
- **Code Example**:
  ```javascript
  // Detect expired token and redirect to login
  if (response.status === 401 && response.data.message.includes('expired')) {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
  ```

**Prevention**:
- Implement token refresh mechanism (future enhancement)
- Store token expiration time and proactively refresh before expiry
- Show "session expired" warning to users

---

### Issue 3: "401 Unauthorized - Invalid token"

**Symptom**: User receives 401 with "Invalid token" or "Could not validate credentials"

**Error Response**:
```json
{
  "error": {
    "type": "http_error",
    "status_code": 401,
    "message": "Invalid token"
  }
}
```

**Root Causes**:
1. Token signature is invalid (tampered or wrong secret)
2. Token format is malformed
3. Token was generated with different JWT_SECRET

**Diagnosis**:
```bash
# Check token format (should be 3 base64 parts separated by dots)
echo $TOKEN | awk -F. '{print NF}'
# Should output: 3

# Verify JWT_SECRET matches between environments
# Backend: Check .env file
grep JWT_SECRET backend/.env

# Try decoding token
python -c "from jose import jwt; from src.config import settings; print(jwt.decode('$TOKEN', settings.JWT_SECRET, algorithms=['HS256']))"
```

**Solution**:
- **Mismatched Secret**: Ensure JWT_SECRET is same in all environments
- **Tampered Token**: User must log in again to get valid token
- **Malformed Token**: Check token storage/retrieval logic
- **Code Example**:
  ```python
  # Verify JWT_SECRET is loaded correctly
  from src.config import settings
  print(f"JWT_SECRET length: {len(settings.JWT_SECRET)}")
  # Should be at least 32 characters
  ```

**Prevention**:
- Use environment-specific secrets (dev, staging, prod)
- Never hardcode JWT_SECRET in code
- Validate token format before sending to backend

---

### Issue 4: "403 Forbidden - Not authorized to access this task"

**Symptom**: User is authenticated but cannot access a specific task

**Error Response**:
```json
{
  "error": {
    "type": "http_error",
    "status_code": 403,
    "message": "Not authorized to access this task"
  }
}
```

**Root Causes**:
1. Task belongs to a different user (horizontal privilege escalation attempt)
2. User is trying to access another user's resource

**Diagnosis**:
```bash
# Check task ownership
curl -X GET http://localhost:8000/tasks/123 \
  -H "Authorization: Bearer $TOKEN"

# Check user's task list
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Verify user_id in token matches task.user_id
python -c "from jose import jwt; print(jwt.get_unverified_claims('$TOKEN')['sub'])"
```

**Solution**:
- **Expected Behavior**: Users can only access their own tasks
- **User Action**: Verify they're accessing the correct task ID
- **Developer Action**: Check if task_id is correct in frontend code

**Prevention**:
- Frontend should only display tasks from user's own list
- Don't allow manual task_id entry in URLs
- Use task slugs or UUIDs instead of sequential IDs (future enhancement)

---

### Issue 5: "404 Not Found" for Existing Task

**Symptom**: User receives 404 for a task that exists in database

**Error Response**:
```json
{
  "error": {
    "type": "http_error",
    "status_code": 404,
    "message": "Task not found"
  }
}
```

**Root Causes**:
1. Task belongs to different user (ownership check returns 404 to prevent ID enumeration)
2. Task was deleted
3. Wrong task_id in request

**Diagnosis**:
```bash
# Check if task exists in database
psql $DATABASE_URL -c "SELECT id, user_id, title FROM tasks WHERE id = 123;"

# Check user's token
python -c "from jose import jwt; print(jwt.get_unverified_claims('$TOKEN')['sub'])"

# Compare user_id from token with task.user_id
```

**Solution**:
- **If task.user_id != token.user_id**: This is expected behavior (security feature)
- **If task doesn't exist**: Task was deleted or wrong ID
- **If task.user_id == token.user_id**: Check authorization logic

**Prevention**:
- Frontend should track task IDs from user's own list
- Don't expose task IDs in URLs (use UUIDs or slugs)

---

### Issue 6: User Cannot See Any Tasks (Empty List)

**Symptom**: GET /tasks returns empty list but user has created tasks

**Error Response**:
```json
{
  "tasks": [],
  "total": 0
}
```

**Root Causes**:
1. Wrong user_id in token (user logged in as different account)
2. Tasks were created with different user_id
3. Database query filtering issue

**Diagnosis**:
```bash
# Check user_id in token
python -c "from jose import jwt; print(jwt.get_unverified_claims('$TOKEN')['sub'])"

# Check tasks in database for this user
psql $DATABASE_URL -c "SELECT id, user_id, title FROM tasks WHERE user_id = <user_id>;"

# Check if tasks exist for different user
psql $DATABASE_URL -c "SELECT user_id, COUNT(*) FROM tasks GROUP BY user_id;"
```

**Solution**:
- **Wrong Account**: User logged in with different email
- **Tasks Missing**: Tasks were deleted or never created
- **Query Issue**: Check backend logs for SQL queries

**Prevention**:
- Show user's email in UI to confirm correct account
- Log task creation with user_id for debugging

---

### Issue 7: Token Works in Postman but Not in Frontend

**Symptom**: Same token works in Postman but fails in frontend application

**Root Causes**:
1. CORS issue (browser blocks request)
2. Authorization header not set correctly in frontend
3. Token stored incorrectly (extra quotes, whitespace)

**Diagnosis**:
```javascript
// Check token in browser console
console.log('Token:', localStorage.getItem('token'));
// Should NOT have quotes around it

// Check Authorization header in Network tab
// Should be: Authorization: Bearer eyJ...
// NOT: Authorization: Bearer "eyJ..."
```

**Solution**:
- **Extra Quotes**: Remove quotes when storing token
  ```javascript
  // Wrong
  localStorage.setItem('token', JSON.stringify(token));

  // Correct
  localStorage.setItem('token', token);
  ```
- **CORS**: Ensure backend allows frontend origin
- **Header Format**: Verify "Bearer " prefix (with space)

**Prevention**:
- Use API client library (axios) with interceptors
- Test token storage/retrieval in browser console

---

### Issue 8: Authorization Logging Not Appearing

**Symptom**: Authorization failures not showing in logs

**Root Causes**:
1. Log level too high (only showing ERROR, not WARNING)
2. Logger not configured correctly
3. Logs going to different file/stream

**Diagnosis**:
```bash
# Check log level
grep LOG_LEVEL backend/.env

# Check logger configuration
grep -r "logging.getLogger" backend/src/

# Tail logs in real-time
tail -f backend/logs/app.log
```

**Solution**:
- **Set Log Level**: Ensure WARNING level or lower
  ```python
  # In backend/src/config.py or main.py
  logging.basicConfig(level=logging.WARNING)
  ```
- **Check Log Output**: Verify logs are written to expected location

**Prevention**:
- Use structured logging (JSON format)
- Centralize logs (e.g., CloudWatch, Datadog)
- Set up log aggregation for production

---

## Debugging Tools

### Tool 1: Decode JWT Token

```bash
# Using Python
python -c "from jose import jwt; import json; print(json.dumps(jwt.get_unverified_claims('$TOKEN'), indent=2))"

# Using jwt.io (paste token in browser)
# https://jwt.io/

# Check expiration
python -c "from jose import jwt; from datetime import datetime; claims = jwt.get_unverified_claims('$TOKEN'); print('Expires:', datetime.fromtimestamp(claims['exp']))"
```

### Tool 2: Test Authorization Manually

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  | jq -r '.access_token')

# Test protected endpoint
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -v

# Check response headers and status code
```

### Tool 3: Check Database State

```sql
-- Check user exists
SELECT id, email, created_at FROM users WHERE email = 'test@example.com';

-- Check user's tasks
SELECT id, user_id, title, created_at FROM tasks WHERE user_id = 123;

-- Check task ownership
SELECT t.id, t.title, t.user_id, u.email
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE t.id = 456;
```

### Tool 4: Enable Debug Logging

```python
# In backend/src/main.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# In backend/src/utils/jwt.py
logger.debug(f"Token payload: {payload}")
logger.debug(f"User ID from token: {user_id}")
```

---

## Production Monitoring

### Metrics to Track

1. **Authorization Failure Rate**
   - Alert if >5% of requests return 401/403
   - Indicates potential attack or configuration issue

2. **Token Expiration Rate**
   - Track how often users hit token expiration
   - Optimize token TTL based on usage patterns

3. **Authorization Latency**
   - Alert if authorization overhead >50ms
   - Indicates database or JWT validation performance issue

4. **Cross-User Access Attempts**
   - Track 403 responses for ownership violations
   - Indicates potential security attack

### Log Queries

```bash
# Count authorization failures by type
grep "Authorization failed" app.log | wc -l

# Find users with most authorization failures
grep "Authorization failed" app.log | grep -oP "user \d+" | sort | uniq -c | sort -rn

# Track token validation failures
grep "Token validation failed" app.log | grep -oP "Token validation failed: \w+" | sort | uniq -c
```

---

## Emergency Procedures

### Procedure 1: Mass Token Invalidation

**Scenario**: Security breach requires invalidating all tokens

**Steps**:
1. Rotate JWT_SECRET in environment variables
2. Restart all backend instances
3. Force all users to re-login
4. Monitor for increased login activity

```bash
# Generate new secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
echo "JWT_SECRET=<new_secret>" >> backend/.env

# Restart backend
systemctl restart backend
```

### Procedure 2: Disable Authorization (Emergency Only)

**Scenario**: Critical bug in authorization blocking all users

**WARNING**: Only use in extreme emergency, creates security vulnerability

```python
# Temporary bypass (DO NOT USE IN PRODUCTION)
# In backend/src/utils/jwt.py
async def get_current_user_emergency_bypass(session: AsyncSession):
    # Return first user (INSECURE - EMERGENCY ONLY)
    result = await session.execute(select(User).limit(1))
    return result.scalar_one()
```

**Recovery**:
1. Fix authorization bug
2. Deploy fix immediately
3. Re-enable normal authorization
4. Audit all actions during bypass period

---

## Support Escalation

### When to Escalate

Escalate to senior engineer if:
- Authorization failures affect >10% of users
- Security vulnerability suspected
- Database corruption suspected
- Issue persists after following this guide

### Information to Provide

When escalating, include:
1. User email and user_id
2. Task ID (if applicable)
3. Token (first 20 characters only)
4. Error message and status code
5. Timestamp of failure
6. Relevant log entries
7. Steps to reproduce

---

## Additional Resources

- **Architecture**: `specs/003-auth-isolation/architecture.md`
- **API Contracts**: `specs/003-auth-isolation/contracts/authorization.md`
- **Security Tests**: `specs/003-auth-isolation/test-results.md`
- **Patterns**: `specs/003-auth-isolation/patterns.md`
- **Quick Start**: `specs/003-auth-isolation/quickstart.md`
