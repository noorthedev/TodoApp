# Research & Technology Decisions

**Feature**: Phase 2 Todo Full-Stack Web Application
**Date**: 2026-02-15
**Status**: Complete

## Overview

This document consolidates research findings for key technology decisions and integration patterns needed for the Phase 2 Todo application. All research tasks have been completed and decisions documented.

## Research Task 1: Better Auth JWT Integration

### Question
How to configure Better Auth to issue JWT tokens and share the secret between frontend and backend?

### Findings

**Better Auth JWT Configuration**:
- Better Auth supports JWT tokens through the `@better-auth/jwt` plugin
- Configuration requires a shared secret key stored in environment variables
- JWT tokens contain user identity claims (user_id, email, expiration)
- Tokens are issued on successful login and returned to the client

**Implementation Pattern**:
```typescript
// Frontend: Better Auth client configuration
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  plugins: [jwtPlugin()],
})
```

**Backend Integration**:
- Better Auth can be integrated with FastAPI as an authentication provider
- Alternative: Implement custom JWT generation using python-jose
- JWT secret must match between frontend and backend for verification

**Token Structure**:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Decision

**Use Better Auth for frontend authentication with custom JWT verification in FastAPI backend.**

**Rationale**:
- Better Auth handles frontend auth flows (signup, login, session management)
- FastAPI backend implements custom JWT verification using python-jose
- Shared JWT_SECRET environment variable enables token validation
- Simpler than full Better Auth backend integration for hackathon timeline

**Configuration Requirements**:
- Frontend: `NEXT_PUBLIC_API_URL`, `BETTER_AUTH_SECRET`
- Backend: `JWT_SECRET` (same value as BETTER_AUTH_SECRET)
- JWT algorithm: HS256 (HMAC with SHA-256)
- Token expiration: 24 hours (configurable)

---

## Research Task 2: FastAPI JWT Verification

### Question
Best practices for JWT verification middleware in FastAPI and dependency injection for authenticated user context?

### Findings

**JWT Library Comparison**:

| Library | Pros | Cons | Recommendation |
|---------|------|------|----------------|
| python-jose | Well-documented, widely used, supports multiple algorithms | Slightly heavier | ✅ Recommended |
| PyJWT | Lightweight, simple API | Less feature-rich | Alternative |
| authlib | Comprehensive OAuth/JWT support | Overkill for simple JWT | Not needed |

**Middleware vs Dependency Pattern**:
- **Middleware**: Runs on every request, can be inefficient
- **Dependency Injection**: Runs only on protected routes, more flexible
- **Recommendation**: Use FastAPI dependency injection

**Implementation Pattern**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401)

# Usage in route
@app.get("/tasks")
async def get_tasks(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    # Query tasks for this user
```

### Decision

**Use python-jose with FastAPI dependency injection for JWT verification.**

**Rationale**:
- python-jose is well-tested and widely used in FastAPI projects
- Dependency injection provides clean separation and testability
- HTTPBearer security scheme handles Authorization header parsing
- Easy to mock for testing

**Implementation Details**:
- Create `get_current_user` dependency in `backend/src/utils/jwt.py`
- Use `Depends(get_current_user)` on all protected routes
- Return user context (user_id, email) for use in route handlers
- Raise HTTPException with 401 status for invalid tokens

---

## Research Task 3: SQLModel with Neon PostgreSQL

### Question
Connection pooling, async vs sync operations, and migration strategy for SQLModel with Neon Serverless?

### Findings

**Neon Connection Pooling**:
- Neon provides built-in connection pooling via connection string
- Use pooled connection string format: `postgresql://user:pass@host/db?sslmode=require`
- No additional pooling library needed for basic use cases
- For high concurrency, consider pgbouncer (optional)

**Async vs Sync SQLModel**:
- SQLModel supports both sync and async operations
- FastAPI works best with async for I/O operations
- Async requires `asyncpg` driver instead of `psycopg2`
- Async pattern: `async with AsyncSession(engine) as session`

**Async Recommendation**:
```python
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

# Async engine
engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True
)

# Async session dependency
async def get_session():
    async with AsyncSession(engine) as session:
        yield session
```

**Migration Strategy Options**:

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| SQLModel.metadata.create_all() | Simple, fast for dev | No version control | ✅ Development |
| Alembic | Full migration management | Complex setup | Production (future) |
| Manual SQL scripts | Explicit control | Manual tracking | Production (Phase 2) |

### Decision

**Use async SQLModel with asyncpg driver and SQLModel.metadata.create_all() for development.**

**Rationale**:
- Async operations align with FastAPI best practices
- Neon's built-in pooling sufficient for Phase 2 scale
- create_all() enables rapid iteration during development
- Manual migration scripts for production deployment

**Implementation Details**:
- Database URL: `postgresql+asyncpg://user:pass@host/db?sslmode=require`
- Async session dependency for all database operations
- Models defined with SQLModel (inherits from SQLAlchemy)
- Create tables on startup: `await SQLModel.metadata.create_all(engine)`

---

## Research Task 4: Next.js App Router Authentication

### Question
Client vs Server Components for auth state, middleware for route protection, and token storage strategy?

### Findings

**Client vs Server Components**:
- **Server Components**: Default in App Router, better performance, no client JS
- **Client Components**: Needed for interactivity, state management, browser APIs
- **Auth State**: Requires Client Components (uses localStorage, React state)

**Component Strategy**:
```typescript
// Server Component (default)
export default async function DashboardPage() {
  // Can fetch data server-side
  return <TaskList /> // Client component for interactivity
}

// Client Component (for auth state)
'use client'
export function TaskList() {
  const { user } = useAuth() // Client-side hook
  // Interactive UI
}
```

**Route Protection Options**:

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| Next.js Middleware | Runs before page load, fast | Limited to edge runtime | ✅ Recommended |
| Client-side check | Simple | Flash of wrong content | Supplement only |
| Server Component check | Type-safe | Slower than middleware | Backup |

**Middleware Pattern**:
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('token') // or check localStorage
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}
```

**Token Storage**:
- **localStorage**: Simple, persists across tabs, vulnerable to XSS
- **httpOnly cookies**: More secure, requires backend cookie handling
- **sessionStorage**: Lost on tab close, not suitable for auth

### Decision

**Use Client Components for auth state with localStorage token storage and Next.js middleware for route protection.**

**Rationale**:
- Client Components necessary for auth state management
- localStorage simpler for hackathon timeline
- Next.js middleware provides fast route protection
- React Context + custom hooks for clean auth API

**Implementation Details**:
- Auth context provider wraps app in root layout
- Custom `useAuth()` hook for components
- Middleware protects `/dashboard/*` routes
- Token stored in localStorage as `auth_token`

---

## Research Task 5: API Client Configuration

### Question
Axios interceptors for JWT injection, token refresh flow, and error handling strategies?

### Findings

**Axios Interceptor Pattern**:
```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

// Request interceptor: inject JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

**Token Refresh Flow**:
- **Option 1**: Refresh token pattern (requires backend support)
- **Option 2**: Silent re-authentication (requires user credentials)
- **Option 3**: Redirect to login on expiration (simplest)

**Error Handling Strategy**:
- 401 Unauthorized: Clear token, redirect to login
- 403 Forbidden: Show "Access denied" message
- 400 Bad Request: Show validation errors
- 500 Server Error: Show generic error message
- Network Error: Show "Connection failed" message

### Decision

**Use Axios with request/response interceptors and redirect-on-expiration strategy.**

**Rationale**:
- Interceptors provide clean separation of concerns
- Automatic token injection on all requests
- Centralized error handling
- Redirect-on-expiration simplest for Phase 2

**Implementation Details**:
- API client in `frontend/src/lib/api.ts`
- Request interceptor adds Authorization header
- Response interceptor handles 401 (redirect to login)
- Custom error messages for different status codes
- No token refresh (future enhancement)

---

## Technology Stack Summary

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Auth**: Better Auth client with JWT plugin
- **API Client**: Axios with interceptors
- **State Management**: React Context + custom hooks
- **Token Storage**: localStorage
- **Route Protection**: Next.js middleware

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Auth**: Custom JWT verification with python-jose
- **ORM**: SQLModel (async)
- **Database Driver**: asyncpg
- **Validation**: Pydantic

### Database
- **Provider**: Neon Serverless PostgreSQL
- **Connection**: Pooled connection string
- **Migration**: SQLModel.metadata.create_all() (dev), manual scripts (prod)

### Shared
- **JWT Algorithm**: HS256
- **JWT Secret**: Shared via environment variables
- **Token Expiration**: 24 hours
- **API Protocol**: REST over HTTPS

---

## Implementation Priorities

1. **Phase 1**: Environment setup and database connection
2. **Phase 2**: Authentication (Better Auth frontend + JWT backend)
3. **Phase 3**: Database models and CRUD endpoints
4. **Phase 4**: JWT verification middleware and authorization
5. **Phase 5**: Frontend UI and API integration
6. **Phase 6**: Testing and security validation

---

## Open Questions Resolved

All research tasks completed. No remaining NEEDS CLARIFICATION markers.

**Status**: ✅ Ready for Phase 1 (Design & Contracts)
