#!/usr/bin/env python3
"""
Security Company -- REST API Security Tester
Module: AppSec Department
=================================================

Automated REST API security testing tool that checks for authentication bypass,
SQL injection, XSS reflection, rate limiting, open redirects, and more.

Usage:
    python api_tester.py --target https://api.example.com --output report.json
    python api_tester.py --target https://api.example.com --token <jwt> --verbose
"""

import argparse
import json
import os
import sys
import re
import time
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("[!] Required package 'requests' not found. Install with: pip install requests")
    sys.exit(1)


# ============================================================
# Test Payloads (all safe / read-only)
# ============================================================

SQL_INJECTION_PAYLOADS = [
    {"name": "Single quote", "payload": "'", "type": "syntax"},
    {"name": "OR 1=1", "payload": "' OR 1=1--", "type": "boolean"},
    {"name": "UNION SELECT", "payload": "' UNION SELECT NULL,NULL,NULL--", "type": "union"},
    {"name": "Comment injection", "payload": "'/*", "type": "comment"},
    {"name": "SLEEP time-based", "payload": "'; WAITFOR DELAY '0:0:3'--", "type": "time"},
    {"name": "String concatenation", "payload": "' || 'test' || '", "type": "concat"},
    {"name": "Integer injection", "payload": "1 OR 1=1", "type": "numeric"},
    {"name": "Encoded quote", "payload": "%27%20OR%201%3D1--", "type": "encoded"},
]

XSS_PAYLOADS = [
    {"name": "Basic script tag", "payload": "<script>alert(1)</script>"},
    {"name": "Image onerror", "payload": "<img src=x onerror=alert(1)>"},
    {"name": "SVG onload", "payload": "<svg onload=alert(1)>"},
    {"name": "Event handler", "payload": '" onmouseover="alert(1)"'},
    {"name": "Encoded XSS", "payload": "&lt;script&gt;alert(1)&lt;/script&gt;"},
    {"name": "JavaScript URI", "payload": "javascript:alert(1)"},
]

AUTH_BYPASS_PAYLOADS = [
    {"path": "/admin", "headers": {"X-Original-URL": "/admin"}},
    {"path": "/api/v1/admin/users", "headers": {"X-Custom-IP-Authorization": "127.0.0.1"}},
    {"path": "/api/v1/admin", "headers": {"X-Forwarded-For": "127.0.0.1"}},
    {"path": "/api/v1/admin", "headers": {"X-Host": "localhost"}},
    {"path": "/api/v1/admin", "headers": {"X-Forwarded-Host": "localhost"}},
    {"path": "/api/v1/admin", "headers": {"X-Rewrite-URL": "/api/v1/admin"}},
]

OPEN_REDIRECT_PATHS = [
    "/auth/logout?next=https://evil.com",
    "/auth/logout?redirect=https://evil.com",
    "/auth/login?returnUrl=https://evil.com",
    "/auth/callback?url=https://evil.com",
    "/redirect?url=https://evil.com",
    "/api/v1/auth/logout?next=https://evil.com",
    "/api/v1/auth/callback?redirect=https://evil.com",
]

COMMON_API_ENDPOINTS = [
    "/api/v1/users/me",
    "/api/v1/users",
    "/api/v1/products",
    "/api/v1/products/search",
    "/api/v1/orders",
    "/api/v1/auth/login",
    "/api/v1/admin/users",
    "/api/v1/checkout",
    "/api/v1/search",
    "/api/v1/upload",
    "/api/v1/comments",
    "/api/v1/reviews",
    "/graphql",
    "/api",
    "/health",
    "/debug",
]


class VulnFinding:
    """Represents a single vulnerability finding."""

    def __init__(self, vuln_id: str, title: str, severity: str, cvss: float,
                 description: str, affected_url: str, evidence: str,
                 remediation: str, cwe: str = "", category: str = "Other"):
        self.vuln_id = vuln_id
        self.title = title
        self.severity = severity
        self.cvss = cvss
        self.description = description
        self.affected_url = affected_url
        self.evidence = evidence
        self.remediation = remediation
        self.cwe = cwe
        self.category = category
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict:
        return {
            "vuln_id": self.vuln_id,
            "title": self.title,
            "severity": self.severity,
            "cvss_score": self.cvss,
            "description": self.description,
            "affected_url": self.affected_url,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "cwe": self.cwe,
            "category": self.category,
            "timestamp": self.timestamp
        }


class APISecurityTester:
    """REST API security testing class."""

    def __init__(self, target: str, token: Optional[str] = None,
                 threads: int = 8, timeout: int = 10, verbose: bool = False):
        self.target = target.rstrip("/")
        self.token = token
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.findings: list[VulnFinding] = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SecurityCompany-APITester/2.1"
        })
        self.session.verify = False
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.vuln_counter = 0
        self.scan_start = None
        self.scan_end = None
        self._discovered_endpoints = []

    def _next_id(self) -> str:
        self.vuln_counter += 1
        return f"API-{self.vuln_counter:03d}"

    def _log(self, msg: str):
        if self.verbose:
            print(f"  [INFO] {msg}")

    def _get(self, url: str, params=None, headers=None) -> Optional[requests.Response]:
        try:
            all_headers = dict(headers) if headers else {}
            return self.session.get(url, params=params, headers=all_headers,
                                    timeout=self.timeout, allow_redirects=False)
        except requests.RequestException as e:
            self._log(f"GET failed: {e}")
            return None

    def _post(self, url: str, data=None, headers=None) -> Optional[requests.Response]:
        try:
            all_headers = dict(headers) if headers else {}
            return self.session.post(url, json=data, headers=all_headers,
                                     timeout=self.timeout, allow_redirects=False)
        except requests.RequestException as e:
            self._log(f"POST failed: {e}")
            return None

    # ---------------------------------------------------------------
    # Endpoint Discovery
    # ---------------------------------------------------------------
    def discover_endpoints(self):
        """Discover API endpoints by probing common paths."""
        self._log("Discovering API endpoints...")
        for endpoint in COMMON_API_ENDPOINTS:
            url = urljoin(self.target, endpoint)
            resp = self._get(url)
            if resp and resp.status_code not in [404, 405]:
                self._discovered_endpoints.append({
                    "path": endpoint,
                    "status": resp.status_code,
                    "methods_allowed": resp.headers.get("Allow", "")
                })
                self._log(f"  Found: {endpoint} -> HTTP {resp.status_code}")

    # ---------------------------------------------------------------
    # Test 1: Authentication Bypass
    # ---------------------------------------------------------------
    def test_auth_bypass(self):
        """Test for common authentication bypass patterns."""
        self._log("Testing authentication bypass...")
        headers_variants = [
            ("X-Original-URL", "/api/v1/admin"),
            ("X-Custom-IP-Authorization", "127.0.0.1"),
            ("X-Forwarded-For", "127.0.0.1"),
            ("X-Host", "localhost"),
            ("X-Forwarded-Host", "localhost"),
            ("X-Rewrite-URL", "/api/v1/admin"),
        ]
        base_url = urljoin(self.target, "/api/v1/admin/users")

        for header_name, header_value in headers_variants:
            test_headers = {header_name: header_value}
            # Without auth token
            clean_session = requests.Session()
            clean_session.verify = False
            clean_session.headers.update({"User-Agent": "SecurityCompany-APITester/2.1"})

            resp = clean_session.get(base_url, headers=test_headers, timeout=self.timeout,
                                     allow_redirects=False)
            if resp and resp.status_code in [200, 201, 204] and "error" not in resp.text.lower():
                self.findings.append(VulnFinding(
                    vuln_id=self._next_id(),
                    title=f"Authentication Bypass via {header_name}",
                    severity="High",
                    cvss=8.0,
                    description=f"The application allows bypassing authentication by setting "
                                f"the '{header_name}' header to '{header_value}'.",
                    affected_url=base_url,
                    evidence=f"Header: {header_name}: {header_value}\n"
                             f"HTTP Status: {resp.status_code}\nResponse: {resp.text[:200]}",
                    remediation=f"Strip or validate the '{header_name}' header at the reverse "
                                f"proxy level before forwarding to the application.",
                    cwe="CWE-287",
                    category="Authentication"
                ))

    # ---------------------------------------------------------------
    # Test 2: SQL Injection (Safe / Read-Only)
    # ---------------------------------------------------------------
    def test_sql_injection(self):
        """Test for SQL injection using safe, read-only payloads."""
        self._log("Testing SQL injection (safe payloads)...")
        search_params = ["q", "query", "search", "term", "keyword", "filter", "id", "user_id"]

        for endpoint in self._discovered_endpoints[:5]:
            path = endpoint["path"]
            url = urljoin(self.target, path)

            for payload_info in SQL_INJECTION_PAYLOADS:
                for param in search_params:
                    start_time = time.time()
                    resp = self._get(url, params={param: payload_info["payload"]})
                    elapsed = time.time() - start_time

                    if not resp:
                        continue

                    # Check for SQL error patterns in response
                    sql_errors = [
                        r"SQL syntax", r"MySQL", r"pgsql", r"SQLite", r"ORA-\d+",
                        r"Microsoft SQL Server", r"Unclosed quotation",
                        r"invalid input syntax", r"unexpected token",
                        r"syntax error near", r"column .* does not exist",
                    ]
                    body = resp.text
                    error_matches = [pat for pat in sql_errors if re.search(pat, body, re.IGNORECASE)]

                    # Time-based detection
                    is_time_based = (payload_info["type"] == "time" and elapsed > 2.5)

                    # Status code anomaly (e.g., 500 on injection)
                    is_error_status = resp.status_code == 500

                    # Error-based detection
                    if error_matches or is_time_based or is_error_status:
                        details = []
                        if error_matches:
                            details.append(f"SQL error patterns found: {', '.join(error_matches)}")
                        if is_time_based:
                            details.append(f"Time-based detection: request took {elapsed:.2f}s")
                        if is_error_status:
                            details.append(f"HTTP 500 error returned")

                        # Check severity
                        severity = "High" if error_matches else "Medium"
                        cvss = 8.5 if error_matches else 6.0

                        self.findings.append(VulnFinding(
                            vuln_id=self._next_id(),
                            title=f"SQL Injection in {path} (param: {param})",
                            severity=severity,
                            cvss=cvss,
                            description=f"SQL injection detected in the '{param}' parameter of "
                                        f"{path}. Payload type: {payload_info['type']}.",
                            affected_url=url,
                            evidence=f"Payload: {payload_info['name']} = '{payload_info['payload']}'\n"
                                     f"HTTP Status: {resp.status_code}\n"
                                     f"Response time: {elapsed:.2f}s\n"
                                     f"{''.join(chr(10) + f'  {d}' for d in details)}\n"
                                     f"Response snippet: {body[:300]}",
                            remediation=f"Use parameterized queries (prepared statements) for "
                                        f"the '{param}' parameter. Never concatenate user input "
                                        f"into SQL queries.",
                            cwe="CWE-89",
                            category="SQL Injection"
                        ))
                        break  # Found vulnerability, move to next endpoint
                else:
                    continue
                break

    # ---------------------------------------------------------------
    # Test 3: XSS Reflection
    # ---------------------------------------------------------------
    def test_xss_reflection(self):
        """Test for reflected XSS in API responses."""
        self._log("Testing XSS reflection...")
        search_params = ["q", "query", "search", "term", "name", "keyword"]

        for endpoint in self._discovered_endpoints[:3]:
            path = endpoint["path"]
            url = urljoin(self.target, path)

            for xss_payload in XSS_PAYLOADS:
                for param in search_params:
                    resp = self._get(url, params={param: xss_payload["payload"]})
                    if not resp:
                        continue

                    # Check if the payload is reflected in the response
                    # without proper encoding
                    if xss_payload["payload"] in resp.text[:2000]:
                        # Check if it's inside a JSON value (less dangerous) or raw HTML
                        content_type = resp.headers.get("Content-Type", "")
                        if "html" in content_type or "text" in content_type:
                            self.findings.append(VulnFinding(
                                vuln_id=self._next_id(),
                                title=f"Reflected XSS in {path} (param: {param})",
                                severity="High",
                                cvss=7.4,
                                description=f"XSS payload reflected without encoding in {path} "
                                            f"via the '{param}' parameter.",
                                affected_url=url,
                                evidence=f"Payload: {xss_payload['payload']}\n"
                                         f"Payload found in response body (raw reflection)\n"
                                         f"Content-Type: {content_type}",
                                remediation=f"Implement output encoding (HTML entity encoding) "
                                            f"for all user-supplied input. Use Content-Security-Policy "
                                            f"as defense-in-depth.",
                                cwe="CWE-79",
                                category="XSS"
                            ))
                            break
                else:
                    continue
                break

    # ---------------------------------------------------------------
    # Test 4: Rate Limiting
    # ---------------------------------------------------------------
    def test_rate_limiting(self):
        """Test if rate limiting is enforced."""
        self._log("Testing rate limiting...")
        test_url = urljoin(self.target, "/api/v1/auth/login")

        request_times = []
        status_codes = []
        rate_limit_headers = {}

        # Send 15 rapid requests
        for i in range(15):
            start = time.time()
            resp = self._post(test_url, data={"email": "test@test.com", "password": f"wrong{i}"})
            elapsed = time.time() - start

            if resp:
                request_times.append(elapsed)
                status_codes.append(resp.status_code)
                # Capture rate limit headers
                for h in resp.headers:
                    if "rate" in h.lower() or "limit" in h.lower() or "retry" in h.lower():
                        rate_limit_headers[h] = resp.headers[h]

                # If we got a 429, rate limiting IS working
                if resp.status_code == 429:
                    self._log("  [PASS] Rate limiting detected (HTTP 429)")
                    return

        # Check results
        got_429 = 429 in status_codes
        has_rate_headers = bool(rate_limit_headers)

        if not got_429 and not has_rate_headers:
            self.findings.append(VulnFinding(
                vuln_id=self._next_id(),
                title="No Rate Limiting on API",
                severity="High",
                cvss=6.8,
                description="The API does not enforce rate limiting. All 15 rapid requests "
                            "were processed without throttling or rejection.",
                affected_url=test_url,
                evidence=f"Sent 15 requests in rapid succession.\n"
                         f"Status codes: {status_codes[:10]}...\n"
                         f"Rate limit headers: None detected\n"
                         f"Average response time: {sum(request_times)/len(request_times):.3f}s",
                remediation="Implement rate limiting (e.g., 100 req/min per IP, "
                            "5 login attempts/min). Return HTTP 429 when limits are exceeded. "
                            "Include RateLimit-* headers in responses.",
                cwe="CWE-770",
                category="Rate Limiting"
            ))
        elif not got_429 and has_rate_headers:
            self.findings.append(VulnFinding(
                vuln_id=self._next_id(),
                title="Rate Limiting Headers Present but Not Enforced",
                severity="Medium",
                cvss=5.0,
                description="Rate limit headers are present but the server does not "
                            "actually enforce the limits.",
                affected_url=test_url,
                evidence=f"Rate limit headers found: {json.dumps(rate_limit_headers)}\n"
                         f"But no HTTP 429 responses observed in {len(request_times)} requests.",
                remediation="Ensure rate limiting is actually enforced when headers indicate limits.",
                cwe="CWE-770",
                category="Rate Limiting"
            ))

    # ---------------------------------------------------------------
    # Test 5: Open Redirect
    # ---------------------------------------------------------------
    def test_open_redirect(self):
        """Test for open redirect vulnerabilities."""
        self._log("Testing open redirects...")

        for redirect_path in OPEN_REDIRECT_PATHS:
            url = urljoin(self.target, redirect_path)
            resp = self._get(url, allow_redirects=False)

            # Actually follow to check
            try:
                resp_follow = self.session.get(url, timeout=self.timeout)
            except requests.RequestException:
                resp_follow = None

            location = None
            if resp:
                location = resp.headers.get("Location", "")
            if not location and resp_follow:
                location = resp_follow.url

            if location and "evil.com" in location:
                self.findings.append(VulnFinding(
                    vuln_id=self._next_id(),
                    title=f"Open Redirect at {redirect_path}",
                    severity="High",
                    cvss=6.5,
                    description="The application redirects to arbitrary external URLs "
                                "without validation, enabling phishing attacks.",
                    affected_url=url,
                    evidence=f"Redirect parameter value: https://evil.com\n"
                             f"Location header: {location}",
                    remediation="Validate redirect URLs against a whitelist of allowed domains. "
                                "Reject any URL that does not match the application's domain.",
                    cwe="CWE-601",
                    category="Open Redirect"
                ))
                break  # Found one is enough to flag

    # ---------------------------------------------------------------
    # Test 6: IDOR Test
    # ---------------------------------------------------------------
    def test_idor(self):
        """Test for Insecure Direct Object References."""
        self._log("Testing for IDOR vulnerabilities...")

        # If we have a token, try accessing resources with different IDs
        if self.token:
            idor_paths = [
                "/api/v1/orders/{id}",
                "/api/v1/users/{id}",
                "/api/v1/invoices/{id}",
                "/api/v1/account/{id}",
            ]

            for path_template in idor_paths:
                for test_id in ["1", "99999", "0"]:
                    path = path_template.replace("{id}", test_id)
                    url = urljoin(self.target, path)
                    resp = self._get(url)

                    if resp and resp.status_code == 200 and resp.text.strip():
                        # Check if response contains data (not just error)
                        try:
                            data = resp.json()
                            if isinstance(data, dict) and "error" not in data:
                                self.findings.append(VulnFinding(
                                    vuln_id=self._next_id(),
                                    title=f"IDOR on {path_template.replace('{id}', test_id)}",
                                    severity="High",
                                    cvss=7.5,
                                    description=f"Insecure Direct Object Reference allows "
                                                f"accessing resource {test_id} without authorization check.",
                                    affected_url=url,
                                    evidence=f"HTTP {resp.status_code} for ID {test_id}\n"
                                             f"Response: {json.dumps(data, indent=2)[:500]}",
                                    remediation=f"Implement ownership checks -- verify the "
                                                f"authenticated user owns the requested resource.",
                                    cwe="CWE-639",
                                    category="Access Control"
                                ))
                                break
                        except (json.JSONDecodeError, ValueError):
                            pass

    # ---------------------------------------------------------------
    # Main Test
    # ---------------------------------------------------------------
    def test(self) -> dict:
        """Run all API security tests and return results."""
        self.scan_start = datetime.utcnow()
        print(f"[*] Security Company API Security Tester v2.1")
        print(f"[*] Target: {self.target}")
        print(f"[*] Auth Token: {'Provided' if self.token else 'None (unauthenticated tests)'}")
        print(f"[*] Started: {self.scan_start.isoformat()}Z")
        print(f"[*] Using {self.threads} threads...")
        print()

        tests = [
            ("Endpoint Discovery", self.discover_endpoints),
            ("Authentication Bypass", self.test_auth_bypass),
            ("SQL Injection", self.test_sql_injection),
            ("XSS Reflection", self.test_xss_reflection),
            ("Rate Limiting", self.test_rate_limiting),
            ("Open Redirect", self.test_open_redirect),
            ("IDOR", self.test_idor),
        ]

        for name, test_fn in tests:
            print(f"  [*] Testing: {name}...")
            try:
                test_fn()
                print(f"      Done -- {len(self.findings)} findings so far")
            except Exception as e:
                print(f"      Error: {e}")

        self.scan_end = datetime.utcnow()

        report = {
            "scanner": "SecurityCompany-APITester",
            "version": "2.1",
            "department": "AppSec",
            "target": self.target,
            "scan_start": self.scan_start.isoformat() + "Z",
            "scan_end": self.scan_end.isoformat() + "Z",
            "duration_seconds": (self.scan_end - self.scan_start).total_seconds(),
            "total_vulnerabilities": len(self.findings),
            "endpoints_discovered": self._discovered_endpoints,
            "summary": {
                "Critical": len([f for f in self.findings if f.severity == "Critical"]),
                "High": len([f for f in self.findings if f.severity == "High"]),
                "Medium": len([f for f in self.findings if f.severity == "Medium"]),
                "Low": len([f for f in self.findings if f.severity == "Low"]),
            },
            "findings": [f.to_dict() for f in self.findings]
        }
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Security Company REST API Security Tester (AppSec Department)"
    )
    parser.add_argument("--target", "-t", required=True, help="Target API URL (e.g., https://api.example.com)")
    parser.add_argument("--token", default=None, help="Authentication token (JWT)")
    parser.add_argument("--output", "-o", default="api_test_report.json", help="Output JSON file")
    parser.add_argument("--threads", type=int, default=8, help="Thread count (default: 8)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    tester = APISecurityTester(
        target=args.target,
        token=args.token,
        threads=args.threads,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    report = tester.test()

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] Test complete. {report['total_vulnerabilities']} vulnerabilities found.")
    print(f"[+] Report saved to: {args.output}")
    print(f"[+] Duration: {report['duration_seconds']:.1f}s")
    print(f"\n    Summary:")
    for sev in ["Critical", "High", "Medium", "Low"]:
        count = report["summary"][sev]
        print(f"      {sev:10s}: {count}")


if __name__ == "__main__":
    main()
