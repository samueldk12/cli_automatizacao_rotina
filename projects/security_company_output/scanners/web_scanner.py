#!/usr/bin/env python3
"""
Security Company -- Web Vulnerability Scanner
Module: WebSec Department
===============================================

Automated web security scanner that checks for common OWASP vulnerabilities,
misconfigured security headers, SSL/TLS issues, and information disclosure.

Usage:
    python web_scanner.py --target https://example.com --output report.json
    python web_scanner.py --target https://example.com --threads 10 --verbose
"""

import argparse
import json
import os
import ssl
import socket
import sys
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning, InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("[!] Required package 'requests' not found. Install with: pip install requests")
    sys.exit(1)


# ============================================================
# Configuration
# ============================================================

SECURITY_HEADERS = {
    "Content-Security-Policy": {
        "severity": "Medium",
        "description": "Missing Content-Security-Policy header. Enables XSS attacks and data exfiltration.",
        "remediation": "Add: Content-Security-Policy: default-src 'self'; script-src 'self'",
        "cwe": "CWE-693"
    },
    "X-Frame-Options": {
        "severity": "Medium",
        "description": "Missing X-Frame-Options header. Vulnerable to clickjacking attacks.",
        "remediation": "Add: X-Frame-Options: DENY or SAMEORIGIN",
        "cwe": "CWE-1021"
    },
    "X-Content-Type-Options": {
        "severity": "Low",
        "description": "Missing X-Content-Type-Options. Browsers may MIME-sniff responses.",
        "remediation": "Add: X-Content-Type-Options: nosniff",
        "cwe": "CWE-693"
    },
    "Strict-Transport-Security": {
        "severity": "Medium",
        "description": "Missing HSTS header. Vulnerable to SSL stripping attacks.",
        "remediation": "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains",
        "cwe": "CWE-319"
    },
    "X-XSS-Protection": {
        "severity": "Low",
        "description": "Missing X-XSS-Protection header (legacy but still useful for old browsers).",
        "remediation": "Add: X-XSS-Protection: 1; mode=block",
        "cwe": "CWE-79"
    },
    "Referrer-Policy": {
        "severity": "Low",
        "description": "Missing Referrer-Policy header. May leak sensitive URL data.",
        "remediation": "Add: Referrer-Policy: strict-origin-when-cross-origin",
        "cwe": "CWE-200"
    },
    "Permissions-Policy": {
        "severity": "Low",
        "description": "Missing Permissions-Policy header. Browser features unrestricted.",
        "remediation": "Add: Permissions-Policy: geolocation=(), microphone=(), camera=()",
        "cwe": "CWE-250"
    },
    "Cache-Control": {
        "severity": "Low",
        "description": "Missing Cache-Control header on potentially sensitive pages.",
        "remediation": "Add: Cache-Control: no-store, no-cache, must-revalidate",
        "cwe": "CWE-525"
    },
}

DANGEROUS_DIRECTORIES = [
    "/uploads/",
    "/admin/",
    "/.env",
    "/config/",
    "/backups/",
    "/.git/",
    "/.git/config",
    "/server-status",
    "/server-info",
    "/wp-admin/",
    "/phpmyadmin/",
    "/api/v1/internal/",
    "/debug/",
    "/test/",
    "/backup/",
    "/db/",
    "/sql/",
    "/temp/",
    "/tmp/",
    "/logs/",
]

INFORMATION_DISCLOSURE_PATTERNS = {
    "Server header reveals version": r"Server:\s+\S+/\d+",
    "X-Powered-By reveals framework": r"X-Powered-By:\s+.+",
    "X-AspNet-Version exposed": r"X-AspNet-Version:\s+.+",
    "X-Runtime header present": r"X-Runtime:\s+.+",
    "Via header reveals proxy": r"Via:\s+.+",
}


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


class WebScanner:
    """Main web vulnerability scanner class."""

    def __init__(self, target: str, threads: int = 10, timeout: int = 10, verbose: bool = False):
        self.target = target.rstrip("/")
        self.parsed = urlparse(self.target)
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.findings: list[VulnFinding] = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SecurityCompany-WebScanner/2.1"
        })
        self.session.verify = False
        self.vuln_counter = 0
        self.scan_start = None
        self.scan_end = None

    def _next_id(self) -> str:
        self.vuln_counter += 1
        return f"WEB-{self.vuln_counter:03d}"

    def _log(self, msg: str):
        if not self.verbose:
            return
        print(f"  [INFO] {msg}")

    def _get(self, url: str, allow_redirects: bool = True) -> Optional[requests.Response]:
        try:
            return self.session.get(url, timeout=self.timeout, allow_redirects=allow_redirects)
        except requests.RequestException as e:
            self._log(f"Request failed for {url}: {e}")
            return None

    def _head(self, url: str) -> Optional[requests.Response]:
        try:
            return self.session.head(url, timeout=self.timeout, allow_redirects=True)
        except requests.RequestException:
            return self._get(url)

    # ---------------------------------------------------------------
    # Check 1: Security Headers
    # ---------------------------------------------------------------
    def check_security_headers(self):
        """Check for missing security headers."""
        self._log("Checking security headers...")
        resp = self._head(self.target)
        if not resp:
            return

        headers_lower = {k.lower(): (k, v) for k, v in resp.headers.items()}

        for header, info in SECURITY_HEADERS.items():
            if header.lower() not in headers_lower:
                self.findings.append(VulnFinding(
                    vuln_id=self._next_id(),
                    title=f"Missing Security Header: {header}",
                    severity=info["severity"],
                    cvss={"Critical": 9.0, "High": 7.0, "Medium": 5.5, "Low": 3.5}.get(info["severity"], 3.0),
                    description=info["description"],
                    affected_url=self.target,
                    evidence=f"Header '{header}' not present in HTTP response.\nResponse headers:\n" +
                             "\n".join(f"  {k}: {v}" for k, v in resp.headers.items()),
                    remediation=info["remediation"],
                    cwe=info["cwe"],
                    category="Security Headers"
                ))

    # ---------------------------------------------------------------
    # Check 2: Server Information Disclosure
    # ---------------------------------------------------------------
    def check_information_disclosure(self):
        """Check for information disclosure via HTTP headers and error pages."""
        self._log("Checking information disclosure...")
        resp = self._head(self.target)
        if not resp:
            return

        for pattern_name, pattern in INFORMATION_DISCLOSURE_PATTERNS.items():
            for header_name, header_value in resp.headers.items():
                if re.search(pattern, f"{header_name}: {header_value}", re.IGNORECASE):
                    self.findings.append(VulnFinding(
                        vuln_id=self._next_id(),
                        title=f"Information Disclosure: {pattern_name}",
                        severity="Low",
                        cvss=3.5,
                        description=f"The server reveals internal technology stack information via the '{header_name}' header.",
                        affected_url=self.target,
                        evidence=f"{header_name}: {header_value}",
                        remediation=f"Remove or obfuscate the '{header_name}' header from production responses.",
                        cwe="CWE-200",
                        category="Information Disclosure"
                    ))

    # ---------------------------------------------------------------
    # Check 3: Directory Listing
    # ---------------------------------------------------------------
    def check_directory_listing(self):
        """Check if directory listing is enabled for common paths."""
        self._log("Checking directory listing...")

        for path in DANGEROUS_DIRECTORIES:
            url = urljoin(self.target, path)
            resp = self._get(url)
            if not resp:
                continue

            body_lower = resp.text.lower()
            listing_indicators = [
                "index of",
                "directory listing",
                "<pre>",
                "last modified",
                "parent directory",
                "size</th>",
                "name</th>",
            ]

            if any(indicator in body_lower for indicator in listing_indicators):
                self.findings.append(VulnFinding(
                    vuln_id=self._next_id(),
                    title=f"Directory Listing Enabled: {path}",
                    severity="Medium",
                    cvss=5.3,
                    description=f"Directory listing is enabled for {path}, potentially exposing sensitive files.",
                    affected_url=url,
                    evidence=f"HTTP {resp.status_code} -- Page title/content indicates directory listing:\n" +
                             resp.text[:500],
                    remediation=f"Disable directory listing in web server config (autoindex off in Nginx, "
                                f"Options -Indexes in Apache) for {path}.",
                    cwe="CWE-548",
                    category="Information Disclosure"
                ))

    # ---------------------------------------------------------------
    # Check 4: Clickjacking
    # ---------------------------------------------------------------
    def check_clickjacking(self):
        """Check if the site can be framed."""
        self._log("Checking clickjacking protections...")
        resp = self._head(self.target)
        if not resp:
            return

        has_xfo = "X-Frame-Options" in resp.headers
        has_csp_frame = "Content-Security-Policy" in resp.headers and "frame-ancestors" in resp.headers.get("Content-Security-Policy", "")

        if not has_xfo and not has_csp_frame:
            self.findings.append(VulnFinding(
                vuln_id=self._next_id(),
                title="Clickjacking -- No Frame Protection",
                severity="Medium",
                cvss=5.4,
                description="The application can be embedded in an iframe on an attacker-controlled page, "
                            "enabling clickjacking attacks.",
                affected_url=self.target,
                evidence="Neither X-Frame-Options nor Content-Security-Policy (frame-ancestors) "
                         "header is present in the HTTP response.",
                remediation="Add 'X-Frame-Options: DENY' or 'SAMEORIGIN', or set "
                            "'Content-Security-Policy: frame-ancestors \"none\"'.",
                cwe="CWE-1021",
                category="Clickjacking"
            ))

    # ---------------------------------------------------------------
    # Check 5: SSL/TLS Configuration
    # ---------------------------------------------------------------
    def check_ssl_tls(self):
        """Check SSL/TLS configuration for deprecated protocols."""
        self._log("Checking SSL/TLS configuration...")
        hostname = self.parsed.hostname
        port = self.parsed.port or 443

        deprecated_protocols = {
            "SSLv2": ssl.PROTOCOL_TLS_CLIENT if hasattr(ssl, 'PROTOCOL_TLS_CLIENT') else None,
            "SSLv3": getattr(ssl, 'PROTOCOL_SSLv3', None),
            "TLSv1.0": getattr(ssl, 'PROTOCOL_TLSv1', None),
            "TLSv1.1": getattr(ssl, 'PROTOCOL_TLSv1_1', None),
        }

        for proto_name, proto_const in deprecated_protocols.items():
            if proto_const is None:
                continue
            try:
                ctx = ssl.SSLContext(proto_const)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                    s.settimeout(5)
                    s.connect((hostname, port))
                    self.findings.append(VulnFinding(
                        vuln_id=self._next_id(),
                        title=f"Deprecated Protocol Enabled: {proto_name}",
                        severity="High",
                        cvss=7.0,
                        description=f"The server accepts connections using {proto_name}, which is deprecated "
                                    f"and vulnerable to known attacks (POODLE, BEAST).",
                        affected_url=f"tls://{hostname}:{port}",
                        evidence=f"Successfully connected to {hostname}:{port} using {proto_name}",
                        remediation=f"Disable {proto_name} on the server. Enforce TLS 1.2 or higher only.",
                        cwe="CWE-326",
                        category="SSL/TLS"
                    ))
            except (ssl.SSLError, OSError, socket.timeout):
                self._log(f"  [PASS] {proto_name} is not supported (good)")

        # Check certificate
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED
            with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                s.settimeout(5)
                s.connect((hostname, port))
                cert = s.getpeercert()
                not_after = cert.get("notAfter", "")
                if not_after:
                    import datetime as dt
                    from calendar import timegm
                    expiry = dt.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    days_left = (expiry - dt.datetime.utcnow()).days
                    if days_left < 30:
                        self.findings.append(VulnFinding(
                            vuln_id=self._next_id(),
                            title="SSL Certificate Expiring Soon",
                            severity="Medium",
                            cvss=4.0,
                            description=f"SSL certificate expires in {days_left} days.",
                            affected_url=f"tls://{hostname}:{port}",
                            evidence=f"Certificate notAfter: {not_after} ({days_left} days remaining)",
                            remediation="Renew the SSL certificate before expiration.",
                            cwe="CWE-295",
                            category="SSL/TLS"
                        ))
        except (ssl.SSLError, OSError) as e:
            self._log(f"  [WARN] Certificate check failed: {e}")

    # ---------------------------------------------------------------
    # Check 6: HTTP Methods
    # ---------------------------------------------------------------
    def check_http_methods(self):
        """Check for dangerous HTTP methods."""
        self._log("Checking dangerous HTTP methods...")

        dangerous_methods = ["TRACE", "TRACK", "DEBUG"]
        for method in dangerous_methods:
            try:
                req = requests.Request(method, self.target)
                prepared = self.session.prepare_request(req)
                resp = self.session.send(prepared, timeout=self.timeout, allow_redirects=False,
                                         verify=False)
                if resp.status_code == 200:
                    self.findings.append(VulnFinding(
                        vuln_id=self._next_id(),
                        title=f"Dangerous HTTP Method Enabled: {method}",
                        severity="Low",
                        cvss=3.1,
                        description=f"The {method} method is enabled, which can be used for "
                                    f"Cross-Site Tracing (XST) attacks.",
                        affected_url=self.target,
                        evidence=f"HTTP {method} returned status {resp.status_code}",
                        remediation=f"Disable the {method} method in web server configuration.",
                        cwe="CWE-693",
                        category="Security Headers"
                    ))
            except requests.RequestException:
                pass

    # ---------------------------------------------------------------
    # Check 7: Backup Files
    # ---------------------------------------------------------------
    def check_backup_files(self):
        """Check for common backup/config files accessible."""
        self._log("Checking for exposed backup files...")
        backup_paths = [
            "/backup.sql", "/db.sql", "/database.sql", "/dump.sql",
            "/.env", "/config.php", "/wp-config.php", "/config.yml",
            "/credentials.json", "/secrets.json", "/.htpasswd",
            "/package.json", "/composer.json", "/requirements.txt",
        ]
        for path in backup_paths:
            url = urljoin(self.target, path)
            resp = self._get(url)
            if resp and resp.status_code == 200:
                content_type = resp.headers.get("Content-Type", "")
                if ("sql" in content_type or "password" in resp.text.lower() or
                        "secret" in resp.text.lower() or "api_key" in resp.text.lower() or
                        path.endswith(".env")):
                    self.findings.append(VulnFinding(
                        vuln_id=self._next_id(),
                        title=f"Exposed Configuration/Backup File: {path}",
                        severity="Critical",
                        cvss=9.0,
                        description=f"The file {path} is publicly accessible and may contain "
                                    f"sensitive configuration data or credentials.",
                        affected_url=url,
                        evidence=f"HTTP 200 for {path}. Content-Type: {content_type}\n"
                                 f"Content preview: {resp.text[:200]}",
                        remediation=f"Remove {path} from publicly accessible directories. "
                                    f"Add to .htaccess or nginx deny rules.",
                        cwe="CWE-538",
                        category="Information Disclosure"
                    ))

    # ---------------------------------------------------------------
    # Check 8: Cookie Security
    # ---------------------------------------------------------------
    def check_cookie_security(self):
        """Check cookie flags (HttpOnly, Secure, SameSite)."""
        self._log("Checking cookie security...")
        # Try login-related paths
        paths_to_check = ["", "/login", "/auth/login", "/api/v1/auth/login"]
        for path in paths_to_check:
            url = urljoin(self.target, path)
            resp = self._get(url)
            if resp and "Set-Cookie" in resp.headers:
                cookie_headers = resp.headers.get_list("Set-Cookie") if hasattr(resp.headers, "get_list") else [resp.headers.get("Set-Cookie")]
                for cookie in cookie_headers:
                    if not cookie:
                        continue
                    issues = []
                    if "HttpOnly" not in cookie:
                        issues.append("missing HttpOnly")
                    if "Secure" not in cookie:
                        issues.append("missing Secure")
                    if "SameSite" not in cookie:
                        issues.append("missing SameSite")
                    if issues:
                        self.findings.append(VulnFinding(
                            vuln_id=self._next_id(),
                            title="Insecure Cookie Configuration",
                            severity="Medium",
                            cvss=5.3,
                            description=f"Session cookie is missing security flags: {', '.join(issues)}.",
                            affected_url=url,
                            evidence=f"Set-Cookie: {cookie}",
                            remediation="Add HttpOnly, Secure, and SameSite=Strict flags to all session cookies.",
                            cwe="CWE-614",
                            category="Session Management"
                        ))
                break  # Only need to check once

    # ---------------------------------------------------------------
    # Main Scan
    # ---------------------------------------------------------------
    def scan(self) -> dict:
        """Run all checks and return results."""
        self.scan_start = datetime.utcnow()
        print(f"[*] Security Company Web Scanner v2.1")
        print(f"[*] Target: {self.target}")
        print(f"[*] Started: {self.scan_start.isoformat()}Z")
        print(f"[*] Running with {self.threads} threads...")
        print()

        checks = [
            ("Security Headers", self.check_security_headers),
            ("Information Disclosure", self.check_information_disclosure),
            ("Directory Listing", self.check_directory_listing),
            ("Clickjacking", self.check_clickjacking),
            ("SSL/TLS Configuration", self.check_ssl_tls),
            ("HTTP Methods", self.check_http_methods),
            ("Backup Files", self.check_backup_files),
            ("Cookie Security", self.check_cookie_security),
        ]

        for name, check_fn in checks:
            print(f"  [*] Running: {name}...")
            try:
                check_fn()
                print(f"      Done -- {len(self.findings)} findings so far")
            except Exception as e:
                print(f"      Error: {e}")

        self.scan_end = datetime.utcnow()

        report = {
            "scanner": "SecurityCompany-WebScanner",
            "version": "2.1",
            "department": "WebSec",
            "target": self.target,
            "scan_start": self.scan_start.isoformat() + "Z",
            "scan_end": self.scan_end.isoformat() + "Z",
            "duration_seconds": (self.scan_end - self.scan_start).total_seconds(),
            "total_vulnerabilities": len(self.findings),
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
        description="Security Company Web Vulnerability Scanner (WebSec Department)"
    )
    parser.add_argument("--target", "-t", required=True, help="Target URL (e.g., https://example.com)")
    parser.add_argument("--output", "-o", default="web_scan_report.json", help="Output JSON file")
    parser.add_argument("--threads", type=int, default=10, help="Thread count (default: 10)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    scanner = WebScanner(
        target=args.target,
        threads=args.threads,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    report = scanner.scan()

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] Scan complete. {report['total_vulnerabilities']} vulnerabilities found.")
    print(f"[+] Report saved to: {args.output}")
    print(f"[+] Duration: {report['duration_seconds']:.1f}s")
    print(f"\n    Summary:")
    for sev in ["Critical", "High", "Medium", "Low"]:
        count = report["summary"][sev]
        print(f"      {sev:10s}: {count}")


if __name__ == "__main__":
    main()
