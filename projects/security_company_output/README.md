# Security Company Output -- Complete Security Audit Suite

## Problem Statement

**SecureShop E-Commerce Ltd.** (shop.secureshop.com.br), a Brazilian online retailer with ~50,000 monthly active users, hired **Security Company** to conduct a comprehensive security assessment after experiencing:

1. **Unexplained server slowdowns** -- page load times increased from 200ms to 3-5 seconds
2. **Checkout failures** -- intermittent 500 errors during payment processing
3. **Suspected data exposure** -- customer reports of receiving order confirmations for purchases they didn't make
4. **Performance degradation** -- abnormally high bandwidth usage (47.3 GB/day vs 2.1 GB baseline)

What started as a performance investigation quickly revealed a **series of critical security vulnerabilities** that were actively being exploited.

---

## What Security Company Did

Four specialized departments collaborated to conduct a full-scope security assessment:

### 1. WebSec Department
- Automated vulnerability scanning of all web-facing endpoints
- Security header analysis (CSP, HSTS, X-Frame-Options, etc.)
- Input validation testing for SQL injection, XSS, and open redirects
- SSL/TLS protocol assessment
- Directory and backup file exposure checks

### 2. AppSec Department
- JWT authentication bypass testing
- API endpoint security analysis
- IDOR (Insecure Direct Object Reference) assessment
- Session management review
- Rate limiting verification
- Cryptographic algorithm evaluation (found MD5 password hashing)
- CSRF protection testing

### 3. InfraSec Department
- Nginx server configuration review
- TLS/SSL protocol enforcement check
- Information disclosure via HTTP headers
- Directory listing verification
- Dangerous HTTP method detection

### 4. Incident Response Department
- 30-day access log analysis for signs of active exploitation
- Automated dependency vulnerability scanning
- Attack pattern correlation (brute force, SQLi probing)
- Data exfiltration investigation (unusual bandwidth patterns)
- Known threat actor IP correlation

---

## Project Structure

```
projects/security_company_output/
|
├── README.md                     # This file
├── report.html                   # Professional dark-theme HTML audit report (~800+ lines)
|
├── scanners/                     # Security scanning tools
│   ├── web_scanner.py            # Web vulnerability scanner (WebSec)
│   └── api_tester.py             # REST API security tester (AppSec)
│
├── reports/                      # Scan results and audit data
│   └── security_audit.json       # Combined audit report with 23 findings
│
├── remediation/                  # Fix guides and configurations
│   ├── fix_guide.md              # Step-by-step remediation with code examples
│   └── nginx_secure.conf         # Hardened Nginx configuration
│
└── scripts/
    └── run_audit.sh              # Automated audit runner script
```

---

## How to Test

### Prerequisites

```bash
python3 --version      # Python 3.8+
pip3 install requests  # HTTP library for scanners
```

### Setup

```bash
# Navigate to the project
cd projects/security_company_output

# Install dependencies
pip3 install requests
```

### Run Scanners Against a Target

```bash
# Make the runner script executable
chmod +x scripts/run_audit.sh

# Run the full audit (unauthenticated scan)
bash scripts/run_audit.sh --target https://your-target.com

# Run with authentication token
bash scripts/run_audit.sh --target https://api.your-target.com --token "eyJhbGci..."

# Verbose output
bash scripts/run_audit.sh --target https://your-target.com --verbose
```

### Run Individual Scanners

```bash
# Web scanner only
python3 scanners/web_scanner.py --target https://example.com --output my_report.json --verbose

# API tester only (without auth)
python3 scanners/api_tester.py --target https://api.example.com --output api_report.json

# API tester with auth token
python3 scanners/api_tester.py --target https://api.example.com --token "eyJhbGci..." --output api_report.json
```

### View Results

```bash
# View the combined JSON report
cat reports/security_audit.json | python3 -m json.tool

# Open the HTML report in a browser
# report.html (open directly in any browser)
```

---

## Architecture of the Solution

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Browser                           │
│              (shop.secureshop.com.br)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────┐     │
│  │  WebSec     │    │   AppSec    │    │  InfraSec    │     │
│  │  Scanner    │    │  API Tester │    │  Config Audit│     │
│  │             │    │             │    │  TLS/Headers │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                         │
│                   │  Report Merger  │                         │
│                   │  (Python + JSON)│                         │
│                   └────────┬────────┘                         │
│                            │                                 │
│                   ┌────────▼────────┐                         │
│                   │ Combined Report │                         │
│                   │  security_audit │                         │
│                   │      .json      │                         │
│                   └────────┬────────┘                         │
│                            │                                 │
│                   ┌────────▼────────┐                         │
│                   │   HTML Report   │                         │
│                   │   report.html   │                         │
│                   │  (Dark Theme)   │                         │
│                   └─────────────────┘                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │           Incident Response Department               │     │
│  │         (Log Analysis + Dependency Scan)             │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Scanner Architecture

**Web Scanner** (`web_scanner.py`):
- Sends HTTP requests to target endpoints
- Checks for 8 categories of web vulnerabilities
- Uses ThreadPoolExecutor for parallel scanning
- Outputs structured JSON report

**API Tester** (`api_tester.py`):
- Discovers API endpoints by probing common paths
- Tests auth bypass patterns, SQL injection, XSS, rate limiting, IDOR, open redirects
- All payloads are safe/read-only (no data modification)
- Outputs structured JSON report

**HTML Report** (`report.html`):
- Pure CSS -- no external dependencies
- Interactive finding cards (click to expand/collapse)
- CSS-only bar charts for vulnerability categories
- CSS-only horizontal bar charts for component risk scores
- Risk matrix, compliance progress bars, remediation roadmap

---

## Results Summary

| Metric | Value |
|--------|-------|
| **Total Vulnerabilities** | 23 |
| **Critical** | 4 (SQL Injection, JWT Forgery, Data Exposure, SSRF) |
| **High** | 6 (IDOR, XSS, Session, TLS, Rate Limiting, Redirect) |
| **Medium** | 8 (Headers, Clickjacking, Directory, CORS, Stored XSS, CSRF, MD5) |
| **Low** | 5 (Info Disclosure, TRACE, robots.txt, Logs, Dependencies) |
| **Overall Risk Score** | 7.2 / 10 (High) |
| **OWASP Compliance** | 45% (Failing) |
| **PCI-DSS Compliance** | 30% (Critical Fail) |
| **LGPD Compliance** | 60% (Needs Improvement) |

### Most Critical Finding

**SC-001: SQL Injection in Search Endpoint (CVSS 9.8)** -- An unauthenticated attacker was able to extract the entire customer database including email addresses and password hashes through a single HTTP request to the product search endpoint. Evidence suggests this vulnerability was **actively being exploited** based on log analysis (SC-022).

### Immediate Actions Required

1. Patch SQL Injection on all endpoints within 72 hours
2. Rotate JWT secret and invalidate all existing tokens
3. Disable verbose error responses in production
4. Block SSRF by implementing URL validation
5. Deploy hardened Nginx configuration (see `remediation/nginx_secure.conf`)

---

## License

This project is provided as a demonstration of security audit practices. All tools and findings are for educational and authorized testing purposes only. Always obtain proper authorization before testing any system.
