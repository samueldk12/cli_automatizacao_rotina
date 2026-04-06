"""
Calculadora de Imposto de Renda para Investimentos - Brasil.

Cobre renda variavel (acoes, FIIs, opcoes), renda fixa (CDB, LCI, LCA, Tesouro),
day trade, compensacao de perdas e geracao de informacoes de DARF.
"""

from __future__ import annotations

import dataclasses
from datetime import date
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

class TipoInvestimento(str, Enum):
    RENDA_VARIAVEL = "renda_variavel"
    RENDA_FIXA = "renda_fixa"
    DAY_TRADE = "day_trade"


class TipoRendaFixa(str, Enum):
    CDB = "CDB"
    LCI = "LCI"    # isenta de IR
    LCA = "LCA"    # isenta de IR
    TESOURO = "Tesouro Direto"
    DEBENTURE = "Debenture"
    OUTROS = "Outros"


@dataclasses.dataclass
class Operacao:
    """Representa uma operacao de compra/venda."""
    descricao: str
    tipo: TipoInvestimento
    data: date
    valor_compra: float
    valor_venda: float
    custo_corretagem: float = 0.0
    tipo_rf: Optional[TipoRendaFixa] = None
    prazo_dias: int = 0       # prazo em dias para renda fixa
    quantidade: int = 1


@dataclasses.dataclass
class ResultadoMensal:
    """Resultado apurado por mes."""
    mes_ano: str
    ganho_liquido: float = 0.0
    perda: float = 0.0
    imposto_devido: float = 0.0
    isento: bool = False
    faixa_aliquota: Optional[str] = None
    tipo: Optional[TipoInvestimento] = None


@dataclasses.dataclass
class DarfInfo:
    """Informacoes para emissao de DARF."""
    codigo_receita: str
    descricao: str
    valor: float
    data_vencimento: date
    periodo_apuracao: str
    multa_juros: float = 0.0


# ---------------------------------------------------------------------------
# Aliquota regressiva de Renda Fixa
# ---------------------------------------------------------------------------

def aliquota_rf(prazo_dias: int) -> float:
    """Retorna a aliquota IRRF conforme o prazo (tabela regressiva).

    Ate 180 dias:     22.5%
    181 a 360 dias:   20.0%
    361 a 720 dias:   17.5%
    Acima de 720 dias: 15.0%
    """
    if prazo_dias <= 180:
        return 0.225
    elif prazo_dias <= 360:
        return 0.20
    elif prazo_dias <= 720:
        return 0.175
    else:
        return 0.15


# ---------------------------------------------------------------------------
# Calculo por operacao
# ---------------------------------------------------------------------------

def calcular_operacao(op: Operacao) -> ResultadoMensal:
    """Calcula o resultado tributario de uma operacao."""
    mes_ano = f"{op.data.month:02d}/{op.data.year}"

    if op.tipo == TipoInvestimento.RENDA_FIXA:
        return _calc_rf(op, mes_ano)
    elif op.tipo == TipoInvestimento.DAY_TRADE:
        return _calc_day_trade(op, mes_ano)
    else:
        return _calc_rv(op, mes_ano)


def _calc_rf(op: Operacao, mes_ano: str) -> ResultadoMensal:
    if op.tipo_rf in (TipoRendaFixa.LCI, TipoRendaFixa.LCA):
        return ResultadoMensal(
            mes_ano=mes_ano, ganho_liquido=0.0, perda=0.0,
            imposto_devido=0.0, isento=True,
            faixa_aliquota="Isento (LCI/LCA)", tipo=op.tipo,
        )

    ganho = op.valor_venda - op.valor_compra - op.custo_corretagem
    alq = aliquota_rf(op.prazo_dias)
    imposto = max(0.0, ganho * alq)

    return ResultadoMensal(
        mes_ano=mes_ano,
        ganho_liquido=round(max(0.0, ganho), 2),
        perda=round(abs(min(0.0, ganho)), 2),
        imposto_devido=round(imposto, 2),
        faixa_aliquota=f"{alq * 100:.1f}%",
        tipo=op.tipo,
    )


def _calc_day_trade(op: Operacao, mes_ano: str) -> ResultadoMensal:
    ganho = op.valor_venda - op.valor_compra - op.custo_corretagem
    alq = 0.20  # Day trade sempre 20%
    imposto = max(0.0, ganho * alq)

    return ResultadoMensal(
        mes_ano=mes_ano,
        ganho_liquido=round(max(0.0, ganho), 2),
        perda=round(abs(min(0.0, ganho)), 2),
        imposto_devido=round(imposto, 2),
        faixa_aliquota="20.0% (Day Trade)",
        tipo=op.tipo,
    )


def _calc_rv(op: Operacao, mes_ano: str) -> ResultadoMensal:
    """Renda variavel: ganhos ate R$20.000/mes sao isentos (swing trade)."""
    ganho = op.valor_venda - op.valor_compra - op.custo_corretagem

    if 0 < ganho <= 20_000:
        return ResultadoMensal(
            mes_ano=mes_ano,
            ganho_liquido=round(ganho, 2),
            perda=0.0,
            imposto_devido=0.0,
            isento=True,
            faixa_aliquota="Isento (ate R$20k/mes)",
            tipo=op.tipo,
        )
    else:
        alq = 0.15
        imposto = max(0.0, ganho * alq)
        return ResultadoMensal(
            mes_ano=mes_ano,
            ganho_liquido=round(max(0.0, ganho), 2),
            perda=round(abs(min(0.0, ganho)), 2),
            imposto_devido=round(imposto, 2),
            faixa_aliquota="15.0%",
            tipo=op.tipo,
        )


# ---------------------------------------------------------------------------
# Compensacao de perdas
# ---------------------------------------------------------------------------

def compensar_perdas(resultados: list[ResultadoMensal]) -> list[ResultadoMensal]:
    """Compensa perdas acumuladas com ganhos futuros."""
    perdas_acumuladas = 0.0

    for res in resultados:
        if res.perda > 0:
            perdas_acumuladas += res.perda
            continue

        if res.ganho_liquido > 0 and perdas_acumuladas > 0:
            compensacao = min(res.ganho_liquido, perdas_acumuladas)
            res.ganho_liquido -= compensacao
            perdas_acumuladas -= compensacao

            # Recalcula imposto
            if res.tipo == TipoInvestimento.DAY_TRADE:
                res.imposto_devido = round(res.ganho_liquido * 0.20, 2)
            elif res.tipo == TipoInvestimento.RENDA_VARIAVEL and res.ganho_liquido > 0:
                res.imposto_devido = round(res.ganho_liquido * 0.15, 2)
            elif res.tipo == TipoInvestimento.RENDA_FIXA and res.faixa_aliquota:
                try:
                    a = float(res.faixa_aliquota.split("%")[0]) / 100
                    res.imposto_devido = round(res.ganho_liquido * a, 2)
                except (ValueError, IndexError):
                    pass

    return resultados


# ---------------------------------------------------------------------------
# DARF
# ---------------------------------------------------------------------------

def gerar_darf(resultado: ResultadoMensal) -> Optional[DarfInfo]:
    if resultado.imposto_devido <= 0:
        return None

    mes, ano = resultado.mes_ano.split("/")
    vm = int(mes) + 1
    va = int(ano)
    if vm > 12:
        vm, va = 1, va + 1

    cod_map = {
        TipoInvestimento.RENDA_VARIAVEL: "6015",
        TipoInvestimento.RENDA_FIXA: "3040",
        TipoInvestimento.DAY_TRADE: "2100",
    }
    cod = cod_map.get(resultado.tipo or TipoInvestimento.RENDA_VARIAVEL, "6015")

    return DarfInfo(
        codigo_receita=cod,
        descricao=f"Ganho de capital - {resultado.tipo.value if resultado.tipo else 'inv'} ({resultado.mes_ano})",
        valor=resultado.imposto_devido,
        data_vencimento=date(va, min(vm, 12), 1),
        periodo_apuracao=resultado.mes_ano,
    )


# ---------------------------------------------------------------------------
# Relatorio consolidado
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class RelatorioConsolidado:
    resultados: list[ResultadoMensal]
    total_ganhos: float
    total_perdas: float
    total_imposto: float
    ganhos_isentos: float
    darfs: list[DarfInfo]


def consolidar(operacoes: list[Operacao]) -> RelatorioConsolidado:
    resultados = [calcular_operacao(o) for o in operacoes]
    resultados = compensar_perdas(resultados)

    tg = sum(r.ganho_liquido for r in resultados)
    tp = sum(r.perda for r in resultados)
    ti = sum(r.imposto_devido for r in resultados)
    gi = sum(r.ganho_liquido for r in resultados if r.isento)
    darfs = [d for d in (gerar_darf(r) for r in resultados) if d is not None]

    return RelatorioConsolidado(
        resultados=resultados,
        total_ganhos=tg,
        total_perdas=tp,
        total_imposto=ti,
        ganhos_isentos=gi,
        darfs=darfs,
    )


def formatar_relatorio(rel: RelatorioConsolidado) -> str:
    linhas = ["=" * 60]
    linhas.append("  RELATORIO IRPF - INVESTIMENTOS")
    linhas.append("=" * 60)
    linhas.append("")
    for r in rel.resultados:
        st = "ISENTO" if r.isento else f"IR: R${r.imposto_devido:.2f}"
        linhas.append(
            f"  [{r.mes_ano}] {r.tipo.value if r.tipo else '?'} | "
            f"Ganho: R${r.ganho_liquido:.2f} | Perda: R${r.perda:.2f} | "
            f"Aliq: {r.faixa_aliquota or 'N/A'} | {st}"
        )
    linhas.append("")
    linhas.append("-" * 60)
    linhas.append(f"  Total Ganhos:       R${rel.total_ganhos:.2f}")
    linhas.append(f"  Total Perdas:        R${rel.total_perdas:.2f}")
    linhas.append(f"  Ganhos Isentos:     R${rel.ganhos_isentos:.2f}")
    linhas.append(f"  Total IR Devido:    R${rel.total_imposto:.2f}")
    linhas.append("")
    if rel.darfs:
        linhas.append("  DARFs A PAGAR:")
        for d in rel.darfs:
            linhas.append(
                f"    Codigo: {d.codigo_receita} | R${d.valor:.2f} | "
                f"Vencimento: {d.data_vencimento.strftime('%d/%m/%Y')}"
            )
    linhas.append("=" * 60)
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n>>> CALCULADORA IRPF - INVESTIMENTOS\n")

    op1 = Operacao(
        descricao="PETR4 swing trade",
        tipo=TipoInvestimento.RENDA_VARIAVEL,
        data=date(2024, 3, 15),
        valor_compra=15_000.0,
        valor_venda=18_500.0,
        custo_corretagem=29.90,
    )
    op2 = Operacao(
        descricao="CDB 120 dias",
        tipo=TipoInvestimento.RENDA_FIXA,
        data=date(2024, 4, 1),
        valor_compra=10_000.0,
        valor_venda=10_650.0,
        tipo_rf=TipoRendaFixa.CDB,
        prazo_dias=120,
    )
    op3 = Operacao(
        descricao="LCI 365 dias (isenta)",
        tipo=TipoInvestimento.RENDA_FIXA,
        data=date(2024, 5, 1),
        valor_compra=5_000.0,
        valor_venda=5_575.0,
        tipo_rf=TipoRendaFixa.LCI,
        prazo_dias=365,
    )
    op4 = Operacao(
        descricao="Day trade - perda",
        tipo=TipoInvestimento.DAY_TRADE,
        data=date(2024, 6, 3),
        valor_compra=50_000.0,
        valor_venda=48_000.0,
        custo_corretagem=5.0,
    )
    op5 = Operacao(
        descricao="Day trade - ganho",
        tipo=TipoInvestimento.DAY_TRADE,
        data=date(2024, 7, 10),
        valor_compra=30_000.0,
        valor_venda=32_500.0,
        custo_corretagem=5.0,
    )

    rel = consolidar([op1, op2, op3, op4, op5])
    print(formatar_relatorio(rel))


if __name__ == "__main__":
    main()
