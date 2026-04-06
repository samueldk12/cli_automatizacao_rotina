"""
Agenda de Pratica Musical Personalizada.

Cria planos de pratica baseados em instrumento, nivel, tempo disponivel
e objetivos (tecnica, repertorio, teoria, percepcao auditiva),
aloca tempo otimamente e gera cronogramas diarios/semanais.
Contem classe ProgressionPlan dataclass.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums & Dataclasses
# ---------------------------------------------------------------------------

class NivelMusical(str, Enum):
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"
    PROFISSIONAL = "profissional"


class TipoPratica(str, Enum):
    TECNICA = "tecnica"
    REPERTORIO = "repertorio"
    TEORIA = "teoria"
    PERCEPCAO = "percepcao_auditiva"
    IMPROVISACAO = "improvisacao"
    LEITURA = "leitura_primeira_vista"


@dataclasses.dataclass
class ProgressionPlan:
    """Plano de progressao musical."""
    nome: str
    instrumento: str
    nivel: NivelMusical
    meses_estimados: int
    objetivos_especificos: list[str] = dataclasses.field(default_factory=list)
    marcos: list[tuple[int, str]] = dataclasses.field(default_factory=list)  # (mes, descricao)


@dataclasses.dataclass
class SessaoPratica:
    """Uma sessao individual de pratica."""
    tipo: TipoPratica
    duracao_minutos: int
    descricao: str
    exercicio: str = ""
    dificuldade: int = 3  # 1-5


@dataclasses.dataclass
class CronogramaDiario:
    """Cronograma de pratica para um dia da semana."""
    dia_semana: str
    total_minutos: int
    sessoes: list[SessaoPratica] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class PlanoPratica:
    """Plano de pratica semanal completo."""
    aluno: str
    instrumento: str
    nivel: NivelMusical
    tempo_semanal_disponivel_min: int
    cronograma: list[CronogramaDiario] = dataclasses.field(default_factory=list)
    planos_progressao: list[ProgressionPlan] = dataclasses.field(default_factory=list)
    recomendacoes: list[str] = dataclasses.field(default_factory=list)


# ---------------------------------------------------------------------------
# Distribuicao de tempo por nivel (fracoes)
# ---------------------------------------------------------------------------

DISTRIBUICAO_POR_NIVEL: dict[NivelMusical, dict[TipoPratica, float]] = {
    NivelMusical.INICIANTE: {
        TipoPratica.TECNICA: 0.25,
        TipoPratica.REPERTORIO: 0.35,
        TipoPratica.TEORIA: 0.10,
        TipoPratica.PERCEPCAO: 0.10,
        TipoPratica.IMPROVISACAO: 0.05,
        TipoPratica.LEITURA: 0.15,
    },
    NivelMusical.INTERMEDIARIO: {
        TipoPratica.TECNICA: 0.20,
        TipoPratica.REPERTORIO: 0.35,
        TipoPratica.TEORIA: 0.10,
        TipoPratica.PERCEPCAO: 0.10,
        TipoPratica.IMPROVISACAO: 0.15,
        TipoPratica.LEITURA: 0.10,
    },
    NivelMusical.AVANCADO: {
        TipoPratica.TECNICA: 0.15,
        TipoPratica.REPERTORIO: 0.40,
        TipoPratica.TEORIA: 0.05,
        TipoPratica.PERCEPCAO: 0.10,
        TipoPratica.IMPROVISACAO: 0.20,
        TipoPratica.LEITURA: 0.10,
    },
    NivelMusical.PROFISSIONAL: {
        TipoPratica.TECNICA: 0.10,
        TipoPratica.REPERTORIO: 0.50,
        TipoPratica.TEORIA: 0.05,
        TipoPratica.PERCEPCAO: 0.10,
        TipoPratica.IMPROVISACAO: 0.15,
        TipoPratica.LEITURA: 0.10,
    },
}

EXERCICIOS: dict[TipoPratica, list[str]] = {
    TipoPratica.TECNICA: [
        "Escalas maiores e menores",
        "Exercicios de digitacao (Hanon/Czerny)",
        "Arpejos em todas as posicoes",
        "Estudos de velocidade e precisao",
        "Pratica de ritmos complexos com metronomo",
    ],
    TipoPratica.REPERTORIO: [
        "Trabalhar passagem a passagem da musica atual",
        "Pratica lenta com metronomo",
        "Interpretacao e fraseado",
        "Memorizacao de trechos",
        "Montagem de programa de concerto",
    ],
    TipoPratica.TEORIA: [
        "Analise harmonica de partituras",
        "Estudo de formas musicais",
        "Intervalos e acordes",
        "Teoria da musica para instrumentistas",
    ],
    TipoPratica.PERCEPCAO: [
        "Ditado melodico",
        "Identificacao de acordes",
        "Reconhecimento de intervalos",
        "Reproducao de frases de ouvido",
    ],
    TipoPratica.IMPROVISACAO: [
        "Improvistacao sobre progressao harmonica",
        "Solo sobre backing track",
        "Variacao de motivos melodicos",
        "Call and response",
    ],
    TipoPratica.LEITURA: [
        "Leitura a primeira vista de partitura nova",
        "Sight-singing",
        "Leitura ritmica",
        "Transposicao a primeira vista",
    ],
}

DURACAO_MAX_SESSAO = 45  # min antes de pausa

# Dias em que cada tipo e praticado
FOCO_SEMANAL: dict[str, list[TipoPratica]] = {
    "Segunda": [TipoPratica.TECNICA, TipoPratica.LEITURA],
    "Terca": [TipoPratica.REPERTORIO],
    "Quarta": [TipoPratica.TECNICA, TipoPratica.PERCEPCAO],
    "Quinta": [TipoPratica.REPERTORIO, TipoPratica.IMPROVISACAO],
    "Sexta": [TipoPratica.REPERTORIO, TipoPratica.TEORIA],
    "Sabado": [],  # sabado revisao geral - todos os tipos
}


# ---------------------------------------------------------------------------
# Funcoes de alocacao
# ---------------------------------------------------------------------------

def contar_dias_tipo(dias_foco: dict[str, list[TipoPratica]], tipo: TipoPratica) -> int:
    """Conta quantos dias da semana incluem este tipo de pratica."""
    return sum(1 for focos in dias_foco.values() if tipo in focos)


def gerar_sessoes(tipo: TipoPratica, minutos: int) -> list[SessaoPratica]:
    """Gera uma ou mais sessoes para um tipo, respeitando duracao maxima."""
    exercicios = EXERCICIOS.get(tipo, ["Pratica livre"])
    sessoes: list[SessaoPratica] = []
    restante = minutos
    idx = 0
    while restante > 0:
        sessao_min = min(restante, DURACAO_MAX_SESSAO)
        ex = exercicios[idx % len(exercicios)]
        sessoes.append(SessaoPratica(
            tipo=tipo,
            duracao_minutos=sessao_min,
            descricao=tipo.value,
            exercicio=ex,
        ))
        restante -= sessao_min
        idx += 1
    return sessoes


def gerar_plano(aluno: str, instrumento: str, nivel: NivelMusical,
                horas_por_semana: float) -> PlanoPratica:
    """Gera um plano de pratica semanal otimizado."""
    minutos_semanal = int(horas_por_semana * 60)
    dist = DISTRIBUICAO_POR_NIVEL[nivel]
    alocacao = {t: int(minutos_semanal * f) for t, f in dist.items()}

    dias = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado"]
    cronograma: list[CronogramaDiario] = []

    for dia in dias:
        sessoes_dia: list[SessaoPratica] = []
        minutos_dia = minutos_semanal // len(dias)
        if dia == "Sabado":
            minutos_dia = int(minutos_semanal * 0.2)  # sabado recebe mais

        focos = FOCO_SEMANAL.get(dia, list(dist.keys()))
        if not focos:
            focos = list(dist.keys())  # sabado: todos

        for tipo in focos:
            minutos_tipo = alocacao.get(tipo, 0)
            n_dias = max(1, contar_dias_tipo(FOCO_SEMANAL, tipo))
            por_dia = max(5, minutos_tipo // n_dias)
            # Limitar ao que cabe no dia
            if por_dia > minutos_dia and sessoes_dia:
                por_dia = minutos_dia - sum(s.duracao_minutos for s in sessoes_dia)
            if por_dia >= 5:
                sessoes_dia.extend(gerar_sessoes(tipo, por_dia))

        total_dia = sum(s.duracao_minutos for s in sessoes_dia)
        cronograma.append(CronogramaDiario(
            dia_semana=dia,
            total_minutos=total_dia,
            sessoes=sessoes_dia,
        ))

    planos_progressao = _gerar_progressao(nivel, instrumento)

    recomendacoes = [
        "Use metronomo em todos os exercicios.",
        "Grave suas praticas periodicamente para auto-avaliacao.",
        "Faca pausas de 5 minutos entre sessoes.",
        "Revise material antigo a cada 2 semanas.",
    ]
    if nivel == NivelMusical.INICIANTE:
        recomendacoes.append("Nao pratique mais que 1h seguida. Qualidade > quantidade.")
    elif nivel == NivelMusical.PROFISSIONAL:
        recomendacoes.append("Foque em detalhes interpretativos e gravacoes.")

    return PlanoPratica(
        aluno=aluno,
        instrumento=instrumento,
        nivel=nivel,
        tempo_semanal_disponivel_min=minutos_semanal,
        cronograma=cronograma,
        planos_progressao=planos_progressao,
        recomendacoes=recomendacoes,
    )


def _gerar_progressao(nivel: NivelMusical, instrumento: str) -> list[ProgressionPlan]:
    """Gera planos de progressao conforme o nivel."""
    planos: list[ProgressionPlan] = []

    if nivel == NivelMusical.INICIANTE:
        planos.append(ProgressionPlan(
            nome=f"Do Iniciante ao Basico em {instrumento}",
            instrumento=instrumento,
            nivel=NivelMusical.INICIANTE,
            meses_estimados=6,
            objetivos_especificos=[
                "Dominar postura e tecnica basica",
                "Tocar escalas maiores (C, G, D)",
                "Ler partitura basica",
                "Executar 3 pecas completas",
            ],
            marcos=[
                (1, "Primeiros sons corretos e postura adequada"),
                (3, "Escala de Do maior fluida"),
                (6, "Primeira peca completa em publico"),
            ],
        ))
    elif nivel == NivelMusical.INTERMEDIARIO:
        planos.append(ProgressionPlan(
            nome=f"Do Intermediario ao Avancado em {instrumento}",
            instrumento=instrumento,
            nivel=NivelMusical.INTERMEDIARIO,
            meses_estimados=12,
            objetivos_especificos=[
                "Dominar escalas em tonalidades complexas",
                "Ampliar repertorio para 10+ pecas",
                "Improvistacao em 3 estilos",
                "Leitura fluente de partituras",
            ],
            marcos=[
                (3, "Escala menor harmonica e melodica dominada"),
                (6, "Primeira improvizacao completa"),
                (9, "Recital de 30 minutos"),
                (12, "Concerto com peca de nivel avancado"),
            ],
        ))
    else:
        planos.append(ProgressionPlan(
            nome=f"Consolidacao Avancada em {instrumento}",
            instrumento=instrumento,
            nivel=nivel,
            meses_estimados=18,
            objetivos_especificos=[
                "Preparar programa de concerto de 60min",
                "Dominar improvisacao avancada",
                "Gravacao profissional",
            ],
            marcos=[
                (6, "Programa de 30 minutos memorizado"),
                (12, "Gravacao demo"),
                (18, "Recital completo com peca contemporanea"),
            ],
        ))
    return planos


def formatar_plano(plano: PlanoPratica) -> str:
    """Formata o plano de pratica como texto legivel."""
    linhas: list[str] = ["=" * 60]
    linhas.append(f"  PLANO DE PRATICA MUSICAL - {plano.aluno}")
    linhas.append("=" * 60)
    linhas.append(f"  Instrumento: {plano.instrumento} | Nivel: {plano.nivel.value}")
    linhas.append(f"  Tempo semanal: {plano.tempo_semanal_disponivel_min}min")
    linhas.append("")

    for cron in plano.cronograma:
        linhas.append(f"  --- {cron.dia_semana} ({cron.total_minutos} min) ---")
        for s in cron.sessoes:
            linhas.append(f"    [{s.duracao_minutos}min] {s.tipo.value}: {s.exercicio}")
        if not cron.sessoes:
            linhas.append("    (Descanso ativo / revisao livre)")
        linhas.append("")

    if plano.planos_progressao:
        linhas.append("-" * 60)
        linhas.append("  PLANOS DE PROGRESSAO:")
        for pp in plano.planos_progressao:
            linhas.append(f"\n    {pp.nome} ({pp.meses_estimados} meses)")
            for obj in pp.objetivos_especificos:
                linhas.append(f"      - {obj}")
            linhas.append("    Marcos:")
            for mes, desc in pp.marcos:
                linhas.append(f"      Mes {mes}: {desc}")

    linhas.append("")
    linhas.append("  RECOMENDACOES:")
    for r in plano.recomendacoes:
        linhas.append(f"    * {r}")
    linhas.append("=" * 60)
    return "\n".join(linhas)


def main() -> None:
    """Demonstracao da agenda de pratica musical."""
    print("\n>>> AGENDA DE PRATICA MUSICAL\n")

    p1 = gerar_plano("Lucas", "Violao", NivelMusical.INICIANTE, 7.0)
    print(formatar_plano(p1))

    print("\n")

    p2 = gerar_plano("Beatriz", "Piano", NivelMusical.AVANCADO, 14.0)
    print(formatar_plano(p2))


if __name__ == "__main__":
    main()
