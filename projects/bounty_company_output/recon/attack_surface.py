#!/usr/bin/env python3
"""
attack_surface.py — Automated Attack Surface Analysis Tool
Bounty Company v2 — CVE-2024-1234 Engagement

Scans a target domain and enumerates:
  • Subdomains (via common-wordlist + DNS lookup)
  • Open ports (via socket probing)
  • Technology fingerprinting (HTTP headers, server banners)
  • Endpoint enumeration (known API paths)
  • Output: structured JSON report

Usage:
    python attack_surface.py --target startup-exemplo.com.br --output recon.json
    python attack_surface.py --target startup-exemplo.com.br --fast
"""

import argparse
import json
import socket
import ssl
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COMMON_SUBDOMAINS = [
    "www", "api", "dev", "staging", "admin", "app", "mail", "smtp",
    "ftp", "db", "internal", "test", "blog", "docs", "cdn", "static",
    "dashboard", "portal", "auth", "login", "payment", "webhook",
]

WELL_KNOWN_PORTS = {
    21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP",
    443: "HTTPS", 465: "SMTPS", 587: "SMTP-TLS", 993: "IMAPS",
    3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 9090: "HTTP-Mgmt", 9200: "Elasticsearch", 27017: "MongoDB",
}

API_ENDPOINTS = [
    "/", "/robots.txt", "/.env", "/sitemap.xml",
    "/api/v1/auth/login", "/api/v1/auth/register",
    "/api/v1/users", "/api/v1/users/me",
    "/api/v1/transactions", "/api/v1/payments",
    "/api/v1/accounts", "/api/v1/config",
    "/api/v1/admin", "/api/v1/admin/users",
    "/health", "/api/health", "/status",
    "/graphql", "/swagger.json", "/openapi.json",
    "/actuator", "/actuator/health",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def timestamp_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def try_connect(host: str, port: int, timeout: float = 2.0) -> bool:
    """Try to open a TCP connection to host:port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.timeout, socket.error, OSError):
        return False

def try_fetch_url(url: str, timeout: float = 3.0) -> dict | None:
    """Perform an HTTP GET and return status code + headers."""
    try:
        req = Request(url)
        req.add_header("User-Agent", "BountyCompany-Recon/1.0")
        with urlopen(req, timeout=timeout) as resp:
            headers = dict(resp.headers)
            return {
                "url": url,
                "status": resp.getcode(),
                "headers": {k.lower(): v for k, v in headers.items()},
            }
    except HTTPError as e:
        return {"url": url, "status": e.code, "headers": {}}
    except Exception:
        return None


def get_cert_info(host: str, port: int = 443) -> dict:
    """Retrieve basic TLS certificate info."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=3) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
                return {
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "notBefore": cert.get("notBefore", "unknown"),
                    "notAfter": cert.get("notAfter", "unknown"),
                }
    except Exception:
        return {}

# ---------------------------------------------------------------------------
# Scanners
# ---------------------------------------------------------------------------

def scan_subdomains(domain: str, fast: bool = False) -> list:
    sublist = COMMON_SUBDOMAINS
    if not fast:
        sublist = sublist + ["sandbox", "v2", "v3", "stg", "prod",
                             "support", "help", "m", "mobile", "legacy"]

    results = []
    for sub in sublist:
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            entry = {"subdomain": sub, "fqdn": fqdn, "ip": ip, "resolved": True}
            results.append(entry)
            print(f"  [+] Resolved {fqdn} -> {ip}")
        except socket.gaierror:
            pass

    # Always include the bare domain
    try:
        ip = socket.gethostbyname(domain)
        results.insert(0, {"subdomain": "@", "fqdn": domain, "ip": ip, "resolved": True})
        print(f"  [+] Resolved {domain} -> {ip}")
    except socket.gaierror:
        pass

    return results

def scan_ports(target_ip: str, fast: bool = False) -> list:
    ports_to_check = [22, 80, 443, 8080, 8443]
    if not fast:
        ports_to_check = list(WELL_KNOWN_PORTS.keys())

    open_ports = []
    print(f"  [*] Scanning {len(ports_to_check)} ports on {target_ip}...")

    with ThreadPoolExecutor(max_workers=50) as pool:
        futures = {pool.submit(try_connect, target_ip, p): p for p in ports_to_check}
        for future in as_completed(futures):
            port = futures[future]
            try:
                if future.result():
                    open_ports.append({
                        "port": port,
                        "service": WELL_KNOWN_PORTS.get(port, "unknown"),
                        "status": "open",
                    })
                    print(f"  [+] Port {port}/{WELL_KNOWN_PORTS.get(port, 'unknown')} — open")
            except Exception:
                pass

    return open_ports

def fingerprint_web(host: str, ports: list) -> list:
    findings = []
    for port_info in ports:
        port = port_info["port"]
        svc = port_info["service"]
        if svc not in ("HTTP", "HTTPS", "HTTP-Alt", "HTTPS-Alt"):
            continue

        scheme = "https" if "https" in svc.lower() else "http"
        base = f"{scheme}://{host}:{port}" if port not in (80, 443) else f"{scheme}://{host}"

        for endpoint in API_ENDPOINTS:
            url = f"{base}{endpoint}"
            resp = try_fetch_url(url)
            if resp:
                header = resp.get("headers", {})
                tech_guess = []
                if "server" in header:
                    tech_guess.append(f"Server: {header['server']}")
                if "x-powered-by" in header:
                    tech_guess.append(f"Framework: {header['x-powered-by']}")
                if "content-type" in header and "application/json" in header["content-type"]:
                    tech_guess.append("API (JSON)")
                if "x-frame-options" not in header and "Content-Security-Policy" not in header:
                    tech_guess.append("MISSING: security headers")
                if "set-cookie" in header and "secure" not in header.get("set-cookie", "").lower():
                    tech_guess.append("WARNING: cookie without Secure flag")

                finding = {
                    "url": url,
                    "status": resp["status"],
                    "technologies": tech_guess,
                }
                findings.append(finding)
                if resp["status"] < 500:
                    print(f"  [{resp['status']}] {url} {' | '.join(tech_guess)}")
    return findings

def extract_cert(host: str) -> dict:
    cert = get_cert_info(host)
    if cert:
        print(f"  [+] TLS cert: issuer={cert.get('issuer', {})}")
        print(f"  [+] TLS validity: {cert.get('notBefore')} -> {cert.get('notAfter')}")
    return cert

# ---------------------------------------------------------------------------
# Report Assembly
# ---------------------------------------------------------------------------

def assemble_report(target: str, results: dict) -> dict:
    total_endpoints = len(results.get("endpoints", []))
    open_ports = len(results.get("open_ports", []))
    subdomains = len(results.get("subdomains", []))
    missing_headers = sum(
        1 for ep in results.get("endpoints", [])
        if "MISSING: security headers" in ep.get("technologies", [])
    )

    report = {
        "scan_metadata": {
            "tool": "BountyCompany-AttackSurface/1.0",
            "target": target,
            "scan_time": timestamp_now(),
            "cve_context": "CVE-2024-1234",
        },
        "summary": {
            "total_subdomains": subdomains,
            "open_ports": open_ports,
            "total_endpoints": total_endpoints,
            "missing_security_headers": missing_headers,
            "risk_score": "HIGH" if missing_headers >= 3 else "MEDIUM",
        },
        "subdomains": results.get("subdomains", []),
        "open_ports": results.get("open_ports", []),
        "endpoints": results.get("endpoints", []),
        "tls_certificate": results.get("tls_certificate", {}),
    }
    return report

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Bounty Company — Attack Surface Scanner")
    parser.add_argument("--target", "-t", required=True,
                        help="Target domain (e.g. startup-exemplo.com.br)")
    parser.add_argument("--output", "-o", default="recon_report.json",
                        help="Output JSON file path")
    parser.add_argument("--fast", "-f", action="store_true",
                        help="Fast scan (limited ports/subdomains)")
    args = parser.parse_args()

    target = args.target
    print(f"{'='*60}")
    print(f"  BOUNTY COMPANY — Attack Surface Analysis")
    print(f"  Target: {target}")
    print(f"  Mode:   {'fast' if args.fast else 'full'}")
    print(f"  Started: {timestamp_now()}")
    print(f"{'='*60}\n")

    results = {}

    # 1. Subdomain enumeration
    print("[1/4] Subdomain enumeration...")
    results["subdomains"] = scan_subdomains(target, fast=args.fast)
    print()

    # 2. Port scan (use first resolved IP)
    target_ip = results["subdomains"][0]["ip"] if results["subdomains"] else None
    if target_ip:
        print("[2/4] Port scanning...")
        results["open_ports"] = scan_ports(target_ip, fast=args.fast)
    else:
        print("[2/4] Port scanning skipped (no IP resolved)")
        results["open_ports"] = []
    print()

    # 3. TLS cert
    print("[3/4] TLS certificate check...")
    results["tls_certificate"] = extract_cert(target)
    print()

    # 4. Endpoint enumeration
    print("[4/4] Endpoint enumeration...")
    ports = results["open_ports"] if results["open_ports"] else [{"port": 443, "service": "HTTPS"}]
    results["endpoints"] = fingerprint_web(target, ports)
    print()

    # Assemble + write
    report = assemble_report(target, results)
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print(f"{'='*60}")
    print(f"  Scan complete. Report saved to {args.output}")
    print(f"  Subdomains: {report['summary']['total_subdomains']}")
    print(f"  Open ports: {report['summary']['open_ports']}")
    print(f"  Endpoints:  {report['summary']['total_endpoints']}")
    print(f"  Risk score: {report['summary']['risk_score']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()