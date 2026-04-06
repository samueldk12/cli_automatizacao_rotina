"""
Módulo: treino_calculator.py
Descrição: Ferramenta para criação de planos de treino personalizados com base
no perfil do atleta, cálculo de progressão de volume/carga e geração
de programação semanal de treinos.

Departamento: treinamento (personal trainer, preparador físico)
Empresa: Esporte & Saúde Centro
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import textwrap


# -----------------------------------------------------------
# Enums
# -----------------------------------------------------------

class NivelFitness(Enum):
    """Nível de condicionamento físico do atleta."""
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"


class ObjetivoTreino(Enum):
    """Objetivo principal do treino."""
    HIPERTROFIA = "hipertrofia"
    RESISTENCIA = "resistencia"
    EMAGRECIMENTO = "emagrecimento"
    FORCA = "forca"
    FUNCIONAL = "funcional"


class Intensidade(Enum):
    """Nível de intensidade da sessão."""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class TipoExercicio(Enum):
    """Categoria do exercício."""
    COMPOSTO = "composto"
    ISOLADO = "isolado"
    CARDIO = "cardio"
    FUNCIONAL = "funcional"
    MOBILIDADE = "mobilidade"


# -----------------------------------------------------------
# Dataclasses de entrada e saída
# -----------------------------------------------------------

@dataclass
class PerfilAtleta:
    """Perfil completo do atleta para geração de treino."""
    nome: str
    idade: int
    nivel: NivelFitness
    objetivo: ObjetivoTreino
    peso_kg: float
    altura_cm: int
    experiencias_previas: Optional[str] = None
    restricoes_medicas: Optional[list[str]] = field(default_factory=list)
    dias_disponiveis: int = 5
    tempo_por_sessao_min: int = 60


@dataclass
class Exercicio:
    """Representação de um exercício no plano."""
    nome: str
    tipo: TipoExercicio
    grupos_musculares: list[str]
    series: int
    repeticoes: int | str  # pode ser "max" ou intervalo textual
    descanso_seg: int
    intensidade: Intensidade
    observacoes: str = ""


@dataclass
class SessaoTreino:
    """Uma sessão de treino (dia específico)."""
    dia: str
    foco: str
    intensidade_geral: Intensidade
    duracao_min: int
    aquecimento: list[str]
    exercicios: list[Exercicio]
    volta_calma: list[str]


@dataclass
class PlanoTreinoSemanal:
    """Plano semanal completo gerado pelo sistema."""
    atleta: PerfilAtleta
    sessoes: list[SessaoTreino]
    semana_inicial_carga_pct: float = 70.0
    observacoes_geral: str = ""


@dataclass
class ProgressaoCarga:
    """Registro de progressão semanal de carga."""
    semana: int
    carga_pct_base: float
    volume_total_series: int
    volume_total_repeticoes: int
    descricao: str


# -----------------------------------------------------------
# Catálogo base de exercícios por grupo muscular
# -----------------------------------------------------------

CATALOGO_EXERCICIOS: dict[str, list[dict]] = {
    "peito": [
        {
            "nome": "Supino reto com barra",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["peito", "tríceps", "ombro anterior"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Supino inclinado com halteres",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["peito superior", "ombro anterior"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Crucifixo máquina (peck deck)",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["peito"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Flexão de braços",
            "tipo": TipoExercicio.FUNCIONAL,
            "grupos_musculares": ["peito", "tríceps", "core"],
            "intensidade": Intensidade.MEDIA,
        },
    ],
    "costas": [
        {
            "nome": "Puxada frontal (lat pulldown)",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["dorsal", "bíceps", "trapezio inferior"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Remada curvada com barra",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["dorsal", "romboides", "bíceps"],
            "intensidade": Intensidade.ALTA,
        },
        {
            "nome": "Remada unilateral com halter",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["dorsal", "bíceps"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Pullover com halter",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["dorsal", "serrátil"],
            "intensidade": Intensidade.BAIXA,
        },
    ],
    "pernas": [
        {
            "nome": "Agachamento livre",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["quadriceps", "gluteos", "posterior de coxa"],
            "intensidade": Intensidade.ALTA,
        },
        {
            "nome": "Leg press 45°",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["quadriceps", "gluteos"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Cadeira extensora",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["quadriceps"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Mesa flexora",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["posterior de coxa"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Stiff com barra",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["posterior de coxa", "gluteos", "lombar"],
            "intensidade": Intensidade.ALTA,
        },
        {
            "nome": "Panturrilha no smith",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["panturrilha"],
            "intensidade": Intensidade.BAIXA,
        },
    ],
    "ombros": [
        {
            "nome": "Desenvolvimento militar com halteres",
            "tipo": TipoExercicio.COMPOSTO,
            "grupos_musculares": ["deltoide anterior", "deltoide lateral", "tríceps"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Elevação lateral",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["deltoide lateral"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Face pull",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["deltoide posterior", "manguito rotador"],
            "intensidade": Intensidade.BAIXA,
        },
    ],
    "bracos": [
        {
            "nome": "Rosca direta com barra",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["bíceps"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Rosca alternada com halteres",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["bíceps"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Tríceps corda na polia",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["tríceps"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Tríceps testa com barra EZ",
            "tipo": TipoExercicio.ISOLADO,
            "grupos_musculares": ["tríceps"],
            "intensidade": Intensidade.BAIXA,
        },
    ],
    "core": [
        {
            "nome": "Prancha frontal isométrica",
            "tipo": TipoExercicio.FUNCIONAL,
            "grupos_musculares": ["core", "transverso do abdomem"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Abdominal infra",
            "tipo": TipoExercicio.FUNCIONAL,
            "grupos_musculares": ["abdome inferior"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Russian twist com peso",
            "tipo": TipoExercicio.FUNCIONAL,
            "grupos_musculares": ["oblíquos", "core"],
            "intensidade": Intensidade.MEDIA,
        },
    ],
    "cardio": [
        {
            "nome": "Esteira - corrida moderada",
            "tipo": TipoExercicio.CARDIO,
            "grupos_musculares": ["cardiovascular", "pernas"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "Bicicleta ergométrica",
            "tipo": TipoExercicio.CARDIO,
            "grupos_musculares": ["cardiovascular", "quadríceps"],
            "intensidade": Intensidade.MEDIA,
        },
        {
            "nome": "HIIT - sprints intervalados",
            "tipo": TipoExercicio.CARDIO,
            "grupos_musculares": ["cardiovascular", "pernas", "core"],
            "intensidade": Intensidade.ALTA,
        },
    ],
    "mobilidade": [
        {
            "nome": "Rotação de tronco com bastão",
            "tipo": TipoExercicio.MOBILIDADE,
            "grupos_musculares": ["coluna toracica", "ombros"],
            "intensidade": Intensidade.BAIXA,
        },
        {
            "nome": "Alongamento dinâmico de quadril",
            "tipo": TipoExercicio.MOBILIDADE,
            "grupos_musculares": ["quadril", "adutores"],
            "intensidade": Intensidade.BAIXA,
        },
    ],
}


# -----------------------------------------------------------
# Funções auxiliares de configuração por objetivo
# -----------------------------------------------------------

def _config_series_repeticoes(objetivo: ObjetivoTreino, nivel: NivelFitness) -> tuple[int, int | str]:
    """Retorna series e repetições baseadas no objetivo e nível."""
    configs = {
        ObjetivoTreino.HIPERTROFIA: {
            NivelFitness.INICIANTE: (3, 12),
            NivelFitness.INTERMEDIARIO: (4, 10),
            NivelFitness.AVANCADO: (4, "8-12"),
        },
        ObjetivoTreino.FORCA: {
            NivelFitness.INICIANTE: (3, 8),
            NivelFitness.INTERMEDIARIO: (4, 6),
            NivelFitness.AVANCADO: (5, "3-5"),
        },
        ObjetivoTreino.RESISTENCIA: {
            NivelFitness.INICIANTE: (2, 15),
            NivelFitness.INTERMEDIARIO: (3, 15),
            NivelFitness.AVANCADO: (3, "15-20"),
        },
        ObjetivoTreino.EMAGRECIMENTO: {
            NivelFitness.INICIANTE: (3, 12),
            NivelFitness.INTERMEDIARIO: (3, "12-15"),
            NivelFitness.AVANCADO: (4, "12-15"),
        },
        ObjetivoTreino.FUNCIONAL: {
            NivelFitness.INICIANTE: (3, 10),
            NivelFitness.INTERMEDIARIO: (3, 12),
            NivelFitness.AVANCADO: (4, "10-15"),
        },
    }
    return configs.get(objetivo, configs[ObjetivoTreino.HIPERTROFIA]).get(
        nivel, configs[ObjetivoTreino.HIPERTROFIA][NivelFitness.INICIANTE]
    )


def _config_descanso_seg(objetivo: ObjetivoTreino) -> int:
    """Tempo de descanso entre séries em segundos."""
    tabela = {
        ObjetivoTreino.HIPERTROFIA: 60,
        ObjetivoTreino.FORCA: 120,
        ObjetivoTreino.RESISTENCIA: 30,
        ObjetivoTreino.EMAGRECIMENTO: 45,
        ObjetivoTreino.FUNCIONAL: 60,
    }
    return tabela.get(objetivo, 60)


def _config_cardio_min(objetivo: ObjetivoTreino, nivel: NivelFitness) -> int:
    """Minutos de cardio recomendados por sessão."""
    tabela = {
        ObjetivoTreino.EMAGRECIMENTO: {NivelFitness.INICIANTE: 20, NivelFitness.INTERMEDIARIO: 30, NivelFitness.AVANCADO: 40},
        ObjetivoTreino.RESISTENCIA: {NivelFitness.INICIANTE: 15, NivelFitness.INTERMEDIARIO: 20, NivelFitness.AVANCADO: 30},
        ObjetivoTreino.HIPERTROFIA: {NivelFitness.INICIANTE: 10, NivelFitness.INTERMEDIARIO: 10, NivelFitness.AVANCADO: 15},
        ObjetivoTreino.FORCA: {NivelFitness.INICIANTE: 5, NivelFitness.INTERMEDIARIO: 10, NivelFitness.AVANCADO: 10},
        ObjetivoTreino.FUNCIONAL: {NivelFitness.INICIANTE: 10, NivelFitness.INTERMEDIARIO: 15, NivelFitness.AVANCADO: 20},
    }
    return tabela.get(objetivo, tabela[ObjetivoTreino.HIPERTROFIA]).get(nivel, 15)


# -----------------------------------------------------------
# Classe principal: Gerenciador de Treinos
# -----------------------------------------------------------

class GerenciadorTreinos:
    """
    Gerencia a criação de planos de treino personalizados.

    Utiliza o perfil do atleta para selecionar exercícios adequados,
    configurar volume, intensidade e gerar uma divisão semanal
    de treinos apropriada.
    """

    def __init__(self, perfil: PerfilAtleta):
        self.perfil = perfil
        self.series, self.repeticoes = _config_series_repeticoes(
            perfil.objetivo, perfil.nivel
        )
        self.descanso = _config_descanso_seg(perfil.objetivo)
        self.cardio_min = _config_cardio_min(perfil.objetivo, perfil.nivel)

    def _criar_exercicio(self, dado: dict, forcar_series: bool = True) -> Exercicio:
        """Converte dados do catálogo em objeto Exercicio."""
        return Exercicio(
            nome=dado["nome"],
            tipo=dado["tipo"],
            grupos_musculares=dado["grupos_musculares"],
            series=self.series if forcar_series else max(2, self.series - 1),
            repeticoes=self.repeticoes,
            descanso_seg=self.descanso,
            intensidade=dado["intensidade"],
        )

    def _montar_sessao(
        self,
        dia: str,
        foco: str,
        grupos_musculares: list[str],
        intensidade: Intensidade,
    ) -> SessaoTreino:
        """Monta uma sessão de treino com aquecimento, exercícios e volta à calma."""
        exercicios: list[Exercicio] = []
        for grupo in grupos_musculares:
            exercicios_grupo = CATALOGO_EXERCICIOS.get(grupo, [])
            # Seleciona exercícios adequados (até 3 por grupo)
            selecionados = exercicios_grupo[:3]
            for ex in selecionados:
                exercicios.append(self._criar_exercicio(ex))

        # Adiciona cardio conforme objetivo
        if self.cardio_min > 5:
            cardio_data = CATALOGO_EXERCICIOS["cardio"]
            exercicios.append(self._criar_exercicio(cardio_data[0], forcar_series=False))

        aquecimento = [
            "5 min de caminhada leve na esteira",
            "Rotação articular (ombros, quadril, tornozelos)",
            "2 séries leves do primeiro exercício composto",
        ]

        volta_calma = [
            "5 min de caminhada leve",
            "Alongamento estático dos grupos trabalhados (30s cada)",
        ]

        return SessaoTreino(
            dia=dia,
            foco=foco,
            intensidade_geral=intensidade,
            duracao_min=self.perfil.tempo_por_sessao_min,
            aquecimento=aquecimento,
            exercicios=exercicios,
            volta_calma=volta_calma,
        )

    def _divisao_semanal(self) -> list[dict]:
        """Retorna a divisão muscular baseada no número de dias disponíveis."""
        dias = self.perfil.dias_disponiveis
        if dias <= 2:
            return [
                {"dia": "Segunda", "foco": "Corpo inteiro A", "grupos": ["peito", "costas", "pernas"], "intensidade": Intensidade.MEDIA},
                {"dia": "Quinta", "foco": "Corpo inteiro B", "grupos": ["ombros", "bracos", "core"], "intensidade": Intensidade.MEDIA},
            ]
        if dias == 3:
            return [
                {"dia": "Segunda", "foco": "Empurrar (peito/ombro/tríceps)", "grupos": ["peito", "ombros"], "intensidade": Intensidade.ALTA},
                {"dia": "Quarta", "foco": "Puxar (costas/bíceps)", "grupos": ["costas", "bracos"], "intensidade": Intensidade.ALTA},
                {"dia": "Sexta", "foco": "Pernas e Core", "grupos": ["pernas", "core"], "intensidade": Intensidade.ALTA},
            ]
        if dias == 4:
            return [
                {"dia": "Segunda", "foco": "Peito e Tríceps", "grupos": ["peito"], "intensidade": Intensidade.ALTA},
                {"dia": "Terça", "foco": "Costas e Bíceps", "grupos": ["costas", "bracos"], "intensidade": Intensidade.ALTA},
                {"dia": "Quinta", "foco": "Pernas Completo", "grupos": ["pernas"], "intensidade": Intensidade.ALTA},
                {"dia": "Sexta", "foco": "Ombros e Core", "grupos": ["ombros", "core"], "intensidade": Intensidade.MEDIA},
            ]
        if dias >= 5:
            return [
                {"dia": "Segunda", "foco": "Peito", "grupos": ["peito"], "intensidade": Intensidade.ALTA},
                {"dia": "Terça", "foco": "Costas", "grupos": ["costas"], "intensidade": Intensidade.ALTA},
                {"dia": "Quarta", "foco": "Pernas", "grupos": ["pernas"], "intensidade": Intensidade.ALTA},
                {"dia": "Quinta", "foco": "Ombros e Core", "grupos": ["ombros", "core"], "intensidade": Intensidade.MEDIA},
                {"dia": "Sexta", "foco": "Braços e Cardio", "grupos": ["bracos", "cardio"], "intensidade": Intensidade.MEDIA},
            ]
        # Fallback
        return [
            {"dia": "Segunda", "foco": "Corpo inteiro", "grupos": ["peito", "costas", "pernas"], "intensidade": Intensidade.MEDIA},
        ]

    def gerar_plano(self) -> PlanoTreinoSemanal:
        """Gera o plano de treino semanal completo."""
        divisao = self._divisao_semanal()
        sessoes = []
        for item in divisao:
            sessao = self._montar_sessao(
                dia=item["dia"],
                foco=item["foco"],
                grupos_musculares=item["grupos"],
                intensidade=item["intensidade"],
            )
            sessoes.append(sessao)

        nivel_texto = self.perfil.nivel.value
        objetivo_texto = self.perfil.objetivo.value
        observacoes = (
            f"Plano para {objetivo_texto} | Nível: {nivel_texto} | "
            f"{self.perfil.dias_disponiveis} dias/semana | "
            f"Carga inicial: {self._carga_inicial_pct()}% do 1RM "
            f"(estimado para iniciantes/intermediarios)"
        )
        if self.perfil.restricoes_medicas:
            restricoes = ", ".join(self.perfil.restricoes_medicas)
            observacoes += f"\nATENÇÃO - Restrições médicas: {restricoes}"

        return PlanoTreinoSemanal(
            atleta=self.perfil,
            sessoes=sessoes,
            semana_inicial_carga_pct=self._carga_inicial_pct(),
            observacoes_geral=observacoes,
        )

    def _carga_inicial_pct(self) -> float:
        """Percentual de carga inicial baseado no nível."""
        return {
            NivelFitness.INICIANTE: 60.0,
            NivelFitness.INTERMEDIARIO: 70.0,
            NivelFitness.AVANCADO: 80.0,
        }.get(self.perfil.nivel, 70.0)

    def gerar_progressao(self, semanas: int = 8) -> list[ProgressaoCarga]:
        """
        Gera tabela de progressão de carga para N semanas.
        Usa periodização linear: +2.5% a 5% de carga por semana,
        com semana de deload a cada 4 semanas.
        """
        carga_base = self._carga_inicial_pct()
        progressoes: list[ProgressaoCarga] = []

        for semana in range(1, semanas + 1):
            # Semana de deload a cada 4 semanas
            if semana % 4 == 0:
                carga = carga_base * 0.6
                vol_series = sum(
                    max(2, ex.series - 1)
                    for sessao in self.gerar_plano().sessoes
                    for ex in sessao.exercicios
                )
                vol_reps = vol_series * max(
                    8 if isinstance(self.repeticoes, int) else 8,
                    1,
                )
                desc = f"Semana de DELLOAD - recuperação ativa"
            else:
                incremento = 0.03  # 3% de progressão semanal
                carga = carga_base * (1 + incremento * (semana - 1))
                carga = min(carga, 95.0)  # Teto de 95%
                vol_series = sum(
                    ex.series
                    for sessao in self.gerar_plano().sessoes
                    for ex in sessao.exercicios
                )
                vol_reps = vol_series * max(
                    10 if isinstance(self.repeticoes, int) else 10,
                    1,
                )
                desc = f"Progressão linear - {carga:.0f}% do 1RM estimado"

            progressoes.append(
                ProgressaoCarga(
                    semana=semana,
                    carga_pct_base=round(carga, 1),
                    volume_total_series=vol_series,
                    volume_total_repeticoes=vol_reps,
                    descricao=desc,
                )
            )

        return progressoes


# -----------------------------------------------------------
# Funções de exibição formatada
# -----------------------------------------------------------

def imprimir_plano(plano: PlanoTreinoSemanal) -> None:
    """Formata e imprime o plano de treino semanal."""
    atleta = plano.atleta
    print("=" * 70)
    print(f" PLANO DE TREINO - {atleta.nome.upper()}")
    print("=" * 70)
    print(textwrap.fill(
        f"Idade: {atleta.idade} anos | Peso: {atleta.peso_kg:.1f} kg | "
        f"Altura: {atleta.altura_cm} cm | Objetivo: {atleta.objetivo.value} | "
        f"Nível: {atleta.nivel.value}"
    ))
    print(f"Dias disponíveis: {atleta.dias_disponiveis} | "
          f"Tempo por sessão: {atleta.tempo_por_sessao_min} min")
    if plano.observacoes_geral:
        print(f"\nObservações: {plano.observacoes_geral}")
    print("-" * 70)

    for sessao in plano.sessoes:
        print(f"\n  >>> {sessao.dia}: {sessao.foco.upper()} "
              f"[Intensidade: {sessao.intensidade_geral.value} | "
              f"{sessao.duracao_min} min]")
        print(f"  Aquecimento:")
        for item in sessao.aquecimento:
            print(f"    - {item}")
        print(f"  Exercícios principais:")
        for i, ex in enumerate(sessao.exercicios, 1):
            reps = ex.repeticoes
            print(f"    {i}. {ex.nome}")
            print(f"       Séries: {ex.series} x {reps} "
                  f"({', '.join(ex.grupos_musculares)})")
            print(f"       Descanso: {ex.descanso_seg}s | "
                  f"Tipo: {ex.tipo.value}")
        print(f"  Volta à calma:")
        for item in sessao.volta_calma:
            print(f"    - {item}")
        print("-" * 70)


def imprimir_progressao(progressoes: list[ProgressaoCarga]) -> None:
    """Imprime tabela de progressão de cargas."""
    print("\n" + "=" * 70)
    print(" PROGRESSÃO DE CARGAS (PERIODIZAÇÃO LINEAR)")
    print("=" * 70)
    print(f"{'Semana':<8} | {'Carga % 1RM':<14} | {'Séries Total':<14} | "
          f"{'Reps Total':<12} | Descrição")
    print("-" * 70)
    for p in progressoes:
        print(f"{p.semana:<8} | {p.carga_pct_base:<14.1f} | "
              f"{p.volume_total_series:<14} | {p.volume_total_repeticoes:<12} | "
              f"{p.descricao}")
    print("=" * 70)


# -----------------------------------------------------------
# Demonstração
# -----------------------------------------------------------

def main() -> None:
    """Demonstração de uso do módulo treino_calculator."""
    print("\n" + "#" * 70)
    print("# DEMONSTRAÇÃO - TREINO CALCULATOR")
    print("# Esporte & Saúde Centro - Departamento de Treinamento")
    print("#" * 70)

    # Exemplo 1: Atleta intermediário buscando hipertrofia
    print("\n--- Exemplo 1: Hipertrofia (Intermediário) ---\n")
    atleta1 = PerfilAtleta(
        nome="Carlos Silva",
        idade=28,
        peso_kg=82.0,
        altura_cm=178,
        nivel=NivelFitness.INTERMEDIARIO,
        objetivo=ObjetivoTreino.HIPERTROFIA,
        dias_disponiveis=5,
        tempo_por_sessao_min=75,
    )

    gerenciador1 = GerenciadorTreinos(atleta1)
    plano1 = gerenciador1.gerar_plano()
    imprimir_plano(plano1)

    progressao1 = gerenciador1.gerar_progressao(semanas=8)
    imprimir_progressao(progressao1)

    # Exemplo 2: Iniciante buscando emagrecimento
    print("\n\n--- Exemplo 2: Emagrecimento (Iniciante) ---\n")
    atleta2 = PerfilAtleta(
        nome="Ana Beatriz",
        idade=35,
        peso_kg=75.0,
        altura_cm=165,
        nivel=NivelFitness.INICIANTE,
        objetivo=ObjetivoTreino.EMAGRECIMENTO,
        dias_disponiveis=3,
        tempo_por_sessao_min=60,
        restricoes_medicas=["Lesão meniscojo direito"],
    )

    gerenciador2 = GerenciadorTreinos(atleta2)
    plano2 = gerenciador2.gerar_plano()
    imprimir_plano(plano2)

    progressao2 = gerenciador2.gerar_progressao(semanas=6)
    imprimir_progressao(progressao2)

    print("\n" + "#" * 70)
    print("# FIM DA DEMONSTRAÇÃO")
    print("#" * 70)


if __name__ == "__main__":
    main()
