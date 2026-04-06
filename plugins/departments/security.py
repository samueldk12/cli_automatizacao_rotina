"""Security Department Plugin - Web auditing, OWASP compliance, pentesting and hardening."""

NAME = "Security"
DESCRIPTION = "Conducts security audits, penetration testing, OWASP compliance checks and infrastructure hardening."
SPECIALISTS = ["web_auditor", "owasp_checker", "pentest_helper", "hardening_guide"]
MIDDLEWARES: list[str] = []
PARENT_COMPANY = None
ROLE = "You are a security department responsible for identifying vulnerabilities, performing penetration tests, enforcing OWASP standards and hardening systems against attacks. Produce actionable remediation plans and ensure compliance with security best practices across all projects."
