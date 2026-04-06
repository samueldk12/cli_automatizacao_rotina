"""
Middleware: Prompt Enhancer (PRE)
Reestrutura o prompt do usuario adicionando contexto, diretrizes e estrutura antes de enviar ao agente.
"""

NAME = "Prompt Enhancer"
DESCRIPTION = "Reestrutura o prompt para ser mais claro, organizado e eficaz antes do envio ao agente."
MIDDLEWARE_TYPE = "prompt_modifier"
RUNS_WHEN = "pre"

_SECTIONS = {
    "objetivo": "Responda a solicitacao do usuario de forma clara e estruturada.",
    "diretrizes": [
        "Seja direto e objetivo, evitando enrolacao.",
        "Se a pergunta for ambigua, declare suas suposicoes antes de responder.",
        "Forneça passos praticos e exemplos concretos quando aplicavel.",
        "Se houver codigo envolvido, inclua comentarios explicando as decisoes importantes.",
    ],
}


def PROMPT_MODIFY(text: str, profile: dict | None = None) -> str:
    """Reestrutura o prompt adicionando contexto, objetivo e diretrizes de resposta."""

    diretrizes_str = "\n".join(f"   - {d}" for d in _SECTIONS["diretrizes"])

    # Se houver perfil, injeta contexto adicional
    perfil_ctx = ""
    if profile:
        role = profile.get("role", "")
        tom = profile.get("tone", "")
        contexto = profile.get("context", "")
        if role:
            perfil_ctx += f"\n   Papel: {role}"
        if tom:
            perfil_ctx += f"\n   Tom desejado: {tom}"
        if contexto:
            perfil_ctx += f"\n   Contexto: {contexto}"

    enhanced = f"""# Contexto da Tarefa

Voce recebeu a seguinte solicitacao:

---
{text}
---

# Objetivo
{_SECTIONS["objetivo"]}
{perfil_ctx}

# Diretrizes de Resposta
{diretrizes_str}

Agora, responda a solicitacao acima seguindo as diretrizes.
"""
    return enhanced.strip()
