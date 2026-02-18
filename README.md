# Phase 2 Todo Full-Stack Web Application

A secure, multi-user task management web application built with Next.js, FastAPI, and PostgreSQL. This project demonstrates modern full-stack development with JWT authentication, RESTful API design, and responsive UI.

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Task Management**: Full CRUD operations for tasks (Create, Read, Update, Delete)
- **Multi-User Support**: Per-user data isolation - users only see their own tasks
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Instant UI updates after task operations
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Security**: Password hashing with bcrypt, JWT token validation, input sanitization

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 16+ (App Router) | React-based UI framework with server/client components |
| **Frontend** | TypeScript | Type-safe JavaScript for better developer experience |
| **Frontend** | Axios | HTTP client with interceptors for JWT token management |
| **Backend** | FastAPI | High-performance Python web framework |
| **Backend** | SQLModel | SQL database ORM with Pydantic integration |
| **Database** | Neon Serverless PostgreSQL | Scalable, serverless PostgreSQL database |
| **Authentication** | JWT (JSON Web Tokens) | Stateless authentication mechanism |
| **Security** | bcrypt | Password hashing algorithm |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Next.js App Router (React Components)               │  │
│  │  - Auth Context (Login/Register/Logout)              │  │
│  │  - Task Management UI (Create/View/Update/Delete)    │  │
│  │  - Responsive Layout & Error Handling                │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ HTTP + JWT                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Axios API Client                                     │  │
│  │  - Request Interceptor (Inject JWT Token)            │  │
│  │  - Response Interceptor (Handle 401 Errors)          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         Backend                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                  │  │
│  │  - CORS Middleware                                    │  │
│  │  - Exception Handlers                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes                                           │  │
│  │  - /auth/register (POST)                              │  │
│  │  - /auth/login (POST)                                 │  │
│  │  - /auth/logout (POST)                                │  │
│  │  - /tasks (GET, POST)                                 │  │
│  │  - /tasks/{id} (GET, PUT, DELETE)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  JWT Middleware                                       │  │
│  │  - Verify JWT Signature                               │  │
│  │  - Extract User Identity                              │  │
│  │  - Enforce Authorization                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLModel ORM                                         │  │
│  │  - User Model (id, email, hashed_password)           │  │
│  │  - Task Model (id, user_id, title, description)      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Neon Serverless PostgreSQL                      │
│  - users table (indexed on email)                           │
│  - tasks table (indexed on user_id)                         │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
phase_II/
├── backend/                    # FastAPI backend application
│   ├── src/
│   │   ├── api/               # API route handlers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   └── tasks.py       # Task CRUD endpoints
│   │   ├── middleware/        # Custom middleware
│   │   │   └── error_handler.py
│   │   ├── models/            # SQLModel database models
│   │   │   ├── user.py        # User model
│   │   │   └── task.py        # Task model
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   │   ├── auth.py        # Auth schemas
│   │   │   └── task.py        # Task schemas
│   │   ├── utils/             # Utility functions
│   │   │   ├── jwt.py         # JWT token handling
│   │   │   ├── security.py    # Password hashing
│   │   │   └── sanitization.py # Input sanitization
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   └── main.py            # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
│
├── frontend/                   # Next.js frontend application
│   ├─ src/
│   │   ├── app/               # Next.js App Router pages
│   │   │   ├── dashboard/     # Dashboard page (protected)
│   │   │   ├── login/         # Login page
│   │   │   ├── register/      # Register page
│   │   │   ├── layout.tsx     # Root layout with AuthProvider
│   │   │   ├── page.tsx       # Home page
│   │   │   └── globals.css    # Global styles
│   │   ├── components/        # React components
│   │   │   ├── auth/          # Authentication components
│   │   │   ├── tasks/         # Task management components
│   │   │   └── ui/            # Reusable UI components
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useAuth.ts     # Authentication hook
│   │   │   └── useTasks.ts    # Task management hook
│   │   ├── lib/               # Utility libraries
│   │   │   ├── api.ts         # Axios API client
│   │   │   ├── auth.ts        # Auth context provider
│   │   │   └── types.ts       # TypeScript type definitions
│   │   └── middleware.ts      # Route protection middleware
│   ├── package.json           # Node.js dependencies
│   └── .env.example           # Environment variables template
│
└── specs/                      # Documentation and specifications
    └── 001-phase2-todo-app/
        ├── spec.md            # Feature requirements
        ├── plan.md            # Implementation plan
        ├── tasks.md           # Task breakdown
        ├── data-model.md      # Database schema
        ├── contracts/         # API contracts (OpenAPI)
        └── quickstart.md      # Setup guide
```

## Quick Start

### Prerequisites

- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **Neon Account**: [Sign up](https://neon.tech/)

### 1. Clone Repository

```bash
git clone <repository-url>
cd phase_II
git checkout 001-phase2-todo-app
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Neon database URL and JWT secret

# Start backend server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start frontend server
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4. Test the Application

1. Navigate to http://localhost:3000/register
2. Create a new account
3. Log in with your credentials
4. Create, view, update, and delete tasks
5. Test logout functionality

For detailed setup instructions, see [Quickstart Guide](specs/001-phase2-todo-app/quickstart.md).

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and receive JWT token
- `POST /auth/logout` - Logout (client-side token removal)

### Tasks (Protected - Requires JWT)

- `GET /tasks` - Get all tasks for authenticated user
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

Full API documentation available at http://localhost:8000/docs when backend is running.

## Authentication Flow

1. **Registration/Login**: User submits credentials → Backend validates → JWT token generated
2. **Token Storage**: Frontend stores JWT in localStorage
3. **API Requests**: Axios interceptor automatically adds `Authorization: Bearer <token>` header
4. **Token Verification**: Backend middleware verifies JWT signature and extracts user identity
5. **Authorization**: Backend filters all queries by authenticated user's ID
6. **Token Expiration**: Frontend interceptor detects 401 errors and redirects to login

## Security Features

- **Password Hashing**: bcrypt with salt rounds for secure password storage
- **JWT Tokens**: Signed tokens with expiration for stateless authentication
- **Input Sanitization**: XSS prevention through HTML tag removal and length limits
- **CORS Configuration**: Restricted to allowed origins only
- **Per-User Data Isolation**: Database queries filtered by authenticated user ID
- **Authorization Checks**: All protected endpoints verify user ownership
- **Environment Variables**: Secrets stored in .env files (never committed)

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

- **Backend**: FastAPI automatic validation with Pydantic schemas
- **Frontend**: TypeScript for type safety
- **Linting**: Follow project code standards
- **Error Handling**: Comprehensive error handling at all layers

### Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test thoroughly
4. Commit with descriptive messages
5. Push and create a pull request

## Documentation

- **[Feature Specification](specs/001-phase2-todo-app/spec.md)**: User stories and requirements
- **[Implementation Plan](specs/001-phase2-todo-app/plan.md)**: Architecture and technical decisions
- **[Task Breakdown](specs/001-phase2-todo-app/tasks.md)**: Detailed implementation tasks
- **[Data Model](specs/001-phase2-todo-app/data-model.md)**: Database schema and relationships
- **[API Contracts](specs/001-phase2-todo-app/contracts/)**: OpenAPI specifications
- **[Quickstart Guide](specs/001-phase2-todo-app/quickstart.md)**: Detailed setup instructions

## Troubleshooting

### Backend Issues

- **Database Connection**: Verify Neon connection string in `.env`
- **Port Conflicts**: Change port with `--port 8001`
- **Module Errors**: Ensure virtual environment is activated

### Frontend Issues

- **CORS Errors**: Verify backend CORS_ORIGINS includes frontend URL
- **API Connection**: Check NEXT_PUBLIC_API_URL in `.env.local`
- **Auth Issues**: Clear localStorage and try logging in again

See [Quickstart Guide](specs/001-phase2-todo-app/quickstart.md) for detailed troubleshooting.

## Contributing

1. Follow the existing code structure and patterns
2. Write tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting PR
5. Follow commit message conventions

## License

This project is part of a hackathon phase and is intended for educational purposes.

## Support

For issues and questions:
- Check the [Quickstart Guide](specs/001-phase2-todo-app/quickstart.md)
- Review API documentation at http://localhost:8000/docs
- Check browser console for frontend errors
- Check terminal output for backend errors

---

**Built with**: Next.js, FastAPI, SQLModel, Neon PostgreSQL, and JWT Authentication

**Last Updated**: 2026-02-16
