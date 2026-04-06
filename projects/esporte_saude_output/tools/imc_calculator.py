"""
Módulo: imc_calculator.py
Descrição: Calculadora fitness que computa IMC, percentual de gordura corpórea,
taxa metabólica basal (TMB), e permite acompanhar métricas do atleta
ao longo do tempo.

Departamento: treinamento e fisioterapia
Empresa: Esporte & Saúde Centro
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
import textwrap


# -----------------------------------------------------------
# Enums
# -----------------------------------------------------------

class Sexo(Enum):
    """Sexo biológico do atleta (usado nos cálculos)."""
    MASCULINO = "masculino"
    FEMININO = "feminino"


class ClassificacaoIMC(Enum):
    """Classificação do IMC conforme OMS."""
    ABAIXO = "Abaixo do peso"
    NORMAL = "Peso normal"
    SOBREPESO = "Sobrepeso"
    OBESIDADE_GRAU_I = "Obesidade Grau I"
    OBESIDADE_GRAU_II = "Obesidade Grau II"
    OBESIDADE_GRAU_III = "Obesidade Grau III"


class ClassificacaoGordura(Enum):
    """Classificação de percentual de gordura por sexo."""
    ESSENCIAL = "Gordura essencial"
    ATLETA = "Atleta"
    BOM = "Bom"
    MEDIO = "Médio"
    ALTO = "Alto"
    MUITO_ALTO = "Muito alto"


class NivelAtividade(Enum):
    """Nível de atividade física para cálculo de gasto calórico."""
    SEDENTARIO = "Sedentário (pouco ou nenhum exercício)"
    LEVE = "Leve (1-3 dias/semana)"
    MODERADO = "Moderado (3-5 dias/semana)"
    INTENSO = "Intenso (6-7 dias/semana)"
    MUITO_INTENSO = "Muito intenso (2x por dia / atleta profissional)"


# -----------------------------------------------------------
# Dataclasses
# -----------------------------------------------------------

@dataclass
class RegistroMetricas:
    """Registro de métricas em uma determinada data."""
    data: date
    peso_kg: float
    altura_cm: float
    cintura_cm: Optional[float] = None
    quadril_cm: Optional[float] = None
    pescoco_cm: Optional[float] = None
    dobra_cutanea_mm: Optional[dict[str, float]] = None
    observacoes: str = ""


@dataclass
class ResultadoIMC:
    """Resultado do cálculo de IMC com classificação."""
    imc: float
    classificacao: str
    peso_ideal_min_kg: float
    peso_ideal_max_kg: float


@dataclass
class ResultadoGorduraCorporal:
    """Resultado do cálculo de percentual de gordura."""
    metodo: str
    percentual: float
    classificacao: str
    massa_gorda_kg: float
    massa_magra_kg: float


@dataclass
class ResultadoTMB:
    """Resultado da Taxa Metabólica Basal."""
    metodo: str
    tmb_kcal: float
    gasto_total_diario_kcal: float
    fator_atividade: float


@dataclass
class PerfilCompletoAtleta:
    """Resultado agregado de todos os cálculos do atleta."""
    registro: RegistroMetricas
    sexo: Sexo
    idade: int
    nivel_atividade: NivelAtividade
    imc: ResultadoIMC
    gordura: Optional[ResultadoGorduraCorporal] = None
    metabolismo: Optional[ResultadoTMB] = None
    cintura_quadril: Optional[float] = None
    resumo: str = ""


# -----------------------------------------------------------
# Constantes
# -----------------------------------------------------------

# Fatores de multiplicação para Gasto Energético Total (GET)
FATORES_ATIVIDADE: dict[NivelAtividade, float] = {
    NivelAtividade.SEDENTARIO: 1.2,
    NivelAtividade.LEVE: 1.375,
    NivelAtividade.MODERADO: 1.55,
    NivelAtividade.INTENSO: 1.725,
    NivelAtividade.MUITO_INTENSO: 1.9,
}

# Faixas de classificação de gordura corporal por sexo
# Formato: (min_pct, max_pct, classificacao)
TABELA_GORDURA: dict[Sexo, list[tuple[float, float, str]]] = {
    Sexo.MASCULINO: [
        (0.0, 5.0, ClassificacaoGordura.ESSENCIAL.value),
        (5.0, 14.0, ClassificacaoGordura.ATLETA.value),
        (14.0, 18.0, ClassificacaoGordura.BOM.value),
        (18.0, 25.0, ClassificacaoGordura.MEDIO.value),
        (25.0, 30.0, ClassificacaoGordura.ALTO.value),
        (30.0, 100.0, ClassificacaoGordura.MUITO_ALTO.value),
    ],
    Sexo.FEMININO: [
        (0.0, 13.0, ClassificacaoGordura.ESSENCIAL.value),
        (13.0, 21.0, ClassificacaoGordura.ATLETA.value),
        (21.0, 25.0, ClassificacaoGordura.BOM.value),
        (25.0, 32.0, ClassificacaoGordura.MEDIO.value),
        (32.0, 38.0, ClassificacaoGordura.ALTO.value),
        (38.0, 100.0, ClassificacaoGordura.MUITO_ALTO.value),
    ],
}


# -----------------------------------------------------------
# Funções de cálculo
# -----------------------------------------------------------

def calcular_imc(peso_kg: float, altura_cm: float) -> ResultadoIMC:
    """
    Calcula o Índice de Massa Corporal (IMC) e classificação.

    Fórmula: IMC = peso / altura²
    A faixa de peso ideal é baseada em IMC 18.5 - 24.9.
    """
    altura_m = altura_cm / 100.0
    imc = peso_kg / (altura_m ** 2)

    # Classificação conforme OMS
    if imc < 18.5:
        classificacao = ClassificacaoIMC.ABAIXO.value
    elif imc < 25.0:
        classificacao = ClassificacaoIMC.NORMAL.value
    elif imc < 30.0:
        classificacao = ClassificacaoIMC.SOBREPESO.value
    elif imc < 35.0:
        classificacao = ClassificacaoIMC.OBESIDADE_GRAU_I.value
    elif imc < 40.0:
        classificacao = ClassificacaoIMC.OBESIDADE_GRAU_II.value
    else:
        classificacao = ClassificacaoIMC.OBESIDADE_GRAU_III.value

    # Peso ideal baseado na faixa de IMC saudável (18.5 - 24.9)
    peso_ideal_min_kg = 18.5 * (altura_m ** 2)
    peso_ideal_max_kg = 24.9 * (altura_m ** 2)

    return ResultadoIMC(
        imc=round(imc, 1),
        classificacao=classificacao,
        peso_ideal_min_kg=round(peso_ideal_min_kg, 1),
        peso_ideal_max_kg=round(peso_ideal_max_kg, 1),
    )


def calcular_gordura_corporal_navy(
    cintura_cm: float,
    pescoco_cm: float,
    altura_cm: float,
    sexo: Sexo,
    peso_kg: float,
    quadril_cm: Optional[float] = None,
) -> ResultadoGorduraCorporal:
    """
    Calcula percentual de gordura pelo método da Marinha dos EUA (Navy).

    Para homens: 86.010 * log10(cintura - pescoco) - 70.041 * log10(altura) + 36.76
    Para mulheres: 163.205 * log10(cintura + quadril - pescoco)
                  - 97.684 * log10(altura) - 78.387
    """
    import math

    if sexo == Sexo.MASCULINO:
        diff = cintura_cm - pescoco_cm
        if diff <= 0:
            raise ValueError("Circunferência da cintura deve ser maior que a do pescoço.")
        pct = 86.010 * math.log10(diff) - 70.041 * math.log10(altura_cm) + 36.76
    else:
        if quadril_cm is None:
            raise ValueError("Para mulheres, a medida do quadril é necessária.")
        soma = cintura_cm + quadril_cm - pescoco_cm
        if soma <= 0:
            raise ValueError("Soma das medidas inválida.")
        pct = 163.205 * math.log10(soma) - 97.684 * math.log10(altura_cm) - 78.387

    pct = max(pct, 1.0)  # Valor mínimo razoável

    # Classificação
    tabela = TABELA_GORDURA[sexo]
    classificacao = _classificar_gordura(pct, tabela)

    # Massas
    massa_gorda_kg = peso_kg * (pct / 100.0)
    massa_magra_kg = peso_kg - massa_gorda_kg

    return ResultadoGorduraCorporal(
        metodo="Método da Marinha dos EUA (Navy)",
        percentual=round(pct, 1),
        classificacao=classificacao,
        massa_gorda_kg=round(massa_gorda_kg, 2),
        massa_magra_kg=round(massa_magra_kg, 2),
    )


def _classificar_gordura(pct: float, tabela: list[tuple[float, float, str]]) -> str:
    """Retorna a classificação de gordura baseado na tabela."""
    for min_val, max_val, classe in tabela:
        if min_val <= pct < max_val:
            return classe
    return tabela[-1][2]  # Última opção como fallback


def calcular_tmb_harris_benedict(
    peso_kg: float,
    altura_cm: float,
    idade: int,
    sexo: Sexo,
    nivel_atividade: NivelAtividade,
) -> ResultadoTMB:
    """
    Calcula a Taxa Metabólica Basal (TMB) pela equação
    revisada de Harris-Benedict (1984) e o Gasto Energético Total.

    Homens: TMB = 88.362 + (13.397 × peso) + (4.799 × altura) - (5.677 × idade)
    Mulheres: TMB = 447.593 + (9.247 × peso) + (3.098 × altura) - (4.330 × idade)
    """
    if sexo == Sexo.MASCULINO:
        tmb = 88.362 + (13.397 * peso_kg) + (4.799 * altura_cm) - (5.677 * idade)
    else:
        tmb = 447.593 + (9.247 * peso_kg) + (3.098 * altura_cm) - (4.330 * idade)

    fator = FATORES_ATIVIDADE[nivel_atividade]
    get = tmb * fator

    return ResultadoTMB(
        metodo="Harris-Benedict (revisada)",
        tmb_kcal=round(tmb, 0),
        gasto_total_diario_kcal=round(get, 0),
        fator_atividade=fator,
    )


def calcular_tmb_mifflin_st_jeor(
    peso_kg: float,
    altura_cm: float,
    idade: int,
    sexo: Sexo,
    nivel_atividade: NivelAtividade,
) -> ResultadoTMB:
    """
    Calcula TMB pela fórmula de Mifflin-St Jeor (1990),
    considerada mais precisa que Harris-Benedict.

    Homens: TMB = (10 × peso) + (6.25 × altura) - (5 × idade) + 5
    Mulheres: TMB = (10 × peso) + (6.25 × altura) - (5 × idade) - 161
    """
    if sexo == Sexo.MASCULINO:
        tmb = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade) + 5
    else:
        tmb = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade) - 161

    fator = FATORES_ATIVIDADE[nivel_atividade]
    get = tmb * fator

    return ResultadoTMB(
        metodo="Mifflin-St Jeor",
        tmb_kcal=round(tmb, 0),
        gasto_total_diario_kcal=round(get, 0),
        fator_atividade=fator,
    )


def calcular_relacao_cintura_quadril(cintura_cm: float, quadril_cm: float) -> float:
    """
    Relação cintura-quadril (RCQ). Indicador de risco cardiovascular.
    RCQ > 0.90 (homens) ou > 0.85 (mulheres) indica risco aumentado.
    """
    if quadril_cm <= 0:
        raise ValueError("Circunferência do quadril deve ser maior que zero.")
    return round(cintura_cm / quadril_cm, 3)


# -----------------------------------------------------------
# Classe principal: Calculadora de Métricas
# -----------------------------------------------------------

class CalculadoraMetricas:
    """
    Calculadora completa de métricas corporais e fisiológicas.

    Centraliza todos os cálculos (IMC, gordura, TMB, RCQ)
    e gera um perfil completo do atleta com resumo em texto.
    """

    def __init__(
        self,
        registro: RegistroMetricas,
        sexo: Sexo,
        idade: int,
        nivel_atividade: NivelAtividade,
    ):
        self.registro = registro
        self.sexo = sexo
        self.idade = idade
        self.nivel_atividade = nivel_atividade

    def calcular_tudo(self) -> PerfilCompletoAtleta:
        """Executa todos os cálculos disponíveis e retorna perfil completo."""
        r = self.registro

        # IMC
        imc_result = calcular_imc(r.peso_kg, r.altura_cm)

        # Gordura corporal (se houver medidas necessárias)
        gordura_result: Optional[ResultadoGorduraCorporal] = None
        if r.cintura_cm and r.pescoco_cm:
            try:
                gordura_result = calcular_gordura_corporal_navy(
                    cintura_cm=r.cintura_cm,
                    pescoco_cm=r.pescoco_cm,
                    altura_cm=r.altura_cm,
                    sexo=self.sexo,
                    peso_kg=r.peso_kg,
                    quadril_cm=r.quadril_cm,
                )
            except ValueError:
                gordura_result = None

        # Metabolismo (ambos os métodos)
        tmb_hb = calcular_tmb_harris_benedict(
            r.peso_kg, r.altura_cm, self.idade, self.sexo, self.nivel_atividade
        )
        tmb_msj = calcular_tmb_mifflin_st_jeor(
            r.peso_kg, r.altura_cm, self.idade, self.sexo, self.nivel_atividade
        )

        # Média dos dois métodos (recomendado para maior precisão)
        tmb_media_kcal = (tmb_hb.tmb_kcal + tmb_msj.tmb_kcal) / 2
        get_media_kcal = (tmb_hb.gasto_total_diario_kcal + tmb_msj.gasto_total_diario_kcal) / 2

        metabolismo = ResultadoTMB(
            metodo="Média (Harris-Benedict + Mifflin-St Jeor)",
            tmb_kcal=round(tmb_media_kcal, 0),
            gasto_total_diario_kcal=round(get_media_kcal, 0),
            fator_atividade=FATORES_ATIVIDADE[self.nivel_atividade],
        )

        # Relação cintura-quadril
        rcq: Optional[float] = None
        if r.cintura_cm and r.quadril_cm and r.quadril_cm > 0:
            rcq = calcular_relacao_cintura_quadril(r.cintura_cm, r.quadril_cm)

        resumo = self._gerar_resumo(imc_result, gordura_result, metabolismo, rcq)

        return PerfilCompletoAtleta(
            registro=r,
            sexo=self.sexo,
            idade=self.idade,
            nivel_atividade=self.nivel_atividade,
            imc=imc_result,
            gordura=gordura_result,
            metabolismo=metabolismo,
            cintura_quadril=rcq,
            resumo=resumo,
        )

    def _gerar_resumo(
        self,
        imc: ResultadoIMC,
        gordura: Optional[ResultadoGorduraCorporal],
        metabolismo: ResultadoTMB,
        rcq: Optional[float],
    ) -> str:
        """Gera um resumo textual das métricas calculadas."""
        linhas = []
        linhas.append(f"IMC: {imc.imc} ({imc.classificacao})")
        linhas.append(
            f"Peso ideal estimado: {imc.peso_ideal_min_kg:.1f} - "
            f"{imc.peso_ideal_max_kg:.1f} kg"
        )

        if gordura:
            linhas.append(
                f"Gordura corporal ({gordura.metodo}): {gordura.percentual}%"
            )
            linhas.append(f"  Classificação: {gordura.classificacao}")
            linhas.append(
                f"  Massa magra: {gordura.massa_magra_kg:.1f} kg | "
                f"Massa gorda: {gordura.massa_gorda_kg:.1f} kg"
            )

        linhas.append(
            f"Taxa Metabólica Basal ({metabolismo.metodo}): "
            f"{int(metabolismo.tmb_kcal)} kcal/dia"
        )
        linhas.append(
            f"Gasto Energético Total: "
            f"{int(metabolismo.gasto_total_diario_kcal)} kcal/dia "
            f"(fator: {metabolismo.fator_atividade})"
        )

        if rcq is not None:
            linhas.append(f"Relação cintura-quadril: {rcq}")
            if self.sexo == Sexo.MASCULINO:
                if rcq > 0.90:
                    linhas.append("  Risco cardiovascular AUMENTADO (RCQ > 0.90)")
                else:
                    linhas.append("  Dentro da faixa saudável (RCQ <= 0.90)")
            else:
                if rcq > 0.85:
                    linhas.append("  Risco cardiovascular AUMENTADO (RCQ > 0.85)")
                else:
                    linhas.append("  Dentro da faixa saudável (RCQ <= 0.85)")

        return "\n".join(linhas)


# -----------------------------------------------------------
# Classe: Historico de Métricas
# -----------------------------------------------------------

class HistoricoMetricas:
    """
    Armazena e acompanha registros de métricas do atleta ao longo do tempo.

    Permite calcular variações (peso, gordura, etc.) e identificar tendências.
    """

    def __init__(self, nome_atleta: str):
        self.nome_atleta = nome_atleta
        self.registros: list[tuple[RegistroMetricas, PerfilCompletoAtleta]] = []

    def adicionar_registro(
        self,
        registro: RegistroMetricas,
        perfil: PerfilCompletoAtleta,
    ) -> None:
        """Adiciona um novo registro ao histórico."""
        self.registros.append((registro, perfil))

    def get_variacao_peso(self) -> Optional[float]:
        """Retorna variação total de peso (kg) entre primeiro e último registro."""
        if len(self.registros) < 2:
            return None
        primeiro = self.registros[0][0].peso_kg
        ultimo = self.registros[-1][0].peso_kg
        return round(ultimo - primeiro, 1)

    def get_variacao_gordura(self) -> Optional[float]:
        """Retorna variação de percentual de gordura entre primeiro e último."""
        if len(self.registros) < 2:
            return None
        g1 = self.registros[0][1].gordura
        g2 = self.registros[-1][1].gordura
        if g1 is None or g2 is None:
            return None
        return round(g2.percentual - g1.percentual, 1)

    def gerar_relatorio_evolucao(self) -> str:
        """Gera relatório textual da evolução do atleta."""
        if not self.registros:
            return f"[{self.nome_atleta}] Nenhum registro disponível."

        linhas = []
        linhas.append(f"\n{'=' * 60}")
        linhas.append(f" RELATÓRIO DE EVOLUÇÃO - {self.nome_atleta.upper()}")
        linhas.append(f"{'=' * 60}")
        linhas.append(
            f"Registros: {len(self.registros)} | "
            f"Período: {self.registros[0][0].data} até {self.registros[-1][0].data}"
        )
        linhas.append("-" * 60)

        for i, (registro, perfil) in enumerate(self.registros, 1):
            linhas.append(f"\n  Registro #{i} - {registro.data}")
            linhas.append(f"  Peso: {registro.peso_kg:.1f} kg | "
                          f"IMC: {perfil.imc.imc} ({perfil.imc.classificacao})")
            if perfil.gordura:
                linhas.append(f"  Gordura: {perfil.gordura.percentual}% "
                              f"({perfil.gordura.classificacao})")
            if perfil.metabolismo:
                linhas.append(f"  GET: {int(perfil.metabolismo.gasto_total_diario_kcal)} kcal/dia")

        # Variações
        peso_var = self.get_variacao_peso()
        if peso_var is not None:
            direcao = "ganhou" if peso_var > 0 else "perdeu"
            linhas.append(
                f"\n  >>> Peso total {direcao}: {abs(peso_var):.1f} kg"
            )

        gordura_var = self.get_variacao_gordura()
        if gordura_var is not None:
            direcao = "aumentou" if gordura_var > 0 else "reduziu"
            linhas.append(
                f"  >>> Gordura corporal {direcao}: {abs(gordura_var):.1f} p.p."
            )

        linhas.append("=" * 60)
        return "\n".join(linhas)


# -----------------------------------------------------------
# Demonstração
# -----------------------------------------------------------

def main() -> None:
    """Demonstração de uso do módulo imc_calculator."""
    print("\n" + "#" * 70)
    print("# DEMONSTRAÇÃO - CALCULADORA DE MÉTRICAS FITNESS")
    print("# Esporte & Saúde Centro - Dept. Treinamento / Fisioterapia")
    print("#" * 70)

    # ---- Exemplo 1: Perfil completo masculino ----
    print("\n--- Exemplo 1: Atleta masculino intermediário ---\n")

    r1 = RegistroMetricas(
        data=date(2025, 4, 6),
        peso_kg=82.0,
        altura_cm=178,
        cintura_cm=88.0,
        quadril_cm=98.0,
        pescoco_cm=38.0,
    )
    calc1 = CalculadoraMetricas(
        registro=r1,
        sexo=Sexo.MASCULINO,
        idade=28,
        nivel_atividade=NivelAtividade.MODERADO,
    )
    perfil1 = calc1.calcular_tudo()
    print(perfil1.resumo)

    # ---- Exemplo 2: Perfil completo feminino ----
    print("\n--- Exemplo 2: Atleta feminina buscando emagrecimento ---\n")

    r2 = RegistroMetricas(
        data=date(2025, 4, 6),
        peso_kg=75.0,
        altura_cm=165,
        cintura_cm=82.0,
        quadril_cm=105.0,
        pescoco_cm=32.0,
    )
    calc2 = CalculadoraMetricas(
        registro=r2,
        sexo=Sexo.FEMININO,
        idade=35,
        nivel_atividade=NivelAtividade.LEVE,
    )
    perfil2 = calc2.calcular_tudo()
    print(perfil2.resumo)

    # ---- Exemplo 3: Histórico de métricas ----
    print("\n--- Exemplo 3: Evolução de atleta (3 meses) ---\n")

    historico = HistoricoMetricas("Carlos Silva")

    dados_mensais = [
        {"data": date(2025, 1, 6), "peso": 88.0, "cintura": 94.0, "quadril": 100.0},
        {"data": date(2025, 2, 3), "peso": 86.5, "cintura": 92.0, "quadril": 99.5},
        {"data": date(2025, 3, 3), "peso": 84.5, "cintura": 90.0, "quadril": 99.0},
        {"data": date(2025, 4, 6), "peso": 82.0, "cintura": 88.0, "quadril": 98.0},
    ]

    for d in dados_mensais:
        reg = RegistroMetricas(
            data=d["data"],
            peso_kg=d["peso"],
            altura_cm=178,
            cintura_cm=d["cintura"],
            quadril_cm=d["quadril"],
            pescoco_cm=38.0,
        )
        calc = CalculadoraMetricas(
            registro=reg,
            sexo=Sexo.MASCULINO,
            idade=28,
            nivel_atividade=NivelAtividade.MODERADO,
        )
        perfil = calc.calcular_tudo()
        historico.adicionar_registro(reg, perfil)

    print(historico.gerar_relatorio_evolucao())

    print("\n" + "#" * 70)
    print("# FIM DA DEMONSTRAÇÃO")
    print("#" * 70)


if __name__ == "__main__":
    main()
