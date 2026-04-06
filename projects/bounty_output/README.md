# Bounty Company - Security Research and Recon Toolkit

A functional bug-bounty reconnaissance and web-vulnerability scanning toolkit created by four specialized bounty_company plugin agents.

## How the bounty_company Plugin Agents Created This

The bounty_company plugin orchestrates four specialized security agents, each contributing a distinct portion of the toolkit:

### 1. recon_specialist -> recon/report.py

Responsible for gathering all publicly available intelligence about a target:
- Subdomain enumeration via Certificate Transparency logs (crt.sh), SecurityTrails API, and DNS brute-force with common prefixes
- Multithreaded TCP port scanning across 28 common ports with banner grabbing and service identification
- Technology detection (Wappalyzer-style) by analyzing HTTP response headers and page body patterns for web servers, frameworks, CDNs, WAFs, and CMS platforms
- DNS record collection (A, AAAA, MX, TXT, NS, SOA, CAA) via Google DNS-over-HTTPS
- TLS certificate inspection including expiry, self-signed detection, protocol details, and SANs

### 2. pentest_engineer -> scanners/web_scanner.py (core security tests)

Built the active security testing modules:
- Security header analysis - checks for 7 critical security headers (CSP, X-Frame-Options, X-Content-Type-Options, HSTS, X-XSS-Protection, Referrer-Policy, Permissions-Policy) with severity-graded findings and weak-value detection
- Reflected XSS testing - probes URL query parameters, X-Forwarded-Host, and Referer headers for un-encoded reflection in HTML responses
- CRLF injection testing via encoded CR/LF sequences in URL paths
- HTTP method assessment - checks OPTIONS for dangerous methods, TRACE for XST, WebDAV for unauthorized uploads
- Open redirect detection - tests 10 common redirect parameters against a controlled external URL

### 3. exploit_developer -> scanners/web_scanner.py (exposed files and info disclosure)

Focused on information disclosure and common misconfigurations:
- Exposed sensitive files - probes 25 paths including .env, .git/config, wp-config.php, phpinfo.php, Swagger specs, database dumps with severity mapping
- Information disclosure - detects server version leakage, X-Powered-By headers, embedded email addresses, sensitive HTML comments
- SSL/TLS assessment - certificate expiry warnings, self-signed certificate detection
- Each finding includes severity classification, evidence, and specific remediation steps

### 4. report_writer -> templates/report.html + report generation

Designed the professional output layer:
- HTML report template - dark-theme responsive design with severity badges, stats cards, category breakdowns, and organized finding cards
- JSON export for machine-readable findings integration
- Summary statistics with severity counts and category distributions

## Installation

```bash
cd projects/bounty_output
pip install -r requirements.txt
```

Dependencies: requests (>=2.28.0), jinja2 (>=3.1.0)

## Usage

### Reconnaissance (subdomain enumeration, port scan, tech detection)

```bash
# Basic scan
python recon/report.py --target example.com

# Custom config
python recon/report.py --target example.com --config config.json

# Skip DNS brute-force (faster, quiet mode)
python recon/report.py --target example.com --no-bruteforce

# Custom output directory
python recon/report.py --target example.com --output ./my_results
```

Output: JSON report at `output/recon_<domain>_<timestamp>.json`

### Web Vulnerability Scanner

```bash
# Basic scan
python scanners/web_scanner.py --target https://example.com

# Without scheme (auto-detects HTTPS)
python scanners/web_scanner.py --target example.com

# With JSON export
python scanners/web_scanner.py --target https://example.com --json

# Custom output directory
python scanners/web_scanner.py --target https://example.com --output ./reports
```

Output: HTML report at `output/scan_<domain>_<timestamp>.html`

## Configuration

Edit config.json to customize:

| Section | Key | Description |
|---------|-----|-------------|
| target | timeout | HTTP request timeout in seconds (default: 10) |
| target | max_concurrent | Max concurrent threads for port scanning (default: 20) |
| recon | enable_crtsh | Enable Certificate Transparency subdomain enum |
| recon | enable_securitytrails | Enable SecurityTrails API (requires key) |
| recon | securitytrails_api_key | SecurityTrails API key |
| recon | common_ports | List of TCP ports to scan |
| scanner | user_agent | User-Agent string for HTTP requests |
| scanner | verify_ssl | SSL certificate verification (default: false) |
| paths_to_check | (array) | Paths to probe for exposed files/directories |

## Project Structure

```
projects/bounty_output/
  config.json
  requirements.txt
  README.md
  recon/
    __init__.py
    report.py             # Subdomain enum + port scan + tech detection
  scanners/
    __init__.py
    web_scanner.py        # Web vulnerability scanner (8 checks)
  templates/
    report.html           # Jinja2 HTML report template
  output/                 # Generated at runtime
    recon_*.json
    scan_*.html
```

## Legal Disclaimer

This toolkit is intended for authorized security research only.

You MUST have explicit, written permission from the target owner before scanning any system. Unauthorized scanning of systems you do not own or have permission to test may violate laws such as the Computer Fraud and Abuse Act (CFAA) in the United States and similar legislation worldwide.

The authors and contributors bear no responsibility for misuse of this toolkit. Always follow the rules of engagement defined in your bug bounty program or scope agreement. Results from this toolkit are preliminary and should be manually verified before reporting to any bug bounty program.

Use responsibly. Test only what you are authorized to test.

Generated by the bounty_company plugin agents: recon_specialist, pentest_engineer, exploit_developer, report_writer.
