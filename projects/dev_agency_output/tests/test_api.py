"""
Pytest test suite for Task Manager API.

Tests cover all 12 API endpoints:
    - Auth: register, login, refresh-token, change-password
    - Tasks: list, create, get, update, delete
    - Users: get-me, update-me
    - Admin: list-users, audit-logs

Configuration: uses an in-memory SQLite database via overridden engine.
"""

import sys
import os
from datetime import datetime, timezone

import pytest

# Ensure parent is on path so api package imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

pytestmark = pytest.mark.anyio

# ============================================================================
# Override the database engine to use SQLite in-memory for tests
# ============================================================================

@pytest.fixture(autouse=True, scope="session")
def configure_test_db():
    """
    Before any test module loads, patch the database engine to use SQLite.
    This must happen before importing api.models (which calls declarative_base).
    """
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    test_session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    # Patch the database module
    import api.database as db_mod
    db_mod.engine = test_engine
    db_mod.async_session = test_session_factory

    yield test_engine


@pytest.fixture(autouse=True, scope="function")
async def setup_tables(configure_test_db):
    """Create all tables before each test, drop after."""
    from api.models import Base
    async with configure_test_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with configure_test_db.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ============================================================================
# HTTPX Client Fixture
# ============================================================================

@pytest.fixture
async def client():
    """Provide an async HTTPX test client backed by the FastAPI app."""
    from httpx import AsyncClient, ASGITransport
    from api.main import app

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ============================================================================
# Test Data Factories
# ============================================================================

TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User",
}

ADMIN_USER = {
    "email": "admin@example.com",
    "username": "admin_user",
    "password": "AdminP@ss456!",
    "full_name": "Admin User",
}


def _register_payload(**overrides):
    payload = dict(TEST_USER)
    payload.update(overrides)
    return payload


def _login_payload(**overrides):
    payload = {"email": TEST_USER["email"], "password": TEST_USER["password"]}
    payload.update(overrides)
    return payload


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _task_payload(**overrides):
    payload = {
        "title": "Sample Task",
        "description": "Task description here",
        "status": "pending",
        "priority": 2,
        "due_date": "2025-12-31T23:59:59Z",
    }
    payload.update(overrides)
    return payload


# ============================================================================
# Registration Tests
# ============================================================================

class TestRegister:
    async def test_register_success(self, client):
        resp = await client.post("/api/v1/auth/register", json=_register_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["role"] == "user"

    async def test_register_duplicate_email(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        dup = _register_payload(username="different")
        resp = await client.post("/api/v1/auth/register", json=dup)
        assert resp.status_code == 400
        assert "already" in resp.json()["detail"].lower()

    async def test_register_duplicate_username(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        dup = _register_payload(email="different@example.com")
        resp = await client.post("/api/v1/auth/register", json=dup)
        assert resp.status_code == 400
        assert "already" in resp.json()["detail"].lower()

    async def test_register_short_password(self, client):
        resp = await client.post("/api/v1/auth/register", json=_register_payload(password="short"))
        assert resp.status_code == 422


# ============================================================================
# Login Tests
# ============================================================================

class TestLogin:
    async def test_login_success(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        resp = await client.post("/api/v1/auth/login", json=_login_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        resp = await client.post("/api/v1/auth/login", json=_login_payload(password="wrong"))
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "anything",
        })
        assert resp.status_code == 401


# ============================================================================
# Token Refresh Tests
# ============================================================================

class TestRefreshToken:
    async def test_refresh_success(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        login_resp = await client.post("/api/v1/auth/login", json=_login_payload())
        refresh_token = login_resp.json()["refresh_token"]

        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_invalid_token(self, client):
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid.token.here",
        })
        assert resp.status_code in (401, 422)


# ============================================================================
# Change Password Tests
# ============================================================================

class TestChangePassword:
    async def test_change_password_success(self, client):
        reg_resp = await client.post("/api/v1/auth/register", json=_register_payload())
        token = reg_resp.json()["access_token"]

        resp = await client.post("/api/v1/auth/change-password", json={
            "current_password": "SecurePass123!",
            "new_password": "NewP@ss456!",
        }, headers=_auth_header(token))
        assert resp.status_code == 200
        assert "password changed" in resp.json()["message"].lower()

        # Login with new password should work
        resp2 = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "NewP@ss456!",
        })
        assert resp2.status_code == 200

    async def test_change_password_wrong_current(self, client):
        reg_resp = await client.post("/api/v1/auth/register", json=_register_payload())
        token = reg_resp.json()["access_token"]

        resp = await client.post("/api/v1/auth/change-password", json={
            "current_password": "wrongpassword",
            "new_password": "NewP@ss456!",
        }, headers=_auth_header(token))
        assert resp.status_code == 400

    async def test_change_password_no_auth(self, client):
        resp = await client.post("/api/v1/auth/change-password", json={
            "current_password": "Test",
            "new_password": "New",
        })
        assert resp.status_code == 401


# ============================================================================
# Task CRUD Tests
# ============================================================================

async def _get_token(client):
    """Helper: register + login, return access token."""
    await client.post("/api/v1/auth/register", json=_register_payload())
    login_resp = await client.post("/api/v1/auth/login", json=_login_payload())
    return login_resp.json()["access_token"]


class TestCreateTask:
    async def test_create_task_success(self, client):
        token = await _get_token(client)
        resp = await client.post("/api/v1/tasks", json=_task_payload(), headers=_auth_header(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Sample Task"
        assert data["priority"] == 2
        assert data["status"] == "pending"

    async def test_create_task_invalid_status(self, client):
        token = await _get_token(client)
        resp = await client.post("/api/v1/tasks", json=_task_payload(status="bogus"), headers=_auth_header(token))
        assert resp.status_code == 422

    async def test_create_task_invalid_priority(self, client):
        token = await _get_token(client)
        resp = await client.post("/api/v1/tasks", json=_task_payload(priority=9), headers=_auth_header(token))
        assert resp.status_code == 422

    async def test_create_task_missing_title(self, client):
        token = await _get_token(client)
        resp = await client.post("/api/v1/tasks", json={"description": "no title"}, headers=_auth_header(token))
        assert resp.status_code == 422

    async def test_create_task_unauthenticated(self, client):
        resp = await client.post("/api/v1/tasks", json=_task_payload())
        assert resp.status_code == 401


class TestListTasks:
    async def test_list_tasks_empty(self, client):
        token = await _get_token(client)
        resp = await client.get("/api/v1/tasks", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_tasks_with_items(self, client):
        token = await _get_token(client)
        # Create 3 tasks
        for i in range(3):
            await client.post("/api/v1/tasks", json=_task_payload(title=f"Task {i}"), headers=_auth_header(token))

        resp = await client.get("/api/v1/tasks", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_list_tasks_filter_by_status(self, client):
        token = await _get_token(client)
        await client.post("/api/v1/tasks", json=_task_payload(title="Pending", status="pending"), headers=_auth_header(token))
        await client.post("/api/v1/tasks", json=_task_payload(title="Done", status="completed"), headers=_auth_header(token))

        resp = await client.get("/api/v1/tasks?status=pending", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert all(t["status"] == "pending" for t in data["items"])

    async def test_list_tasks_filter_by_priority(self, client):
        token = await _get_token(client)
        await client.post("/api/v1/tasks", json=_task_payload(title="Low", priority=1), headers=_auth_header(token))
        await client.post("/api/v1/tasks", json=_task_payload(title="High", priority=3), headers=_auth_header(token))

        resp = await client.get("/api/v1/tasks?priority=1", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Low"

    async def test_list_tasks_pagination(self, client):
        token = await _get_token(client)
        for i in range(5):
            await client.post("/api/v1/tasks", json=_task_payload(title=f"Task {i}"), headers=_auth_header(token))

        resp = await client.get("/api/v1/tasks?page=1&page_size=2", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["pages"] == 3

    async def test_list_tasks_user_isolation(self, client):
        token1 = await _get_token(client)
        await client.post("/api/v1/tasks", json=_task_payload(title="User1 Task"), headers=_auth_header(token1))

        # Second user
        await client.post("/api/v1/auth/register", json=_register_payload(email="u2@test.com", username="user2"))
        login_resp = await client.post("/api/v1/auth/login", json={"email": "u2@test.com", "password": "SecurePass123!"})
        token2 = login_resp.json()["access_token"]

        resp = await client.get("/api/v1/tasks", headers=_auth_header(token2))
        data = resp.json()
        assert data["total"] == 0

    async def test_list_tasks_search(self, client):
        token = await _get_token(client)
        await client.post("/api/v1/tasks", json=_task_payload(title="Buy groceries"), headers=_auth_header(token))
        await client.post("/api/v1/tasks", json=_task_payload(title="Fix bugs"), headers=_auth_header(token))

        resp = await client.get("/api/v1/tasks?search=groceries", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Buy groceries"


class TestGetTask:
    async def test_get_task_success(self, client):
        token = await _get_token(client)
        create_resp = await client.post("/api/v1/tasks", json=_task_payload(), headers=_auth_header(token))
        task_id = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/tasks/{task_id}", headers=_auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id
        assert resp.json()["title"] == "Sample Task"

    async def test_get_task_not_found(self, client):
        token = await _get_token(client)
        resp = await client.get("/api/v1/tasks/nonexistent-id", headers=_auth_header(token))
        assert resp.status_code == 404

    async def test_get_task_belongs_to_other_user(self, client):
        token1 = await _get_token(client)
        create_resp = await client.post("/api/v1/tasks", json=_task_payload(), headers=_auth_header(token1))
        task_id = create_resp.json()["id"]

        await client.post("/api/v1/auth/register", json=_register_payload(email="u2@test.com", username="user2"))
        login_resp = await client.post("/api/v1/auth/login", json={"email": "u2@test.com", "password": "SecurePass123!"})
        token2 = login_resp.json()["access_token"]

        resp = await client.get(f"/api/v1/tasks/{task_id}", headers=_auth_header(token2))
        assert resp.status_code == 404


class TestUpdateTask:
    async def test_update_task_success(self, client):
        token = await _get_token(client)
        create_resp = await client.post("/api/v1/tasks", json=_task_payload(), headers=_auth_header(token))
        task_id = create_resp.json()["id"]

        resp = await client.put(f"/api/v1/tasks/{task_id}", json={
            "title": "Updated Title",
            "status": "in_progress",
            "priority": 4,
        }, headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
        assert data["priority"] == 4

    async def test_update_task_empty_body(self, client):
        token = await _get_token(client)
        create_resp = await client.post("/api/v1/tasks", json=_task_payload(), headers=_auth_header(token))
        task_id = create_resp.json()["id"]

        resp = await client.put(f"/api/v1/tasks/{task_id}", json={}, headers=_auth_header(token))
        assert resp.status_code == 400

    async def test_update_task_not_found(self, client):
        token = await _get_token(client)
        resp = await client.put("/api/v1/tasks/nonexistent", json={"title": "X"}, headers=_auth_header(token))
        assert resp.status_code == 404


class TestDeleteTask:
    async def test_delete_task_success(self, client):
        token = await _get_token(client)
        create_resp = await client.post("/api/v1/tasks", json=_task_payload(), headers=_auth_header(token))
        task_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/tasks/{task_id}", headers=_auth_header(token))
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

        # Verify actually deleted
        resp2 = await client.get(f"/api/v1/tasks/{task_id}", headers=_auth_header(token))
        assert resp2.status_code == 404

    async def test_delete_task_not_found(self, client):
        token = await _get_token(client)
        resp = await client.delete("/api/v1/tasks/nonexistent", headers=_auth_header(token))
        assert resp.status_code == 404


# ============================================================================
# User Profile Tests
# ============================================================================

class TestGetMe:
    async def test_get_me_success(self, client):
        token = await _get_token(client)
        resp = await client.get("/api/v1/users/me", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "hashed_password" not in data

    async def test_get_me_unauthenticated(self, client):
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 401


class TestUpdateMe:
    async def test_update_me_full_name(self, client):
        token = await _get_token(client)
        resp = await client.patch("/api/v1/users/me", json={
            "full_name": "Updated Full Name",
        }, headers=_auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Full Name"

    async def test_update_me_no_fields(self, client):
        token = await _get_token(client)
        resp = await client.patch("/api/v1/users/me", json={}, headers=_auth_header(token))
        assert resp.status_code == 400


# ============================================================================
# Admin Tests
# ============================================================================

async def _register_admin(client):
    """Register admin user and return access token."""
    await client.post("/api/v1/auth/register", json=_register_payload(**ADMIN_USER))
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": ADMIN_USER["email"],
        "password": ADMIN_USER["password"],
    })
    return login_resp.json()["access_token"]


class TestAdminListUsers:
    async def test_admin_list_users(self, client):
        admin_token = await _register_admin(client)
        resp = await client.get("/api/v1/admin/users", headers=_auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    async def test_non_admin_cannot_list_users(self, client):
        user_token = await _get_token(client)
        resp = await client.get("/api/v1/admin/users", headers=_auth_header(user_token))
        assert resp.status_code == 403

    async def test_unauthenticated_cannot_list_users(self, client):
        resp = await client.get("/api/v1/admin/users")
        assert resp.status_code == 401


class TestAdminAuditLogs:
    async def test_admin_get_audit_logs(self, client):
        admin_token = await _register_admin(client)
        resp = await client.get("/api/v1/admin/audit-logs", headers=_auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_non_admin_cannot_get_audit_logs(self, client):
        user_token = await _get_token(client)
        resp = await client.get("/api/v1/admin/audit-logs", headers=_auth_header(user_token))
        assert resp.status_code == 403


# ============================================================================
# Health Check Test
# ============================================================================

class TestHealthCheck:
    async def test_health_check(self, client):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
