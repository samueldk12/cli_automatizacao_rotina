"""
Pydantic schemas for request/response validation.

Provides serializable models for:
    - User registration, login, response
    - Token pairs (access + refresh)
    - Task creation, update, response
    - Paginated task lists
    - Audit log entries
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================================================
# Authentication
# ============================================================================

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=120)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores and hyphens allowed)")
        return v.lower().strip()


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Pair of access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request body for refreshing an access token."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Request body for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ============================================================================
# User
# ============================================================================

class UserResponse(BaseModel):
    """Public user information returned by API."""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Fields a user can update on their own profile."""
    full_name: Optional[str] = Field(None, max_length=120)
    email: Optional[EmailStr] = None


class UserUpdateByAdmin(BaseModel):
    """Fields an admin can update on any user."""
    full_name: Optional[str] = Field(None, max_length=120)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================================
# Task
# ============================================================================

VALID_STATUSES = {"pending", "in_progress", "completed", "cancelled"}
VALID_PRIORITIES = {1, 2, 3, 4}
PRIORITY_LABELS = {1: "low", 2: "medium", 3: "high", 4: "urgent"}


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: str = Field(default="pending")
    priority: int = Field(default=2, ge=1, le=4)
    due_date: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if v not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be 1-4 (got {v})")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (partial update)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    due_date: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower().strip()
            if v not in VALID_STATUSES:
                raise ValueError(
                    f"Invalid status '{v}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
                )
        return v


class TaskResponse(BaseModel):
    """Full task object returned by API."""
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: int
    priority_label: Optional[str] = None
    due_date: Optional[datetime] = None
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj) -> "TaskResponse":
        instance = super().model_validate(obj)
        instance.priority_label = PRIORITY_LABELS.get(obj.priority, "unknown")
        return instance


# ============================================================================
# Pagination
# ============================================================================

class TaskListResponse(BaseModel):
    """Paginated list of tasks."""
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaginationParams(BaseModel):
    """Common pagination query parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============================================================================
# Task Filters
# ============================================================================

class TaskFilterParams(BaseModel):
    """Query parameters for filtering tasks."""
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    overdue: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=200)


# ============================================================================
# Audit Log
# ============================================================================

class AuditLogResponse(BaseModel):
    """Audit log entry returned by API."""
    id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Health / API Info
# ============================================================================

class HealthResponse(BaseModel):
    """Health check endpoint response."""
    status: str
    version: str
    timestamp: datetime


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
