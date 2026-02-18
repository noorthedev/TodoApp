# Quick Start Guide: Frontend UI & API Integration Layer

**Feature**: 004-frontend-ui-integration
**Date**: 2026-02-16
**Purpose**: Get the frontend application running quickly for development and testing

---

## Prerequisites

Before starting, ensure you have:

- **Node.js**: Version 18.0 or higher
- **npm/yarn/pnpm**: Package manager installed
- **Backend API**: Running at `http://localhost:8000` (from feature 002-backend-api-db)
- **Database**: Neon PostgreSQL configured and accessible
- **Git**: For version control

---

## Initial Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
# or
yarn install
# or
pnpm install
```

**Key Dependencies**:
- `next@16+` - Next.js framework
- `react@18+` - React library
- `better-auth` - Authentication library
- `axios` - HTTP client
- `tailwindcss` - Styling framework
- `typescript` - Type safety

---

### 2. Environment Configuration

Create `.env.local` in the `frontend/` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# Optional: Development Settings
NODE_ENV=development
```

**Important**:
- `NEXT_PUBLIC_API_URL`: Must match your backend API URL
- `BETTER_AUTH_SECRET`: Generate a secure random string (min 32 characters)
- Never commit `.env.local` to version control

---

### 3. Start Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The application will start at `http://localhost:3000`

---

## Quick Test Scenarios

### Scenario 1: User Registration Flow

**Goal**: Verify new user can register and access dashboard

**Steps**:
1. Navigate to `http://localhost:3000`
2. Click "Register" button
3. Enter email: `test@example.com`
4. Enter password: `password123`
5. Submit form

**Expected Result**:
- User is registered in database
- JWT token is stored in localStorage
- User is redirected to `/dashboard`
- Dashboard displays empty task list

**Verification**:
```bash
# Check localStorage in browser DevTools
localStorage.getItem('auth_token')  # Should return JWT token
```

---

### Scenario 2: Login Flow

**Goal**: Verify existing user can log in

**Steps**:
1. Navigate to `http://localhost:3000/login`
2. Enter registered email and password
3. Submit form

**Expected Result**:
- User is authenticated
- JWT token is stored in localStorage
- User is redirected to `/dashboard`

**Verification**:
```bash
# Check API request in Network tab
# Should see Authorization: Bearer <token> header
```

---

### Scenario 3: Create Task

**Goal**: Verify authenticated user can create a task

**Steps**:
1. Log in to dashboard
2. Click "Add Task" button
3. Enter title: "Test Task"
4. Enter description: "This is a test"
5. Submit form

**Expected Result**:
- Task is created via POST /tasks
- Task appears in task list
- Task shows correct title and description

**Verification**:
```bash
# Check backend logs
# Should see: POST /tasks - 201 Created
```

---

### Scenario 4: Update Task

**Goal**: Verify user can edit existing task

**Steps**:
1. Click "Edit" button on a task
2. Change title to "Updated Task"
3. Submit form

**Expected Result**:
- Task is updated via PUT /tasks/{id}
- Task list reflects new title
- Updated timestamp changes

---

### Scenario 5: Delete Task

**Goal**: Verify user can delete a task

**Steps**:
1. Click "Delete" button on a task
2. Confirm deletion in modal

**Expected Result**:
- Task is deleted via DELETE /tasks/{id}
- Task is removed from list
- No error messages

---

### Scenario 6: Toggle Task Completion

**Goal**: Verify user can mark task as complete/incomplete

**Steps**:
1. Click checkbox on a task

**Expected Result**:
- Task completion status toggles
- Task is updated via PUT /tasks/{id}
- UI shows strikethrough for completed tasks

---

### Scenario 7: Logout Flow

**Goal**: Verify user can log out

**Steps**:
1. Click "Logout" button in header
2. Confirm logout

**Expected Result**:
- JWT token is removed from localStorage
- User is redirected to `/login`
- Attempting to access `/dashboard` redirects to login

---

### Scenario 8: Route Protection

**Goal**: Verify unauthenticated users cannot access protected routes

**Steps**:
1. Clear localStorage (remove auth_token)
2. Navigate to `http://localhost:3000/dashboard`

**Expected Result**:
- Middleware intercepts request
- User is redirected to `/login?redirect=/dashboard`
- After login, user is redirected back to `/dashboard`

---

### Scenario 9: Session Expiration

**Goal**: Verify expired tokens are handled gracefully

**Steps**:
1. Log in and get JWT token
2. Wait for token to expire (or manually set expired token)
3. Make an API request (e.g., fetch tasks)

**Expected Result**:
- API returns 401 Unauthorized
- Response interceptor catches error
- User is redirected to `/login?session_expired=true`
- Error message: "Session expired. Please log in again."

---

### Scenario 10: Error Handling

**Goal**: Verify API errors are displayed to user

**Steps**:
1. Stop backend API server
2. Try to create a task

**Expected Result**:
- Network error is caught
- Error message displayed: "Network error. Please check your connection."
- Loading state is cleared
- User can retry

---

## Development Workflow

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

---

### Building for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

---

### Linting and Formatting

```bash
# Run ESLint
npm run lint

# Fix ESLint errors
npm run lint -- --fix

# Format with Prettier (if configured)
npm run format
```

---

## Common Issues and Solutions

### Issue 1: API Connection Failed

**Symptom**: "Network error. Please check your connection."

**Solution**:
1. Verify backend API is running at `http://localhost:8000`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is configured on backend

---

### Issue 2: Token Not Attached to Requests

**Symptom**: 401 Unauthorized on protected endpoints

**Solution**:
1. Check localStorage has `auth_token`
2. Verify Axios interceptor is configured
3. Check Authorization header in Network tab

---

### Issue 3: Redirect Loop on Login

**Symptom**: Infinite redirects between `/login` and `/dashboard`

**Solution**:
1. Check middleware logic in `middleware.ts`
2. Verify token is being stored correctly
3. Clear localStorage and try again

---

### Issue 4: Better Auth Configuration Error

**Symptom**: "Better Auth secret not configured"

**Solution**:
1. Ensure `BETTER_AUTH_SECRET` is set in `.env.local`
2. Restart development server after changing env vars
3. Generate a secure random string (min 32 characters)

---

### Issue 5: Styles Not Loading

**Symptom**: Unstyled components, no TailwindCSS

**Solution**:
1. Verify `tailwind.config.js` is configured
2. Check `globals.css` imports Tailwind directives
3. Restart development server

---

## Integration with Backend

### API Endpoints Used

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/auth/register` | POST | User registration | No |
| `/auth/login` | POST | User login | No |
| `/auth/logout` | POST | User logout | Yes |
| `/tasks` | GET | List user's tasks | Yes |
| `/tasks` | POST | Create new task | Yes |
| `/tasks/{id}` | GET | Get specific task | Yes |
| `/tasks/{id}` | PUT | Update task | Yes |
| `/tasks/{id}` | DELETE | Delete task | Yes |

---

### Authentication Flow

```
1. User submits login form
   ↓
2. Frontend calls POST /auth/login
   ↓
3. Backend validates credentials
   ↓
4. Backend returns JWT token
   ↓
5. Frontend stores token in localStorage
   ↓
6. Frontend attaches token to all requests via interceptor
   ↓
7. Backend validates token and returns user-specific data
```

---

### Data Flow Example: Create Task

```
1. User fills task form
   ↓
2. TaskForm calls taskContext.createTask(data)
   ↓
3. TaskContext calls API client POST /tasks
   ↓
4. Axios interceptor attaches JWT token
   ↓
5. Backend validates token, creates task
   ↓
6. Backend returns created task
   ↓
7. TaskContext updates local state
   ↓
8. TaskList re-renders with new task
```

---

## Debugging Tips

### Enable Verbose Logging

Add to `.env.local`:
```bash
NEXT_PUBLIC_LOG_LEVEL=debug
```

---

### Inspect API Requests

1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Check request headers, payload, response

---

### Check JWT Token

```javascript
// In browser console
const token = localStorage.getItem('auth_token');
console.log(token);

// Decode JWT (without verification)
const payload = JSON.parse(atob(token.split('.')[1]));
console.log(payload);
```

---

### React DevTools

Install React DevTools extension to:
- Inspect component tree
- View component props and state
- Track re-renders
- Debug Context values

---

## Next Steps

After verifying the quick start scenarios:

1. **Run Full Test Suite**: Execute all unit and integration tests
2. **Review Components**: Inspect component implementations
3. **Test Responsive Design**: Verify mobile, tablet, desktop layouts
4. **Performance Testing**: Check load times and API response times
5. **Security Review**: Verify token handling and route protection
6. **Accessibility Testing**: Test with screen readers and keyboard navigation

---

## Additional Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **Better Auth Documentation**: https://better-auth.com/docs
- **Axios Documentation**: https://axios-http.com/docs/intro
- **TailwindCSS Documentation**: https://tailwindcss.com/docs
- **React Documentation**: https://react.dev

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review backend API logs
3. Inspect browser console for errors
4. Verify environment configuration
5. Consult feature specification: `specs/004-frontend-ui-integration/spec.md`
