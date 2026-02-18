# API Contracts Documentation

**Feature**: Phase 2 Todo Full-Stack Web Application
**Date**: 2026-02-15
**OpenAPI Version**: 3.0.3

## Overview

This directory contains the API contract specifications for the Phase 2 Todo application. The API follows RESTful principles and uses JWT-based authentication for secure access to user-specific resources.

## Files

- `openapi.yaml` - Complete OpenAPI 3.0 specification with all endpoints, schemas, and examples

## API Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://api.phase2-todo.example.com` (to be configured)

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### Obtaining a Token

1. Register a new user: `POST /auth/register`
2. Login with credentials: `POST /auth/login`
3. Receive JWT token in response
4. Include token in all subsequent requests

### Token Format

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-02-15T10:30:00Z"
  }
}
```

## Endpoints Summary

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login and get JWT token | No |
| POST | `/auth/logout` | Logout (invalidate session) | Yes |

### Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks` | Get all tasks for user | Yes |
| POST | `/tasks` | Create new task | Yes |
| GET | `/tasks/{task_id}` | Get specific task | Yes |
| PUT | `/tasks/{task_id}` | Update task | Yes |
| DELETE | `/tasks/{task_id}` | Delete task | Yes |

## Request/Response Examples

### Register User

**Request**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-02-15T10:30:00Z"
  }
}
```

### Login User

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-02-15T10:30:00Z"
  }
}
```

### Create Task

**Request**:
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the Phase 2 Todo application"
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for the Phase 2 Todo application",
  "is_completed": false,
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T10:30:00Z"
}
```

### Get All Tasks

**Request**:
```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Complete project documentation",
      "description": "Write comprehensive documentation for the Phase 2 Todo application",
      "is_completed": false,
      "created_at": "2026-02-15T10:30:00Z",
      "updated_at": "2026-02-15T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "title": "Review code changes",
      "description": null,
      "is_completed": true,
      "created_at": "2026-02-15T11:00:00Z",
      "updated_at": "2026-02-15T11:30:00Z"
    }
  ],
  "total": 2
}
```

### Update Task

**Request**:
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "title": "Update project documentation",
    "is_completed": true
  }'
```

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Update project documentation",
  "description": "Write comprehensive documentation for the Phase 2 Todo application",
  "is_completed": true,
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-15T12:00:00Z"
}
```

### Delete Task

**Request**:
```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (204 No Content):
```
(empty response body)
```

## Error Responses

### 400 Bad Request (Validation Error)

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

### 401 Unauthorized (Invalid Token)

```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden (Authorization Error)

```json
{
  "detail": "Not authorized to access this task"
}
```

### 404 Not Found

```json
{
  "detail": "Task not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side error |

## Data Validation Rules

### User Registration
- Email: Must be valid email format, unique across all users
- Password: Minimum 8 characters, maximum 100 characters

### Task Creation/Update
- Title: Required, 1-255 characters
- Description: Optional, maximum 10,000 characters
- is_completed: Boolean (true/false)

## Security Considerations

### Authentication
- All passwords are hashed before storage (never stored plaintext)
- JWT tokens expire after 24 hours (configurable)
- Tokens must be included in Authorization header for protected endpoints

### Authorization
- Users can only access their own tasks
- All task queries are filtered by authenticated user_id
- Attempting to access another user's task returns 403 Forbidden

### Input Validation
- All request bodies are validated using Pydantic schemas
- Invalid data returns 400 Bad Request with detailed error messages
- SQL injection prevented by SQLModel parameterized queries
- XSS prevented by proper output encoding

## Testing the API

### Using cURL

See examples above for cURL commands.

### Using Postman

1. Import `openapi.yaml` into Postman
2. Set environment variable `baseUrl` to `http://localhost:8000`
3. Register a user and save the token
4. Set Authorization header: `Bearer <token>`
5. Test all endpoints

### Using Swagger UI

When the backend is running, visit:
```
http://localhost:8000/docs
```

This provides an interactive API documentation interface where you can:
- View all endpoints and schemas
- Try out API calls directly from the browser
- See request/response examples

## CORS Configuration

The backend must be configured to allow requests from the frontend origin:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rate Limiting

Currently not implemented. For production, consider:
- Rate limiting per IP address
- Rate limiting per user (after authentication)
- Throttling for expensive operations

## Versioning

Current API version: v1 (implicit in base URL)

Future versions can be added as:
- `/v2/tasks` (URL versioning)
- `Accept: application/vnd.api+json; version=2` (header versioning)

## Support

For API issues or questions:
- Check the OpenAPI specification: `openapi.yaml`
- Review the data model: `../data-model.md`
- Consult the implementation plan: `../plan.md`

---

**Last Updated**: 2026-02-15
**Maintained By**: Phase 2 Todo Team
