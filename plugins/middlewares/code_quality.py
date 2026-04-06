"""
Middleware: Code Quality (POST)
Revisa codigo presente na saida do agente, adicionando sugestoes de qualidade e verificando padroes.
"""

import re

NAME = "Code Quality"
DESCRIPTION = "Revisa codigo na saida, sugere melhorias de qualidade e verifica padroes comuns."
MIDDLEWARE_TYPE = "output_modifier"
RUNS_WHEN = "post"

# Padrões de más práticas comuns em código
_BAD_PATTERNS = {
    "hardcoded_secret": (
        re.compile(r"(?i)(password|secret|token|api_key)\s*=\s*['\"][^'\"<>]{4,}['\"]"),
        "Credencial hardcoded detectada. Use variaveis de ambiente ou vault.",
    ),
    "print_debug": (
        re.compile(r"\bprint\s*\("),
        "Instrucoes print() encontradas. Considere usar logging para producao.",
    ),
    "except_bare": (
        re.compile(r"except\s*:"),
        "except bare detectado. Especifique a excecao (ex: except Exception:).",
    ),
    "eval_usage": (
        re.compile(r"\beval\s*\("),
        "Uso de eval() detectado. Isso e um risco de seguranca. Use alternativas seguras.",
    ),
    "exec_usage": (
        re.compile(r"\bexec\s*\("),
        "Uso de exec() detectado. Isso e um risco de seguranca. Evite.",
    ),
    "todo_fixme": (
        re.compile(r"#\s*(TODO|FIXME|HACK|XXX|BUG)", re.IGNORECASE),
        "Comentarios TODO/FIXME encontrados no codigo.",
    ),
    "import_star": (
        re.compile(r"from\s+\S+\s+import\s+\*"),
        "import * detectado. Prefira imports explicitos para clareza.",
    ),
    "sql_injection_risk": (
        re.compile(r"(?i)(execute|query)\s*\(.*%s.*f['\"]|f['\"]\S*(?:SELECT|INSERT|UPDATE|DELETE)"),
        "Possivel risco de SQL injection. Use parametros em vez de interpolacao de strings.",
    ),
}

# Bloco de código detectável ```linguagem ... ```
_CODE_BLOCK = re.compile(r"```(\w+)?\n([\s\S]*?)```")


def OUTPUT_MODIFY(text: str, profile: dict | None = None) -> str:
    """Analisa blocos de codigo na saida e adiciona relatorio de qualidade."""

    code_blocks = list(_CODE_BLOCK.finditer(text))
    if not code_blocks:
        # Sem blocos de codigo: retorna texto original
        return text

    issues = []
    for match in code_blocks:
        lang = match.group(1) or "desconhecida"
        code = match.group(2)
        line_offset = text[:match.start()].count("\n") + 1

        for label, (pattern, suggestion) in _BAD_PATTERNS.items():
            matches = list(pattern.finditer(code))
            for m in matches:
                line_num = code[:m.start()].count("\n") + line_offset
                snippet = m.group(0).strip()[:60]
                issues.append(
                    f"   - [{label}] linha ~{line_num}: `{snippet}` -> {suggestion}"
                )

    if not issues:
        # Sem problemas encontrados: adiciona nota positiva
        footer = "\n\n[Code Quality] Nenhum problema comum detectado nos blocos de codigo analisados."
    else:
        unique_issues = list(dict.fromkeys(issues))  # remove duplicatas mantendo ordem
        footer = (
            f"\n\n--- Relatorio de Qualidade de Codigo ---\n"
            f"Foram encontrados {len(unique_issues)} aviso(s):\n"
            + "\n".join(unique_issues)
            + f"\n{'-' * 40}"
        )

    return text + footer
