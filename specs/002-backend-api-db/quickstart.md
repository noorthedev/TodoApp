# Quickstart Guide: Backend API & Database Layer

**Feature**: Backend API & Database Layer
**Date**: 2026-02-16
**Estimated Setup Time**: 20-30 minutes

## Overview

This guide will help you set up and test the backend API locally. The backend provides RESTful endpoints for user authentication and task management with persistent storage in Neon PostgreSQL.

## Prerequisites

### Required Software

- **Python**: 3.11 or higher
  - Check: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/

- **pip**: Latest version (comes with Python)
  - Check: `pip --version`
  - Upgrade: `pip install --upgrade pip`

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
- **httpie**: Command-line HTTP client (https://httpie.io/)

## Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd phase_II

# Checkout the feature branch
git checkout 002-backend-api-db
```

## Step 2: Database Setup (Neon PostgreSQL)

### 2.1 Create Neon Project

1. Log in to https://console.neon.tech/
2. Click "Create Project"
3. Choose a project name (e.g., "backend-api-db")
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
pydantic-settings==2.1.0
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

The database tables will be created automatically on first startup. To verify:

```bash
# Start the server (tables will be created)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

## Step 4: Verify Backend

### 4.1 Check API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

### 4.2 Test with cURL

**Register a new user**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "created_at": "2026-02-16T10:30:00Z"
  }
}
```

**Save the token** for subsequent requests:
```bash
export TOKEN="<your_access_token>"
```

**Create a task**:
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Testing the API"}'
```

**Get all tasks**:
```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN"
```

## Step 5: Test with Postman

### 5.1 Import OpenAPI Specification

1. Open Postman
2. Click "Import"
3. Select "File" tab
4. Choose `specs/002-backend-api-db/contracts/openapi.yaml`
5. Click "Import"

### 5.2 Set Up Environment

1. Click "Environments" in Postman
2. Create new environment "Backend API Dev"
3. Add variables:
   - `base_url`: http://localhost:8000
   - `token`: (leave empty, will be set automatically)

### 5.3 Test Sequence

**1. Register User**:
- Request: POST {{base_url}}/auth/register
- Body:
  ```json
  {
    "email": "postman@example.com",
    "password": "PostmanTest123!"
  }
  ```
- In "Tests" tab, add:
  ```javascript
  pm.environment.set("token", pm.response.json().access_token);
  ```

**2. Create Task**:
- Request: POST {{base_url}}/tasks
- Authorization: Bearer Token → {{token}}
- Body:
  ```json
  {
    "title": "My first task",
    "description": "Testing from Postman"
  }
  ```

**3. Get All Tasks**:
- Request: GET {{base_url}}/tasks
- Authorization: Bearer Token → {{token}}

**4. Update Task**:
- Request: PUT {{base_url}}/tasks/1
- Authorization: Bearer Token → {{token}}
- Body:
  ```json
  {
    "title": "Updated task",
    "is_completed": true
  }
  ```

**5. Delete Task**:
- Request: DELETE {{base_url}}/tasks/1
- Authorization: Bearer Token → {{token}}

## Step 6: Run Tests

### 6.1 Install Test Dependencies

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install test dependencies
pip install pytest pytest-asyncio httpx
```

### 6.2 Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### 6.3 Expected Test Output

```
============================= test session starts ==============================
collected 15 items

tests/test_auth.py ........                                              [ 53%]
tests/test_tasks.py .......                                              [100%]

============================== 15 passed in 2.34s ===============================
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
- Ensure `JWT_SECRET` in `.env` is set
- Regenerate secret: `openssl rand -hex 32`
- Check token hasn't expired (default: 24 hours)

### Database Issues

#### Issue: "relation does not exist" errors
**Solution**: Restart the server to trigger table creation
```bash
uvicorn src.main:app --reload
```

#### Issue: "password authentication failed"
**Solution**:
- Verify Neon connection string is correct
- Check that password doesn't contain special characters that need URL encoding
- Try resetting database password in Neon console

### API Issues

#### Issue: 401 Unauthorized on protected endpoints
**Solution**:
- Verify token is included in Authorization header
- Check token format: `Bearer <token>`
- Ensure token hasn't expired
- Try logging in again to get a fresh token

#### Issue: 403 Forbidden when accessing tasks
**Solution**:
- Verify you're accessing your own tasks
- Check that user_id in token matches task owner
- Try creating a new task and accessing it

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit files in `backend/src/`
   - FastAPI auto-reloads on file changes
   - Check http://localhost:8000/docs for updated API

2. **Database Changes**:
   - Update models in `backend/src/models/`
   - Restart server to apply changes
   - For production, use Alembic migrations

3. **Testing Changes**:
   - Write tests in `backend/tests/`
   - Run `pytest` to verify
   - Check coverage with `pytest --cov`

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

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection string | postgresql+asyncpg://user:pass@host/db |
| JWT_SECRET | Secret key for JWT signing | 32-character hex string |
| JWT_ALGORITHM | JWT signing algorithm | HS256 |
| JWT_EXPIRATION_HOURS | Token expiration time | 24 |
| CORS_ORIGINS | Allowed frontend origins | http://localhost:3000 |
| DEBUG | Enable debug mode | True |

## API Endpoints Summary

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and receive JWT token
- `POST /auth/logout` - Logout (client-side)

### Tasks (Protected)
- `GET /tasks` - Get all user's tasks
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

## Next Steps

After completing this quickstart:

1. **Review Documentation**:
   - Read `specs/002-backend-api-db/spec.md` for requirements
   - Review `specs/002-backend-api-db/plan.md` for architecture
   - Check `specs/002-backend-api-db/data-model.md` for database schema

2. **Explore the API**:
   - Visit http://localhost:8000/docs
   - Try out different endpoints
   - Review request/response formats

3. **Run Tests**:
   - Execute backend tests: `pytest`
   - Review test coverage
   - Write additional tests

4. **Start Development**:
   - Review `specs/002-backend-api-db/tasks.md` (when available)
   - Pick a task to implement
   - Follow the development workflow

## Support

If you encounter issues not covered in this guide:

1. Check the troubleshooting section above
2. Review error messages carefully
3. Check terminal output for backend errors
4. Consult the API documentation at http://localhost:8000/docs
5. Review the OpenAPI specification in `contracts/openapi.yaml`

## Security Notes

⚠️ **Important for Production**:

- Change all default secrets and passwords
- Use environment-specific configuration
- Enable HTTPS for all connections
- Implement rate limiting
- Add proper logging and monitoring
- Review security best practices in the constitution
- Never commit `.env` files to version control

---

**Last Updated**: 2026-02-16
**Maintained By**: Backend API Team
