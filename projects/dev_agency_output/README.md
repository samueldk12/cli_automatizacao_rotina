# Dev Agency — Task Manager API

## Problem Statement

A startup needed a production-ready Task Manager API to serve as the backend for a future React frontend. The requirements:

- User registration and authentication with JWT (access + refresh tokens)
- Full task CRUD (create, read, update, delete) with deadline management
- Priority levels and status tracking
- Role-based access control (user vs. admin)
- Pagination, filtering, and search
- Audit logging for compliance
- Containerized deployment (Docker + PostgreSQL)
- Comprehensive test coverage
- API documentation for frontend integration

**Timeline**: 1 week sprint from design to deploy-ready.

## Solution Architecture

```
+-------------------------------------+
|             React App               |
|        (Future Frontend)            |
+------------------+------------------+
                   | HTTP/JSON
                   v
+-------------------------------------+
|          FastAPI Application        |
|                                     |
|  +---------+ +----------+ +-------+ |
|  |  Auth   | |  Tasks   | | Admin | |
|  | Routes  | |  Routes  | |Routes | |
|  |         | |          | |       | |
|  |--Regist | |--CRUD    | |--List | |
|  |--Login  | |--Filter  | |--Audit| |
|  |--Refresh| |--Search  | |--Users| |
|  |--PwdChg | |--Pagin.  | |       | |
|  +----+----+ +----+-----+ +-------+ |
|       |            |                |
|       v            v                |
|  +----------------------+           |
|  |  SQLAlchemy Async    | (ORM)    |
|  +----------+-----------+           |
|             |                       |
|  +----------v-----------+           |
|  |  Rate Limiter/CORS   | (MW)     |
|  +----------+-----------+           |
+-------------+-----------------------+
              |
              v
+-------------------------------------+
|          PostgreSQL 16              |
|                                     |
|  Tables: users | tasks | audit_logs |
+-------------------------------------+
```

## Quick Start

### With Docker (Recommended)
```bash
cd dev_agency_output
docker compose up --build -d
# API at http://localhost:8000
# Docs at http://localhost:8000/api/docs
```

### Local Development
```bash
cd dev_agency_output
pip install -r requirements.txt
# Use SQLite for quick dev without PostgreSQL:
export DATABASE_URL="sqlite+aiosqlite:///./local.db"
uvicorn api.main:app --reload
```

## API Endpoints (12 Total)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | No | Register new user |
| POST | `/api/v1/auth/login` | No | Login, get tokens |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| POST | `/api/v1/auth/change-password` | Yes | Change password |
| GET | `/api/v1/tasks` | Yes | List tasks (paginated, filterable) |
| POST | `/api/v1/tasks` | Yes | Create task |
| GET | `/api/v1/tasks/{id}` | Yes | Get task by ID |
| PUT | `/api/v1/tasks/{id}` | Yes | Update task |
| DELETE | `/api/v1/tasks/{id}` | Yes | Delete task |
| GET | `/api/v1/users/me` | Yes | Get current user profile |
| PATCH | `/api/v1/users/me` | Yes | Update profile |
| GET | `/api/v1/admin/users` | Admin | List all users |
| GET | `/api/v1/admin/audit-logs` | Admin | View audit logs |

## API Documentation

Interactive docs at **/api/docs** (Swagger UI) and **/api/redoc** (ReDoc).

## Running Tests
```bash
cd dev_agency_output
pytest tests/ -v --tb=short
```

Tests use an in-memory SQLite database for fast, isolated test runs.

## Project Structure
```
dev_agency_output/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + all routes
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── dependencies.py  # Auth deps + role checker
│   ├── database.py      # Async DB engine + session
│   └── auth_utils.py    # Password hashing + JWT tokens
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Full endpoint test suite
├── docker-compose.yml   # API + PostgreSQL services
├── requirements.txt     # Python dependencies
├── report.html          # Project status dashboard
└── README.md            # This file
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (async) |
| Validation | Pydantic V2 |
| Auth | PyJWT + bcrypt |
| Database | PostgreSQL 16 |
| Testing | pytest + httpx |
| Deployment | Docker Compose |

## What Each Sub-Agent Did

- **Tech Lead Agent**: Designed architecture, chose tech stack, defined API contract (endpoints, schemas, auth flow)
- **Backend Agent**: Implemented the FastAPI application with all 12 endpoints, middleware, models, and dependencies
- **Tests Agent**: Wrote comprehensive test suite covering all endpoints including edge cases (auth, CRUD, pagination, isolation, admin-only access)
- **DevOps Agent**: Configured docker-compose with PostgreSQL, health checks, and environment variables
- **Docs Agent**: Created interactive OpenAPI docs (Swagger UI), project README, and HTML status report

## License

Internal project — Dev Agency / MYC 2024.
