"""
Middleware: Security Checker (BOTH)
Analise de seguranca:
  - PRE: adiciona checklist de seguranca ao prompt para o agente considerar.
  - POST: verifica a resposta por credenciais expostas, segredos, IPs, chaves, etc.
"""

import re

NAME = "Security Checker"
DESCRIPTION = "Analise de seguranca: adiciona checklist ao prompt e verifica resposta por dados sensiveis expostos."
MIDDLEWARE_TYPE = "content_filter"
RUNS_WHEN = "both"

# Padrões para detectar credenciais/segredos na saida
_SECRET_PATTERNS = {
    "chave AWS": re.compile(r"AKIA[0-9A-Z]{16}"),
    "token GitHub": re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}"),
    "senha/credential": re.compile(r"(?i)(password|senha|passwd)\s*[:=]\s*\S{4,}", re.IGNORECASE),
    "JWT token": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "IP address": re.compile(r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
    "CPF": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "chave API generica": re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*[A-Za-z0-9]{16,}", re.IGNORECASE),
}


def PROMPT_MODIFY(text: str, profile: dict | None = None) -> str:
    """Adiciona checklist de seguranca ao prompt antes do envio."""

    checklist = """
# Checklist de Seguranca

Ao formular sua resposta, lembre-se:
   - NUNCA inclua credenciais, senhas, chaves de API ou segredos reais no texto gerado.
   - Use placeholders como SUA_CHAVE_AQUI ou <api_key> ao inves de valores reais.
   - Nao exponha enderecos IP internos, CPFs ou dados pessoais.
   - Se o exemplo exigir configuracao, use valores ficticios.
   - Mencione recomendacoes de boas praticas de seguranca relevantes ao tema.
"""

    return f"{text}\n{checklist}".strip()


def OUTPUT_MODIFY(text: str, profile: dict | None = None) -> str:
    """Verifica a saida do agente por credenciais e dados sensiveis expostos."""

    findings = []

    for label, pattern in _SECRET_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            findings.extend(matches)

    if findings:
        # Ofusca os segredos encontrados
        result = text
        for secret in findings:
            if len(secret) > 8:
                masked = secret[:4] + "****" + secret[-4:]
            else:
                masked = "****"
            result = result.replace(secret, masked, 1)

        warning = (
            f"\n\n[AVISO DE SEGURANCA] O conteudo original continha {len(findings)} item(ns) "
            f"que parecem ser dados sensiveis/credenciais. Foram ofuscados na saida."
        )
        result += warning
        return result

    return text
