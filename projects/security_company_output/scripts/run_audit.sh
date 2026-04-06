#!/usr/bin/env bash
# ============================================================
# Security Company -- Automated Security Audit Runner
# ============================================================
# Runs all security scanners and generates a combined report.
#
# Usage:
#   ./run_audit.sh --target https://shop.secureshop.com.br
#   ./run_audit.sh --target https://shop.secureshop.com.br --output audit_results/
#   ./run_audit.sh --target https://shop.secureshop.com.br --token "eyJhbG..."
#
# Requirements: python3, pip, requests
# ============================================================

set -euo pipefail

# -- Configuration --------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SCANNER_DIR="${PROJECT_DIR}/scanners"
REPORT_DIR="${PROJECT_DIR}/reports"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
OUTPUT_DIR="${REPORT_DIR}/audit_${TIMESTAMP}"
TARGET=""
TOKEN=""
VERBOSE=""

# -- Default target values for demo/testing -------------------------
DEFAULT_TARGET="https://shop.secureshop.com.br"

# -- Colors ---------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# -- Banner ---------------------------------------------------------
print_banner() {
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "  ╔══════════════════════════════════════════════════╗"
    echo "  ║     Security Company -- Automated Audit v2.1    ║"
    echo "  ║     WebSec  |  AppSec  |  InfraSec  | IR       ║"
    echo "  ╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

usage() {
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --target URL      Target URL (required)"
    echo "  -o, --output DIR      Output directory (default: reports/audit_<timestamp>)"
    echo "  --token TOKEN         JWT token for authenticated scans"
    echo "  -v, --verbose         Verbose output"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --target https://shop.secureshop.com.br"
    echo "  $0 --target https://api.example.com --token eyJhbG... --output results/"
    echo ""
    exit 0
}

# -- Parse Arguments ------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --token)
            TOKEN="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}[!] Unknown option: $1${NC}"
            usage
            ;;
    esac
done

if [ -z "$TARGET" ]; then
    echo -e "${YELLOW}[!] No target specified. Using default: ${DEFAULT_TARGET}${NC}"
    TARGET="${DEFAULT_TARGET}"
fi

# -- Header ---------------------------------------------------------
print_banner
echo -e "${BOLD}Target:${NC} ${TARGET}"
echo -e "${BOLD}Timestamp:${NC} ${TIMESTAMP}"
echo -e "${BOLD}Output:${NC} ${OUTPUT_DIR}"
echo ""

# -- Check Dependencies ---------------------------------------------
echo -e "${BLUE}[1/5] Checking dependencies...${NC}"

# Check python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] python3 is not installed or not in PATH${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "  [OK] ${PYTHON_VERSION}"

# Check requests library
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}  [!] requests library not found. Installing...${NC}"
    pip3 install requests 2>/dev/null || pip install requests 2>/dev/null
fi
echo -e "  [OK] requests library available"

mkdir -p "$OUTPUT_DIR"
echo -e "  [OK] Output directory: ${OUTPUT_DIR}"
echo ""

# -- Run Web Scanner ------------------------------------------------
echo -e "${BLUE}[2/5] Running WebSec Scanner (web_scanner.py)...${NC}"
echo "  Scanning: ${TARGET}"

WEBSC_REPORT="${OUTPUT_DIR}/web_scan.json"
python3 "${SCANNER_DIR}/web_scanner.py" \
    --target "$TARGET" \
    --output "$WEBSC_REPORT" \
    $VERBOSE \
    2>&1 || {
        echo -e "${YELLOW}  [WARN] Web scanner failed or target unreachable. Creating empty report.${NC}"
        cat > "$WEBSC_REPORT" << EOFJ
{
  "scanner": "SecurityCompany-WebScanner",
  "version": "2.1",
  "department": "WebSec",
  "target": "$TARGET",
  "scan_start": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "scan_end": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_vulnerabilities": 0,
  "summary": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
  "findings": []
}
EOFJ
    }
echo ""

# -- Run API Tester -------------------------------------------------
echo -e "${BLUE}[3/5] Running AppSec API Tester (api_tester.py)...${NC}"
echo "  Testing: ${TARGET}"

API_REPORT="${OUTPUT_DIR}/api_test.json"
API_TOKEN_ARG=""
if [ -n "$TOKEN" ]; then
    API_TOKEN_ARG="--token ${TOKEN}"
fi

python3 "${SCANNER_DIR}/api_tester.py" \
    --target "$TARGET" \
    --output "$API_REPORT" \
    $API_TOKEN_ARG \
    $VERBOSE \
    2>&1 || {
        echo -e "${YELLOW}  [WARN] API tester failed or target unreachable. Creating empty report.${NC}"
        cat > "$API_REPORT" << EOFJ
{
  "scanner": "SecurityCompany-APITester",
  "version": "2.1",
  "department": "AppSec",
  "target": "$TARGET",
  "scan_start": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "scan_end": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_vulnerabilities": 0,
  "summary": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
  "findings": []
}
EOFJ
    }
echo ""

# -- Generate Combined Report ---------------------------------------
echo -e "${BLUE}[4/5] Generating combined audit report...${NC}"

python3 - "$WEBSC_REPORT" "$API_REPORT" "$OUTPUT_DIR" "$TARGET" << 'PYEOF'
import json
import sys
from datetime import datetime

web_report_path = sys.argv[1]
api_report_path = sys.argv[2]
output_dir = sys.argv[3]
target = sys.argv[4]

# Load reports
with open(web_report_path) as f:
    web = json.load(f)
with open(api_report_path) as f:
    api = json.load(f)

# Merge findings
all_findings = []
all_findings.extend(web.get("findings", []))
all_findings.extend(api.get("findings", []))

summary = {
    "Critical": sum(1 for f in all_findings if f.get("severity") == "Critical"),
    "High": sum(1 for f in all_findings if f.get("severity") == "High"),
    "Medium": sum(1 for f in all_findings if f.get("severity") == "Medium"),
    "Low": sum(1 for f in all_findings if f.get("severity") == "Low"),
}

combined = {
    "scanner": "SecurityCompany-CombinedAudit",
    "version": "2.1",
    "target": target,
    "scan_date": datetime.utcnow().isoformat() + "Z",
    "sources": {
        "web_scanner": web_report_path.split('/')[-1],
        "api_tester": api_report_path.split('/')[-1],
    },
    "total_vulnerabilities": len(all_findings),
    "summary": summary,
    "findings": all_findings,
}

combined_path = f"{output_dir}/combined_audit.json"
with open(combined_path, "w") as f:
    json.dump(combined, f, indent=2)

print(f"  Combined report: {combined_path}")
print(f"  Total vulnerabilities: {len(all_findings)}")
for sev in ["Critical", "High", "Medium", "Low"]:
    print(f"    {sev}: {summary[sev]}")
PYEOF

echo ""

# -- Summary --------------------------------------------------------
echo -e "${BLUE}[5/5] Audit Summary${NC}"
echo "  ═════════════════════════════════════════════"

if [ -f "${OUTPUT_DIR}/web_scan.json" ]; then
    WEB_VULNS=$(python3 -c "import json; d=json.load(open('${OUTPUT_DIR}/web_scan.json')); print(d.get('total_vulnerabilities', 0))" 2>/dev/null || echo "0")
    echo -e "  WebSec Scanner:     ${WEB_VULNS} vulnerabilities found"
fi

if [ -f "${OUTPUT_DIR}/api_test.json" ]; then
    API_VULNS=$(python3 -c "import json; d=json.load(open('${OUTPUT_DIR}/api_test.json')); print(d.get('total_vulnerabilities', 0))" 2>/dev/null || echo "0")
    echo -e "  AppSec API Tester:  ${API_VULNS} vulnerabilities found"
fi

echo "  ═════════════════════════════════════════════"
echo ""
echo -e "${BOLD}Reports generated in: ${GREEN}${OUTPUT_DIR}${NC}"
echo ""
echo -e "  Files:"
echo -e "    - web_scan.json       (WebSec findings)"
echo -e "    - api_test.json       (AppSec findings)"
echo -e "    - combined_audit.json (Combined results)"
echo ""
echo -e "${CYAN}To view findings:${NC}"
echo -e "    cat ${OUTPUT_DIR}/combined_audit.json | python3 -m json.tool"
echo ""
echo -e "Done."
