# Research: Backend API & Database Layer

**Feature**: Backend API & Database Layer
**Date**: 2026-02-16
**Status**: Complete

## Overview

This document captures the research and technical decisions made for implementing the backend API and database layer. All technology choices align with the project constitution and hackathon requirements.

## Technology Decisions

### 1. API Framework: FastAPI

**Decision**: Use FastAPI as the backend web framework

**Rationale**:
- High performance with async/await support (critical for database operations)
- Automatic OpenAPI documentation generation
- Built-in request/response validation with Pydantic
- Type hints provide excellent IDE support and catch errors early
- Modern Python framework with active community
- Native support for dependency injection (useful for database sessions)

**Alternatives Considered**:
- **Flask**: More mature but lacks async support and automatic validation
- **Django REST Framework**: Full-featured but heavier, includes ORM we don't need (using SQLModel)
- **Starlette**: Lower-level, FastAPI is built on top of it with better DX

**Implementation Notes**:
- Use async route handlers for all database operations
- Leverage dependency injection for database sessions and authentication
- Use Pydantic models for request/response validation
- Enable automatic OpenAPI docs at `/docs` endpoint

---

### 2. ORM: SQLModel

**Decision**: Use SQLModel for database models and queries

**Rationale**:
- Combines SQLAlchemy (mature ORM) with Pydantic (validation)
- Type-safe models with Python type hints
- Async support via SQLAlchemy 2.0
- Single model definition serves as both ORM model and Pydantic schema
- Reduces code duplication between database and API layers
- Excellent integration with FastAPI

**Alternatives Considered**:
- **SQLAlchemy directly**: More verbose, requires separate Pydantic models
- **Tortoise ORM**: Async-first but less mature, smaller ecosystem
- **Raw SQL with asyncpg**: Maximum performance but no type safety, more boilerplate

**Implementation Notes**:
- Define models with SQLModel table=True
- Use async session management
- Leverage Pydantic validation in models
- Use select() queries for type-safe database operations

---

### 3. Database Driver: asyncpg

**Decision**: Use asyncpg for PostgreSQL async connections

**Rationale**:
- Fastest PostgreSQL driver for Python
- Native async/await support
- Required for SQLModel async operations
- Excellent performance for concurrent requests
- Well-maintained and stable

**Alternatives Considered**:
- **psycopg2**: Synchronous only, blocks event loop
- **psycopg3**: Async support but newer, less battle-tested

**Implementation Notes**:
- Connection string format: `postgresql+asyncpg://user:pass@host/db`
- Use connection pooling for efficiency
- Configure pool size based on expected load

---

### 4. Authentication: JWT with python-jose

**Decision**: Use JWT tokens for stateless authentication with python-jose library

**Rationale**:
- Stateless authentication (no server-side session storage)
- Tokens can be verified without database lookup
- Standard format (RFC 7519) with wide library support
- python-jose provides cryptographic signing and verification
- Integrates well with FastAPI security utilities

**Alternatives Considered**:
- **Session-based auth**: Requires server-side storage, doesn't scale horizontally
- **PyJWT**: Similar but python-jose has better FastAPI integration

**Implementation Notes**:
- Use HS256 algorithm (HMAC with SHA-256)
- Store secret key in environment variable
- Set reasonable expiration time (24 hours default)
- Include user_id and email in token payload
- Use HTTPBearer security scheme in FastAPI

---

### 5. Password Hashing: passlib with bcrypt

**Decision**: Use passlib with bcrypt for password hashing

**Rationale**:
- Industry-standard password hashing
- Bcrypt is designed to be slow (resistant to brute-force)
- Automatic salt generation
- passlib provides high-level API with best practices
- Future-proof (can upgrade to argon2 if needed)

**Alternatives Considered**:
- **argon2**: More modern but requires C library installation
- **scrypt**: Good but bcrypt is more widely adopted
- **PBKDF2**: Weaker than bcrypt for password hashing

**Implementation Notes**:
- Use CryptContext with bcrypt scheme
- Let passlib handle salt generation automatically
- Never store plaintext passwords
- Hash on registration, verify on login

---

### 6. Database: Neon Serverless PostgreSQL

**Decision**: Use Neon Serverless PostgreSQL (already specified in requirements)

**Rationale**:
- Serverless architecture (auto-scaling, pay-per-use)
- PostgreSQL compatibility (standard SQL, ACID compliance)
- Built-in connection pooling
- Automatic backups and point-in-time recovery
- Low latency with edge locations
- No infrastructure management required

**Implementation Notes**:
- Use provided connection string from Neon console
- Enable SSL mode (required by Neon)
- Configure connection pool size appropriately
- Use async driver (asyncpg) for best performance

---

### 7. Input Validation: Pydantic

**Decision**: Use Pydantic for request/response validation

**Rationale**:
- Built into FastAPI (automatic validation)
- Type-safe with Python type hints
- Clear error messages for validation failures
- Supports complex validation rules
- Can define custom validators
- Integrates with SQLModel models

**Implementation Notes**:
- Define separate schemas for Create, Update, and Response
- Use Field() for constraints (min_length, max_length, etc.)
- Add custom validators for business logic
- Sanitize input to prevent XSS attacks

---

### 8. Error Handling: FastAPI Exception Handlers

**Decision**: Use FastAPI's exception handler system

**Rationale**:
- Centralized error handling
- Consistent error response format
- Can catch specific exception types
- Prevents internal details from leaking
- Supports custom exception classes

**Implementation Notes**:
- Create custom exception handlers for common errors
- Return standardized JSON error responses
- Use appropriate HTTP status codes
- Log errors for debugging
- Don't expose stack traces in production

---

### 9. API Documentation: OpenAPI (Swagger)

**Decision**: Use FastAPI's automatic OpenAPI generation

**Rationale**:
- Zero-effort documentation (generated from code)
- Interactive API testing via Swagger UI
- Standard format (OpenAPI 3.0)
- Always up-to-date with code
- Can export for external tools

**Implementation Notes**:
- Add docstrings to route handlers
- Use response_model for type information
- Document error responses
- Include example requests/responses
- Available at `/docs` endpoint

---

### 10. Testing: pytest with pytest-asyncio

**Decision**: Use pytest for testing with async support

**Rationale**:
- Industry-standard Python testing framework
- pytest-asyncio enables async test functions
- Rich fixture system for test setup
- Excellent assertion introspection
- Large ecosystem of plugins

**Implementation Notes**:
- Use pytest fixtures for database setup/teardown
- Test async functions with @pytest.mark.asyncio
- Use TestClient for API endpoint testing
- Mock external dependencies
- Aim for high test coverage

---

## Architecture Patterns

### Dependency Injection

Use FastAPI's dependency injection for:
- Database session management (get_session)
- Authentication (get_current_user)
- Configuration access

### Async/Await

Use async/await throughout:
- All route handlers are async
- All database operations are async
- Use async context managers for sessions

### Layered Architecture

Clear separation of concerns:
- **API Layer** (routes): Handle HTTP requests/responses
- **Schema Layer** (Pydantic): Validate and serialize data
- **Model Layer** (SQLModel): Define database structure
- **Utility Layer**: Reusable functions (JWT, hashing, etc.)

---

## Performance Considerations

### Database Indexes

Add indexes on:
- `users.email` (unique, for login lookups)
- `tasks.user_id` (for filtering user's tasks)

### Connection Pooling

Configure appropriate pool size:
- Default: 5-10 connections
- Adjust based on concurrent request load
- Monitor connection usage

### Query Optimization

- Use select() with filters instead of loading all records
- Avoid N+1 queries (use joins/eager loading if needed)
- Limit result sets with pagination

---

## Security Best Practices

### Input Sanitization

- Remove HTML tags from user input
- Limit string lengths
- Validate email format
- Escape special characters

### SQL Injection Prevention

- Use parameterized queries (SQLModel handles this)
- Never concatenate user input into SQL
- Validate all input types

### Authentication Security

- Hash passwords with bcrypt
- Use secure JWT secret (32+ random bytes)
- Set token expiration
- Verify tokens on every protected request
- Don't include sensitive data in JWT payload

### Authorization

- Check user ownership on all resource access
- Return 403 Forbidden for unauthorized access
- Filter queries by user_id
- Never trust client-provided user_id

---

## Deployment Considerations

### Environment Variables

Required variables:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT signing
- `JWT_ALGORITHM`: Algorithm (default: HS256)
- `JWT_EXPIRATION_HOURS`: Token lifetime (default: 24)
- `CORS_ORIGINS`: Allowed frontend origins
- `DEBUG`: Enable debug mode (default: False)

### CORS Configuration

- Allow frontend origin (http://localhost:3000 for dev)
- Enable credentials for cookie/auth headers
- Restrict in production to actual frontend domain

### Logging

- Log authentication events (login, registration, failures)
- Log task operations (create, update, delete)
- Use structured logging for easier parsing
- Don't log sensitive data (passwords, tokens)

---

## Conclusion

All technology choices are well-established, production-ready, and align with the project constitution. The stack provides excellent developer experience with type safety, automatic validation, and comprehensive documentation. Performance and security requirements are met through async operations, proper indexing, and industry-standard security practices.

**Next Steps**: Proceed to Phase 1 (Design & Contracts) to define data models and API contracts.
