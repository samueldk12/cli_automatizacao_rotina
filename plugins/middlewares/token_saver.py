"""
Token Saver - Economia de Tokens
Middleware que otimiza prompts e saidas para reduzir consumo de tokens.
Remove redundancias, compresssao de texto e foca no essencial.
"""

NAME = "Token Saver"
DESCRIPTION = "Otimiza prompts e saidas para reduzir consumo de tokens"
TYPE = "both"


def process_prompt(agent_profile: dict, original_prompt: str) -> str:
    """Otimiza o prompt removendo redundancias antes de enviar."""
    instruction = (
        "\n\n[TOKEN SAVER: Responda de forma concisa. "
        "Evite repeticoes. Vaya direto ao ponto. "
        "Use bullet points quando possivel. "
        "Nao repita a pergunta na resposta. "
        "Se a resposta pode ser dada em 1 frase, use 1 frase.]\n\n"
    )
    return instruction + original_prompt


def process_output(agent_profile: dict, original_output: str) -> str:
    """Otimiza a saida removendo enchimento."""
    return (
        original_output
        .replace("Em resumo,", "")
        .replace("Em conclusao,", "")
        .replace("Como podemos ver,", "")
        .replace("E importante notar que", "")
        .replace("Vale ressaltar que", "")
        .replace("Em outras palavras,", "")
        .replace("Dito isto,", "")
    )
