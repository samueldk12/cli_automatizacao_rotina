# Task Manager API

> **Full-stack task management application — built by the `dev_agency` company plugin.**

## How This Project Was Generated

This project is the output of the **`dev_agency`** (Agencia de Software) company plugin from the [CLI Automacao Rotina](https://github.com/user/cli_automatizacao_rotina) project.

The `dev_agency` plugin is a "company" composed of 4 specialist sub-agents that collaborate to produce complete software projects:

```
dev_agency
├── tech_lead       → Architecture, tech decisions, code review
├── dev_frontend    → UI/UX, React components, HTML/CSS
├── dev_backend     → FastAPI REST API, database models, auth
└── devops          → Docker, docker-compose, deployment config
```

### Each Sub-Agent's Contribution

| Agent | Department | What They Produced |
|-------|-----------|-------------------|
| **tech_lead** | gestao | Defined the architecture (FastAPI + React + Docker), decided on JWT auth, designed the data model, set project structure, established conventions |
| **dev_backend** | desenvolvimento | Built `backend/main.py` with full CRUD operations, user authentication (register/login), PostgreSQL-compatible SQLAlchemy models, JWT token management, stats endpoint, CORS middleware |
| **dev_frontend** | desenvolvimento | Created `frontend/index.html` with React 18 (CDN-based), `frontend/app.js` with complete auth flow, task CRUD UI, status badges, filtering, confirmation modals, responsive design |
| **devops** | infra | Wrote `Dockerfile.backend` (Python 3.12 slim), `Dockerfile.frontend` (Nginx with API proxy), `docker-compose.yml` with health checks and service dependencies |

### Workflow Simulation

```
1. tech_lead receives the prompt: "Build a Task Manager API"
2. tech_lead defines architecture → writes design decisions
3. dev_backend and dev_frontend work in parallel:
   - dev_backend creates API endpoints, models, auth flow
   - dev_frontend creates UI components, state management
4. devops creates containerization setup
5. tech_lead performs code review on all files
6. Final output: this project directory
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│  ┌───────────┐  ┌─────────────┐  ┌────────────────────┐ │
│  │ AuthPage  │  │ Dashboard   │  │ TaskModal/Edit     │ │
│  │ Register  │  │ StatsCards  │  │ ConfirmDialog      │ │
│  │ Login     │  │ TaskList    │  │                    │ │
│  └─────┬─────┘  └──────┬──────┘  └────────┬───────────┘ │
│        │               │                   │             │
│        └───────────────┼───────────────────┘             │
│                    HTTP / REST API                       │
└────────────────────────┬────────────────────────────────┘
                         │ /api/*
                         │
┌────────────────────────┼────────────────────────────────┐
│                     Backend (FastAPI)                   │
│                        ┌──────────────┐                 │
│                        │ CORS / Auth  │                 │
│                        │  Middleware  │                 │
│                        └──────┬───────┘                 │
│                   ┌───────────┼───────────────┐         │
│                   │           │               │         │
│             ┌─────▼──┐  ┌────▼────┐   ┌──────▼────┐   │
│             │  /auth │  │ /tasks  │   │  /stats   │   │
│             │register│  │ CRUD    │   │  summary  │   │
│             │ login  │  │ filter  │   │           │   │
│             └─────┬──┘  └────┬────┘   └──────┬────┘   │
│                   │           │               │         │
│                   └───────────┼──────────────—┘         │
│                         SQLAlchemy                      │
│                    ┌─────────────┐                      │
│                    │  SQLite DB  │                      │
│                    └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, SQLite, JWT (python-jose), bcrypt
- **Frontend:** React 18 (CDN), Babel Standalone, vanilla CSS
- **Infrastructure:** Docker, Docker Compose, Nginx (static + reverse proxy)

## Running the Project

### Option 1: Docker Compose (Recommended)

```bash
cd projects/dev_agency_output

# Build and start all services
docker compose up --build -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop
docker compose down
```

The application will be available at:
- Frontend: `http://localhost:80`
- API: `http://localhost:8000` (also accessible at `http://localhost/api` through nginx)
- API Docs (Swagger): `http://localhost:8000/docs`

### Option 2: Run Backend Locally

```bash
cd projects/dev_agency_output/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open `frontend/index.html` in your browser and set `API_BASE_URL` to `http://localhost:8000`.

## API Documentation

### Authentication

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/auth/register` | Create new user | `{ username, email, password }` |
| POST | `/auth/login` | Login | `{ username, password }` |

Returns `{ access_token, token_type }` on success.

### Tasks (all require Bearer token)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List all user tasks |
| GET | `/tasks/filter?status_filter=pending` | Filter by status |
| GET | `/tasks/{id}` | Get single task |
| PUT | `/tasks/{id}` | Update task |
| PATCH | `/tasks/{id}/status?new_status=completed` | Quick status update |
| DELETE | `/tasks/{id}` | Delete task |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/stats/summary` | Task statistics for current user |

### Example: Full Workflow with curl

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"samuel","email":"sam@example.com","password":"secret123"}'

# Login (save token)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"samuel","password":"secret123"}' | jq -r .access_token)

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Setup CI/CD pipeline","description":"Configure GitHub Actions","priority":"high"}'

# List tasks
curl http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Update status
curl -X PATCH "http://localhost:8000/tasks/TASK_ID/status?new_status=in_progress" \
  -H "Authorization: Bearer $TOKEN"

# Stats
curl http://localhost:8000/stats/summary \
  -H "Authorization: Bearer $TOKEN"
```

## Project Structure

```
dev_agency_output/
├── backend/
│   ├── main.py              # FastAPI application (by dev_backend)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html            # React app shell (by dev_frontend)
│   └── app.js                # React components (by dev_frontend)
├── docker-compose.yml        # Orchestration (by devops)
├── Dockerfile.backend        # Backend container (by devops)
└── Dockerfile.frontend       # Frontend container (by devops)
```

## Link to Main Project

This project was generated by the **dev_agency** company plugin as part of the [CLI Automacao Rotina](https://github.com/user/cli_automatizacao_rotina) ecosystem.

- Plugin source: `plugins/companies/dev_agency.py`
- Plugin docs: See `plugins/companies/` in the main repository
- The dev_agency plugin demonstrates how a multi-agent "company" can autonomously produce a complete, functional software project from a single prompt.
