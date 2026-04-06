"""
Task Manager API - FastAPI backend
Authored by: dev_backend agent (dev_agency company plugin)
Review: tech_lead

Features:
- JWT authentication (register / login)
- Full CRUD for tasks (per-user isolation)
- Task stats summary endpoint
- SQLite storage for simplicity (swap to Postgres via DATABASE_URL)
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-agency-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
DATABASE = os.getenv("DATABASE_URL", "sqlite:///./taskmanager.db")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
engine = create_engine(DATABASE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="pending")   # pending | in_progress | completed | cancelled
    priority = Column(String(20), default="medium")  # low | medium | high
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=True)
    owner = relationship("User", back_populates="tasks")


Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    owner_id: str
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Task Manager API",
    description="REST API for task management - built by dev_agency company plugin",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Health ----------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ---- Auth ------------------------------------------------------------------
@app.post("/auth/register", response_model=Token, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.username == user_in.username)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    existing_email = db.execute(select(User).where(User.email == user_in.email)).scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=str(uuid4()),
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token)


@app.post("/auth/login", response_model=Token)
def login(login: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.username == login.username)).scalar_one_or_none()
    if not user or not verify_password(login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token)


# ---- Tasks CRUD ------------------------------------------------------------
@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = Task(
        id=str(uuid4()),
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        due_date=task_in.due_date,
        owner_id=user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tasks = db.execute(
        select(Task)
        .where(Task.owner_id == user.id)
        .order_by(Task.created_at.desc())
    ).scalars().all()
    return tasks


@app.get("/tasks/filter", response_model=list[TaskResponse])
def filter_tasks(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Task).where(Task.owner_id == user.id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == priority_filter)
    query = query.order_by(Task.created_at.desc())
    tasks = db.execute(query).scalars().all()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == user.id)
    ).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == user.id)
    ).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    for key, value in update_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


from fastapi import Query

@app.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: str,
    new_status: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Quick status transition endpoint."""
    task = db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == user.id)
    ).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    valid_statuses = {"pending", "in_progress", "completed", "cancelled"}
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")
    task.status = new_status
    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == user.id)
    ).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None


# ---- Stats -----------------------------------------------------------------
@app.get("/stats/summary")
def stats_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tasks = db.execute(select(Task).where(Task.owner_id == user.id)).scalars().all()
    return {
        "total": len(tasks),
        "pending": sum(1 for t in tasks if t.status == "pending"),
        "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
        "completed": sum(1 for t in tasks if t.status == "completed"),
        "cancelled": sum(1 for t in tasks if t.status == "cancelled"),
        "high_priority": sum(1 for t in tasks if t.priority == "high"),
    }


# ---- Bootstrap -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
