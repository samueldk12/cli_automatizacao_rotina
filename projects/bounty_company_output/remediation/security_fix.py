#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
security_fix.py — CVE-2024-1234 Patched Code (Before/After Comparison)
Bounty Company v2 — Remediation Package

Shows the vulnerable code (BEFORE) and the patched code (AFTER)
for the SQL injection vulnerability in Flask-based authentication.

Usage:
    python security_fix.py          # prints comparison to stdout
    python security_fix.py --patch  # writes patched files to disk
    python security_fix.py --check  # validates existing code is patched
"""

import argparse
import re
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# BEFORE — Vulnerable Code (as found during pentest)
# ---------------------------------------------------------------------------

VULNERABLE_CODE = r'''
# ──── BEFORE: models/auth_vulnerable.py ────
# WARNING — THIS CODE IS VULNERABLE. DO NOT USE IN PRODUCTION.

import sqlite3
from flask import Blueprint, request, jsonify
import hashlib

auth_bp = Blueprint("auth", __name__)


def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn


@auth_bp.route("/api/v1/auth/login", methods=["POST"])
def login_vulnerable():
    """⚠️  VULNERABLE — SQL Injection via string interpolation."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    db = get_db()

    # BUG: Directly interpolating user input into SQL string
    query = (
        f"SELECT id, username, password_hash, role, email, cpf "
        f"FROM users WHERE username = '{username}' "
        f"AND password_hash = '{hashlib.md5(password.encode()).hexdigest()}'"
    )

    result = db.execute(query).fetchone()

    if result:
        # BUG: MD5 instead of bcrypt (weak hashing)
        # BUG: No rate limiting
        # BUG: No MFA
        return jsonify({
            "token": generate_weak_token(result["id"]),
            "user_id": result["id"],
            "role": result["role"],
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user_vulnerable(user_id):
    """⚠️  VULNERABLE — No ownership check (IDOR)."""
    db = get_db()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query).fetchone()

    if result:
        return jsonify(dict(result)), 200
    return jsonify({"error": "User not found"}), 404


@auth_bp.route("/api/v1/admin/users", methods=["GET"])
def list_all_users_vulnerable():
    """⚠️  VULNERABLE — No role verification."""
    db = get_db()
    query = "SELECT * FROM users"
    results = db.execute(query).fetchall()
    return jsonify([dict(r) for r in results]), 200


def generate_weak_token(user_id):
    """⚠️  VULNERABLE — MD5 token is trivially forgeable."""
    import time
    return hashlib.md5(f"{user_id}{time.time()}secret".encode()).hexdigest()
'''

# ---------------------------------------------------------------------------
# AFTER — Patched Code
# ---------------------------------------------------------------------------

PATCHED_CODE = r'''
# ──── AFTER: models/auth_patched.py ────
# CVE-2024-1234 — PATCHED (2024-06-28)
#
# Fixes applied:
#   1. Parameterized queries (eliminates SQLi)
#   2. BCrypt password hashing (replaces weak MD5)
#   3. JWT with proper expiration (replaces MD5 token)
#   4. Rate limiting via flask-limiter
#   5. Input validation with regex whitelist
#   6. Ownership validation (prevents IDOR)
#   7. Role-based access control (prevents unauthorized admin access)
#   8. Proper error handling (prevents information disclosure)

import sqlite3
import re
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt
import jwt  # PyJWT >= 2.0

auth_bp = Blueprint("auth", __name__)

# ── Rate Limiter ─────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

JWT_SECRET = None  # Load from environment in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 1

# ── Input Validation ─────────────────────────────────────────────
USERNAME_RE = re.compile(r"^[\w\.\-]{3,50}$")
EMAIL_RE = re.compile(r"^[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,}$")


def validate_username(username: str) -> bool:
    """Whitelist validation: only allow safe characters."""
    return bool(USERNAME_RE.match(username))


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    return bool(EMAIL_RE.match(email))


# ── Database ─────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn


# ── Auth Decorators ──────────────────────────────────────────────
def require_auth(f):
    """Decorator to require a valid JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing authorization header"}), 401

        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
            )
            request.user = payload  # attach to request context
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


def require_role(required_role: str):
    """Decorator to require a specific user role."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_role = getattr(request.user, {}).get("role", "")
            if user_role != required_role:
                return jsonify({"error": "Insufficient privileges"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── PATCHED ENDPOINTS ────────────────────────────────────────────

@auth_bp.route("/api/v1/auth/login", methods=["POST"])
@limiter.limit("10 per minute")  # Rate limiting!
def login_patched():
    """✅  PATCHED — Parameterized query + bcrypt + JWT."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    # FIX 1: Input validation
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400

    db = get_db()
    try:
        # FIX 2: Parameterized query — prevents ALL SQL injection
        cursor = db.execute(
            "SELECT id, username, password_hash, role, email "
            "FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()

        if not result:
            # Consistent error message — don't reveal whether user exists
            return jsonify({"error": "Invalid credentials"}), 401

        # FIX 3: BCrypt verification (constant-time comparison)
        if not bcrypt.checkpw(
            password.encode("utf-8"), result["password_hash"].encode("utf-8")
        ):
            return jsonify({"error": "Invalid credentials"}), 401

        # FIX 4: JWT with expiration
        token = jwt.encode(
            {
                "user_id": result["id"],
                "role": result["role"],
                "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
                "iat": datetime.now(timezone.utc),
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,
        )

        return jsonify({
            "token": token,
            "user_id": result["id"],
            "role": result["role"],
        }), 200

    except Exception:
        # FIX 5: Generic error — don't leak stack traces
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
@require_auth
def get_user_patched(user_id):
    """✅  PATCHED — Ownership validation (prevents IDOR)."""
    current_user_id = request.user.get("user_id")

    # FIX: Only allow access to own data OR admins
    if current_user_id != user_id and request.user.get("role") != "admin":
        return jsonify({"error": "Access denied"}), 403

    db = get_db()
    try:
        # Parameterized query (also fixes SQLi here)
        result = db.execute(
            "SELECT id, username, email, role FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not result:
            return jsonify({"error": "User not found"}), 404

        # FIX: Don't return sensitive fields (hash, CPF, etc.)
        return jsonify({
            "id": result["id"],
            "username": result["username"],
            "email": result["email"],
        }), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/api/v1/admin/users", methods=["GET"])
@require_auth
@require_role("admin")  # FIX: Role verification!
def list_all_users_patched():
    """✅  PATCHED — Requires admin role + paginated + minimal fields."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    offset = (page - 1) * per_page

    db = get_db()
    try:
        # Pagination prevents mass data extraction
        results = db.execute(
            "SELECT id, username, email, role, created_at "
            "FROM users LIMIT ? OFFSET ?",
            (per_page, offset)
        ).fetchall()

        # FIX: Only return non-sensitive fields
        users = [{
            "id": r["id"],
            "username": r["username"],
            "email": r["email"],
            "role": r["role"],
            "created_at": r["created_at"],
        } for r in results]

        return jsonify({
            "page": page,
            "per_page": per_page,
            "users": users,
        }), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


# ── Security Headers Middleware ───────────────────────────────────

@auth_bp.after_request
def add_security_headers(response):
    """Add security headers to every response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'"
    )
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
'''

# ---------------------------------------------------------------------------
# SQLAlchemy ORM Alternative (bonus)
# ---------------------------------------------------------------------------

ORM_MIGRATION = '''
# ──── BONUS: SQLAlchemy ORM Migration ────
# For long-term maintainability, consider migrating to SQLAlchemy ORM.
# The ORM inherently uses parameterized queries.

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default="user")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# PATCHED login with ORM (parameterized by default):
@auth_bp.route("/api/v1/auth/login", methods=["POST"])
@limiter.limit("10 per minute")
def login_orm():
    data = request.get_json()
    username = data.get("username", "")

    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(data.get("password", "")):
        # JWT generation...
        return jsonify({
            "token": generate_jwt(user),
            "user_id": user.id,
            "role": user.role,
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401
'''

# ---------------------------------------------------------------------------
# Diff Printer
# ---------------------------------------------------------------------------

def print_comparison():
    """Print a side-by-side before/after comparison."""
    print("=" * 70)
    print("  CVE-2024-1234 — VULNERABLE CODE vs. PATCHED CODE")
    print("=" * 70)

    print("\n" + "─" * 35 + " BEFORE ❌ " + "─" * 35)
    print(textwrap.dedent(VULNERABLE_CODE))

    print("\n\n" + "─" * 36 + " AFTER ✅ " + "─" * 36)
    print(textwrap.dedent(PATCHED_CODE))

    print("\n" + "─" * 30 + " ORM ALTERNATIVE " + "─" * 30)
    print(textwrap.dedent(ORM_MIGRATION))


def print_fixes_summary():
    """Print a summary table of all fixes applied."""
    fixes = [
        ("#1", "SQL Injection", "Parameterized queries", "CRITICAL", "REPLACED"),
        ("#2", "Weak Hashing",  "MD5 → BCrypt",      "CRITICAL", "REPLACED"),
        ("#3", "Weak Tokens",   "MD5 → JWT with exp", "HIGH",    "REPLACED"),
        ("#4", "No Rate Limit", "flask-limiter layer", "HIGH",   "ADDED"),
        ("#5", "No Input Val",  "regex whitelist",     "HIGH",   "ADDED"),
        ("#6", "IDOR",          "Ownership check",     "MEDIUM",  "ADDED"),
        ("#7", "No RBAC",       "@require_role dector", "MEDIUM", "ADDED"),
        ("#8", "Info Leak",     "Generic 500 errors",  "LOW",    "FIXED"),
        ("#9", "No Headers",    "Security headers",    "LOW",    "ADDED"),
        ("#10","Mass Enum",     "Pagination",          "LOW",    "ADDED"),
    ]

    print(f"\n  {'Fix':<6} {'Vulnerability':<20} {'Fix Applied':<25} {'Severity':<10} {'Status'}")
    print(f"  {'-'*6} {'-'*20} {'-'*25} {'-'*10} {'-'*10}")
    for fix_id, vuln, fix_text, sev, status in fixes:
        print(f"  {fix_id:<6} {vuln:<20} {fix_text:<25} {sev:<10} {status}")

    print(f"\n  Total fixes: {len(fixes)}")
    print(f"  Critical/High: 5 | Medium: 2 | Low: 3")

# ---------------------------------------------------------------------------
# Code Checker
# ---------------------------------------------------------------------------

VULNERABLE_PATTERNS = [
    (r"WHERE\s+username\s*=\s*['\"]?\s*\{", "F-string SQL interpolation"),
    (r"WHERE\s+.*\+.*username",            "String concatenation in SQL"),
    (r"hashlib\.md5\(.*password",           "MD5 password hashing"),
    (r"md5\(.*time\.time\(\).*secret",      "Weak token generation"),
    (r"db\.execute\(f\"",                   "F-string in db.execute"),
]


def check_file(filepath: str) -> list:
    """Scan a Python file for known vulnerable patterns."""
    path = Path(filepath)
    if not path.exists():
        print(f"  File not found: {filepath}")
        return []

    content = path.read_text()
    findings = []

    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern, description in VULNERABLE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": str(path),
                    "line": line_num,
                    "code": line.strip(),
                    "vulnerability": description,
                    "cve": "CVE-2024-1234",
                })

    return findings

# ---------------------------------------------------------------------------
# Patch Writer
# ────────────────────────────────────────────────────────────────────

def write_patch_files():
    """
    Write the patched code to sample files for demonstration.
    In production, these would be reviewed and committed by the dev team.
    """
    output_dir = Path("patched_output")
    output_dir.mkdir(exist_ok=True)

    files = {
        "models/auth_patched.py": PATCHED_CODE,
        "models/orm_alternative.py": ORM_MIGRATION,
    }

    for filepath, content in files.items():
        full_path = output_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(textwrap.dedent(content))
        print(f"  [+] Written: {full_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Bounty Company — CVE-2024-1234 Security Fix Package"
    )
    parser.add_argument("--patch", action="store_true",
                        help="Write patched files to disk")
    parser.add_argument("--check", metavar="FILE",
                        help="Check a Python file for vulnerable patterns")
    args = parser.parse_args()

    if args.patch:
        print("\nWriting patched files...")
        write_patch_files()
        print("Done.")
    elif args.check:
        print(f"\nScanning {args.check} for CVE-2024-1234 patterns...")
        findings = check_file(args.check)
        if findings:
            print(f"\n  ⚠️  Found {len(findings)} potential vulnerabilities:\n")
            for f in findings:
                print(f"  Line {f['line']}: {f['vulnerability']}")
                print(f"    {f['code']}")
        else:
            print("\n  ✅ No CVE-2024-1234 patterns detected in this file.")
    else:
        print_comparison()
        print_fixes_summary()


if __name__ == "__main__":
    main()