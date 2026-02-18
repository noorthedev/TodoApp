# Routes Contract: Frontend UI & API Integration Layer

**Feature**: 004-frontend-ui-integration
**Date**: 2026-02-16
**Purpose**: Define route structure, protection, and navigation patterns

## Overview

This document defines all application routes, their protection requirements, and navigation behavior using Next.js App Router conventions.

---

## Route Structure

### Public Routes (No Authentication Required)

#### `/` - Landing Page
**File**: `app/page.tsx`
**Purpose**: Application landing page
**Behavior**:
- Displays welcome message and app description
- Shows "Login" and "Register" buttons
- Redirects to `/dashboard` if already authenticated

---

#### `/login` - Login Page
**File**: `app/(auth)/login/page.tsx`
**Purpose**: User login interface
**Behavior**:
- Displays LoginForm component
- Redirects to `/dashboard` on successful login
- Shows error message on failed login
- Redirects to `/dashboard` if already authenticated
**Query Parameters**:
- `session_expired=true`: Shows "Session expired" message
- `redirect=/path`: Redirect path after login (default: `/dashboard`)

---

#### `/register` - Registration Page
**File**: `app/(auth)/register/page.tsx`
**Purpose**: User registration interface
**Behavior**:
- Displays RegisterForm component
- Auto-logs in user after successful registration
- Redirects to `/dashboard` on success
- Shows error message on failed registration
- Redirects to `/dashboard` if already authenticated

---

### Protected Routes (Authentication Required)

#### `/dashboard` - Dashboard Page
**File**: `app/(protected)/dashboard/page.tsx`
**Purpose**: Main task management interface
**Behavior**:
- Displays TaskList component with user's tasks
- Shows "Add Task" button
- Fetches tasks on mount
- Shows loading state during fetch
- Shows error message on fetch failure
- Redirects to `/login` if not authenticated

**Layout**: Uses `app/(protected)/layout.tsx` with Header and Navigation

---

#### `/tasks/[id]` - Task Detail Page (Optional)
**File**: `app/(protected)/tasks/[id]/page.tsx`
**Purpose**: View and edit single task
**Behavior**:
- Displays task details
- Shows edit and delete buttons
- Fetches task by ID on mount
- Shows 404 if task not found
- Shows 403 if not authorized
- Redirects to `/login` if not authenticated

**Note**: This route is optional - task editing can be done via modal on dashboard

---

## Route Groups

### `(auth)` - Authentication Route Group
**Purpose**: Group public authentication pages
**Layout**: `app/(auth)/layout.tsx`
**Behavior**:
- Minimal layout (no header/navigation)
- Centered content
- Redirects to `/dashboard` if authenticated

**Routes**:
- `/login`
- `/register`

---

### `(protected)` - Protected Route Group
**Purpose**: Group authenticated pages
**Layout**: `app/(protected)/layout.tsx`
**Behavior**:
- Full layout with Header and Navigation
- Checks authentication on mount
- Redirects to `/login` if not authenticated

**Routes**:
- `/dashboard`
- `/tasks/[id]` (optional)

---

## Route Protection Strategy

### Middleware-Based Protection

**File**: `middleware.ts`

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('authorization')?.replace('Bearer ', '');

  const isAuthPage = request.nextUrl.pathname.startsWith('/login') ||
                     request.nextUrl.pathname.startsWith('/register');

  const isProtectedPage = request.nextUrl.pathname.startsWith('/dashboard') ||
                          request.nextUrl.pathname.startsWith('/tasks');

  // Redirect to dashboard if authenticated and on auth page
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Redirect to login if not authenticated and on protected page
  if (!token && isProtectedPage) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/tasks/:path*',
    '/login',
    '/register',
  ],
};
```

**Behavior**:
- Runs before page renders (edge middleware)
- Checks for JWT token in cookies or Authorization header
- Redirects unauthenticated users to `/login`
- Redirects authenticated users away from auth pages
- Preserves intended destination in `redirect` query parameter

---

### Layout-Based Protection (Fallback)

**File**: `app/(protected)/layout.tsx`

```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import Header from '@/components/layout/Header';
import Navigation from '@/components/layout/Navigation';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { session, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !session.isAuthenticated) {
      router.push('/login');
    }
  }, [session.isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!session.isAuthenticated) {
    return null; // Will redirect via useEffect
  }

  return (
    <div>
      <Header user={session.user} onLogout={() => {/* logout logic */}} />
      <Navigation items={navItems} currentPath={pathname} />
      <main>{children}</main>
    </div>
  );
}
```

**Behavior**:
- Client-side protection as fallback
- Shows loading spinner during auth check
- Redirects to `/login` if not authenticated
- Wraps protected pages with Header and Navigation

---

## Navigation Patterns

### Programmatic Navigation

```typescript
import { useRouter } from 'next/navigation';

const router = useRouter();

// Navigate to dashboard
router.push('/dashboard');

// Navigate with query parameters
router.push('/login?session_expired=true');

// Navigate back
router.back();

// Replace current route (no history entry)
router.replace('/dashboard');
```

---

### Link Component Navigation

```typescript
import Link from 'next/link';

<Link href="/dashboard">Go to Dashboard</Link>
<Link href="/login?redirect=/dashboard">Login</Link>
```

---

### Redirect After Login

```typescript
// In LoginForm component
const router = useRouter();
const searchParams = useSearchParams();

const handleLogin = async (email: string, password: string) => {
  await login(email, password);

  // Get redirect path from query parameter
  const redirect = searchParams.get('redirect') || '/dashboard';
  router.push(redirect);
};
```

---

## Route Metadata

### Page Titles

```typescript
// app/(protected)/dashboard/page.tsx
export const metadata = {
  title: 'Dashboard | Todo App',
  description: 'Manage your tasks',
};
```

### Dynamic Titles

```typescript
// app/(protected)/tasks/[id]/page.tsx
export async function generateMetadata({ params }: { params: { id: string } }) {
  const task = await getTask(params.id);
  return {
    title: `${task.title} | Todo App`,
  };
}
```

---

## Error Handling

### 404 Not Found

**File**: `app/not-found.tsx`

```typescript
export default function NotFound() {
  return (
    <div>
      <h1>404 - Page Not Found</h1>
      <Link href="/dashboard">Go to Dashboard</Link>
    </div>
  );
}
```

---

### Error Boundary

**File**: `app/error.tsx`

```typescript
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h1>Something went wrong</h1>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

---

## Loading States

### Page-Level Loading

**File**: `app/(protected)/dashboard/loading.tsx`

```typescript
export default function Loading() {
  return <LoadingSpinner size="lg" />;
}
```

**Behavior**: Shown while page is loading (automatic with Next.js)

---

## Route Transitions

### Loading Indicator

```typescript
'use client';

import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

export function RouteLoadingIndicator() {
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    const timeout = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timeout);
  }, [pathname]);

  if (!isLoading) return null;

  return <div className="loading-bar">Loading...</div>;
}
```

---

## Route Testing

### Protected Route Test

```typescript
describe('Protected Routes', () => {
  it('should redirect to login when not authenticated', () => {
    // Clear token
    localStorage.removeItem('auth_token');

    // Navigate to protected route
    router.push('/dashboard');

    // Assert redirected to login
    expect(router.pathname).toBe('/login');
  });

  it('should allow access when authenticated', () => {
    // Set valid token
    localStorage.setItem('auth_token', 'valid_token');

    // Navigate to protected route
    router.push('/dashboard');

    // Assert on dashboard
    expect(router.pathname).toBe('/dashboard');
  });
});
```

---

## Route Security

### CSRF Protection
- Not applicable (stateless JWT, no cookies for auth)

### XSS Protection
- Sanitize all user inputs
- Use Content Security Policy (CSP)
- Avoid dangerouslySetInnerHTML

### Route Enumeration
- All routes are public knowledge (client-side routing)
- Protection is at data level (API authorization)

---

## Performance Optimization

### Route Prefetching

```typescript
// Next.js automatically prefetches Link components
<Link href="/dashboard" prefetch={true}>Dashboard</Link>

// Programmatic prefetch
router.prefetch('/dashboard');
```

### Code Splitting

```typescript
// Lazy load heavy components
const TaskForm = dynamic(() => import('@/components/tasks/TaskForm'), {
  loading: () => <LoadingSpinner />,
});
```

---

## Future Enhancements

- Role-based routing (admin routes)
- Nested protected routes
- Route-level permissions
- Breadcrumb navigation
- Route analytics
- Deep linking support
