# API Client Contract: Frontend UI & API Integration Layer

**Feature**: 004-frontend-ui-integration
**Date**: 2026-02-16
**Purpose**: Define the API client interface, interceptors, and error handling

## Overview

The API client is a centralized Axios instance that handles all HTTP communication with the backend API. It automatically attaches JWT tokens, handles errors consistently, and provides typed API functions.

---

## API Client Configuration

### Base Configuration

```typescript
// lib/api/client.ts

import axios, { AxiosInstance, AxiosError } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Environment Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API base URL (required)

**Configuration Options**:
- `baseURL`: Backend API endpoint
- `timeout`: Request timeout (10s default)
- `headers`: Default headers for all requests

---

## Request Interceptor (JWT Token Attachment)

### Purpose
Automatically attach JWT token to all authenticated requests

### Implementation

```typescript
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('auth_token');

    // Attach token to Authorization header if present
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
```

**Behavior**:
- Reads JWT token from localStorage
- Attaches token to `Authorization` header as `Bearer <token>`
- Runs before every request
- Does not block requests if token is missing (public endpoints)

---

## Response Interceptor (Error Handling)

### Purpose
Centralized error handling and token expiration detection

### Implementation

```typescript
apiClient.interceptors.response.use(
  (response) => {
    // Success response - return data directly
    return response;
  },
  (error: AxiosError<ErrorResponse>) => {
    // Handle different error scenarios

    // 401 Unauthorized - Token expired or invalid
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login?session_expired=true';
      return Promise.reject(new Error('Session expired. Please log in again.'));
    }

    // 403 Forbidden - Not authorized
    if (error.response?.status === 403) {
      return Promise.reject(new Error('You do not have permission to perform this action.'));
    }

    // 404 Not Found
    if (error.response?.status === 404) {
      return Promise.reject(new Error('Resource not found.'));
    }

    // 422 Validation Error
    if (error.response?.status === 422) {
      const message = error.response.data?.error?.message || 'Validation failed.';
      return Promise.reject(new Error(message));
    }

    // 500 Server Error
    if (error.response?.status === 500) {
      return Promise.reject(new Error('Server error. Please try again later.'));
    }

    // Network Error (no response)
    if (!error.response) {
      return Promise.reject(new Error('Network error. Please check your connection.'));
    }

    // Generic error
    const message = error.response?.data?.error?.message || 'An unexpected error occurred.';
    return Promise.reject(new Error(message));
  }
);
```

**Error Handling Strategy**:
- 401: Clear token, redirect to login
- 403: Permission denied message
- 404: Resource not found message
- 422: Validation error with details
- 500: Generic server error
- Network error: Connection issue message

---

## Authentication API Functions

### POST /auth/register

```typescript
// lib/api/auth.ts

export async function register(email: string, password: string): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/register', {
    email,
    password,
  });
  return response.data;
}
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Errors**:
- 400: Email already registered
- 422: Validation error (invalid email, weak password)

---

### POST /auth/login

```typescript
export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/login', {
    email,
    password,
  });
  return response.data;
}
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Errors**:
- 401: Invalid credentials
- 422: Validation error

---

### POST /auth/logout

```typescript
export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout');
  // Note: Backend logout is informational only (stateless JWT)
  // Actual logout happens by removing token from localStorage
}
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out. Please remove the token from client storage."
}
```

---

## Task API Functions

### GET /tasks

```typescript
// lib/api/tasks.ts

export async function getTasks(): Promise<TaskListResponse> {
  const response = await apiClient.get<TaskListResponse>('/tasks');
  return response.data;
}
```

**Request**: No body (JWT token in header)

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "title": "My task",
      "description": "Task description",
      "is_completed": false,
      "created_at": "2026-02-16T10:00:00Z",
      "updated_at": "2026-02-16T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Errors**:
- 401: Unauthorized (no token or expired token)

---

### POST /tasks

```typescript
export async function createTask(data: TaskFormState): Promise<TaskResponse> {
  const response = await apiClient.post<TaskResponse>('/tasks', {
    title: data.title,
    description: data.description || null,
  });
  return response.data;
}
```

**Request**:
```json
{
  "title": "New task",
  "description": "Optional description"
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "user_id": 1,
  "title": "New task",
  "description": "Optional description",
  "is_completed": false,
  "created_at": "2026-02-16T10:05:00Z",
  "updated_at": "2026-02-16T10:05:00Z"
}
```

**Errors**:
- 401: Unauthorized
- 422: Validation error (title missing, too long, etc.)

---

### GET /tasks/{id}

```typescript
export async function getTask(id: number): Promise<TaskResponse> {
  const response = await apiClient.get<TaskResponse>(`/tasks/${id}`);
  return response.data;
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "My task",
  "description": "Task description",
  "is_completed": false,
  "created_at": "2026-02-16T10:00:00Z",
  "updated_at": "2026-02-16T10:00:00Z"
}
```

**Errors**:
- 401: Unauthorized
- 403: Not authorized (task belongs to another user)
- 404: Task not found

---

### PUT /tasks/{id}

```typescript
export async function updateTask(id: number, data: Partial<TaskFormState>): Promise<TaskResponse> {
  const response = await apiClient.put<TaskResponse>(`/tasks/${id}`, data);
  return response.data;
}
```

**Request** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "is_completed": true
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "is_completed": true,
  "created_at": "2026-02-16T10:00:00Z",
  "updated_at": "2026-02-16T10:10:00Z"
}
```

**Errors**:
- 401: Unauthorized
- 403: Not authorized
- 404: Task not found
- 422: Validation error

---

### DELETE /tasks/{id}

```typescript
export async function deleteTask(id: number): Promise<void> {
  await apiClient.delete(`/tasks/${id}`);
}
```

**Response** (204 No Content): Empty body

**Errors**:
- 401: Unauthorized
- 403: Not authorized
- 404: Task not found

---

## Helper Functions

### Toggle Task Completion

```typescript
export async function toggleTaskComplete(task: Task): Promise<TaskResponse> {
  return updateTask(task.id, {
    is_completed: !task.is_completed,
  });
}
```

**Purpose**: Convenience function to toggle completion status

---

## Error Handling Pattern

### In Components

```typescript
try {
  setIsLoading(true);
  setError(null);

  const tasks = await getTasks();
  setTasks(tasks.tasks);

} catch (error) {
  // Error already formatted by interceptor
  setError(error instanceof Error ? error.message : 'An error occurred');

} finally {
  setIsLoading(false);
}
```

**Pattern**:
1. Set loading state
2. Clear previous errors
3. Call API function
4. Update state on success
5. Catch and display error
6. Clear loading state

---

## Type Definitions

```typescript
// lib/types/api.ts

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
  };
}

export interface TaskResponse {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
}

export interface ErrorResponse {
  error: {
    type: string;
    status_code: number;
    message: string;
    details?: any;
  };
}
```

---

## Testing Strategy

### Unit Tests

```typescript
// __tests__/lib/api/auth.test.ts

describe('Auth API', () => {
  it('should login successfully', async () => {
    // Mock axios response
    // Call login function
    // Assert response structure
  });

  it('should handle login error', async () => {
    // Mock axios error
    // Call login function
    // Assert error message
  });
});
```

### Integration Tests

```typescript
// __tests__/integration/api-client.test.ts

describe('API Client Interceptors', () => {
  it('should attach JWT token to requests', async () => {
    // Set token in localStorage
    // Make API call
    // Assert Authorization header present
  });

  it('should redirect on 401 error', async () => {
    // Mock 401 response
    // Make API call
    // Assert redirect to login
  });
});
```

---

## Security Considerations

1. **Token Storage**: localStorage (consider httpOnly cookies for production)
2. **HTTPS Only**: Enforce HTTPS in production
3. **CORS**: Backend must allow frontend origin
4. **Token Expiration**: Handled by interceptor (redirect to login)
5. **XSS Protection**: Sanitize all user inputs
6. **CSRF**: Not applicable (stateless JWT, no cookies)

---

## Performance Considerations

1. **Timeout**: 10s default (adjust based on network conditions)
2. **Request Cancellation**: Use AbortController for long requests
3. **Retry Logic**: Not implemented (consider for network errors)
4. **Caching**: Not implemented (consider SWR/React Query for future)

---

## Future Enhancements

- Token refresh mechanism
- Request retry with exponential backoff
- Request deduplication
- Response caching
- Request cancellation on component unmount
- Upload progress tracking
- Download progress tracking
