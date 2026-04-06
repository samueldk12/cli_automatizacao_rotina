"""
Calculadora de Folha de Pagamento CLT - Brasil.

Calcula INSS (tabela progressiva 2024), IRRF, FGTS (8%), 13o salario,
ferias + 1/3 constitucional, horas extras (50%, 100%),
adicional noturno (20%), salario liquido e custo empregador.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

class RegimeTrabalho(str, Enum):
    MENSALISTA = "mensalista"
    HORISTA = "horista"


@dataclasses.dataclass
class Funcionario:
    """Dados do funcionario."""
    nome: str
    cpf: str
    cargo: str
    salario_bruto: float
    regime: RegimeTrabalho = RegimeTrabalho.MENSALISTA
    dependentes: int = 0
    data_admissao: str = ""


@dataclasses.dataclass
class RegistroHorasExtras:
    """Registro de horas extras e noturnas."""
    horas_50: float = 0.0       # HE 50% (dias uteis)
    horas_100: float = 0.0      # HE 100% (dominicos/feriados)
    horas_noturnas: float = 0.0  # Horas noturnas (adicional 20%)


@dataclasses.dataclass
class Descontos:
    """Descontos aplicados na folha."""
    inss: float = 0.0
    irrf: float = 0.0
    outros: float = 0.0
    total: float = 0.0


@dataclasses.dataclass
class Proventos:
    """Proventos da folha."""
    salario_base: float = 0.0
    horas_extras_50: float = 0.0
    horas_extras_100: float = 0.0
    adicional_noturno: float = 0.0
    outros: float = 0.0
    total: float = 0.0


@dataclasses.dataclass
class FolhaPagamento:
    """Recibo de folha de pagamento."""
    funcionario: Funcionario
    proventos: Proventos
    descontos: Descontos
    fgts_mes: float = 0.0
    salario_liquido: float = 0.0


@dataclasses.dataclass
class CustoEmpregador:
    """Custo total para o empregador."""
    salario_bruto: float
    encargos_inss_empresa: float   # 20% patronal
    fgts: float                    # 8%
    costos_acidentarios: float     # RAT
    outros_encargos: float
    custo_total_mensal: float
    custo_13_ferias: float         # 13o + ferias + 1/3
    custo_anual_estimado: float


# ---------------------------------------------------------------------------
# INSS - Tabela Progressiva 2024
# ---------------------------------------------------------------------------

TETO_INSS = 7786.02


def calcular_inss(salario: float) -> float:
    """Calcula INSS por faixas progressivas conforme tabela 2024.

    Faixa 1: ate R$1.412,00      -> 7.5%
    Faixa 2: R$1.412,01 a 2.666,68 -> 9%
    Faixa 3: R$2.666,69 a 4.000,03 -> 12%
    Faixa 4: R$4.000,04 a 7.786,02 -> 14%
    """
    salario = min(salario, TETO_INSS)
    inss = 0.0

    f1_base = min(salario, 1412.00)
    inss += f1_base * 0.075

    if salario > 1412.00:
        f2_base = min(salario, 2666.68) - 1412.00
        inss += f2_base * 0.09

    if salario > 2666.68:
        f3_base = min(salario, 4000.03) - 2666.68
        inss += f3_base * 0.12

    if salario > 4000.03:
        f4_base = salario - 4000.03
        inss += f4_base * 0.14

    return round(inss, 2)


def calcular_inss_empresa(salario: float) -> float:
    """INSS patronal: 20% sobre o salario (sem teto para a empresa)."""
    return round(salario * 0.20, 2)


# ---------------------------------------------------------------------------
# IRRF - Tabela 2024
# ---------------------------------------------------------------------------

TABELA_IRRF = [
    # (limite, aliquota, deducao)
    (2112.00, 0.0, 0.0),
    (2826.65, 0.075, 158.40),
    (3751.05, 0.15, 370.40),
    (4664.68, 0.225, 651.73),
    (float("inf"), 0.275, 884.96),
]

DEDUCAO_DEPENDENTE = 189.59


def calcular_irrf(base_calculo: float, dependentes: int = 0) -> float:
    """Calcula IRRF com base na tabela simplificada 2024."""
    base_ajustada = base_calculo - (dependentes * DEDUCAO_DEPENDENTE)

    if base_ajustada <= 2112.00:
        return 0.0

    for limite, aliquota, deducao in TABELA_IRRF:
        if base_ajustada <= limite:
            return round(max(0.0, base_ajustada * aliquota - deducao), 2)

    return 0.0


# ---------------------------------------------------------------------------
# Horas Extras
# ---------------------------------------------------------------------------

def valor_hora_normal(salario_bruto: float) -> float:
    """Valor da hora normal (jornada 220h)."""
    return salario_bruto / 220


def calcular_valor_he(salario_bruto: float, horas: float, perc_adicional: float) -> float:
    """Calcula valor de horas extras.

    HE = valor_hora * (1 + adicional) * horas
    """
    vh = valor_hora_normal(salario_bruto)
    return round(vh * (1 + perc_adicional) * horas, 2)


def calcular_adicional_noturno(salario_bruto: float, horas_noturnas: float) -> float:
    """Calcula adicional noturno: 20% sobre as horas noturnas."""
    vh = valor_hora_normal(salario_bruto)
    return round(vh * 0.20 * horas_noturnas, 2)


# ---------------------------------------------------------------------------
# 13o Salario
# ---------------------------------------------------------------------------

def calcular_13_salario(salario_bruto: float, meses_trabalhados: int) -> tuple[float, float]:
    """Calcula as duas parcelas do 13o.

    Retorna (parcela1, parcela2).
    parcela1 = 50% do proporcional (sem descontos).
    parcela2 = resto - INSS - IRRF.
    """
    proporcional = salario_bruto * (meses_trabalhados / 12)
    p1 = round(proporcional * 0.5, 2)

    # 2a parcela: valor restante com descontos
    base = proporcional * 0.5
    inss = calcular_inss(proporcional)
    irrf = calcular_irrf(proporcional - inss)
    p2 = round(max(0.0, base - inss * 0.5 - irrf * 0.5), 2)

    return p1, p2


# ---------------------------------------------------------------------------
# Ferias
# ---------------------------------------------------------------------------

def calcular_ferias(salario_bruto: float, dias: int = 30) -> float:
    """Calcula ferias + 1/3 constitucional."""
    valor = salario_bruto * (dias / 30)
    terco = valor / 3
    return round(valor + terco, 2)


# ---------------------------------------------------------------------------
# Calculo da folha
# ---------------------------------------------------------------------------

def calcular_folha(func: Funcionario, horas: Optional[RegistroHorasExtras] = None,
                   outros_descontos: float = 0.0) -> FolhaPagamento:
    """Calcula a folha de pagamento completa de um funcionario."""
    proventos = Proventos(salario_base=func.salario_bruto)

    if horas:
        proventos.horas_extras_50 = calcular_valor_he(
            func.salario_bruto, horas.horas_50, 0.50)
        proventos.horas_extras_100 = calcular_valor_he(
            func.salario_bruto, horas.horas_100, 1.00)
        proventos.adicional_noturno = calcular_adicional_noturno(
            func.salario_bruto, horas.horas_noturnas)

    proventos.total = round(
        proventos.salario_base
        + proventos.horas_extras_50
        + proventos.horas_extras_100
        + proventos.adicional_noturno
        + proventos.outros,
        2
    )

    inss = calcular_inss(proventos.total)
    base_irrf = proventos.total - inss
    irrf = calcular_irrf(base_irrf, func.dependentes)

    descontos = Descontos(
        inss=inss,
        irrf=irrf,
        outros=outros_descontos,
        total=round(inss + irrf + outros_descontos, 2),
    )

    fgts = round(func.salario_bruto * 0.08, 2)
    liquido = round(proventos.total - descontos.total, 2)

    return FolhaPagamento(
        funcionario=func,
        proventos=proventos,
        descontos=descontos,
        fgts_mes=fgts,
        salario_liquido=liquido,
    )


# ---------------------------------------------------------------------------
# Custo Empregador
# ---------------------------------------------------------------------------

def calcular_custo_empregador(salario_bruto: float,
                               rat: float = 0.02,
                               outros_encargos: float = 0.0) -> CustoEmpregador:
    """Calcula o custo total para o empregador."""
    inss_emp = calcular_inss_empresa(salario_bruto)
    fgts = salario_bruto * 0.08
    cust_acid = salario_bruto * rat

    custo_mensal = salario_bruto + inss_emp + fgts + cust_acid + outros_encargos

    # Custo anual inclui 13o e ferias + 1/3
    custo_13 = salario_bruto
    custo_ferias = calcular_ferias(salario_bruto)
    custo_13_ferias = custo_13 + custo_ferias

    return CustoEmpregador(
        salario_bruto=salario_bruto,
        encargos_inss_empresa=inss_emp,
        fgts=round(fgts, 2),
        costos_acidentarios=round(cust_acid, 2),
        outros_encargos=outros_encargos,
        custo_total_mensal=round(custo_mensal, 2),
        custo_13_ferias=round(custo_13_ferias, 2),
        custo_anual_estimado=round(custo_mensal * 12 + custo_13_ferias, 2),
    )


def formatar_folha(fp: FolhaPagamento) -> str:
    """Formata a folha como texto."""
    linhas = ["=" * 62]
    linhas.append("  FOLHA DE PAGAMENTO - CLT")
    linhas.append("=" * 62)
    f = fp.funcionario
    linhas.append(f"  Nome: {f.nome} | CPF: {f.cpf} | Cargo: {f.cargo}")
    linhas.append(f"  Dependentes: {f.dependentes}")
    linhas.append("")
    linhas.append("  PROVENTOS:")
    p = fp.proventos
    linhas.append(f"    Salario Base:        R${p.salario_base:>12.2f}")
    if p.horas_extras_50 > 0:
        linhas.append(f"    HE 50%:              R${p.horas_extras_50:>12.2f}")
    if p.horas_extras_100 > 0:
        linhas.append(f"    HE 100%:             R${p.horas_extras_100:>12.2f}")
    if p.adicional_noturno > 0:
        linhas.append(f"    Adicional Noturno:   R${p.adicional_noturno:>12.2f}")
    linhas.append(f"    TOTAL PROVENTOS:    R${p.total:>12.2f}")
    linhas.append("")
    linhas.append("  DESCONTOS:")
    d = fp.descontos
    linhas.append(f"    INSS:                R${d.inss:>12.2f}")
    linhas.append(f"    IRRF:                R${d.irrf:>12.2f}")
    if d.outros > 0:
        linhas.append(f"    Outros:              R${d.outros:>12.2f}")
    linhas.append(f"    TOTAL DESCONTOS:    R${d.total:>12.2f}")
    linhas.append("")
    linhas.append("-" * 62)
    linhas.append(f"  FGTS Mes (8%):        R${fp.fgts_mes:>12.2f}")
    linhas.append(f"  SALARIO LIQUIDO:      R${fp.salario_liquido:>12.2f}")
    linhas.append("=" * 62)
    return "\n".join(linhas)


def formatar_custo_empregador(ce: CustoEmpregador) -> str:
    """Formata o custo empregador."""
    linhas = ["=" * 62]
    linhas.append("  CUSTO EMPREGADOR")
    linhas.append("=" * 62)
    linhas.append(f"  Salario Bruto:             R${ce.salario_bruto:>12.2f}")
    linhas.append(f"  INSS Patronal (20%):       R${ce.encargos_inss_empresa:>12.2f}")
    linhas.append(f"  FGTS (8%):                 R${ce.fgts:>12.2f}")
    linhas.append(f"  RAT/Acidente Trabalho:     R${ce.costos_acidentarios:>12.2f}")
    if ce.outros_encargos > 0:
        linhas.append(f"  Outros Encargos:         R${ce.outros_encargos:>12.2f}")
    linhas.append("-" * 62)
    linhas.append(f"  CUSTO MENSAL:            R${ce.custo_total_mensal:>12.2f}")
    linhas.append(f"  13o + Ferias (+1/3):     R${ce.custo_13_ferias:>12.2f}")
    linhas.append(f"  CUSTO ANUAL ESTIMADO:   R${ce.custo_anual_estimado:>12.2f}")
    linhas.append("=" * 62)
    return "\n".join(linhas)


def main() -> None:
    """Demonstracao da calculadora de folha."""
    print("\n>>> CALCULADORA FOLHA DE PAGAMENTO CLT\n")

    # Exemplo 1: Analista, salario medio
    func1 = Funcionario(
        nome="Joao da Silva",
        cpf="123.456.789-00",
        cargo="Analista de Sistemas",
        salario_bruto=5500.00,
        dependentes=1,
    )
    fp1 = calcular_folha(func1)
    print(formatar_folha(fp1))
    print("")

    ce1 = calcular_custo_empregador(5500.00)
    print(formatar_custo_empregador(ce1))

    # Exemplo 2: Operador com horas extras
    func2 = Funcionario(
        nome="Maria Santos",
        cpf="987.654.321-00",
        cargo="Operadora de Maquinas",
        salario_bruto=1412.00,
        dependentes=2,
    )
    he2 = RegistroHorasExtras(horas_50=20.0, horas_100=8.0, horas_noturnas=40.0)
    fp2 = calcular_folha(func2, horas=he2)
    print(formatar_folha(fp2))

    # Exemplo 3: Diretoria
    func3 = Funcionario(
        nome="Carlos Diretor",
        cpf="111.222.333-44",
        cargo="Diretor Financeiro",
        salario_bruto=15000.00,
        dependentes=3,
    )
    fp3 = calcular_folha(func3)
    print(formatar_folha(fp3))

    ce3 = calcular_custo_empregador(15000.00)
    print(formatar_custo_empregador(ce3))

    # Ferias e 13o
    print("\n>>> FERIAS E 13o SALARIO\n")
    print(f"Ferias (30d) de Joao: R${calcular_ferias(5500.00):,.2f}")
    p1, p2 = calcular_13_salario(5500.00, 12)
    print(f"1a parcela 13o: R${p1:,.2f}")
    print(f"2a parcela 13o: R${p2:,.2f}")


if __name__ == "__main__":
    main()
