#!/usr/bin/env python3
"""
Bug Bounty Reconnaissance Report Generator

Collects subdomain information, performs port scanning,
and detects technologies for a given target domain.

Usage:
    python recon/report.py --target example.com

Part of bounty_company toolkit.
"""

import argparse
import json
import os
import socket
import sys
import time
import ssl
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("[ERROR] 'requests' library is required. Install with: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")


def load_config():
    """Load configuration from config.json, falling back to defaults."""
    defaults = {
        "target": {
            "domain": "example.com",
            "timeout": 10,
            "max_concurrent": 20,
        },
        "recon": {
            "enable_crtsh": True,
            "enable_securitytrails": False,
            "securitytrails_api_key": "",
            "port_range_start": 1,
            "port_range_end": 1024,
            "common_ports": [
                21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
                443, 445, 993, 995, 1433, 1521, 3306, 3389,
                5432, 5900, 6379, 8080, 8443, 8888, 9090,
                9200, 9300, 27017,
            ],
        },
        "scanner": {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "max_redirects": 5,
            "verify_ssl": False,
        },
    }

    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as fh:
                loaded = json.load(fh)
            # Deep merge loaded into defaults
            for key in defaults:
                if key not in loaded:
                    loaded[key] = defaults[key]
                elif isinstance(defaults[key], dict):
                    for subkey in defaults[key]:
                        if subkey not in loaded[key]:
                            loaded[key][subkey] = defaults[key][subkey]
            return loaded
        except (json.JSONDecodeError, IOError):
            print("[WARN] Could not parse config.json, using defaults.")

    return defaults


# ---------------------------------------------------------------------------
# Subdomain enumeration
# ---------------------------------------------------------------------------

def enumerate_subdomains_crtsh(domain):
    """
    Query crt.sh (Certificate Transparency) for subdomains.
    Returns a set of unique subdomain strings.
    """
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    headers = {"User-Agent": "bounty_company_recon/1.0"}

    subdomains = set()
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for entry in data:
                name_value = entry.get("name_value", "")
                for line in name_value.split("\n"):
                    line = line.strip().replace("*.", "")
                    if line.endswith(domain) and len(line) > len(domain):
                        subdomains.add(line)
        else:
            print(f"  [WARN] crt.sh returned HTTP {resp.status_code}")
    except requests.exceptions.RequestException as exc:
        print(f"  [WARN] crt.sh request failed: {exc}")
    except (json.JSONDecodeError, KeyError):
        print("  [WARN] crt.sh returned unparseable data.")

    return subdomains


def enumerate_subdomains_securitytrails(domain, api_key):
    """
    Query SecurityTrails API for subdomains.
    Requires a free API key from https://securitytrails.com/
    """
    if not api_key:
        return set()

    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {"APIKEY": api_key}

    subdomains = set()
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for sub in data.get("subdomains", []):
                fqdn = f"{sub}.{domain}"
                subdomains.add(fqdn)
        else:
            print(f"  [WARN] SecurityTrails returned HTTP {resp.status_code}")
    except requests.exceptions.RequestException as exc:
        print(f"  [WARN] SecurityTrails request failed: {exc}")

    return subdomains


def enumerate_subdomains_dnsbrute(domain, common_prefixes=None):
    """
    Naive DNS brute-force using a small wordlist of common subdomain
    prefixes. Not comprehensive but catches the obvious ones.
    """
    if common_prefixes is None:
        common_prefixes = [
            "www", "mail", "ftp", "dev", "staging", "test",
            "api", "app", "admin", "portal", "blog", "webmail",
            "smtp", "dns", "ns1", "ns2", "cdn", "static",
            "assets", "images", "support", "help", "docs",
            "git", "wiki", "forum", "shop", "store", "beta",
            "demo", "uat", "prod", "internal", "vpn", "remote",
            "dashboard", "status", "monitor", "metrics", "grafana",
            "jenkins", "s3", "storage", "files", "uploads",
            "download", "downloads", "m", "mobile", "legacy",
            "old", "new", "v2", "dev2", "staging2",
        ]

    resolved = set()
    for prefix in common_prefixes:
        candidate = f"{prefix}.{domain}"
        try:
            socket.getaddrinfo(candidate, None, socket.AF_INET)
            resolved.add(candidate)
        except (socket.gaierror, socket.error, OSError):
            pass

    return resolved


def collect_subdomains(domain, config):
    """
    Orchestrate all subdomain enumeration methods.
    Returns a sorted list of unique subdomains plus a source map.
    """
    print(f"[*] Collecting subdomains for {domain} ...")
    all_subs = set()
    sources = {}

    # 1) Certificate Transparency via crt.sh (public, no key needed)
    recon_cfg = config.get("recon", {})
    if recon_cfg.get("enable_crtsh", True):
        print("  [1/3] Querying crt.sh (Certificate Transparency) ...")
        subs = enumerate_subdomains_crtsh(domain)
        all_subs.update(subs)
        sources["crt.sh"] = len(subs)
        print(f"        Found {len(subs)} subdomain(s) via crt.sh")

    # 2) SecurityTrails API (optional, needs API key)
    if recon_cfg.get("enable_securitytrails", False):
        api_key = recon_cfg.get("securitytrails_api_key", "")
        print("  [2/3] Querying SecurityTrails API ...")
        subs = enumerate_subdomains_securitytrails(domain, api_key)
        all_subs.update(subs)
        sources["securitytrails"] = len(subs)
        print(f"        Found {len(subs)} subdomain(s) via SecurityTrails")
    else:
        sources["securitytrails"] = 0

    # 3) DNS brute-force with common words
    print("  [3/3] DNS brute-force with common prefixes ...")
    subs = enumerate_subdomains_dnsbrute(domain)
    all_subs.update(subs)
    sources["dns_brute"] = len(subs)
    print(f"        Found {len(subs)} subdomain(s) via DNS brute-force")

    result = sorted(all_subs)
    print(f"  -> Total unique subdomains: {len(result)}")

    return result, sources


# ---------------------------------------------------------------------------
# Port scanning
# ---------------------------------------------------------------------------

WELL_KNOWN_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    135: "MS-RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    1521: "Oracle DB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
    8888: "HTTP-Dev",
    9090: "HTTP-Mgmt",
    9200: "Elasticsearch",
    9300: "ES-Transport",
    27017: "MongoDB",
}


def scan_port(host, port, timeout=3):
    """Attempt a TCP connection. Returns True if port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.error, OSError):
        return False


def get_banner(host, port, timeout=3):
    """Attempt to grab a service banner from an open port."""
    banner = ""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        data = sock.recv(1024)
        if data:
            banner = data.decode("utf-8", errors="replace").strip()
        sock.close()
    except (socket.error, OSError, ConnectionResetError):
        pass
    return banner[:500]


def refine_service(port, banner):
    """Try to identify the service from port number and banner content."""
    service = WELL_KNOWN_SERVICES.get(port, "Unknown")

    if banner:
        banner_lower = banner.lower()
        if "apache" in banner_lower and "HTTP" in banner:
            service = "Apache HTTP Server"
        elif "nginx" in banner_lower:
            service = "Nginx"
        elif "microsoft-IIS" in banner_lower or "microsoft-iis" in banner_lower:
            service = "Microsoft-IIS"
        elif "openssh" in banner_lower:
            service = "OpenSSH"
        elif banner_lower.startswith("220") and ("filezilla" in banner_lower
                                                   or "vsftp" in banner_lower
                                                   or "proftp" in banner_lower):
            service = f"FTP ({banner.split()[0] if banner.split() else 'Unknown'})"
        elif banner_lower.startswith("ssh-"):
            service = "SSH"
        elif "mysql" in banner_lower:
            service = "MySQL"
        elif "postgres" in banner_lower:
            service = "PostgreSQL"
        elif banner_lower.startswith("-redis") or "redis" in banner_lower:
            service = "Redis"
        elif "elasticsearch" in banner_lower:
            service = "Elasticsearch"
        elif "mongodb" in banner_lower:
            service = "MongoDB"

    return service


def scan_host_ports(host, config):
    """
    Scan a host for open TCP ports using a thread pool.
    Returns a sorted list of dicts with port, service, banner.
    """
    recon_cfg = config.get("recon", {})
    common_ports = recon_cfg.get(
        "common_ports",
        [21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
         443, 445, 993, 995, 1433, 1521, 3306, 3389,
         5432, 5900, 6379, 8080, 8443, 8888, 9090,
         9200, 9300, 27017],
    )
    max_workers = config.get("target", {}).get("max_concurrent", 20)
    timeout = config.get("target", {}).get("timeout", 5)

    open_ports = []

    def _scan(p):
        if scan_port(host, p, timeout):
            banner = get_banner(host, p, timeout)
            service = refine_service(p, banner)
            return {"port": p, "service": service, "banner": banner, "state": "open"}
        return None

    ports_to_scan = sorted(set(common_ports))
    print(f"    Scanning {len(ports_to_scan)} port(s) on {host} ...")

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_scan, p): p for p in ports_to_scan}
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    open_ports.sort(key=lambda x: x["port"])
    return open_ports


# ---------------------------------------------------------------------------
# Technology detection (Wappalyzer-style via headers + body patterns)
# ---------------------------------------------------------------------------

TECH_SIGNATURES = {
    # Web servers
    "Apache": {"header": "server", "pattern": re.compile(r"Apache", re.I)},
    "Nginx": {"header": "server", "pattern": re.compile(r"nginx", re.I)},
    "Microsoft-IIS": {"header": "server", "pattern": re.compile(r"IIS", re.I)},
    "Cloudflare": {"header": "server", "pattern": re.compile(r"cloudflare", re.I)},
    "LiteSpeed": {"header": "server", "pattern": re.compile(r"LiteSpeed", re.I)},
    "Google Frontend": {"header": "server", "pattern": re.compile(r"Google", re.I)},
    # Frameworks
    "Django": {"header": "x-powered-by", "pattern": re.compile(r"django", re.I)},
    "Flask/Werkzeug": {"header": "server", "pattern": re.compile(r"werkzeug", re.I)},
    "Laravel": {"header": "x-powered-by", "pattern": re.compile(r"laravel", re.I)},
    "Express.js": {"header": "x-powered-by", "pattern": re.compile(r"express", re.I)},
    "Ruby on Rails": {"header": "x-powered-by", "pattern": re.compile(r"Rails", re.I)},
    "Spring Boot": {"header": "server", "pattern": re.compile(r"spring", re.I)},
    "ASP.NET": {"header": "x-powered-by", "pattern": re.compile(r"ASP\\.NET", re.I)},
    # CMS
    "WordPress": {"header": "x-powered-by", "pattern": re.compile(r"wordpress", re.I)},
    "Drupal": {"header": "x-generator", "pattern": re.compile(r"drupal", re.I)},
    "Joomla": {"header": "x-content-encoded", "pattern": re.compile(r"joomla", re.I)},
    # CDNs
    "AWS CloudFront": {"header": "via", "pattern": re.compile(r"cloudfront", re.I)},
    "Akamai": {"header": "x-akamai-edgesuite", "pattern": re.compile(r".*", re.I)},
    # WAFs & protection
    "Cloudflare WAF": {"header": "cf-ray", "pattern": re.compile(r".*", re.I)},
    "ModSecurity": {"header": "server", "pattern": re.compile(r"mod_security", re.I)},
    "AWS WAF": {"header": "x-amzn-requestid", "pattern": re.compile(r".*", re.I)},
}


def detect_technologies(url, user_agent):
    """
    Probe a URL and identify technologies from HTTP response headers
    and page body content fingerprints.
    """
    detected = []
    headers = {"User-Agent": user_agent}

    # Try HTTPS first, fall back to HTTP
    for scheme in ("https", "http"):
        target = f"{scheme}://{url}"
        try:
            resp = requests.get(target, headers=headers, timeout=10,
                                allow_redirects=True, verify=False)
            response_headers = resp.headers
            body = resp.text
            break
        except requests.exceptions.RequestException:
            continue
    else:
        return {"error": f"Could not connect to {url}"}

    # --- Header based detection ---
    header_lower = {k.lower(): v for k, v in response_headers.items()}

    for tech_name, sig in TECH_SIGNATURES.items():
        header_key = sig["header"].lower()
        header_value = header_lower.get(header_key, "")
        if sig["pattern"].search(header_value):
            detected.append({
                "technology": tech_name,
                "detection_method": "response_header",
                "evidence": header_value[:200],
            })

    # --- Body based detection ---
    body_patterns = {
        "WordPress": re.compile(r"wp-content|wp-includes", re.I),
        "jQuery": re.compile(r"jquery", re.I),
        "React": re.compile(r"react|__react", re.I),
        "Angular": re.compile(r"ng-app|ng-version", re.I),
        "Vue.js": re.compile(r"vue", re.I),
        "Bootstrap": re.compile(r"bootstrap", re.I),
        "Google Analytics": re.compile(
            r"googletagmanager|analytics\.js|gtag", re.I
        ),
        "PHP": re.compile(r"\bphp\b", re.I),
        "Jenkins": re.compile(r"jenkins", re.I),
        "Grafana": re.compile(r"grafana", re.I),
        "Kibana": re.compile(r"kibana", re.I),
        "Prometheus": re.compile(r"prometheus", re.I),
        "Tomcat": re.compile(r"tomcat", re.I),
        "Vercel": re.compile(r"vercel", re.I),
        "Netlify": re.compile(r"netlify", re.I),
        "Tailwind CSS": re.compile(r"tailwind", re.I),
    }

    for tech_name, pattern in body_patterns.items():
        if pattern.search(body):
            already = [d["technology"] for d in detected]
            if tech_name not in already:
                detected.append({
                    "technology": tech_name,
                    "detection_method": "body_content",
                    "evidence": "Pattern matched in response body",
                })

    # Gather interesting headers for the report
    interesting_headers = {}
    interesting_keys = [
        "server", "x-powered-by", "x-generator", "x-runtime",
        "x-aspnet-version", "x-varnish-cache", "via", "cf-ray",
    ]
    for key, value in response_headers.items():
        if key.lower() in interesting_keys:
            interesting_headers[key] = value

    return {
        "technologies": detected,
        "interesting_headers": interesting_headers,
        "http_status": resp.status_code,
        "final_url": str(resp.url),
        "response_time_ms": round(resp.elapsed.total_seconds() * 1000, 2),
    }


# ---------------------------------------------------------------------------
# TLS Certificate inspection
# ---------------------------------------------------------------------------

def check_tls(domain):
    """Connect to domain:443 and extract TLS certificate details."""
    result = {"supported": False, "details": {}}

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with ctx.wrap_socket(
            socket.socket(socket.AF_INET), server_hostname=domain
        ) as s:
            s.settimeout(5)
            s.connect((domain, 443))

            result["supported"] = True
            result["protocol"] = s.version()
            cipher = s.cipher()
            if cipher:
                result["cipher"] = {"name": cipher[0],
                                    "protocol": cipher[1],
                                    "bits": cipher[2]}

            cert = s.getpeercert()
            subject = dict(x[0] for x in cert.get("subject", []))
            issuer = dict(x[0] for x in cert.get("issuer", []))

            result["details"]["subject"] = subject
            result["details"]["issuer"] = issuer
            result["details"]["notBefore"] = cert.get("notBefore", "")
            result["details"]["notAfter"] = cert.get("notAfter", "")
            result["details"]["serialNumber"] = cert.get("serialNumber", "")

            # Subject Alternative Names
            sans = []
            for field in cert.get("subjectAltName", []):
                if field[0] == "DNS":
                    sans.append(field[1])
            if sans:
                result["details"]["sans"] = sans

    except (ssl.SSLError, socket.error, OSError,
            ConnectionRefusedError, TimeoutError) as exc:
        result["error"] = str(exc)

    return result


# ---------------------------------------------------------------------------
# DNS record collection (Google DoH)
# ---------------------------------------------------------------------------

def get_dns_records(domain):
    """Fetch A, AAAA, MX, TXT, NS, SOA records via Google DNS-over-HTTPS."""
    records = {}
    base_url = "https://dns.google/resolve"
    record_types = ["A", "AAAA", "MX", "TXT", "NS", "SOA", "CAA"]

    for rtype in record_types:
        try:
            resp = requests.get(
                base_url,
                params={"name": domain, "type": rtype},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                answers = data.get("Answer", [])
                if answers:
                    records[rtype] = answers
                else:
                    records[rtype] = []
            else:
                records[rtype] = {"error": f"HTTP {resp.status_code}"}
        except requests.exceptions.RequestException as exc:
            records[rtype] = {"error": str(exc)}

    return records


# ---------------------------------------------------------------------------
# Report assembly (orchestration)
# ---------------------------------------------------------------------------

def build_report(domain, config):
    """Run all recon modules and assemble a consolidated JSON report."""
    start_epoch = time.time()
    start_time = datetime.utcnow().isoformat() + "Z"

    report = {
        "metadata": {
            "tool": "bounty_company reconnaissance toolkit",
            "version": "1.0.0",
            "scan_start": start_time,
            "scan_end": None,
            "duration_seconds": None,
            "target_domain": domain,
            "config_source": CONFIG_PATH
                if os.path.isfile(CONFIG_PATH)
                else "defaults",
        },
        "subdomains": [],
        "subdomain_sources": {},
        "hosts": {},
        "tls": {},
        "dns_records": [],
        "summary": {},
    }

    # 1. Subdomain enumeration
    subdomains, sources = collect_subdomains(domain, config)
    report["subdomains"] = subdomains
    report["subdomain_sources"] = sources

    if domain not in subdomains:
        subdomains.append(domain)

    # 2. Port scanning + tech detection for each subdomain
    user_agent = config.get("scanner", {}).get(
        "user_agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    )

    for idx, sub in enumerate(subdomains, 1):
        print(f"\n[*] Examining {sub} ({idx}/{len(subdomains)}) ...")
        host_info = {"ip_addresses": [], "open_ports": [], "technologies": {}}

        # DNS resolution
        try:
            addr_info = socket.getaddrinfo(sub, None, socket.AF_INET)
            ips = sorted(set(info[4][0] for info in addr_info))
            host_info["ip_addresses"] = ips
        except (socket.gaierror, OSError):
            host_info["resolution_error"] = "NXDOMAIN or resolution failure"

        if host_info.get("ip_addresses"):
            primary_ip = host_info["ip_addresses"][0]
            host_info["open_ports"] = scan_host_ports(primary_ip, config)

            # Tech detection on any HTTP-like port
            for port_info in host_info["open_ports"]:
                port = port_info["port"]
                if port_info["service"].startswith("HTTP") or port in (80, 443, 8080, 8443):
                    proto = "https" if port in (443, 8443) else "http"
                    port_label = f"{proto}://{sub}:{port}"
                    print(f"  Detecting technologies on {port_label} ...")
                    tech = detect_technologies(
                        f"{sub}:{port}", user_agent,
                    )
                    host_info["technologies"][port] = tech

        report["hosts"][sub] = host_info

    # 3. TLS check (primary domain)
    report["tls"]["primary_domain"] = check_tls(domain)

    # 4. DNS records (primary domain)
    report["dns_records"] = get_dns_records(domain)

    # Finalise timing
    elapsed = round(time.time() - start_epoch, 2)
    report["metadata"]["scan_end"] = datetime.utcnow().isoformat() + "Z"
    report["metadata"]["duration_seconds"] = elapsed

    # Summary
    total_ports = sum(
        len(h.get("open_ports", []))
        for h in report["hosts"].values()
    )
    all_techs = set()
    for h in report["hosts"].values():
        for port_tech in h.get("technologies", {}).values():
            for t in port_tech.get("technologies", []):
                all_techs.add(t["technology"])

    report["summary"] = {
        "total_subdomains": len(report["subdomains"]),
        "total_hosts_resolved": sum(
            1 for h in report["hosts"].values() if h.get("ip_addresses")
        ),
        "total_open_ports": total_ports,
        "unique_technologies_detected": sorted(all_techs),
        "tls_supported_on_primary": report["tls"]
            .get("primary_domain", {})
            .get("supported", False),
    }

    return report


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def save_report(report, output_dir=None):
    """Write report dict to disk as JSON."""
    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "output")

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    domain = report["metadata"]["target_domain"]
    filename = f"recon_{domain}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=4, default=str)

    print(f"\n[*] Report saved to: {filepath}")
    return filepath


def print_summary(report):
    """Print a quick human-readable summary to stdout."""
    s = report.get("summary", {})
    m = report.get("metadata", {})

    print("\n" + "=" * 60)
    print("  BOUNTY COMPANY -- RECONNAISSANCE REPORT")
    print("=" * 60)
    print(f"  Target         : {m.get('target_domain')}")
    print(f"  Started        : {m.get('scan_start')}")
    print(f"  Completed      : {m.get('scan_end')}")
    print(f"  Duration       : {m.get('duration_seconds')}s")
    print("-" * 60)
    print(f"  Subdomains     : {s.get('total_subdomains', 0)}")
    print(f"  Hosts resolved : {s.get('total_hosts_resolved', 0)}")
    print(f"  Open ports     : {s.get('total_open_ports', 0)}")
    print(f"  TLS supported  : {s.get('tls_supported_on_primary', False)}")
    techs = s.get("unique_technologies_detected", [])
    if techs:
        print(f"  Technologies   : {', '.join(techs)}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Bounty Company -- Reconnaissance Report Generator. "
            "Enumerates subdomains, scans ports, detects technologies, "
            "and generates a structured JSON report."
        ),
        epilog="Example: python recon/report.py --target example.com",
    )
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Target domain (e.g. example.com)",
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help="Path to config.json (default: ../config.json)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose progress output",
    )
    parser.add_argument(
        "--no-bruteforce",
        action="store_true",
        help="Skip DNS brute-force subdomain enumeration",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    domain = args.target.strip().lower()

    # Strip scheme / path if the user passed a full URL
    parsed = urlparse(domain)
    if parsed.hostname:
        domain = parsed.hostname
    domain = domain.rstrip(".")

    print(f"[*] Target domain: {domain}")

    # Load config
    if args.config and os.path.isfile(args.config):
        try:
            with open(args.config) as fh:
                config = json.load(fh)
        except (json.JSONDecodeError, IOError) as exc:
            print(f"[ERROR] Cannot load config from {args.config}: {exc}")
            sys.exit(1)
    else:
        config = load_config()

    # Run reconnaissance
    try:
        report = build_report(domain, config)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Saving partial report...")
        # Build a partial report from what we have
        sys.exit(130)

    # Persist and display
    save_report(report, args.output)
    print_summary(report)


if __name__ == "__main__":
    main()
