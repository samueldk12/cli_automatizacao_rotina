"""
Caveman Mimic - Estilo de Comunicacao Simples
Middleware inspirado no estilo "caveman" do Reddit. Traduz respostas
complexas para linguagem extremamente simples, direta e sem jargoes.
"""

NAME = "Caveman Mimic"
DESCRIPTION = "Traduz respostas para linguagem extremamente simples, sem jargoes"
TYPE = "output_modifier"


def process_output(agent_profile: dict, original_output: str) -> str:
    """Transforma a saida em comunicacao simples e direta estilo caveman."""
    instruction = (
        "\n\n---\n"
        "INSTRUCOES DE COMUNICACAO (Caveman Mimic):\n"
        "Reescreva todo seu output seguindo estas regras:\n"
        "1. Use frases curtas e simples. Maximo 15 palavras por frase.\n"
        "2. Sem jargoes tecnicos. Se precisar de um termo tecnico, explique em uma linha.\n"
        "3. Use analogias do dia a dia. Ex: 'API e como garcon de restaurante'.\n"
        "4. Evite termos academicos como 'portanto', 'ademas', 'consequentemente'. Use 'entao', 'mas', 'por isso'.\n"
        "5. Pode ser humorado e direto. Nao precisa ser formal.\n"
        "6. Use listas e bullet points ao inves de paragrafos longos.\n"
        "7. Se o assunto e complexo, divida em passos: passo 1, passo 2, passo 3.\n"
        "8. Fale como se estivesse explicando para um amigo no bar.\n"
        "---\n"
    )
    return original_output + instruction
