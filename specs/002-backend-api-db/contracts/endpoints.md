# API Endpoints Documentation

**Feature**: Backend API & Database Layer
**Date**: 2026-02-16
**Base URL**: `http://localhost:8000` (development)

## Overview

This document provides detailed documentation for all API endpoints, including request/response formats, authentication requirements, and example usage.

## Authentication

All endpoints under `/tasks` require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Tokens are obtained from `/auth/register` or `/auth/login` endpoints.

---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Validation**:
- Email must be valid email format
- Password must be at least 8 characters
- Email must not already exist

**Success Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-02-16T10:30:00Z"
  }
}
```

**Error Responses**:

400 Bad Request - Email already exists:
```json
{
  "detail": "Email already registered"
}
```

400 Bad Request - Invalid input:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'
```

---

### POST /auth/login

Authenticate user and receive JWT token.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-02-16T10:30:00Z"
  }
}
```

**Error Responses**:

401 Unauthorized - Invalid credentials:
```json
{
  "detail": "Invalid email or password"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'
```

**Notes**:
- Password is verified against bcrypt hash
- Error message doesn't reveal whether email exists (security)
- Token expires after 24 hours (configurable)

---

### POST /auth/logout

Logout endpoint (client-side token invalidation).

**Authentication**: Not required

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/auth/logout
```

**Notes**:
- This is an informational endpoint
- Actual logout happens client-side by removing the token
- JWT tokens are stateless and cannot be invalidated server-side

---

## Task Endpoints

### GET /tasks

Get all tasks for the authenticated user.

**Authentication**: Required (JWT token)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Complete project documentation",
      "description": "Write comprehensive API documentation",
      "is_completed": false,
      "created_at": "2026-02-16T10:30:00Z",
      "updated_at": "2026-02-16T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "title": "Review pull requests",
      "description": null,
      "is_completed": true,
      "created_at": "2026-02-16T09:00:00Z",
      "updated_at": "2026-02-16T11:00:00Z"
    }
  ],
  "total": 2
}
```

**Error Responses**:

401 Unauthorized - Missing or invalid token:
```json
{
  "detail": "Invalid or expired token"
}
```

**Example cURL**:
```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Notes**:
- Returns only tasks belonging to the authenticated user
- Tasks are ordered by created_at descending (newest first)
- Empty array returned if user has no tasks

---

### POST /tasks

Create a new task for the authenticated user.

**Authentication**: Required (JWT token)

**Request Body**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation with examples"
}
```

**Validation**:
- Title is required (1-255 characters)
- Description is optional (max 10,000 characters)

**Success Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation with examples",
  "is_completed": false,
  "created_at": "2026-02-16T10:30:00Z",
  "updated_at": "2026-02-16T10:30:00Z"
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

401 Unauthorized:
```json
{
  "detail": "Invalid or expired token"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"title":"Complete documentation","description":"Write API docs"}'
```

**Notes**:
- Task is automatically associated with authenticated user
- is_completed defaults to false
- Timestamps are set automatically

---

### GET /tasks/{task_id}

Get a specific task by ID.

**Authentication**: Required (JWT token)

**Path Parameters**:
- `task_id` (integer): Task ID

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "is_completed": false,
  "created_at": "2026-02-16T10:30:00Z",
  "updated_at": "2026-02-16T10:30:00Z"
}
```

**Error Responses**:

401 Unauthorized:
```json
{
  "detail": "Invalid or expired token"
}
```

403 Forbidden - Task belongs to another user:
```json
{
  "detail": "Not authorized to access this task"
}
```

404 Not Found:
```json
{
  "detail": "Task not found"
}
```

**Example cURL**:
```bash
curl -X GET http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Notes**:
- User can only access their own tasks
- Returns 403 if task exists but belongs to another user
- Returns 404 if task doesn't exist

---

### PUT /tasks/{task_id}

Update an existing task.

**Authentication**: Required (JWT token)

**Path Parameters**:
- `task_id` (integer): Task ID

**Request Body** (all fields optional):
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "is_completed": true
}
```

**Validation**:
- Title: 1-255 characters (if provided)
- Description: max 10,000 characters (if provided)
- is_completed: boolean (if provided)

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Updated task title",
  "description": "Updated description",
  "is_completed": true,
  "created_at": "2026-02-16T10:30:00Z",
  "updated_at": "2026-02-16T12:00:00Z"
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

401 Unauthorized:
```json
{
  "detail": "Invalid or expired token"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to access this task"
}
```

404 Not Found:
```json
{
  "detail": "Task not found"
}
```

**Example cURL**:
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated title","is_completed":true}'
```

**Notes**:
- Only provided fields are updated (partial update)
- updated_at timestamp is automatically updated
- User can only update their own tasks

---

### DELETE /tasks/{task_id}

Delete an existing task.

**Authentication**: Required (JWT token)

**Path Parameters**:
- `task_id` (integer): Task ID

**Success Response** (204 No Content):
- Empty response body

**Error Responses**:

401 Unauthorized:
```json
{
  "detail": "Invalid or expired token"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to access this task"
}
```

404 Not Found:
```json
{
  "detail": "Task not found"
}
```

**Example cURL**:
```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Notes**:
- Task is permanently deleted
- User can only delete their own tasks
- Returns 204 with no body on success

---

## Error Handling

### Standard Error Format

All errors return JSON with a `detail` field:

```json
{
  "detail": "Error message"
}
```

### Validation Errors

Pydantic validation errors return detailed information:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

### HTTP Status Codes

- **200 OK**: Successful GET/PUT request
- **201 Created**: Successful POST request
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## Authentication Flow

1. **Register**: POST /auth/register → Receive JWT token
2. **Login**: POST /auth/login → Receive JWT token
3. **Use Token**: Include in Authorization header for all /tasks requests
4. **Token Expiration**: Token expires after 24 hours, user must login again
5. **Logout**: POST /auth/logout + remove token from client storage

---

## Testing with Postman

### Setup

1. Create a new Postman collection
2. Add environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (will be set automatically)

### Test Sequence

1. **Register User**:
   - POST {{base_url}}/auth/register
   - Save `access_token` to `token` variable

2. **Create Task**:
   - POST {{base_url}}/tasks
   - Authorization: Bearer {{token}}

3. **Get Tasks**:
   - GET {{base_url}}/tasks
   - Authorization: Bearer {{token}}

4. **Update Task**:
   - PUT {{base_url}}/tasks/1
   - Authorization: Bearer {{token}}

5. **Delete Task**:
   - DELETE {{base_url}}/tasks/1
   - Authorization: Bearer {{token}}

---

## Rate Limiting

Currently not implemented. Consider adding for production:
- Rate limit per IP address
- Rate limit per user (based on JWT)
- Different limits for auth vs task endpoints

---

## Pagination

Currently not implemented. For large task lists, consider adding:
- Query parameters: `?page=1&limit=20`
- Response includes: `total`, `page`, `pages`, `items`

---

## Filtering and Sorting

Currently not implemented. Potential enhancements:
- Filter by completion status: `?is_completed=true`
- Sort by field: `?sort=created_at&order=desc`
- Search by title: `?search=documentation`

---

## Conclusion

This API follows RESTful conventions with clear, predictable endpoints. All endpoints are documented with examples and error cases. Authentication is handled via JWT tokens with proper authorization checks on all protected resources.
