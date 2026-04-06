# Security Scanner Toolkit — security_company Output

Toolkit de scanning de segurança gerado pelo plugin **security_company** do MYC.

## Sub-agentes que geraram este projeto

| Sub-agente | Contribuição |
|-----------|-------------|
| web_security | Header scanner, OWASP Top 10 checklist |
| app_security | Port scanner com threading |

## Ferramentas

### Header Scanner
Escaneia headers de segurança HTTP e dá nota A+ a F.

```bash
python scanners/header_scanner.py --target https://example.com
python scanners/header_scanner.py --target https://example.com --json
```

### Port Scanner
Escaneia portas abertas com detecção de serviço.

```bash
python scanners/port_scanner.py --target example.com
python scanners/port_scanner.py --target example.com --common-high
```

### OWASP Top 10 Checklist

Checklist completa no `checklists/owasp_top10.md` com os 10 riscos críticos.

---

*Plugin: myc agent-company security_company — [repo](https://github.com/samueldk12/cli_automatizacao_rotina)*
