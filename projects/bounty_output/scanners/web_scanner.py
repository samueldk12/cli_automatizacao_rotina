#!/usr/bin/env python3
"""
Web Vulnerability Scanner

Scans a web target for common security issues:
  - Missing or weak security headers
  - Reflected XSS via URL parameters and request headers
  - Common misconfigurations (exposed files, dangerous HTTP methods)
  - Information disclosure (server versions, comments, emails)
  - CRLF injection, open redirects, SSL/TLS issues

Exports findings as an HTML report.

Usage:
    python scanners/web_scanner.py --target https://example.com

Part of bounty_company toolkit.
"""

import argparse
import json
import os
import re
import socket
import sys
import time
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("[ERROR] 'requests' library is required. Install: pip install requests")
    sys.exit(1)

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("[ERROR] 'jinja2' is required. Install: pip install jinja2")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config():
    """Load config.json or fall back to built-in defaults."""
    defaults = {
        "scanner": {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "max_redirects": 5,
            "verify_ssl": False,
            "scan_depth": 1,
            "xss_payloads": [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
                "<svg/onload=alert(1)>",
                "\" onfocus=alert(1) autofocus=\"",
                "javascript:alert(1)",
            ],
        },
        "paths_to_check": [
            "robots.txt",
            "sitemap.xml",
            ".env",
            "wp-config.php",
            ".git/config",
            ".git/HEAD",
            "phpinfo.php",
            "admin/",
            "wp-login.php",
            "wp-admin/",
            ".htaccess",
            "server-status",
            "backup.zip",
            "backup.sql",
            "dump.sql",
            "config.php",
            "config.yml",
            "config.yaml",
            "api/v1/",
            "swagger.json",
            "swagger-ui.html",
            "graphql",
            ".well-known/security.txt",
            "crossdomain.xml",
            "clientaccesspolicy.xml",
        ],
        "report": {
            "title": "Web Vulnerability Scan Report",
            "author": "bounty_company toolkit",
            "output_dir": "output",
        },
    }

    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as fh:
                loaded = json.load(fh)
            for key in defaults:
                if key not in loaded:
                    loaded[key] = defaults[key]
                elif isinstance(defaults[key], dict):
                    for sub in defaults[key]:
                        if sub not in loaded[key]:
                            loaded[key][sub] = defaults[key][sub]
            return loaded
        except (json.JSONDecodeError, IOError):
            pass

    return defaults


# ---------------------------------------------------------------------------
# Finding model
# ---------------------------------------------------------------------------

class Finding:
    """A single security finding with severity and remediation advice."""

    SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]

    def __init__(self, title, severity, description, evidence="",
                 recommendation="", url="", test_type=""):
        self.title = title
        self.severity = severity
        self.description = description
        self.evidence = evidence
        self.recommendation = recommendation
        self.url = url
        self.test_type = test_type
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def to_dict(self):
        return {
            "title": self.title,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "url": self.url,
            "test_type": self.test_type,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Scan session
# ---------------------------------------------------------------------------

class ScanSession:
    """requests.Session wrapper configured for security scanning."""

    def __init__(self, config):
        scanner = config.get("scanner", {})
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": scanner.get(
                "user_agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36",
            )
        })
        self.session.max_redirects = scanner.get("max_redirects", 5)
        self.session.verify = scanner.get("verify_ssl", False)
        self.timeout = 10

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(url, **kwargs)

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, url, **kwargs)


# ---------------------------------------------------------------------------
# CHECK 1 - Security Headers
# ---------------------------------------------------------------------------

def check_security_headers(session, base_url, findings):
    """Check for missing or misconfigured HTTP security headers."""
    expected = {
        "Content-Security-Policy": {
            "severity": "HIGH",
            "description": (
                "Content-Security-Policy (CSP) header is missing. Without "
                "CSP, the page is more susceptible to cross-site scripting "
                "(XSS) and data injection attacks."
            ),
            "recommendation": (
                "Set a strict CSP header, e.g. "
                "Content-Security-Policy: default-src 'self'"
            ),
        },
        "X-Frame-Options": {
            "severity": "MEDIUM",
            "description": (
                "X-Frame-Options is missing. The site may be vulnerable "
                "to clickjacking."
            ),
            "recommendation": (
                "Set X-Frame-Options: DENY or SAMEORIGIN."
            ),
        },
        "X-Content-Type-Options": {
            "severity": "MEDIUM",
            "description": (
                "X-Content-Type-Options is missing. Browsers may MIME-sniff "
                "responses, enabling drive-by download attacks."
            ),
            "recommendation": "Set X-Content-Type-Options: nosniff.",
        },
        "Strict-Transport-Security": {
            "severity": "HIGH",
            "description": (
                "HTTP Strict Transport Security (HSTS) is missing. Users "
                "may be vulnerable to protocol downgrade attacks."
            ),
            "recommendation": (
                "Set Strict-Transport-Security: max-age=31536000; "
                "includeSubDomains."
            ),
        },
        "X-XSS-Protection": {
            "severity": "LOW",
            "description": (
                "X-XSS-Protection header is absent (deprecated in modern "
                "browsers but still useful as a defense-in-depth layer)."
            ),
            "recommendation": "Set X-XSS-Protection: 1; mode=block.",
        },
        "Referrer-Policy": {
            "severity": "LOW",
            "description": (
                "Referrer-Policy is missing. The full URL may be leaked "
                "to third-party sites via the Referer header."
            ),
            "recommendation": (
                "Set Referrer-Policy: strict-origin-when-cross-origin."
            ),
        },
        "Permissions-Policy": {
            "severity": "LOW",
            "description": (
                "Permissions-Policy is missing. Browser features such as "
                "camera, microphone, and geolocation may not be restricted."
            ),
            "recommendation": (
                "Set Permissions-Policy to restrict unneeded features."
            ),
        },
    }

    # Try HTTPS then HTTP
    parsed = urlparse(base_url)
    target_host = parsed.netloc or parsed.path
    for scheme in ("https", "http"):
        test_url = f"{scheme}://{target_host}"
        try:
            resp = session.get(test_url)
            break
        except requests.exceptions.RequestException:
            continue
    else:
        findings.append(Finding(
            title="Cannot reach target for header checks",
            severity="INFO",
            description=f"Unable to connect to {base_url}.",
            url=base_url,
            test_type="security_headers",
        ))
        return

    headers_lower = {k.lower(): (k, v) for k, v in resp.headers.items()}

    for header_name, info in expected.items():
        key = header_name.lower()
        if key not in headers_lower:
            findings.append(Finding(
                title=f"Missing: {header_name}",
                severity=info["severity"],
                description=info["description"],
                evidence=f"Header not found in response.",
                recommendation=info["recommendation"],
                url=test_url,
                test_type="security_headers",
            ))
        else:
            _, value = headers_lower[key]
            if header_name == "X-Frame-Options" and \
                    value.upper() not in ("DENY", "SAMEORIGIN"):
                findings.append(Finding(
                    title="Weak X-Frame-Options",
                    severity="MEDIUM",
                    description=f"X-Frame-Options value '{value}' may not "
                                "sufficiently prevent clickjacking.",
                    evidence=f"X-Frame-Options: {value}",
                    recommendation="Set to DENY or SAMEORIGIN.",
                    url=test_url,
                    test_type="security_headers",
                ))
            if header_name == "X-XSS-Protection" and "0" in value:
                findings.append(Finding(
                    title="X-XSS-Protection is disabled",
                    severity="MEDIUM",
                    description="The header explicitly disables XSS filtering.",
                    evidence=f"X-XSS-Protection: {value}",
                    recommendation="Set to: 1; mode=block",
                    url=test_url,
                    test_type="security_headers",
                ))


# ---------------------------------------------------------------------------
# CHECK 2 - Reflected XSS
# ---------------------------------------------------------------------------

def check_reflected_xss(session, base_url, findings):
    """Probe for reflected XSS via query params and custom headers."""
    payloads = [
        "<script>alert(1)</script>",
        "<svg/onload=alert(1)>",
        "<img src=x onerror=alert(1)>",
    ]
    target = base_url.rstrip("/")

    # Via query parameter
    for payload in payloads:
        test_url = f"{target}/?q={requests.utils.quote(payload)}"
        try:
            resp = session.get(test_url)
            if payload in resp.text and len(resp.text) > 50:
                idx = resp.text.index(payload)
                ctx = resp.text[max(0, idx - 40):idx + len(payload) + 40]
                findings.append(Finding(
                    title="Reflected XSS via URL parameter",
                    severity="HIGH",
                    description=(
                        "A payload injected in a query parameter was "
                        "reflected without encoding, suggesting a "
                        "cross-site scripting vulnerability."
                    ),
                    evidence=f"URL: {test_url}\nContext: ...{ctx}...",
                    recommendation=(
                        "Apply context-aware output encoding and set a "
                        "Content-Security-Policy."
                    ),
                    url=test_url,
                    test_type="xss_reflection",
                ))
                break
        except requests.exceptions.RequestException:
            pass

    # Via X-Forwarded-Host
    evil = "<svg/onload=alert(1)>.evil.com"
    try:
        resp = session.get(target, headers={"X-Forwarded-Host": evil})
        if evil in resp.text:
            findings.append(Finding(
                title="Reflected XSS via X-Forwarded-Host",
                severity="HIGH",
                description=(
                    "The X-Forwarded-Host header value is reflected in "
                    "the response without encoding."
                ),
                evidence=f"X-Forwarded-Host: {evil}",
                recommendation="Do not echo request headers in HTML.",
                url=target,
                test_type="xss_reflection",
            ))
    except requests.exceptions.RequestException:
        pass

    # Via Referer
    bad_ref = f"{target}/<script>alert(1)</script>"
    try:
        resp = session.get(target, headers={"Referer": bad_ref})
        if "<script>alert(1)</script>" in resp.text:
            findings.append(Finding(
                title="Reflected XSS via Referer header",
                severity="HIGH",
                description="The Referer header is reflected without encoding.",
                evidence=f"Referer: {bad_ref}",
                recommendation="Encode data from request headers.",
                url=target,
                test_type="xss_reflection",
            ))
    except requests.exceptions.RequestException:
        pass


# ---------------------------------------------------------------------------
# CHECK 3 - CRLF Injection
# ---------------------------------------------------------------------------

def check_crlf_injection(session, base_url, findings):
    """Test for HTTP response splitting via encoded CRLF."""
    test_url = base_url.rstrip("/") + "/%0d%0aX-Crlf-Test%3a%201"
    try:
        resp = session.get(test_url)
        if resp.headers.get("x-crlf-test"):
            findings.append(Finding(
                title="CRLF Injection detected",
                severity="CRITICAL",
                description=(
                    "Injected CRLF characters in the URL were interpreted "
                    "as an HTTP header separator (HTTP response splitting)."
                ),
                evidence="X-Crlf-Test header appeared in the response.",
                recommendation="Reject or encode CR/LF in URLs and inputs.",
                url=test_url,
                test_type="crlf_injection",
            ))
    except requests.exceptions.RequestException:
        pass


# ---------------------------------------------------------------------------
# CHECK 4 - Exposed Sensitive Files
# ---------------------------------------------------------------------------

def check_exposed_files(session, base_url, findings):
    """Probe common paths for exposed configuration and backup files."""
    config = load_config()
    paths = config.get("paths_to_check", [])
    base = base_url.rstrip("/") + "/"

    sensitive = {
        ".env": ("HIGH",
                 "An .env file is publicly accessible and may contain "
                 "database credentials, API keys, and other secrets."),
        ".git/config": ("HIGH",
                        "Git config is exposed. Repository URLs and "
                        "usernames may be visible."),
        ".git/HEAD": ("MEDIUM",
                       "Git HEAD file is visible. The repo may be browsable."),
        "wp-config.php": ("HIGH",
                           "WordPress config exposed -- likely contains "
                           "database credentials and salt keys."),
        "phpinfo.php": ("HIGH",
                         "phpinfo() reveals PHP version, server paths, "
                         "environment variables, and modules."),
        ".htaccess": ("MEDIUM",
                       "Apache .htaccess is accessible, revealing server "
                       "configuration details."),
        "server-status": ("HIGH",
                           "Apache server-status leaks client IPs and "
                           "active connection details."),
        "swagger.json": ("MEDIUM",
                          "OpenAPI spec exposed to the public."),
        "swagger-ui.html": ("MEDIUM",
                              "Swagger UI is publicly accessible."),
        "admin/": ("MEDIUM",
                    "Admin directory is accessible."),
        "backup.zip": ("HIGH",
                        "Backup archive is publicly downloadable."),
        "dump.sql": ("HIGH",
                      "Database dump is publicly accessible."),
        "graphql": ("LOW",
                     "GraphQL endpoint is publicly accessible. Introspection "
                     "may expose the full schema."),
    }

    for path in paths:
        url = base + path
        try:
            resp = session.get(url, allow_redirects=False, timeout=10)
            if resp.status_code == 200 and len(resp.text) > 50:
                sev, desc = sensitive.get(path, ("INFO", None))
                findings.append(Finding(
                    title=f"Exposed: /{path}",
                    severity=sev,
                    description=desc or (
                        f"/{path} returned HTTP 200 with content. "
                        "Manual review recommended."
                    ),
                    evidence=f"HTTP {resp.status_code}, "
                             f"{len(resp.text)} bytes",
                    recommendation=(
                        f"Remove or restrict access to /{path}."
                        if desc else "Verify if this should be public."
                    ),
                    url=url,
                    test_type="exposed_sensitive_files",
                ))
        except requests.exceptions.RequestException:
            pass


# ---------------------------------------------------------------------------
# CHECK 5 - HTTP Methods
# ---------------------------------------------------------------------------

def check_http_methods(session, base_url, findings):
    """Test OPTIONS, TRACE, and dangerous method enablement."""
    target = base_url.rstrip("/")

    try:
        resp = session.request("OPTIONS", target)
        methods = set()
        for h in ("Allow", "Public"):
            val = resp.headers.get(h, "")
            if val:
                methods.update(m.strip() for m in val.split(","))

        if methods:
            dangerous = {"PUT", "DELETE", "PATCH", "TRACE", "CONNECT"}
            found = methods.intersection(dangerous)
            if found:
                findings.append(Finding(
                    title="Dangerous HTTP methods enabled",
                    severity="MEDIUM",
                    description=(
                        f"These methods can modify server state or aid "
                        f"attacks: {', '.join(sorted(found))}."
                    ),
                    evidence=f"Allowed: {', '.join(sorted(methods))}",
                    recommendation="Disable methods that are not needed.",
                    url=target,
                    test_type="http_methods",
                ))

        if resp.headers.get("DAV"):
            findings.append(Finding(
                title="WebDAV is enabled",
                severity="MEDIUM",
                description="WebDAV may allow unauthorised file operations.",
                evidence=f"DAV: {resp.headers['DAV']}",
                recommendation="Disable WebDAV unless required.",
                url=target,
                test_type="http_methods",
            ))
    except requests.exceptions.RequestException:
        pass

    # TRACE check (separate request)
    try:
        resp = session.request("TRACE", target)
        if resp.status_code == 200:
            findings.append(Finding(
                title="HTTP TRACE method enabled",
                severity="MEDIUM",
                description=(
                    "TRACE responses echo the request and can be "
                    "abused for Cross-Site Tracing (XST)."
                ),
                evidence="TRACE returned HTTP 200.",
                recommendation="Disable TRACE in server config.",
                url=target,
                test_type="http_methods",
            ))
    except requests.exceptions.RequestException:
        pass


# ---------------------------------------------------------------------------
# CHECK 6 - Information Disclosure
# ---------------------------------------------------------------------------

def check_information_disclosure(session, base_url, findings):
    """Look for version leaks, sensitive comments, and emails in responses."""
    target = base_url.rstrip("/") + "/"
    try:
        resp = session.get(target)
    except requests.exceptions.RequestException:
        return

    # Server version
    server = resp.headers.get("Server", "")
    if server:
        ver = re.search(r"(?:Apache|nginx|IIS|gunicorn)/([\d.]+)", server, re.I)
        if ver:
            findings.append(Finding(
                title="Server version disclosure",
                severity="LOW",
                description=f"The Server header leaks version info ({server}).",
                evidence=f"Server: {server}",
                recommendation="Suppress version info (ServerTokens Prod).",
                url=target,
                test_type="information_disclosure",
            ))
        else:
            findings.append(Finding(
                title="Server header present",
                severity="INFO",
                description=f"Server: {server}",
                url=target,
                test_type="information_disclosure",
            ))

    # X-Powered-By
    xpb = resp.headers.get("X-Powered-By", "")
    if xpb:
        findings.append(Finding(
            title="X-Powered-By header detected",
            severity="LOW",
            description=f"Technology stack revealed: {xpb}",
            evidence=f"X-Powered-By: {xpb}",
            recommendation="Remove the X-Powered-By header.",
            url=target,
            test_type="information_disclosure",
        ))

    # Emails
    emails = sorted(set(
        re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                   resp.text)
    ))
    if emails:
        findings.append(Finding(
            title=f"Email addresses found ({len(emails)})",
            severity="INFO",
            description="Emails in page source may aid social engineering.",
            evidence=", ".join(emails[:10]),
            url=target,
            test_type="information_disclosure",
        ))

    # HTML comments with keywords
    for comment in re.findall(r"<!--(.*?)-->", resp.text, re.DOTALL):
        c = comment.strip()
        if any(k in c.lower() for k in [
            "password", "secret", "key", "token", "database",
            "internal", "todo", "fixme", "debug", "staging",
        ]):
            findings.append(Finding(
                title="Suspicious HTML comment",
                severity="MEDIUM",
                description="A comment appears to contain internal notes.",
                evidence=f"<!-- {c[:200]} -->",
                recommendation="Strip comments in production builds.",
                url=target,
                test_type="information_disclosure",
            ))
            break


# ---------------------------------------------------------------------------
# CHECK 7 - SSL / TLS
# ---------------------------------------------------------------------------

def check_ssl_tls(session, base_url, findings):
    """Basic SSL certificate checks on port 443."""
    host = urlparse(base_url).hostname
    if not host:
        return

    try:
        ctx = __import__("ssl").create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = __import__("ssl").CERT_NONE
        with ctx.wrap_socket(
            socket.socket(socket.AF_INET), server_hostname=host
        ) as s:
            s.settimeout(5)
            s.connect((host, 443))
            cert = s.getpeercert()

            not_after = cert.get("notAfter", "")
            if not_after:
                from datetime import datetime as dt
                try:
                    expiry = dt.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    days_left = (expiry - dt.utcnow()).days
                    if days_left <= 0:
                        findings.append(Finding(
                            title="SSL certificate has expired",
                            severity="CRITICAL",
                            description=f"Certificate expired on {not_after}.",
                            url=base_url,
                            test_type="ssl_tls",
                        ))
                    elif days_left <= 30:
                        findings.append(Finding(
                            title="SSL certificate expiring soon",
                            severity="MEDIUM",
                            description=f"Expires in {days_left} days.",
                            evidence=f"Expiry: {not_after}",
                            url=base_url,
                            test_type="ssl_tls",
                        ))
                except ValueError:
                    pass

            subject = dict(x[0] for x in cert.get("subject", []))
            issuer = dict(x[0] for x in cert.get("issuer", []))
            if subject == issuer and subject:
                findings.append(Finding(
                    title="Self-signed SSL certificate",
                    severity="HIGH",
                    description="Certificate is self-signed.",
                    evidence=f"Subject: {subject}",
                    url=base_url,
                    test_type="ssl_tls",
                ))
    except (ConnectionRefusedError, OSError, Exception):
        pass


# ---------------------------------------------------------------------------
# CHECK 8 - Open Redirect
# ---------------------------------------------------------------------------

def check_open_redirect(session, base_url, findings):
    """Test common redirect parameters for open redirect flaws."""
    target = base_url.rstrip("/")
    evil = "https://evil.com"
    params = [
        "next", "redirect", "url", "return", "returnTo",
        "redirect_uri", "goto", "dest", "destination", "redir",
    ]

    for p in params:
        test_url = f"{target}/?{p}={evil}"
        try:
            resp = session.get(test_url, allow_redirects=False, timeout=10)
            if resp.status_code in (301, 302, 303, 307, 308):
                loc = resp.headers.get("Location", "")
                if evil in loc:
                    findings.append(Finding(
                        title=f"Open redirect via '{p}'",
                        severity="MEDIUM",
                        description=(
                            f"The '{p}' parameter redirects to user-supplied "
                            f"URLs, enabling phishing attacks."
                        ),
                        evidence=f"Location: {loc}",
                        recommendation="Validate redirect targets against "
                                       "a whitelist of allowed domains.",
                        url=test_url,
                        test_type="open_redirect",
                    ))
                    break
        except requests.exceptions.RequestException:
            pass


# ---------------------------------------------------------------------------
# HTML report generation
# ---------------------------------------------------------------------------

INLINE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ title }}</title>
<style>
:root{--bg:#0f1117;--card:#1a1d27;--text:#e0e0e0;--muted:#888;--border:#2a2d3a}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Segoe UI,Tahoma,Geneva,Verdana,sans-serif;background:var(--bg);color:var(--text);padding:2rem}
.container{max-width:1100px;margin:0 auto}
h1{font-size:2rem;margin-bottom:.25rem}
h2{font-size:1.4rem;margin:1.5rem 0 .75rem;border-bottom:1px solid var(--border);padding-bottom:.5rem}
h3{font-size:1.1rem;margin-bottom:.25rem}
.meta{color:var(--muted);margin-bottom:2rem}
.stats{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:2rem}
.sc{flex:1;min-width:130px;background:var(--card);border-radius:8px;padding:1rem;text-align:center;border:1px solid var(--border)}
.sc .n{font-size:2rem;font-weight:700}
.sc .l{color:var(--muted);font-size:.85rem}
.f{background:var(--card);border-radius:8px;padding:1.25rem;margin-bottom:1rem;border-left:4px solid var(--border)}
.f.CRITICAL{border-left-color:#dc3545} .f.HIGH{border-left-color:#fd7e14}
.f.MEDIUM{border-left-color:#ffc107} .f.LOW{border-left-color:#17a2b8}
.f.INFO{border-left-color:#6c757d}
.b{display:inline-block;padding:.12rem .5rem;border-radius:4px;font-size:.7rem;font-weight:700;color:#fff}
.b.CRITICAL{background:#dc3545} .b.HIGH{background:#fd7e14}
.b.MEDIUM{background:#ffc107;color:#000} .b.LOW{background:#17a2b8} .b.INFO{background:#6c757d}
.ev{background:#12141c;padding:.75rem;border-radius:4px;font:monospace .85rem;white-space:pre-wrap;margin:.5rem 0;color:#c0c0c0}
.rec{color:#4fc3f7;font-size:.9rem}
.ft{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--border);color:var(--muted);font-size:.85rem;text-align:center}
</style>
</head>
<body>
<div class="container">
<h1>{{ title }}</h1>
<p class="meta">Target: <b>{{ target }}</b> | {{ scan_date }} | {{ author }}</p>
<h2>Summary</h2>
<div class="stats">
{% for lvl in ["CRITICAL","HIGH","MEDIUM","LOW","INFO"] %}
<div class="sc"><div class="n" style="color:{% if lvl=='CRITICAL' %}#dc3545{% elif lvl=='HIGH' %}#fd7e14{% elif lvl=='MEDIUM' %}#ffc107{% elif lvl=='LOW' %}#17a2b8{% else %}#6c757d{% endif %}">{{ counts.get(lvl, 0) }}</div><div class="l">{{ lvl }}</div></div>
{% endfor %}
</div>
<p>{{ total }} finding(s).</p>
<h2>Findings</h2>
{% for f in findings %}
<div class="f {{ f.severity }}">
<h3><span class="b {{ f.severity }}">{{ f.severity }}</span> {{ f.title }}</h3>
<p>{{ f.description }}</p>
{% if f.url %}<p><b>URL:</b> <code>{{ f.url }}</code></p>{% endif %}
{% if f.evidence %}<div class="ev">{{ f.evidence }}</div>{% endif %}
{% if f.recommendation %}<p class="rec"><b>Fix:</b> {{ f.recommendation }}</p>{% endif %}
<p style="color:var(--muted);font-size:.7rem;margin-top:.5rem">{{ f.timestamp }}</p>
</div>
{% else %}
<p>No findings.</p>
{% endfor %}
<div class="ft"><p>Generated by <b>bounty_company</b> toolkit</p></div>
</div>
</body>
</html>"""


def generate_html_report(findings, target, output_dir=None, config=None):
    """Render and write an HTML report."""
    rcfg = (config or {}).get("report", {})
    title = rcfg.get("title", "Web Vulnerability Scan Report")
    author = rcfg.get("author", "bounty_company toolkit")

    counts = Counter(f.severity for f in findings)
    for lvl in Finding.SEVERITY_LEVELS:
        counts.setdefault(lvl, 0)

    order = {s: i for i, s in enumerate(Finding.SEVERITY_LEVELS)}
    sorted_f = sorted(findings, key=lambda f: (order.get(f.severity, 99), f.title))

    env = Environment()
    try:
        if os.path.isdir(TEMPLATES_DIR):
            env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
            tmpl = env.get_template("report.html")
        else:
            tmpl = env.from_string(INLINE_HTML)
    except Exception:
        tmpl = env.from_string(INLINE_HTML)

    html = tmpl.render(
        title=title,
        target=target,
        author=author,
        scan_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        findings=[f.to_dict() for f in sorted_f],
        counts=dict(counts),
        total=len(sorted_f),
    )

    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "output")
    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe = (urlparse(target).hostname or "target").replace(".", "_")
    path = os.path.join(output_dir, f"scan_{safe}_{ts}.html")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"\n[*] HTML report -> {path}")
    return path


# ---------------------------------------------------------------------------
# Scan pipeline
# ---------------------------------------------------------------------------

def run_scan(target, config):
    """Execute all checks and return the list of findings."""
    if not urlparse(target).scheme:
        target = "https://" + target

    print(f"[*] Starting scan: {target}")
    t0 = time.time()
    sess = ScanSession(config)
    findings = []

    print("  [1/8] Security headers ...")
    check_security_headers(sess, target, findings)

    print("  [2/8] Reflected XSS ...")
    check_reflected_xss(sess, target, findings)

    print("  [3/8] CRLF injection ...")
    check_crlf_injection(sess, target, findings)

    print("  [4/8] Exposed sensitive files ...")
    check_exposed_files(sess, target, findings)

    print("  [5/8] HTTP methods ...")
    check_http_methods(sess, target, findings)

    print("  [6/8] Information disclosure ...")
    check_information_disclosure(sess, target, findings)

    print("  [7/8] SSL/TLS ...")
    check_ssl_tls(sess, target, findings)

    print("  [8/8] Open redirect ...")
    check_open_redirect(sess, target, findings)

    elapsed = round(time.time() - t0, 2)
    sev = Counter(f.severity for f in findings)

    print(f"\n{'=' * 50}")
    print("  BOUNTY COMPANY -- WEB SCAN RESULTS")
    print(f"{'=' * 50}")
    print(f"  Target  : {target}")
    print(f"  Duration: {elapsed}s")
    print(f"  Findings: {len(findings)}")
    for lvl in Finding.SEVERITY_LEVELS:
        c = sev.get(lvl, 0)
        if c:
            print(f"    {lvl}: {c}")
    print("=" * 50)

    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Bounty Company -- Web Vulnerability Scanner",
        epilog="Example: python scanners/web_scanner.py --target https://example.com",
    )
    p.add_argument("--target", "-t", required=True,
                   help="Target URL (e.g. https://example.com)")
    p.add_argument("--config", "-c", default=None,
                   help="Path to config.json")
    p.add_argument("--output", "-o", default=None,
                   help="Report output directory")
    p.add_argument("--json", action="store_true", dest="json_out",
                   help="Also save findings as JSON")
    return p.parse_args()


def main():
    args = parse_args()
    config = load_config()

    if args.config and os.path.isfile(args.config):
        try:
            with open(args.config) as fh:
                config = json.load(fh)
        except Exception as exc:
            print(f"[ERROR] Bad config file: {exc}")
            sys.exit(1)

    findings = run_scan(args.target, config)
    generate_html_report(findings, args.target, args.output, config)

    if args.json_out:
        out = args.output or os.path.join(PROJECT_ROOT, "output")
        os.makedirs(out, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out, f"findings_{ts}.json")
        with open(path, "w") as fh:
            json.dump([f.to_dict() for f in findings], fh, indent=4)
        print(f"[*] JSON -> {path}")


if __name__ == "__main__":
    main()
