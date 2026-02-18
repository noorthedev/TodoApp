# Authorization Dependency Pattern

**Feature**: 003-auth-isolation
**Date**: 2026-02-16
**Status**: Validated and Documented

## Overview

This document describes the centralized authorization pattern used throughout the Task Management API. All authorization logic is implemented using FastAPI's dependency injection system, ensuring consistency, type safety, and fail-secure behavior.

## Core Pattern: Dependency Injection

### Single Source of Truth

All authorization logic is centralized in a single dependency function:

**Location**: `backend/src/utils/jwt.py`
**Function**: `get_current_user(credentials, session) -> User`

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Dependency to get the current authenticated user.

    Args:
        credentials: HTTP Bearer token from request header
        session: Database session

    Returns:
        Current authenticated User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
```

### Usage Pattern

Every protected endpoint uses the same dependency injection pattern:

```python
from fastapi import APIRouter, Depends
from src.models.user import User
from src.utils.jwt import get_current_user

router = APIRouter()

@router.get("/protected-resource")
async def get_protected_resource(
    current_user: User = Depends(get_current_user),  # Authorization dependency
    session: AsyncSession = Depends(get_session),
):
    """Protected endpoint - requires authentication."""
    # current_user is guaranteed to be authenticated
    # Use current_user.id to filter/verify ownership
    pass
```

## Audit Results

### Task Endpoints (backend/src/api/tasks.py)

All 5 task endpoints consistently use the authorization dependency:

1. **GET /tasks** (List all tasks)
   ```python
   async def get_tasks(
       current_user: User = Depends(get_current_user),  ✓
       session: AsyncSession = Depends(get_session),
   ):
   ```

2. **POST /tasks** (Create task)
   ```python
   async def create_task(
       task_data: TaskCreate,
       current_user: User = Depends(get_current_user),  ✓
       session: AsyncSession = Depends(get_session),
   ):
   ```

3. **GET /tasks/{task_id}** (Get specific task)
   ```python
   async def get_task(
       task_id: int,
       current_user: User = Depends(get_current_user),  ✓
       session: AsyncSession = Depends(get_session),
   ):
   ```

4. **PUT /tasks/{task_id}** (Update task)
   ```python
   async def update_task(
       task_id: int,
       task_data: TaskUpdate,
       current_user: User = Depends(get_current_user),  ✓
       session: AsyncSession = Depends(get_session),
   ):
   ```

5. **DELETE /tasks/{task_id}** (Delete task)
   ```python
   async def delete_task(
       task_id: int,
       current_user: User = Depends(get_current_user),  ✓
       session: AsyncSession = Depends(get_session),
   ):
   ```

**Result**: ✅ All task endpoints consistently use the authorization dependency

### Auth Endpoints (backend/src/api/auth.py)

Public endpoints that intentionally do NOT use authorization:

1. **POST /auth/register** - Public (creates new user)
2. **POST /auth/login** - Public (authenticates user)
3. **POST /auth/logout** - Public (informational only)

**Result**: ✅ Auth endpoints correctly omit authorization (public by design)

### Authorization Logic Duplication Check

**Locations Checked**:
- `backend/src/api/tasks.py` - Uses `Depends(get_current_user)` only
- `backend/src/api/auth.py` - No authorization logic (public endpoints)
- `backend/src/utils/jwt.py` - Single implementation of authorization logic

**Result**: ✅ No duplication found - all authorization logic is centralized in `get_current_user`

## Benefits of This Pattern

### 1. Consistency
- All protected endpoints use the exact same authorization mechanism
- No variation in how authentication is checked
- Reduces risk of security gaps from inconsistent implementation

### 2. Type Safety
- FastAPI validates dependencies at startup
- Missing `current_user` parameter causes type error during development
- IDE autocomplete and type checking work correctly

### 3. Fail-Secure by Default
- Forgetting to add the dependency causes immediate failure
- No silent authorization bypass possible
- Developers must explicitly add authorization to each endpoint

### 4. Maintainability
- Single location to update authorization logic
- Changes propagate automatically to all endpoints
- Easy to add new authorization requirements (e.g., roles, permissions)

### 5. Testability
- Can mock `get_current_user` dependency in tests
- Consistent test patterns across all endpoints
- Easy to test authorization failures

## Fail-Secure Behavior

### What Happens If Developer Forgets Authorization?

**Scenario**: Developer creates new endpoint without `current_user` dependency

```python
@router.get("/new-endpoint")
async def new_endpoint(session: AsyncSession = Depends(get_session)):
    # Forgot to add current_user dependency!
    # Trying to access current_user will cause NameError
    tasks = await session.execute(select(Task).where(Task.user_id == current_user.id))
    # NameError: name 'current_user' is not defined
```

**Result**:
- Code fails immediately with `NameError` during development
- FastAPI won't start if type hints are used incorrectly
- No silent authorization bypass - failure is loud and obvious

### Type Safety Example

```python
# CORRECT - Type-safe and authorized
@router.get("/tasks")
async def get_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # current_user is guaranteed to be User object
    tasks = await session.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    return tasks

# WRONG - Will cause type error
@router.get("/tasks")
async def get_tasks(
    session: AsyncSession = Depends(get_session),
):
    # current_user is not defined - NameError at runtime
    tasks = await session.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    return tasks
```

## Adding New Protected Endpoints

### Step-by-Step Guide

1. **Import the dependency**:
   ```python
   from src.utils.jwt import get_current_user
   from src.models.user import User
   ```

2. **Add the dependency to your endpoint**:
   ```python
   @router.get("/your-endpoint")
   async def your_endpoint(
       current_user: User = Depends(get_current_user),  # Add this line
       session: AsyncSession = Depends(get_session),
   ):
   ```

3. **Use current_user for authorization**:
   ```python
   # Filter queries by user_id
   result = await session.execute(
       select(YourModel).where(YourModel.user_id == current_user.id)
   )

   # Verify ownership
   if resource.user_id != current_user.id:
       raise HTTPException(status_code=403, detail="Not authorized")
   ```

4. **Test the endpoint**:
   - Test with valid token (should succeed)
   - Test with missing token (should return 403)
   - Test with expired token (should return 401)
   - Test with tampered token (should return 401)

### Complete Example

See `specs/003-auth-isolation/examples/new-endpoint.py` for a complete working example.

## Common Patterns

### Pattern 1: List Resources (Filter by User)

```python
@router.get("/resources", response_model=ResourceList)
async def get_resources(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get all resources for authenticated user."""
    result = await session.execute(
        select(Resource)
        .where(Resource.user_id == current_user.id)
        .order_by(Resource.created_at.desc())
    )
    resources = result.scalars().all()
    return ResourceList(resources=resources, total=len(resources))
```

### Pattern 2: Create Resource (Force User ID)

```python
@router.post("/resources", response_model=ResourceResponse)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create new resource for authenticated user."""
    new_resource = Resource(
        user_id=current_user.id,  # Force authenticated user_id
        title=resource_data.title,
        # ... other fields
    )
    session.add(new_resource)
    await session.commit()
    await session.refresh(new_resource)
    return ResourceResponse.model_validate(new_resource)
```

### Pattern 3: Get Specific Resource (Verify Ownership)

```python
@router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get specific resource by ID."""
    # Fetch resource
    result = await session.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Verify ownership
    if resource.user_id != current_user.id:
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to access "
            f"resource {resource_id} owned by user {resource.user_id}"
        )
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    return ResourceResponse.model_validate(resource)
```

### Pattern 4: Update Resource (Verify Ownership)

```python
@router.put("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_data: ResourceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update resource."""
    # Fetch resource
    result = await session.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Verify ownership
    if resource.user_id != current_user.id:
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to update "
            f"resource {resource_id} owned by user {resource.user_id}"
        )
        raise HTTPException(status_code=403, detail="Not authorized to update this resource")

    # Update fields
    if resource_data.title is not None:
        resource.title = resource_data.title
    # ... update other fields

    session.add(resource)
    await session.commit()
    await session.refresh(resource)

    return ResourceResponse.model_validate(resource)
```

### Pattern 5: Delete Resource (Verify Ownership)

```python
@router.delete("/resources/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete resource."""
    # Fetch resource
    result = await session.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Verify ownership
    if resource.user_id != current_user.id:
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to delete "
            f"resource {resource_id} owned by user {resource.user_id}"
        )
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")

    await session.delete(resource)
    await session.commit()
```

## Security Checklist for New Endpoints

When adding a new protected endpoint, verify:

- [ ] Endpoint uses `current_user: User = Depends(get_current_user)` parameter
- [ ] List operations filter by `current_user.id`
- [ ] Create operations force `user_id=current_user.id`
- [ ] Read/Update/Delete operations verify ownership before proceeding
- [ ] Authorization failures are logged with `logger.warning()`
- [ ] 403 Forbidden returned for ownership violations
- [ ] 404 Not Found returned for non-existent resources
- [ ] Tests cover: valid token, missing token, expired token, cross-user access

## Future Enhancements

### Role-Based Access Control (RBAC)

When adding roles, the pattern extends naturally:

```python
from src.utils.jwt import get_current_user, require_role

@router.get("/admin/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("admin")),  # Additional authorization
    session: AsyncSession = Depends(get_session),
):
    """Admin-only endpoint to get all users."""
    # Only admins can reach this code
    pass
```

### Permission-Based Access

```python
from src.utils.jwt import get_current_user, require_permission

@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("resource:delete")),
    session: AsyncSession = Depends(get_session),
):
    """Delete resource (requires delete permission)."""
    pass
```

## References

- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- Implementation: `backend/src/utils/jwt.py`, `backend/src/api/tasks.py`
- Architecture: `specs/003-auth-isolation/architecture.md`
- Review Findings: `specs/003-auth-isolation/review-findings.md`
