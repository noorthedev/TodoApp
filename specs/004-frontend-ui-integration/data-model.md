# Data Model: Frontend UI & API Integration Layer

**Feature**: 004-frontend-ui-integration
**Date**: 2026-02-16
**Type**: Frontend State Management

## Overview

This document defines the data structures and state management entities for the frontend application. Unlike backend data models, these represent client-side state, TypeScript interfaces, and React Context structures.

**Note**: The frontend does not define database schemas. It consumes data from the backend API (002-backend-api-db) and manages local application state.

---

## State Entities

### 1. User Session (Authentication State)

**Purpose**: Represents the authenticated user's session and authentication status

**TypeScript Interface**:
```typescript
interface UserSession {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  expiresAt: number | null; // Unix timestamp
}

interface User {
  id: number;
  email: string;
}
```

**State Management**: Managed by AuthContext

**Lifecycle**:
- Created: On successful login or registration
- Updated: On token refresh (future enhancement)
- Destroyed: On logout or token expiration

**Storage**: JWT token stored in localStorage, session state in React Context

**Validation Rules**:
- `isAuthenticated` must be true if `token` is present
- `token` must be valid JWT format
- `expiresAt` must be in the future for active sessions

---

### 2. Task (Task Entity)

**Purpose**: Represents a task item from the backend API

**TypeScript Interface**:
```typescript
interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string; // ISO 8601 format
  updated_at: string; // ISO 8601 format
}
```

**State Management**: Managed by TaskContext or local component state

**Lifecycle**:
- Fetched: From GET /tasks or GET /tasks/{id}
- Created: Via POST /tasks
- Updated: Via PUT /tasks/{id}
- Deleted: Via DELETE /tasks/{id}

**Validation Rules**:
- `title` is required, max 200 characters
- `description` is optional, max 1000 characters
- `is_completed` defaults to false
- `user_id` must match authenticated user (enforced by backend)

**Relationships**:
- Belongs to User (via user_id)
- Filtered by authenticated user on frontend

---

### 3. Task List State

**Purpose**: Represents the collection of tasks with metadata

**TypeScript Interface**:
```typescript
interface TaskListState {
  tasks: Task[];
  total: number;
  isLoading: boolean;
  error: string | null;
}
```

**State Management**: Managed by TaskContext

**Lifecycle**:
- Initialized: Empty array on mount
- Loaded: Populated from GET /tasks
- Updated: When tasks are created, updated, or deleted

**Validation Rules**:
- `tasks` array must contain only tasks belonging to authenticated user
- `total` must match `tasks.length`
- `isLoading` true during API requests
- `error` contains user-friendly error message on failure

---

### 4. Form State (Task Creation/Edit)

**Purpose**: Represents form input state for task creation and editing

**TypeScript Interface**:
```typescript
interface TaskFormState {
  title: string;
  description: string;
  is_completed: boolean;
}

interface TaskFormErrors {
  title?: string;
  description?: string;
}
```

**State Management**: Local component state (useState)

**Lifecycle**:
- Initialized: Empty for create, populated for edit
- Validated: On input change and form submit
- Submitted: Sent to API on valid form
- Reset: After successful submission

**Validation Rules**:
- `title` required, 1-200 characters
- `description` optional, max 1000 characters
- `is_completed` boolean, defaults to false

---

### 5. UI State

**Purpose**: Represents global UI state (modals, notifications, loading)

**TypeScript Interface**:
```typescript
interface UIState {
  isModalOpen: boolean;
  modalContent: React.ReactNode | null;
  notification: Notification | null;
  globalLoading: boolean;
}

interface Notification {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number; // milliseconds
}
```

**State Management**: React Context or local state

**Lifecycle**:
- Modal: Opened/closed on user actions
- Notification: Shown after API responses, auto-dismissed after duration
- Global loading: True during critical operations (login, initial load)

---

### 6. API Response Types

**Purpose**: Type definitions for API responses

**TypeScript Interfaces**:
```typescript
// Success responses
interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface TaskResponse {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
}

// Error responses
interface ErrorResponse {
  error: {
    type: string;
    status_code: number;
    message: string;
    details?: any;
  };
}
```

**Usage**: Type safety for API client functions and response handling

---

## State Management Architecture

### Context Providers

**AuthContext**:
```typescript
interface AuthContextType {
  session: UserSession;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}
```

**TaskContext**:
```typescript
interface TaskContextType {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (data: TaskFormState) => Promise<Task>;
  updateTask: (id: number, data: Partial<TaskFormState>) => Promise<Task>;
  deleteTask: (id: number) => Promise<void>;
  toggleComplete: (id: number) => Promise<Task>;
}
```

### Custom Hooks

**useAuth**:
```typescript
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

**useTasks**:
```typescript
const useTasks = () => {
  const context = useContext(TaskContext);
  if (!context) throw new Error('useTasks must be used within TaskProvider');
  return context;
};
```

---

## Data Flow

### Authentication Flow
```
1. User submits login form
   ↓
2. LoginForm calls authContext.login(email, password)
   ↓
3. AuthContext calls API client POST /auth/login
   ↓
4. API returns { access_token, user }
   ↓
5. AuthContext stores token in localStorage
   ↓
6. AuthContext updates session state
   ↓
7. Middleware allows access to protected routes
   ↓
8. User redirected to dashboard
```

### Task CRUD Flow
```
1. Dashboard mounts
   ↓
2. useEffect calls taskContext.fetchTasks()
   ↓
3. TaskContext calls API client GET /tasks
   ↓
4. API returns { tasks: [...], total: N }
   ↓
5. TaskContext updates tasks state
   ↓
6. TaskList component re-renders with tasks
   ↓
7. User creates/updates/deletes task
   ↓
8. TaskContext calls appropriate API endpoint
   ↓
9. API returns updated task or success
   ↓
10. TaskContext updates local state
   ↓
11. UI reflects changes
```

---

## State Persistence

**Persisted State** (survives page refresh):
- JWT token (localStorage)
- User email (derived from token)

**Ephemeral State** (cleared on refresh):
- Task list (refetched on mount)
- Form state (reset on navigation)
- UI state (modals, notifications)

**Rationale**: Tasks are refetched to ensure data consistency with backend. Token persistence enables session continuity.

---

## State Synchronization

**Challenge**: Keeping frontend state in sync with backend

**Strategy**:
1. **Single Source of Truth**: Backend API is authoritative
2. **Refetch on Mount**: Always fetch fresh data when components mount
3. **Optimistic Updates**: Not implemented (server-confirmed updates only)
4. **Error Handling**: Revert to previous state on API errors
5. **Stale Data**: Accept eventual consistency (no real-time updates)

---

## Type Safety

**TypeScript Configuration**:
- Strict mode enabled
- No implicit any
- Strict null checks
- All API responses typed

**Benefits**:
- Catch type errors at compile time
- Better IDE autocomplete
- Easier refactoring
- Self-documenting code

---

## State Management Best Practices

1. **Minimize Global State**: Only auth and tasks in Context, rest in local state
2. **Colocate State**: Keep state close to where it's used
3. **Immutable Updates**: Use spread operators, never mutate state directly
4. **Derived State**: Compute from existing state, don't store redundantly
5. **Error Boundaries**: Catch and display React errors gracefully

---

## Future Enhancements

**Out of scope for current phase**:
- Caching strategy (SWR, React Query)
- Optimistic UI updates
- Real-time synchronization (WebSockets)
- Offline support (IndexedDB)
- State persistence beyond token (Redux Persist)
