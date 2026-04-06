"""
Middleware: Summarizer (POST)
Cria um resumo executivo estruturado da saida do agente, destacando pontos-chave em formato organizado.
"""

import re

NAME = "Summarizer"
DESCRIPTION = "Cria resumo executivo estruturado da saida, destacando pontos-chave de forma organizada."
MIDDLEWARE_TYPE = "output_modifier"
RUNS_WHEN = "post"

# Regex para capturar headers e listas do markdown
_HEADERS = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
_LIST_ITEMS = re.compile(r"^[\s]*[-*]\s+(.+)$", re.MULTILINE)
_CODE_BLOCKS = re.compile(r"```(\w+)?\n([\s\S]*?)```")
_ORDERED_LIST = re.compile(r"^[\s]*\d+\.\s+(.+)$", re.MULTILINE)


def _extract_structure(text: str) -> dict:
    """Extrai secoes, topico e itens de lista do texto."""

    sections = []
    for match in _HEADERS.finditer(text):
        level = len(match.group(1))
        title = match.group(2).strip()
        sections.append({"level": level, "title": title})

    list_items = [m.group(1).strip() for m in _LIST_ITEMS.finditer(text)]
    ordered_items = [m.group(1).strip() for m in _ORDERED_LIST.finditer(text)]

    code_langs = set()
    for m in _CODE_BLOCKS.finditer(text):
        lang = m.group(1) or "generico"
        code_langs.add(lang)

    return {
        "sections": sections,
        "list_items": list_items,
        "ordered_items": ordered_items,
        "code_langs": code_langs,
    }


def _get_preview_paragraph(text: str, max_words: int = 80) -> str:
    """Retorna o primeiro paragrafo significativo como previa."""
    # Remove blocos de codigo e markdown headers para obter texto corrido
    cleaned = _CODE_BLOCKS.sub("", text)
    cleaned = re.sub(r"#{1,3}\s+.+", "", cleaned)
    cleaned = re.sub(r"[`\*]", "", cleaned)

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    if not paragraphs:
        return ""

    preview = paragraphs[0]
    words = preview.split()
    if len(words) > max_words:
        preview = " ".join(words[:max_words]) + "..."
    return preview


def OUTPUT_MODIFY(text: str, profile: dict | None = None) -> str:
    """Gera resumo executivo estruturado e anexa ao final da saida."""

    structure = _extract_structure(text)
    preview = _get_preview_paragraph(text)

    # Se o texto for curto (< 300 chars), nao vale a pena resumir
    if len(text) < 300:
        return text

    summary_parts = ["\n\n--- Resumo Executivo ---"]

    # Topico: indica se existe titulo principal
    if structure["sections"]:
        main_title = structure["sections"][0]["title"]
        summary_parts.append(f"Topico: {main_title}")

    # Subsecoes
    if len(structure["sections"]) > 1:
        sub = [s["title"] for s in structure["sections"][1:] if s["level"] <= 2]
        summary_parts.append(f"Secoes: {', '.join(sub)}")

    # Previa
    if preview:
        summary_parts.append(f"Previa: {preview}")

    # Itens de lista encontrados
    all_items = structure["list_items"] + structure["ordered_items"]
    if all_items:
        top_items = all_items[:5]
        summary_parts.append("Pontos-chave:")
        for item in top_items:
            # Trunca itens longos
            if len(item) > 100:
                item = item[:97] + "..."
            summary_parts.append(f"  - {item}")

    # Linguagens de codigo
    if structure["code_langs"]:
        langs = ", ".join(sorted(structure["code_langs"]))
        summary_parts.append(f"Linguagens de codigo: {langs}")

    # Contagem rapida
    word_count = len(text.split())
    line_count = text.count("\n") + 1
    summary_parts.append(f"Extensao: ~{word_count} palavras, {line_count} linhas")

    summary_parts.append("---")

    return text + "\n".join(summary_parts)
