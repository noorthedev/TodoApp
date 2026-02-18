# Backend API - Task Management System

FastAPI backend with SQLModel ORM and Neon PostgreSQL database.

## Prerequisites

- Python 3.11 or higher
- Neon PostgreSQL account and database
- pip package manager

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Neon database credentials and JWT secret
```

4. Run the server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest
```

## Project Structure

```
backend/
├── src/
│   ├── api/          # API route handlers
│   ├── models/       # SQLModel database models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── utils/        # Utility functions (JWT, security, sanitization)
│   ├── middleware/   # Custom middleware
│   ├── config.py     # Configuration settings
│   ├── database.py   # Database connection
│   └── main.py       # FastAPI application
└── tests/            # Test files
```

## Environment Variables

See `.env.example` for required configuration.
