# Component Contracts: Frontend UI & API Integration Layer

**Feature**: 004-frontend-ui-integration
**Date**: 2026-02-16
**Purpose**: Define component interfaces, props, and behavior contracts

## Overview

This document defines the contracts for all React components in the application, including props interfaces, expected behavior, and usage patterns.

---

## Authentication Components

### LoginForm

**Purpose**: User login form with email and password inputs

**Props**:
```typescript
interface LoginFormProps {
  onSuccess?: () => void; // Callback after successful login
  redirectTo?: string;    // Redirect path after login (default: /dashboard)
}
```

**Behavior**:
- Displays email and password input fields
- Validates inputs before submission
- Shows loading state during API call
- Displays error messages from API
- Redirects to dashboard on success
- Stores JWT token in localStorage

**Usage**:
```tsx
<LoginForm onSuccess={() => router.push('/dashboard')} />
```

---

### RegisterForm

**Purpose**: User registration form with email and password inputs

**Props**:
```typescript
interface RegisterFormProps {
  onSuccess?: () => void; // Callback after successful registration
  redirectTo?: string;    // Redirect path after registration (default: /dashboard)
}
```

**Behavior**:
- Displays email, password, and confirm password fields
- Validates email format and password strength
- Shows loading state during API call
- Displays error messages from API
- Auto-logs in user after successful registration
- Redirects to dashboard on success

**Usage**:
```tsx
<RegisterForm onSuccess={() => router.push('/dashboard')} />
```

---

### LogoutButton

**Purpose**: Button to log out the current user

**Props**:
```typescript
interface LogoutButtonProps {
  variant?: 'primary' | 'secondary' | 'text'; // Button style
  onLogout?: () => void;                       // Callback after logout
}
```

**Behavior**:
- Displays logout button
- Clears JWT token from localStorage
- Clears auth context state
- Redirects to login page
- Shows confirmation dialog (optional)

**Usage**:
```tsx
<LogoutButton variant="text" onLogout={() => console.log('Logged out')} />
```

---

## Task Components

### TaskList

**Purpose**: Display list of tasks with loading and error states

**Props**:
```typescript
interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  onTaskClick?: (task: Task) => void;
  onTaskUpdate?: (task: Task) => void;
  onTaskDelete?: (taskId: number) => void;
}
```

**Behavior**:
- Displays tasks in a list or grid layout
- Shows loading spinner when isLoading is true
- Shows error message when error is present
- Shows empty state when tasks array is empty
- Emits events for task interactions
- Responsive layout (stacks on mobile)

**Usage**:
```tsx
<TaskList
  tasks={tasks}
  isLoading={isLoading}
  error={error}
  onTaskClick={(task) => setSelectedTask(task)}
  onTaskUpdate={(task) => handleUpdate(task)}
  onTaskDelete={(id) => handleDelete(id)}
/>
```

---

### TaskItem

**Purpose**: Display a single task with actions

**Props**:
```typescript
interface TaskItemProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
  onToggleComplete?: (task: Task) => void;
  showActions?: boolean; // Show edit/delete buttons (default: true)
}
```

**Behavior**:
- Displays task title, description, completion status
- Shows timestamps (created, updated)
- Checkbox to toggle completion
- Edit and delete action buttons
- Strikethrough text for completed tasks
- Hover effects for interactivity

**Usage**:
```tsx
<TaskItem
  task={task}
  onEdit={(task) => openEditModal(task)}
  onDelete={(id) => confirmDelete(id)}
  onToggleComplete={(task) => toggleComplete(task)}
/>
```

---

### TaskForm

**Purpose**: Form for creating or editing tasks

**Props**:
```typescript
interface TaskFormProps {
  task?: Task;                              // Existing task for edit mode
  onSubmit: (data: TaskFormState) => void;  // Submit handler
  onCancel?: () => void;                    // Cancel handler
  isLoading?: boolean;                      // Loading state
  error?: string | null;                    // Error message
}
```

**Behavior**:
- Displays title and description input fields
- Validates inputs before submission
- Shows loading state during API call
- Displays error messages
- Pre-fills fields in edit mode
- Emits submit event with form data
- Emits cancel event on cancel button

**Usage**:
```tsx
<TaskForm
  task={selectedTask}
  onSubmit={(data) => handleSubmit(data)}
  onCancel={() => closeModal()}
  isLoading={isSubmitting}
  error={error}
/>
```

---

### TaskDeleteConfirm

**Purpose**: Confirmation dialog for task deletion

**Props**:
```typescript
interface TaskDeleteConfirmProps {
  task: Task;
  isOpen: boolean;
  onConfirm: (taskId: number) => void;
  onCancel: () => void;
  isLoading?: boolean;
}
```

**Behavior**:
- Displays modal with task title
- Shows confirmation message
- Confirm and cancel buttons
- Disables buttons during deletion
- Closes on confirm or cancel

**Usage**:
```tsx
<TaskDeleteConfirm
  task={taskToDelete}
  isOpen={showDeleteModal}
  onConfirm={(id) => deleteTask(id)}
  onCancel={() => setShowDeleteModal(false)}
  isLoading={isDeleting}
/>
```

---

## UI Components

### Button

**Purpose**: Reusable button component with variants

**Props**:
```typescript
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'text';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  isLoading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}
```

**Behavior**:
- Renders button with appropriate styling
- Shows loading spinner when isLoading is true
- Disables button when disabled or isLoading
- Applies variant and size styles
- Supports custom className for overrides

**Usage**:
```tsx
<Button variant="primary" isLoading={isSubmitting} onClick={handleClick}>
  Submit
</Button>
```

---

### Input

**Purpose**: Reusable input component with validation

**Props**:
```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  maxLength?: number;
  className?: string;
}
```

**Behavior**:
- Renders input field with label
- Shows error message below input
- Applies error styling when error is present
- Disables input when disabled is true
- Enforces maxLength if provided

**Usage**:
```tsx
<Input
  type="email"
  label="Email"
  value={email}
  onChange={setEmail}
  error={emailError}
  required
/>
```

---

### Modal

**Purpose**: Reusable modal dialog component

**Props**:
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  closeOnOverlayClick?: boolean; // Default: true
}
```

**Behavior**:
- Displays modal overlay and content
- Centers modal on screen
- Closes on overlay click (if enabled)
- Closes on ESC key press
- Prevents body scroll when open
- Animates in/out

**Usage**:
```tsx
<Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="Edit Task">
  <TaskForm task={task} onSubmit={handleSubmit} />
</Modal>
```

---

### LoadingSpinner

**Purpose**: Loading indicator component

**Props**:
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}
```

**Behavior**:
- Displays animated spinner
- Applies size and color styles
- Accessible (aria-label)

**Usage**:
```tsx
<LoadingSpinner size="lg" />
```

---

## Layout Components

### Header

**Purpose**: Application header with navigation and user menu

**Props**:
```typescript
interface HeaderProps {
  user: User | null;
  onLogout: () => void;
}
```

**Behavior**:
- Displays app logo/title
- Shows navigation links
- Displays user email
- Shows logout button
- Responsive (hamburger menu on mobile)

**Usage**:
```tsx
<Header user={user} onLogout={handleLogout} />
```

---

### Navigation

**Purpose**: Navigation menu component

**Props**:
```typescript
interface NavigationProps {
  items: NavItem[];
  currentPath: string;
}

interface NavItem {
  label: string;
  path: string;
  icon?: React.ReactNode;
}
```

**Behavior**:
- Displays navigation links
- Highlights active link
- Responsive layout
- Supports icons

**Usage**:
```tsx
<Navigation
  items={[
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Profile', path: '/profile' },
  ]}
  currentPath={pathname}
/>
```

---

## Component Testing Contracts

### Unit Tests

Each component must have:
- Render test (component renders without crashing)
- Props test (component accepts and uses props correctly)
- Event test (component emits events correctly)
- State test (component manages internal state correctly)
- Error test (component handles errors gracefully)

### Integration Tests

Key user flows must be tested:
- Login flow (LoginForm → API → redirect)
- Task creation flow (TaskForm → API → TaskList update)
- Task deletion flow (TaskDeleteConfirm → API → TaskList update)

---

## Accessibility Requirements

All components must:
- Use semantic HTML elements
- Include ARIA labels where needed
- Support keyboard navigation
- Provide focus indicators
- Have sufficient color contrast
- Work with screen readers

---

## Responsive Design Contracts

All components must:
- Work on mobile (320px+)
- Work on tablet (768px+)
- Work on desktop (1024px+)
- Use mobile-first approach
- Stack vertically on small screens
- Use appropriate touch targets (44px minimum)

---

## Performance Contracts

Components must:
- Avoid unnecessary re-renders (React.memo where appropriate)
- Use lazy loading for heavy components
- Debounce expensive operations
- Optimize images and assets
- Keep bundle size minimal

---

## Error Handling Contracts

Components must:
- Display user-friendly error messages
- Provide retry mechanisms where appropriate
- Gracefully degrade on errors
- Log errors for debugging
- Never crash the entire app (use Error Boundaries)
