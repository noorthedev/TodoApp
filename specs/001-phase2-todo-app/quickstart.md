# Quickstart Guide: Phase 2 Todo Application

**Feature**: Phase 2 Todo Full-Stack Web Application
**Date**: 2026-02-15
**Estimated Setup Time**: 30-45 minutes

## Overview

This guide will help you set up and run the Phase 2 Todo application locally. The application consists of a Next.js frontend, FastAPI backend, and Neon PostgreSQL database.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python**: 3.11 or higher
  - Check: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/

- **Node.js**: 18.0 or higher
  - Check: `node --version`
  - Download: https://nodejs.org/

- **npm**: 9.0 or higher (comes with Node.js)
  - Check: `npm --version`

- **Git**: Latest version
  - Check: `git --version`
  - Download: https://git-scm.com/

### Required Accounts

- **Neon Account**: For PostgreSQL database
  - Sign up: https://neon.tech/
  - Create a new project and note the connection string

### Optional Tools

- **Postman**: For API testing (https://www.postman.com/)
- **VS Code**: Recommended code editor (https://code.visualstudio.com/)

## Project Structure

```
phase_II/
├── backend/              # FastAPI backend
│   ├── src/             # Source code
│   ├── tests/           # Backend tests
│   ├── requirements.txt # Python dependencies
│   └── .env             # Backend environment variables
├── frontend/            # Next.js frontend
│   ├── src/            # Source code
│   ├── tests/          # Frontend tests
│   ├── package.json    # Node dependencies
│   └── .env.local      # Frontend environment variables
└── specs/              # Documentation and specifications
```

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd phase_II

# Checkout the feature branch
git checkout 001-phase2-todo-app
```

## Step 2: Database Setup (Neon PostgreSQL)

### 2.1 Create Neon Project

1. Log in to https://console.neon.tech/
2. Click "Create Project"
3. Choose a project name (e.g., "phase2-todo")
4. Select a region close to you
5. Click "Create Project"

### 2.2 Get Connection String

1. In your Neon project dashboard, click "Connection Details"
2. Copy the connection string (it looks like):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
3. Save this for the next step

### 2.3 Test Connection (Optional)

```bash
# Install psql if not already installed
# On macOS: brew install postgresql
# On Ubuntu: sudo apt-get install postgresql-client

# Test connection
psql "postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

# If successful, you'll see a psql prompt. Type \q to exit.
```

## Step 3: Backend Setup

### 3.1 Navigate to Backend Directory

```bash
cd backend
```

### 3.2 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 3.3 Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Expected dependencies** (will be in requirements.txt):
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

### 3.4 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Add the following to `.env`**:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000

# Application
DEBUG=True
```

**Important**:
- Replace `DATABASE_URL` with your Neon connection string
- Change `postgresql://` to `postgresql+asyncpg://` for async support
- Generate a secure JWT_SECRET: `openssl rand -hex 32`

### 3.5 Initialize Database

```bash
# Run database initialization (creates tables)
python -m src.database

# Or if you have a migration script:
python scripts/init_db.py
```

### 3.6 Start Backend Server

```bash
# Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

### 3.7 Verify Backend

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/ (should return a welcome message)

## Step 4: Frontend Setup

### 4.1 Open New Terminal

Keep the backend running and open a new terminal window.

```bash
cd phase_II/frontend
```

### 4.2 Install Dependencies

```bash
# Install Node.js dependencies
npm install

# This will install Next.js, React, Axios, and other dependencies
```

### 4.3 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local file
nano .env.local  # or use your preferred editor
```

**Add the following to `.env.local`**:
```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Important**:
- `NEXT_PUBLIC_API_URL` points to your backend server

### 4.4 Start Frontend Server

```bash
# Start the Next.js development server
npm run dev

# You should see:
# ▲ Next.js 16.x.x
# - Local:        http://localhost:3000
# - Ready in X.Xs
```

### 4.5 Verify Frontend

Open your browser and visit:
- **Home Page**: http://localhost:3000
- **Login Page**: http://localhost:3000/login
- **Register Page**: http://localhost:3000/register

## Step 5: Test the Application

### 5.1 Register a New User

1. Navigate to http://localhost:3000/register
2. Enter email: `test@example.com`
3. Enter password: `TestPass123!`
4. Click "Register"
5. You should be redirected to the dashboard

### 5.2 Create a Task

1. On the dashboard, find the "Create Task" form
2. Enter title: `My First Task`
3. Enter description: `Testing the application`
4. Click "Create"
5. The task should appear in your task list

### 5.3 Update a Task

1. Click on the task you just created
2. Click "Edit" or the edit icon
3. Change the title or mark as completed
4. Click "Save"
5. Changes should be reflected immediately

### 5.4 Delete a Task

1. Click on a task
2. Click "Delete" or the delete icon
3. Confirm deletion
4. Task should be removed from the list

### 5.5 Test Authentication

1. Click "Logout" in the navigation
2. Try to access http://localhost:3000/dashboard
3. You should be redirected to the login page
4. Log in with your credentials
5. You should be redirected back to the dashboard

## Step 6: Run Tests

### 6.1 Backend Tests

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment if not already active
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### 6.2 Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## Troubleshooting

### Backend Issues

#### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue: "Connection refused" or database connection errors
**Solution**:
- Verify Neon connection string is correct in `.env`
- Check that connection string uses `postgresql+asyncpg://`
- Ensure Neon database is running (check Neon console)
- Test connection with psql

#### Issue: "Port 8000 already in use"
**Solution**:
- Kill the process using port 8000: `lsof -ti:8000 | xargs kill -9` (macOS/Linux)
- Or use a different port: `uvicorn src.main:app --port 8001`

#### Issue: JWT token errors
**Solution**:
- Ensure `JWT_SECRET` in backend `.env` matches `BETTER_AUTH_SECRET` in frontend `.env.local`
- Regenerate secret: `openssl rand -hex 32`

### Frontend Issues

#### Issue: "Module not found" errors
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

#### Issue: "CORS policy" errors in browser console
**Solution**:
- Verify backend CORS configuration includes `http://localhost:3000`
- Check that `NEXT_PUBLIC_API_URL` in `.env.local` is correct
- Restart both backend and frontend servers

#### Issue: "Failed to fetch" or network errors
**Solution**:
- Ensure backend is running on http://localhost:8000
- Check browser console for specific error messages
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

#### Issue: Authentication not working
**Solution**:
- Clear browser localStorage: Open DevTools → Application → Local Storage → Clear
- Verify JWT secrets match between frontend and backend
- Check browser console for token-related errors

### Database Issues

#### Issue: "relation does not exist" errors
**Solution**: Run database initialization
```bash
cd backend
python -m src.database
```

#### Issue: "password authentication failed"
**Solution**:
- Verify Neon connection string is correct
- Check that password doesn't contain special characters that need URL encoding
- Try resetting database password in Neon console

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit files in `backend/src/`
   - FastAPI auto-reloads on file changes
   - Check http://localhost:8000/docs for updated API

2. **Frontend Changes**:
   - Edit files in `frontend/src/`
   - Next.js auto-reloads on file changes
   - Changes appear immediately in browser

3. **Database Changes**:
   - Update models in `backend/src/models/`
   - Run migrations or recreate tables
   - Test with sample data

### Git Workflow

```bash
# Create a new branch for your work
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add feature description"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
```

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection string | postgresql+asyncpg://user:pass@host/db |
| JWT_SECRET | Secret key for JWT signing | 32-character hex string |
| JWT_ALGORITHM | JWT signing algorithm | HS256 |
| JWT_EXPIRATION_HOURS | Token expiration time | 24 |
| CORS_ORIGINS | Allowed frontend origins | http://localhost:3000 |
| DEBUG | Enable debug mode | True |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API base URL | http://localhost:8000 |
| BETTER_AUTH_SECRET | JWT secret (must match backend) | Same as JWT_SECRET |
| NEXT_PUBLIC_APP_URL | Frontend base URL | http://localhost:3000 |

## Next Steps

After completing this quickstart:

1. **Review Documentation**:
   - Read `specs/001-phase2-todo-app/spec.md` for requirements
   - Review `specs/001-phase2-todo-app/plan.md` for architecture
   - Check `specs/001-phase2-todo-app/data-model.md` for database schema

2. **Explore the API**:
   - Visit http://localhost:8000/docs
   - Try out different endpoints
   - Review request/response formats

3. **Run Tests**:
   - Execute backend tests: `pytest`
   - Execute frontend tests: `npm test`
   - Review test coverage

4. **Start Development**:
   - Review `specs/001-phase2-todo-app/tasks.md` (when available)
   - Pick a task to implement
   - Follow the development workflow

## Support

If you encounter issues not covered in this guide:

1. Check the troubleshooting section above
2. Review error messages carefully
3. Check browser console (F12) for frontend errors
4. Check terminal output for backend errors
5. Consult the API documentation at http://localhost:8000/docs

## Security Notes

⚠️ **Important for Production**:

- Change all default secrets and passwords
- Use environment-specific configuration
- Enable HTTPS for all connections
- Implement rate limiting
- Add proper logging and monitoring
- Review security best practices in the constitution

---

**Last Updated**: 2026-02-15
**Maintained By**: Phase 2 Todo Team
