# OWASP Top 10 2021 — Checklist de Segurança

## A01: Broken Access Control
- [ ] Verificar se usuários podem acessar recursos de outros usuários (IDOR)
- [ ] Testar elevação de privilégio (horizontal e vertical)
- [ ] Verificar CORS configurado corretamente
- **Ferramentas**: Burp Suite, OWASP ZAP

## A02: Cryptographic Failures
- [ ] Dados sensíveis em trânsito usam TLS 1.2+
- [ ] Dados sensíveis em repouso são encriptados (AES-256 mínimo)
- [ ] Senhas com hash adequado (bcrypt, argon2, scrypt)
- [ ] Chaves criptográficas não hardcodeadas
- **Ferramentas**: `ssllabs-cli`, code review

## A03: Injection
- [ ] SQL: usar prepared statements / ORM com binding
- [ ] NoSQL: validar/sanetizar todas as inputs
- [ ] OS Command Injection: evitar system() ou usar safe APIs
- [ ] XSS: output encoding, CSP headers
- **Ferramentas**: sqlmap, Semgrep, code review

## A04: Insecure Design
- [ ] Threat modeling feito para cada feature nova
- [ ] Padrões seguros de design documentados
- [ ] Rate limiting implementado
- **Ferramentas**: OWASP Threat Dragon, STRIDE

## A05: Security Misconfiguration
- [ ] Headers de segurança configurados
- [ ] Contas/default removidas
- [ ] Error messages não expõem stack traces
- [ ] Diretórios não listáveis
- **Ferramentas**: Header Scanner, Nikto

## A06: Vulnerable and Outdated Components
- [ ] Dependências auditadas (npm audit, pip-audit, cargo audit)
- [ ] Versões mais recentes de frameworks
- [ ] Componentes não suportados removidos
- **Ferramentas**: Dependabot, Snyk, OWASP Dependency-Check

## A07: Identification and Authentication Failures
- [ ] Rate limiting em endpoints de login
- [ ] Senhas fracas rejeitadas
- [ ] MFA disponível
- [ ] Session management seguro (HttpOnly, Secure, SameSite)
- **Ferramentas**: Burp Suite, custom scripts

## A08: Software and Data Integrity Failures
- [ ] CI/CD pipeline assina artefatos
- [ ] Deserialização segura (evitar pickle, usar JSON/YAML)
- [ ] Verificação de assinatura de packages (Supply Chain)
- **Ferramentas**: Sigstore, in-toto

## A09: Security Logging and Monitoring Failures
- [ ] Logs de segurança gerados (falhas de auth, access denied)
- [ ] PII não logada
- [ ] Alertas configurados para anomalias
- **Ferramentas**: ELK Stack, Grafana, Prometheus

## A10: Server-Side Request Forgery (SSRF)
- [ ] URLs de input não podem acessar recursos internos
- [ ] Allowlist de destinos permitidos
- [ ] DNS rebinding protegido
- **Ferramentas**: SSRF test cases, Burp Collaborator

---
*Gerado pelo plugin security_company — myc agent-company security_company*
