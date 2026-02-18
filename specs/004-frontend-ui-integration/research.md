# Research & Technical Decisions: Frontend UI & API Integration Layer

**Feature**: 004-frontend-ui-integration
**Date**: 2026-02-16
**Status**: Complete

## Overview

This document captures the technical research and decisions made for implementing the frontend UI layer that integrates with the secured backend API. All decisions prioritize simplicity, maintainability, and alignment with existing backend architecture.

---

## Decision 1: Next.js App Router vs Pages Router

**Decision**: Use Next.js 16+ App Router

**Rationale**:
- App Router is the current recommended approach for new Next.js projects
- Server Components enable better performance and SEO
- Route groups `(auth)` and `(protected)` provide clean separation of authenticated vs public routes
- Middleware integration is more straightforward for route protection
- Better TypeScript support and type inference

**Alternatives Considered**:
- **Pages Router**: Older, more mature, but being phased out. Less optimal for our use case with protected routes.
- **Create React App**: No built-in routing, SSR, or middleware. Would require additional libraries.

**Implementation Impact**: File-based routing in `app/` directory, use of Server and Client Components, middleware for route protection

---

## Decision 2: Better Auth vs NextAuth.js vs Custom Auth

**Decision**: Use Better Auth for authentication flows

**Rationale**:
- Specified in project requirements and constraints
- Modern authentication library designed for Next.js
- Handles JWT token generation and validation
- Integrates well with backend JWT system
- Simpler configuration than NextAuth.js for our use case

**Alternatives Considered**:
- **NextAuth.js**: More feature-rich but heavier. Overkill for simple email/password auth.
- **Custom Auth**: More control but requires implementing token refresh, session management, security best practices from scratch.

**Implementation Impact**: Better Auth configuration in `lib/auth/better-auth.ts`, session management utilities, integration with API client

---

## Decision 3: Axios vs Fetch API for HTTP Client

**Decision**: Use Axios for API communication

**Rationale**:
- Built-in request/response interceptors (critical for JWT token attachment)
- Automatic JSON transformation
- Better error handling out of the box
- Request cancellation support
- Timeout configuration
- Widely used and well-documented

**Alternatives Considered**:
- **Fetch API**: Native browser API, no dependencies. However, requires manual interceptor implementation, no built-in timeout, more verbose error handling.
- **SWR/React Query**: Data fetching libraries with caching. Too heavy for our simple CRUD operations, adds complexity.

**Implementation Impact**: Axios instance in `lib/api/client.ts` with interceptors for JWT tokens and error handling

---

## Decision 4: React Context vs Redux vs Zustand for State Management

**Decision**: Use React Context API for global state

**Rationale**:
- Simple state requirements (auth session, task list)
- No complex state transformations or middleware needed
- Built into React, no additional dependencies
- Sufficient for our scale (single user, ~100 tasks)
- Easy to understand and maintain

**Alternatives Considered**:
- **Redux**: Overkill for our simple state. Adds boilerplate and complexity.
- **Zustand**: Lightweight alternative to Redux. Good option but unnecessary for our needs.
- **Jotai/Recoil**: Atomic state management. Too complex for our use case.

**Implementation Impact**: AuthContext and TaskContext providers, custom hooks (useAuth, useTasks)

---

## Decision 5: TailwindCSS vs CSS Modules vs Styled Components

**Decision**: Use TailwindCSS for styling

**Rationale**:
- Utility-first approach enables rapid development
- Built-in responsive design utilities (mobile-first)
- Consistent design system out of the box
- Excellent Next.js integration
- Small bundle size with purging
- No runtime overhead (unlike CSS-in-JS)

**Alternatives Considered**:
- **CSS Modules**: More verbose, requires writing custom CSS. Slower development.
- **Styled Components**: Runtime overhead, larger bundle size, not ideal for Next.js Server Components.
- **Plain CSS**: No design system, harder to maintain consistency.

**Implementation Impact**: TailwindCSS configuration, utility classes in components, responsive design with breakpoint utilities

---

## Decision 6: TypeScript vs JavaScript

**Decision**: Use TypeScript for type safety

**Rationale**:
- Catch errors at compile time, not runtime
- Better IDE support and autocomplete
- Type safety for API responses and component props
- Easier refactoring and maintenance
- Industry best practice for production applications
- Next.js has excellent TypeScript support

**Alternatives Considered**:
- **JavaScript**: Faster initial development but more runtime errors, harder to maintain as codebase grows.

**Implementation Impact**: TypeScript configuration, type definitions for API responses, component props, auth session

---

## Decision 7: localStorage vs httpOnly Cookies for JWT Storage

**Decision**: Use localStorage for JWT tokens (with option to migrate to httpOnly cookies)

**Rationale**:
- Simpler implementation for MVP
- Works with current backend JWT system
- Easy to access from client-side code
- Sufficient security with HTTPS and CSP

**Security Considerations**:
- Vulnerable to XSS attacks (mitigated by input sanitization and CSP)
- httpOnly cookies are more secure but require backend changes
- Document as future enhancement in risks section

**Alternatives Considered**:
- **httpOnly Cookies**: More secure (not accessible via JavaScript). Requires backend to set cookies, CORS configuration changes.
- **sessionStorage**: Cleared on tab close. Poor UX for our use case.

**Implementation Impact**: Token storage in `lib/auth/session.ts`, token retrieval in API client interceptors

---

## Decision 8: Optimistic UI Updates vs Server-Confirmed Updates

**Decision**: Use server-confirmed updates with loading states

**Rationale**:
- Simpler implementation
- Ensures UI always reflects server state
- Avoids rollback complexity on API errors
- Loading states provide clear feedback
- Sufficient for our performance targets (<3s for CRUD operations)

**Alternatives Considered**:
- **Optimistic Updates**: Better perceived performance but adds complexity for error handling and rollback. Not necessary for our performance targets.

**Implementation Impact**: Loading states during API calls, UI updates after successful API response

---

## Decision 9: Component Library vs Custom Components

**Decision**: Build custom components with TailwindCSS (consider shadcn/ui for complex components)

**Rationale**:
- Full control over styling and behavior
- No unnecessary dependencies
- TailwindCSS provides sufficient utilities
- Can add shadcn/ui components as needed (copy-paste, not dependency)

**Alternatives Considered**:
- **Material-UI**: Heavy, opinionated design. Doesn't match our needs.
- **Chakra UI**: Good option but adds dependency. Our UI is simple enough for custom components.
- **shadcn/ui**: Copy-paste components built with Radix UI and TailwindCSS. Good for complex components (modals, dropdowns) if needed.

**Implementation Impact**: Custom Button, Input, Modal, LoadingSpinner components in `components/ui/`

---

## Decision 10: Route Protection Strategy

**Decision**: Use Next.js middleware for route protection at the edge

**Rationale**:
- Runs before page renders (better UX, no flash of protected content)
- Centralized protection logic
- Efficient (runs at edge, not in every component)
- Standard Next.js pattern for authentication

**Alternatives Considered**:
- **Component-level protection**: Requires checking auth in every protected component. Prone to errors.
- **Layout-level protection**: Better than component-level but still allows initial render before redirect.

**Implementation Impact**: Middleware in `middleware.ts`, route matching for protected paths, redirect to login for unauthenticated users

---

## Technology Stack Summary

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Framework | Next.js | 16+ | App Router, Server Components, Middleware |
| UI Library | React | 18+ | Included with Next.js |
| Language | TypeScript | 5.0+ | Type safety, better DX |
| Styling | TailwindCSS | 3.x | Utility-first, responsive design |
| Auth | Better Auth | Latest | JWT integration, session management |
| HTTP Client | Axios | 1.x | Interceptors, error handling |
| State | React Context | Built-in | Simple state, no extra deps |
| Testing | Jest + RTL | Latest | Component and integration tests |

---

## Integration Points with Backend

**Backend API**: `002-backend-api-db` (FastAPI + SQLModel + Neon PostgreSQL)
**Authorization**: `003-auth-isolation` (JWT validation, ownership enforcement)

**API Endpoints Used**:
- POST /auth/register - User registration
- POST /auth/login - User authentication
- POST /auth/logout - User logout (informational)
- GET /tasks - List user's tasks
- POST /tasks - Create new task
- GET /tasks/{id} - Get specific task
- PUT /tasks/{id} - Update task
- DELETE /tasks/{id} - Delete task

**Authentication Flow**:
1. User submits login form → Frontend calls POST /auth/login
2. Backend validates credentials → Returns JWT token
3. Frontend stores token in localStorage
4. Frontend attaches token to all API requests via Axios interceptor
5. Backend validates token and returns user-specific data

---

## Performance Considerations

**Target Metrics**:
- Initial page load: <3s
- Task list load: <2s
- CRUD operations: <3s
- Login/registration: <30s

**Optimization Strategies**:
- Next.js automatic code splitting
- Server Components for static content
- Client Components only where interactivity needed
- TailwindCSS purging for minimal CSS bundle
- Lazy loading for modals and forms
- Debouncing for search/filter (future enhancement)

---

## Security Considerations

**Implemented**:
- JWT tokens in Authorization header
- Route protection via middleware
- Input validation before API calls
- HTTPS in production
- CORS configuration on backend

**Future Enhancements**:
- Content Security Policy (CSP)
- httpOnly cookies for tokens
- Token refresh mechanism
- Rate limiting on frontend
- XSS protection via input sanitization

---

## Development Workflow

1. **Setup**: Initialize Next.js project, install dependencies
2. **Auth**: Implement Better Auth, login/register pages
3. **Protection**: Add middleware for route protection
4. **API Client**: Create Axios instance with interceptors
5. **Task UI**: Build task list, forms, CRUD operations
6. **State**: Implement Context providers and hooks
7. **Styling**: Apply TailwindCSS, responsive design
8. **Testing**: Write component and integration tests
9. **Polish**: Error handling, loading states, UX improvements

---

## Open Questions / Future Enhancements

**Resolved in this phase**: All technical decisions made, no open questions

**Future Enhancements** (out of scope for current phase):
- Token refresh mechanism
- Offline functionality with service workers
- Real-time updates with WebSockets
- Advanced animations and transitions
- Dark mode support
- Internationalization (i18n)
- Progressive Web App (PWA) features
- Analytics and error tracking
