"""
Task Manager API — Complete FastAPI Application

A production-ready API for task management with:
    - JWT authentication (access + refresh tokens)
    - User registration and management
    - Task CRUD with deadlines, priorities, and status
    - Role-based access control (user / admin)
    - Pagination, filtering, and search
    - Rate limiting middleware
    - Audit logging
    - Health check endpoint

Endpoints (12 total):
    Auth:   POST /register, POST /login, POST /refresh, POST /change-password
    Tasks:  GET, POST /tasks      GET, PUT, DELETE /tasks/{id}
    Users:  GET /users             GET /users/{id}
    Admin:  GET /audit-logs        PATCH /users/{id}
"""

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from math import ceil
from typing import Optional

import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth_utils import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from .database import close_db, init_db
from .dependencies import (
    get_current_user,
    get_db,
    log_audit,
    require_role,
)
from .models import AuditLog, Task, User
from .schemas import (
    AuditLogResponse,
    HealthResponse,
    MessageResponse,
    PaginationParams,
    PasswordChange,
    RefreshTokenRequest,
    TaskCreate,
    TaskFilterParams,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
    UserUpdateByAdmin,
)

# ============================================================================
# Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup, close connections on shutdown."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Task Manager API",
    description="Production-ready Task Manager API for startup MVP",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Rate Limiting Middleware
# ============================================================================

rate_limit_store = defaultdict(list)
RATE_LIMIT_MAX = 60  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple in-memory rate limiter (use Redis in production)."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    # Clean old entries
    rate_limit_store[client_ip] = [
        ts for ts in rate_limit_store[client_ip] if now - ts < RATE_LIMIT_WINDOW
    ]

    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Try again later."},
        )

    rate_limit_store[client_ip].append(now)
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
    response.headers["X-RateLimit-Remaining"] = str(
        max(0, RATE_LIMIT_MAX - len(rate_limit_store[client_ip]))
    )
    return response


# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
    )


# ============================================================================
# Authentication Endpoints (4 endpoints)
# ============================================================================

@app.post("/api/v1/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user. Returns user data and tokens."""
    # Check for duplicate email
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # Check for duplicate username
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken.",
        )

    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        role="user",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id, user.role)

    return {
        "user": UserResponse.model_validate(user),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access + refresh tokens."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalars().first()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id, user.role)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@app.post("/api/v1/auth/refresh", response_model=TokenResponse, tags=["Auth"])
async def refresh_token(body: RefreshTokenRequest):
    """Exchange a refresh token for a new access/refresh token pair."""
    from .dependencies import _decode_token

    payload = _decode_token(body.refresh_token, "refresh")
    user_id = payload.get("sub")
    user_role = payload.get("role")

    new_access = create_access_token(user_id, user_role)
    new_refresh = create_refresh_token(user_id, user_role)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
    )


@app.post("/api/v1/auth/change-password", response_model=MessageResponse, tags=["Auth"])
async def change_password(
    body: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the authenticated user's password."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    current_user.hashed_password = hash_password(body.new_password)
    await db.commit()

    return MessageResponse(message="Password changed successfully.")


# ============================================================================
# Task Endpoints (5 endpoints: list + create list, get, update, delete)
# ============================================================================

@app.get("/api/v1/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[int] = Query(None, ge=1, le=4),
    overdue: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List tasks for the current user with optional filtering and pagination.

    Filters: status, priority, overdue, search (title/description)
    """
    query = select(Task).where(Task.owner_id == current_user.id)

    if status_filter:
        query = query.where(Task.status == status_filter.lower())
    if priority is not None:
        query = query.where(Task.priority == priority)
    if overdue is True:
        query = query.where(
            Task.due_date < datetime.now(timezone.utc),
            Task.status != "completed",
            Task.status != "cancelled",
        )
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
            )
        )

    # Total count for pagination
    count_query = select(func.count(Task.id)).select_from(Task).where(Task.owner_id == current_user.id)
    # Reapply filters for count
    if status_filter:
        count_query = count_query.where(Task.status == status_filter.lower())
    if priority is not None:
        count_query = count_query.where(Task.priority == priority)
    if overdue is True:
        count_query = count_query.where(
            Task.due_date < datetime.now(timezone.utc),
            Task.status != "completed",
            Task.status != "cancelled",
        )
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
            )
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    pages = max(1, ceil(total / page_size))
    offset = (page - 1) * page_size

    query = query.order_by(Task.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    tasks = result.scalars().all()

    items = [TaskResponse.from_orm(t) for t in tasks]
    return TaskListResponse(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )


@app.post("/api/v1/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task for the authenticated user."""
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        owner_id=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return TaskResponse.from_orm(task)


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific task by ID (must belong to the current user)."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    return TaskResponse.from_orm(task)


@app.put("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a task. Only the owner can modify their tasks."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    update_data = task_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return TaskResponse.from_orm(task)


@app.delete("/api/v1/tasks/{task_id}", response_model=MessageResponse, tags=["Tasks"])
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task. Only the owner can delete their tasks."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    await db.delete(task)
    await db.commit()
    return MessageResponse(message="Task deleted successfully.")


# ============================================================================
# User Endpoints (2 endpoints)
# ============================================================================

@app.get("/api/v1/users/me", response_model=UserResponse, tags=["Users"])
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@app.patch("/api/v1/users/me", response_model=UserResponse, tags=["Users"])
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated user's profile."""
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


# ============================================================================
# Admin Endpoints (2 endpoints)
# ============================================================================

@app.get("/api/v1/admin/users", response_model=dict, tags=["Admin"])
async def list_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """List all users in the system (admin only)."""
    offset = (page - 1) * page_size

    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar() or 0
    pages = max(1, ceil(total / page_size))

    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
    )
    users = result.scalars().all()

    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@app.get("/api/v1/admin/audit-logs", response_model=dict, tags=["Admin"])
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs with optional filtering (admin only)."""
    query = select(AuditLog)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    total_result = await db.execute(select(func.count(AuditLog.id)).select_from(AuditLog))
    total = total_result.scalar() or 0
    pages = max(1, ceil(total / page_size))

    offset = (page - 1) * page_size
    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": [AuditLogResponse.model_validate(l) for l in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


# ============================================================================
# Run with: uvicorn api.main:app --reload
# ============================================================================

import os

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
    )
