"""
Modulo: plano_alimentar.py
Descricao: Calculadora nutricional que cria planos alimentares para atletas
com base em objetivos (hipertrofia, emagrecimento, manutencao, definicao),
realiza calculos de macronutrientes (proteinas, carboidratos, gorduras)
e distribui as refeicoes ao longo do dia.

Departamento: nutricao (nutricionista esportivo)
Empresa: Esporte & Saude Centro
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import textwrap


# -----------------------------------------------------------
# Enums
# -----------------------------------------------------------

class ObjetivoNutricional(Enum):
    """Objetivo do plano alimentar."""
    HIPERTROFIA = "hipertrofia"
    EMAGRECIMENTO = "emagrecimento"
    MANUTENCAO = "manutencao"
    DEFINICAO = "definicao"


class NivelAtividade(Enum):
    """Nivel de atividade fisica para calculo calorico."""
    SEDENTARIO = "Sedentario"
    LEVE = "Leve (1-3 dias/semana)"
    MODERADO = "Moderado (3-5 dias/semana)"
    INTENSO = "Intenso (6-7 dias/semana)"
    ATLETA = "Atleta profissional (2x/dia)"


class RestricaoAlimentar(Enum):
    """Restricoes alimentares possiveis."""
    NENHUMA = "Nenhuma"
    SEM_LACTOSE = "Sem lactose"
    SEM_GLUTEN = "Sem gluten"
    VEGETARIANO = "Vegetariano"
    VEGANO = "Vegano"


# -----------------------------------------------------------
# Dataclasses
# -----------------------------------------------------------

@dataclass
class DadosAtleta:
    """Dados do atleta para calculo nutricional."""
    nome: str
    idade: int
    peso_kg: float
    altura_cm: float
    sexo: str  # "M" ou "F"
    objetivo: ObjetivoNutricional
    nivel_atividade: NivelAtividade
    restricoes: list[RestricaoAlimentar] = field(default_factory=list)
    refeicoes_por_dia: int = 5


@dataclass
class Macronutrientes:
    """Distribuicao de macronutrientes para um dia."""
    calorias_totais_kcal: float
    proteinas_g: float
    carboidratos_g: float
    gorduras_g: float
    proteinas_kcal: float
    carboidratos_kcal: float
    gorduras_kcal: float
    proporcao_pct: str  # ex: "30/50/20"


@dataclass
class Refeicao:
    """Representa uma refeicao individual."""
    nome: str            # ex: "Cafe da manha"
    horario: str         # ex: "07:00"
    calorias_kcal: float
    proteinas_g: float
    carboidratos_g: float
    gorduras_g: float
    alimentos: list[str]


@dataclass
class PlanoAlimentar:
    """Plano alimentar diario completo."""
    atleta: DadosAtleta
    macronutrientes: Macronutrientes
    refeicoes: list[Refeicao]
    recomendacoes: list[str] = field(default_factory=list)
    observacoes: str = ""


# -----------------------------------------------------------
# Constantes
# -----------------------------------------------------------

KCAL_POR_G_PROTEINA = 4
KCAL_POR_G_CARB = 4
KCAL_POR_G_GORDURA = 9

# Proporcoes de macros por objetivo (% proteina / % carboidrato / % gordura)
PROP_MACRO: dict[ObjetivoNutricional, tuple[float, float, float]] = {
    ObjetivoNutricional.HIPERTROFIA: (0.30, 0.50, 0.20),
    ObjetivoNutricional.EMAGRECIMENTO: (0.40, 0.30, 0.30),
    ObjetivoNutricional.MANUTENCAO: (0.25, 0.50, 0.25),
    ObjetivoNutricional.DEFINICAO: (0.35, 0.35, 0.30),
}

# Faixas de g de proteina por kg de peso
PROTEINA_POR_KG: dict[ObjetivoNutricional, tuple[float, float]] = {
    ObjetivoNutricional.HIPERTROFIA: (1.8, 2.2),
    ObjetivoNutricional.EMAGRECIMENTO: (2.0, 2.4),
    ObjetivoNutricional.MANUTENCAO: (1.2, 1.6),
    ObjetivoNutricional.DEFINICAO: (2.0, 2.2),
}

# Distribuicao percentual de calorias por refeicao
DISTRIBUICAO_REFEICOES: dict[int, list[tuple[str, str, float]]] = {
    4: [
        ("Cafe da manha", "07:30", 0.25),
        ("Almoco", "12:30", 0.35),
        ("Lanche da tarde", "16:00", 0.15),
        ("Jantar", "19:30", 0.25),
    ],
    5: [
        ("Cafe da manha", "07:00", 0.20),
        ("Lanche da manha", "10:00", 0.10),
        ("Almoco", "12:30", 0.30),
        ("Lanche da tarde", "15:30", 0.15),
        ("Jantar", "19:00", 0.25),
    ],
    6: [
        ("Cafe da manha", "07:00", 0.20),
        ("Lanche da manha", "10:00", 0.10),
        ("Almoco", "12:30", 0.25),
        ("Lanche da tarde", "15:30", 0.10),
        ("Pre-treino", "17:30", 0.10),
        ("Jantar", "19:30", 0.25),
    ],
}

# Sugestoes de alimentos padrao
SUGESTOES_PADRAO: dict[str, list[str]] = {
    "Cafe da manha": [
        "3 ovos mexidos",
        "2 fatias de pao integral com queijo branco",
        "1 banana com aveia e mel",
        "1 xicara de cafe com leite desnatado",
    ],
    "Lanche da manha": [
        "1 maca + 10 castanhas de caju",
        "1 pote de iogurte natural com granola",
    ],
    "Almoco": [
        "150g de peito de frango grelhado",
        "150g de arroz integral",
        "100g de feijao preto",
        "Salada verde (alface, tomate, pepino) a vontade",
        "1 colher de azeite de oliva extra-virgem",
        "1 fatia de abacaxi",
    ],
    "Lanche da tarde": [
        "Shake whey protein (30g) com 200ml de leite e 1 banana",
        "2 fatias de pao integral com pasta de amendoim",
    ],
    "Jantar": [
        "150g de tilapia ou salmao grelhado",
        "200g de batata doce cozida",
        "Legumes salteados (brocolis, cenoura, abobrinha)",
        "1 colher de azeite de oliva",
    ],
    "Pre-treino": [
        "1 banana com pasta de amendoim",
        "40g de aveia com 200ml de leite",
    ],
}

SUGESTOES_VEGETARIANO: dict[str, list[str]] = {
    "Cafe da manha": [
        "Mingau de aveia com frutas vermelhas e sementes de chia",
        "2 fatias de pao integral com tofu temperado",
        "1 xicara de cafe com leite de aveia",
    ],
    "Lanche da manha": [
        "Mix de frutas secas e nuts (40g)",
        "1 banana",
    ],
    "Almoco": [
        "200g de lentilha ou grao-de-bico",
        "150g de arroz integral",
        "Salada de quinoa com legumes",
        "1 colher de azeite de oliva",
    ],
    "Lanche da tarde": [
        "Shake de proteina vegetal com fruta",
        "Torrada integral com homus",
    ],
    "Jantar": [
        "Strogonoff de cogumelos",
        "200g de batata doce",
        "Legumes assados (abobrinha, berinjela, pimentao)",
    ],
    "Pre-treino": [
        "Banana com aveia e canela",
        "Dates com pasta de amendoim",
    ],
}

SUGESTOES_VEGANO: dict[str, list[str]] = {
    "Cafe da manha": [
        "Panqueca de banana com aveia (vegana)",
        "Mingau de aveia com leite de amendoas e frutas",
        "Cafe preto ou com leite de soja",
    ],
    "Lanche da manha": [
        "1 maca + 15g de almonds",
        "Palitos de cenoura com homus",
    ],
    "Almoco": [
        "200g de feijao ou lentilha",
        "150g de arroz integral",
        "Tempeh grelhado com legumes",
        "Salada completa com azeite e limao",
    ],
    "Lanche da tarde": [
        "Shake de proteina vegetal com leite de amendoas",
        "Torrada de arroz com pasta de amendoim",
    ],
    "Jantar": [
        "Bowl de quinoa com grao-de-bico, abacate e legumes",
        "Sopa de legumes com tofu",
    ],
    "Pre-treino": [
        "Banana com pasta de amendoim",
        "Rice cakes com homus e tomate",
    ],
}


# -----------------------------------------------------------
# Funcoes de calculo
# -----------------------------------------------------------

def _calcular_tmb(peso_kg: float, altura_cm: float, idade: int, sexo: str) -> float:
    """
    Calcula Taxa Metabolica Basal pela formula de Mifflin-St Jeor.

    Homens: (10 x peso) + (6.25 x altura) - (5 x idade) + 5
    Mulheres: (10 x peso) + (6.25 x altura) - (5 x idade) - 161
    """
    if sexo.upper() == "M":
        return (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade) + 5
    else:
        return (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade) - 161


def _fator_atividade(nivel: NivelAtividade) -> float:
    """Retorna o fator multiplicador de atividade."""
    return {
        NivelAtividade.SEDENTARIO: 1.2,
        NivelAtividade.LEVE: 1.375,
        NivelAtividade.MODERADO: 1.55,
        NivelAtividade.INTENSO: 1.725,
        NivelAtividade.ATLETA: 1.9,
    }.get(nivel, 1.55)


def _ajuste_objetivo(objetivo: ObjetivoNutricional, get: float) -> float:
    """
    Ajusta calorias totais conforme objetivo.

    Hipertrofia: superavit de ~400 kcal
    Emagrecimento: defict de ~500 kcal
    Manutencao: sem ajuste
    Definicao: defict de ~300 kcal
    """
    ajustes = {
        ObjetivoNutricional.HIPERTROFIA: 400,
        ObjetivoNutricional.EMAGRECIMENTO: -500,
        ObjetivoNutricional.MANUTENCAO: 0,
        ObjetivoNutricional.DEFINICAO: -300,
    }
    resultado = get + ajustes.get(objetivo, 0)
    return max(resultado, 1200)  # Minimo de 1200 kcal


def calcular_macronutrientes(
    peso_kg: float,
    altura_cm: float,
    idade: int,
    sexo: str,
    objetivo: ObjetivoNutricional,
    nivel_atividade: NivelAtividade,
) -> Macronutrientes:
    """
    Calcula a distribuicao completa de macronutrientes para um dia.

    1. Calcula TMB (Mifflin-St Jeor)
    2. Multiplica pelo fator de atividade (GET)
    3. Ajusta conforme objetivo (superavit/defict)
    4. Define proporcao de macros conforme objetivo
    5. Converte em gramas
    """
    tmb = _calcular_tmb(peso_kg, altura_cm, idade, sexo)
    get = tmb * _fator_atividade(nivel_atividade)
    calorias_totais = _ajuste_objetivo(objetivo, get)

    pct_prot, pct_carb, pct_gord = PROP_MACRO[objetivo]

    prot_kcal = calorias_totais * pct_prot
    carb_kcal = calorias_totais * pct_carb
    gord_kcal = calorias_totais * pct_gord

    prot_g = prot_kcal / KCAL_POR_G_PROTEINA
    carb_g = carb_kcal / KCAL_POR_G_CARB
    gord_g = gord_kcal / KCAL_POR_G_GORDURA

    # Verifica se proteina por kg esta na faixa recomendada
    range_prot = PROTEINA_POR_KG[objetivo]
    prot_min_g = range_prot[0] * peso_kg

    if prot_g < prot_min_g:
        prot_g = prot_min_g
        prot_kcal = prot_g * KCAL_POR_G_PROTEINA
        restante = calorias_totais - prot_kcal - gord_kcal
        carb_kcal = max(restante, 0)
        carb_g = carb_kcal / KCAL_POR_G_CARB

    return Macronutrientes(
        calorias_totais_kcal=round(calorias_totais, 0),
        proteinas_g=round(prot_g, 1),
        carboidratos_g=round(carb_g, 1),
        gorduras_g=round(gord_g, 1),
        proteinas_kcal=round(prot_kcal, 0),
        carboidratos_kcal=round(carb_kcal, 0),
        gorduras_kcal=round(gord_kcal, 0),
        proporcao_pct=f"{int(pct_prot * 100)}/{int(pct_carb * 100)}/{int(pct_gord * 100)}",
    )


# -----------------------------------------------------------
# Classe principal
# -----------------------------------------------------------

class GerenciadorPlanoAlimentar:
    """
    Cria planos alimentares completos baseados no perfil do atleta.

    Calcula macronutrientes, distribui calorias nas refeicoes e
    gera sugestoes de cardapio considerando restricoes alimentares.
    """

    def __init__(self, atleta: DadosAtleta):
        self.atleta = atleta
        self.macros = self._calcular_macros()

    def _calcular_macros(self) -> Macronutrientes:
        """Calcula macronutrientes do atleta."""
        return calcular_macronutrientes(
            peso_kg=self.atleta.peso_kg,
            altura_cm=self.atleta.altura_cm,
            idade=self.atleta.idade,
            sexo=self.atleta.sexo,
            objetivo=self.atleta.objetivo,
            nivel_atividade=self.atleta.nivel_atividade,
        )

    def _obter_catalogo_alimentos(self) -> dict[str, list[str]]:
        """Seleciona catalogo de alimentos conforme restricoes."""
        restricoes = self.atleta.restricoes

        if RestricaoAlimentar.VEGANO in restricoes:
            return SUGESTOES_VEGANO
        elif RestricaoAlimentar.VEGETARIANO in restricoes:
            return SUGESTOES_VEGETARIANO
        return SUGESTOES_PADRAO

    def _get_distribuicao_refeicoes(self) -> list[tuple[str, str, float]]:
        """Retorna tabela de distribuicao de refeicoes."""
        n = self.atleta.refeicoes_por_dia
        if n >= 6:
            return DISTRIBUICAO_REFEICOES[6]
        elif n >= 5:
            return DISTRIBUICAO_REFEICOES[5]
        return DISTRIBUICAO_REFEICOES[4]

    def gerar_plano(self) -> PlanoAlimentar:
        """Gera plano alimentar diario completo."""
        catalogo = self._obter_catalogo_alimentos()
        distribuicao = self._get_distribuicao_refeicoes()
        cal_total = self.macros.calorias_totais_kcal
        refeicoes: list[Refeicao] = []

        for nome, horario, pct_cal in distribuicao:
            cal_refeicao = cal_total * pct_cal

            prot_refeicao = self.macros.proteinas_g * pct_cal
            carb_refeicao = self.macros.carboidratos_g * pct_cal
            gord_refeicao = self.macros.gorduras_g * pct_cal

            alimentos = catalogo.get(nome, ["Refeicao balanceada - consulte seu nutricionista"])

            refeicoes.append(Refeicao(
                nome=nome,
                horario=horario,
                calorias_kcal=round(cal_refeicao, 0),
                proteinas_g=round(prot_refeicao, 1),
                carboidratos_g=round(carb_refeicao, 1),
                gorduras_g=round(gord_refeicao, 1),
                alimentos=alimentos,
            ))

        return PlanoAlimentar(
            atleta=self.atleta,
            macronutrientes=self.macros,
            refeicoes=refeicoes,
            recomendacoes=self._gerar_recomendacoes(),
            observacoes=self._gerar_observacoes(),
        )

    def _gerar_recomendacoes(self) -> list[str]:
        """Gera recomendacoes nutricionais personalizadas."""
        recs: list[str] = []
        obj = self.atleta.objetivo

        hidratacao_ml = self.atleta.peso_kg * 35
        recs.append(
            f"Hidratacao: beber {hidratacao_ml / 1000:.1f}L de agua por dia"
        )

        if obj == ObjetivoNutricional.HIPERTROFIA:
            recs.append("Consumir proteina de alto valor biologico em todas as refeicoes")
            recs.append("Priorizar carboidratos antes e apos o treino")
            recs.append("Considerar suplementacao de creatina (3-5g/dia)")

        elif obj == ObjetivoNutricional.EMAGRECIMENTO:
            recs.append("Manter alta ingestao de proteinas para preservar massa magra")
            recs.append("Priorizar fibras e alimentos de baixa densidade calorica")
            recs.append("Evitar liquidos caloricos (sucos, refrigerantes)")

        elif obj == ObjetivoNutricional.DEFINICAO:
            recs.append("Manter deficit calorico moderado para preservar massa muscular")
            recs.append("Alta proteina (2.0+ g/kg) para anticatabolismo")
            recs.append("Carboidratos concentrados no periodo peri-treino")

        else:  # manutencao
            recs.append("Manter equilibrio entre ingestao e gasto calorico")
            recs.append("Variedade alimentar para garantir micronutrientes")

        recs.append("Hidratacao durante treino: 200-300ml a cada 15-20 min")
        return recs

    def _gerar_observacoes(self) -> str:
        """Gera notas e observacoes do plano."""
        m = self.macros
        nota = (
            f"Plano para {self.atleta.objetivo.value} | "
            f"{self.atleta.refeicoes_por_dia} refeicoes/dia\n"
            f"Proteina: {m.proteinas_g:.0f}g ({m.proteinas_g / self.atleta.peso_kg:.1f} g/kg) | "
            f"Carboidratos: {m.carboidratos_g:.0f}g | "
            f"Gorduras: {m.gorduras_g:.0f}g\n"
        )
        if self.atleta.restricoes:
            r_str = ", ".join(r.value for r in self.atleta.restricoes if r != RestricaoAlimentar.NENHUMA)
            if r_str:
                nota += f"Restricoes: {r_str}\n"

        nota += (
            "IMPORTANTE: Plano gerado automaticamente como referencia. "
            "Consulte um nutricionista esportivo para validacao."
        )
        return nota


# -----------------------------------------------------------
# Funcoes de exibicao
# -----------------------------------------------------------

def imprimir_plano(plano: PlanoAlimentar) -> None:
    """Formata e imprime o plano alimentar de forma legivel."""
    atleta = plano.atleta
    macros = plano.macronutrientes

    print("=" * 70)
    print(f" PLANO ALIMENTAR - {atleta.nome.upper()}")
    print("=" * 70)
    print(textwrap.fill(
        f"Idade: {atleta.idade} anos | Sexo: {atleta.sexo} | "
        f"Peso: {atleta.peso_kg:.1f} kg | Altura: {atleta.altura_cm} cm | "
        f"Objetivo: {atleta.objetivo.value} | Nivel: {atleta.nivel_atividade.value}"
    ))
    print("-" * 70)

    print(f"\n  RESUMO DE MACRONUTRIENTES DIARIOS")
    print(f"  Calorias totais: {int(macros.calorias_totais_kcal)} kcal "
          f"(proporcao P/C/G: {macros.proporcao_pct})")
    print(f"  Proteinas:   {macros.proteinas_g:.1f} g ")
    print(f"  Carboidratos: {macros.carboidratos_g:.1f} g")
    print(f"  Gorduras:    {macros.gorduras_g:.1f} g")
    print(f"  Proteina/kg: {macros.proteinas_g / atleta.peso_kg:.1f} g/kg")

    print(f"\n  DISTRIBUICAO DE REFEICOES")
    print("-" * 70)

    for ref in plano.refeicoes:
        print(f"\n  [{ref.horario}] {ref.nome.upper()}")
        print(f"  {int(ref.calorias_kcal)} kcal | "
              f"P: {ref.proteinas_g:.1f}g | C: {ref.carboidratos_g:.1f}g | G: {ref.gorduras_g:.1f}g")
        print(f"  Sugestoes:")
        for al in ref.alimentos:
            print(f"    - {al}")

    print(f"\n  RECOMENDACOES")
    print("-" * 70)
    for rec in plano.recomendacoes:
        print(f"  * {rec}")

    if plano.observacoes:
        print(f"\n  {plano.observacoes}")

    print("=" * 70)


# -----------------------------------------------------------
# Demonstracao
# -----------------------------------------------------------

def main() -> None:
    """Demonstracao de uso do modulo plano_alimentar."""
    print("\n" + "#" * 70)
    print("# DEMONSTRACAO - PLANO ALIMENTAR")
    print("# Esporte & Saude Centro - Departamento de Nutricao Esportiva")
    print("#" * 70)

    # Exemplo 1: Hipertrofia
    print("\n--- Exemplo 1: Hipertrofia (Homem, atividade intensa) ---\n")
    atleta1 = DadosAtleta(
        nome="Carlos Silva",
        idade=28,
        peso_kg=82.0,
        altura_cm=178,
        sexo="M",
        objetivo=ObjetivoNutricional.HIPERTROFIA,
        nivel_atividade=NivelAtividade.INTENSO,
        refeicoes_por_dia=6,
    )
    ger1 = GerenciadorPlanoAlimentar(atleta1)
    imprimir_plano(ger1.gerar_plano())

    # Exemplo 2: Emagrecimento
    print("\n\n--- Exemplo 2: Emagrecimento (Mulher, atividade moderada) ---\n")
    atleta2 = DadosAtleta(
        nome="Ana Beatriz",
        idade=35,
        peso_kg=75.0,
        altura_cm=165,
        sexo="F",
        objetivo=ObjetivoNutricional.EMAGRECIMENTO,
        nivel_atividade=NivelAtividade.MODERADO,
        refeicoes_por_dia=5,
        restricoes=[RestricaoAlimentar.SEM_LACTOSE],
    )
    ger2 = GerenciadorPlanoAlimentar(atleta2)
    imprimir_plano(ger2.gerar_plano())

    # Exemplo 3: Manutencao vegetariano
    print("\n\n--- Exemplo 3: Manutencao (Homem, vegetariano) ---\n")
    atleta3 = DadosAtleta(
        nome="Rafael Costa",
        idade=32,
        peso_kg=70.0,
        altura_cm=175,
        sexo="M",
        objetivo=ObjetivoNutricional.MANUTENCAO,
        nivel_atividade=NivelAtividade.MODERADO,
        refeicoes_por_dia=4,
        restricoes=[RestricaoAlimentar.VEGETARIANO],
    )
    ger3 = GerenciadorPlanoAlimentar(atleta3)
    imprimir_plano(ger3.gerar_plano())

    print("\n" + "#" * 70)
    print("# FIM DA DEMONSTRACAO")
    print("#" * 70)


if __name__ == "__main__":
    main()
