"""
Middleware: Text Compressor (POST)
Comprime e resume a saida do agente, removendo texto desnecessario mas mantendo informacoes-chave.
"""

import re

NAME = "Text Compressor"
DESCRIPTION = "Resume e comprime saidas longas removendo enrolacao, mantendo informacoes essenciais."
MIDDLEWARE_TYPE = "output_modifier"
RUNS_WHEN = "post"

# Palavras/frases de enchimento comuns para remover
_FILLER_PATTERNS = [
    r"(?i)it is important to note that\s*",
    r"(?i)it is worth mentioning that\s*",
    r"(?i)as we can see,?\s*",
    r"(?i)in conclusion,?\s*",
    r"(?i)overall,?\s*",
    r"(?i)essentially,?\s*",
    r"(?i)basically,?\s*",
    r"(?i)in order to\s*",
    r"(?i)due to the fact that\s*",
    r"(?i)it should be noted that\s*",
]

# Regex para detectar blocos de explicacao longa desnecessaria
_LONG_PREAMBLE = re.compile(
    r"(?i)^(great question|thanks for asking|sure,?\s*i can help|absolutely|of course|happy to help|certainly|let me explain).*?[.!?\n]+",
    re.DOTALL,
)


def OUTPUT_MODIFY(text: str, profile: dict | None = None) -> str:
    """Comprime a saida removendo preambulos, enchimento e redundancia."""

    result = text

    # Remove preambulos desnecessarios
    result = _LONG_PREAMBLE.sub("", result)

    # Remove frases de enchimento
    pattern = "|".join(_FILLER_PATTERNS)
    result = re.sub(pattern, "", result)

    # Colapsa multiplas linhas vazias
    result = re.sub(r"\n{3,}", "\n\n", result)

    # Remove espacos excessivos em linhas
    result = re.sub(r"  +", " ", result)

    # Se o texto ainda for muito longo (> 2000 chars), adiciona nota
    max_chars = 2000
    if len(result) > max_chars:
        # Mantem os primeiros max_chars chars
        result = result[:max_chars].rsplit("\n", 1)[0]
        result += "\n\n[... texto comprimido — saida original truncada para brevidade ...]"

    return result.strip()
