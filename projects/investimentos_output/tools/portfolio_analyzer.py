"""
Analisador de Carteiras de Investimento
========================================
Modulo para analise de carteiras de investimento com metricas de
retorno, risco e correlacao entre ativos. Focado no mercado brasileiro.

Departamentos analise_mercado, gestao_portfolios, risk_compliance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ──────────────────────────────────────────────────────────────
#  Tipos auxiliares
# ──────────────────────────────────────────────────────────────
RetornosSerie = List[float]
PesoMap = Dict[str, float]
RetornosMap = Dict[str, RetornosSerie]


# ──────────────────────────────────────────────────────────────
#  Dataclasses
# ──────────────────────────────────────────────────────────────
@dataclass
class Ativo:
    """Representa um ativo na carteira."""
    ticker: str
    preco_atual: float
    quantidade: float
    classe: str  # "acoes", "renda_fixa", "fii", "cripto", etc.
    retornos_diarios: RetornosSerie = field(default_factory=list)
    custo_medio: float = 0.0

    @property
    def valor_posicao(self) -> float:
        return self.preco_atual * self.quantidade

    @property
    def resultado(self) -> float:
        return (self.preco_atual - self.custo_medio) * self.quantidade


@dataclass
class MetricasCarteira:
    """Metricas consolidadas da carteira."""
    rentabilidade_diaria: float
    rentabilidade_mensal: float
    rentabilidade_anual: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    volatilidade_anual: float
    var_95_diario: float
    correlacoes: Dict[Tuple[str, str], float] = field(default_factory=dict)
    detalhes_ativos: Dict[str, Dict[str, float]] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────
#  Classe principal
# ──────────────────────────────────────────────────────────────
class PortfolioAnalyzer:
    """
    Analisador de carteiras de investimento.

    Recebe uma lista de ativos com series historicas de retornos diarios
    e calcula metricas consolidadas de retorno e risco.
    """

    DIAS_UTEIS_MES = 21
    DIAS_UTEIS_ANO = 252
    TAXA_LIVRE_RISCO_ANUAL = 0.105  # ~Selic 10.5% a.a.

    def __init__(
        self,
        ativos: List[Ativo],
        pesos: Optional[PesoMap] = None,
        taxa_livre_risco: Optional[float] = None,
    ) -> None:
        self.ativos = {a.ticker: a for a in ativos}
        self._validar_pesos(pesos)
        self.pesos = pesos or self._pesos_mercado()
        self.taxa_livre = taxa_livre or self.TAXA_LIVRE_RISCO_ANUAL

    # ── Validacao / utilidades ──────────────────────────────
    def _validar_pesos(self, pesos: Optional[PesoMap]) -> None:
        if pesos is None:
            return
        total = sum(pesos.values())
        if not math.isclose(total, 1.0, abs_tol=1e-6):
            raise ValueError(f"Pesos devem somar 1.0, recebido {total:.4f}")

    def _pesos_mercado(self) -> PesoMap:
        total_valor = sum(a.valor_posicao for a in self.ativos.values())
        if total_valor == 0:
            n = len(self.ativos)
            return {t: 1.0 / n for t in self.ativos}
        return {
            t: a.valor_posicao / total_valor for t, a in self.ativos.items()
        }

    @staticmethod
    def _media(vals: List[float]) -> float:
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    @staticmethod
    def _desvio_padrao(vals: List[float], media: float) -> float:
        if len(vals) < 2:
            return 0.0
        var = sum((v - media) ** 2 for v in vals) / (len(vals) - 1)
        return math.sqrt(var)

    # ── Calculos de retorno ────────────────────────────────
    def retorno_carteira(self, retornos_map: RetornosMap) -> RetornosSerie:
        """Retorno diario ponderado da carteira."""
        if not retornos_map:
            return []
        n_dias = len(next(iter(retornos_map.values())))
        serie = []
        for dia in range(n_dias):
            ret_dia = 0.0
            for ticker, rets in retornos_map.items():
                peso = self.pesos.get(ticker, 0.0)
                if dia < len(rets):
                    ret_dia += peso * rets[dia]
            serie.append(ret_dia)
        return serie

    def rentabilidade_acumulada(self, serie: RetornosSerie) -> float:
        """Rentabilidade acumulada a partir de retornos diarios (juros compostos)."""
        acum = 1.0
        for r in serie:
            acum *= (1.0 + r)
        return acum - 1.0

    def rentabilidade_anualizada(
        self, rentabilidade_acum: float, n_dias: int
    ) -> float:
        """Anualiza a rentabilidade acumulada."""
        if n_dias <= 0:
            return 0.0
        return (1.0 + rentabilidade_acum) ** (self.DIAS_UTEIS_ANO / n_dias) - 1.0

    # ── Calculos de risco ──────────────────────────────────
    def volatilidade_anual(self, serie: RetornosSerie) -> float:
        media = self._media(serie)
        sigma = self._desvio_padrao(serie, media)
        return sigma * math.sqrt(self.DIAS_UTEIS_ANO)

    def sharpe_ratio(self, serie: RetornosSerie) -> float:
        """Indice de Sharpe - retorno excedente por unidade de risco total."""
        ret_anual = self.rentabilidade_anualizada(
            self.rentabilidade_acumulada(serie), len(serie)
        )
        vol = self.volatilidade_anual(serie)
        if vol == 0:
            return 0.0
        return (ret_anual - self.taxa_livre) / vol

    def sortino_ratio(self, serie: RetornosSerie) -> float:
        """Indice de Sortino - considera apenas downside deviation."""
        ret_anual = self.rentabilidade_anualizada(
            self.rentabilidade_acumulada(serie), len(serie)
        )
        rf_diario = (1.0 + self.taxa_livre) ** (1 / self.DIAS_UTEIS_ANO) - 1.0
        downside_sq = [
            (r - rf_diario) ** 2 for r in serie if r < rf_diario
        ]
        if not downside_sq:
            return 0.0
        downside_dev = (sum(downside_sq) / len(serie)) ** 0.5 * math.sqrt(self.DIAS_UTEIS_ANO)
        if downside_dev == 0:
            return 0.0
        return (ret_anual - self.taxa_livre) / downside_dev

    def max_drawdown(self, serie: RetornosSerie) -> float:
        """
        Maximo drawdown: maior perda do pico ao vale (valor absoluto).
        Valores sao negativos ou zero.
        """
        pico = 0.0
        dd_max = 0.0
        acum = 0.0
        for r in serie:
            acum += r
            acum_ret = acum  # aproximacao log
            if acum_ret > pico:
                pico = acum_ret
            dd = acum_ret - pico
            if dd < dd_max:
                dd_max = dd
        return dd_max

    def var_historico(self, serie: RetornosSerie, conf: float = 0.95) -> float:
        """Value at Risk historico no nivel de confianca informado."""
        if not serie:
            return 0.0
        ordenada = sorted(serie)
        idx = int((1 - conf) * len(ordenada))
        return ordenada[idx]

    # ── Correlacao entre ativos ────────────────────────────
    def matriz_correlacao(self, retornos_map: RetornosMap) -> Dict[Tuple[str, str], float]:
        """Calcula a matriz de correlacao par a par entre ativos."""
        tickers = sorted(retornos_map.keys())
        resultados: Dict[Tuple[str, str], float] = {}
        for i, t1 in enumerate(tickers):
            for j, t2 in enumerate(tickers):
                if i > j:
                    continue
                r1 = retornos_map[t1]
                r2 = retornos_map[t2]
                n = min(len(r1), len(r2))
                if n < 2:
                    resultados[(t1, t2)] = 0.0
                    continue
                s1 = r1[:n]
                s2 = r2[:n]
                m1 = self._media(s1)
                m2 = self._media(s2)
                cov = sum((a - m1) * (b - m2) for a, b in zip(s1, s2)) / (n - 1)
                dp1 = self._desvio_padrao(s1, m1)
                dp2 = self._desvio_padrao(s2, m2)
                if dp1 == 0 or dp2 == 0:
                    corr = 0.0
                else:
                    corr = cov / (dp1 * dp2)
                resultados[(t1, t2)] = corr
                resultados[(t2, t1)] = corr
        return resultados

    # ── Relatorio completo ─────────────────────────────────
    def analisar(
        self,
        retornos_map: RetornosMap,
        valor_total_carteira: Optional[float] = None,
    ) -> MetricasCarteira:
        """
        Executa todas as analises e retorna MetricasCarteira.
        """
        serie = self.retorno_carteira(retornos_map)
        n_dias = len(serie)

        ret_acum = self.rentabilidade_acumulada(serie)
        ret_diaria = self._media(serie) * 100
        ret_mensal = ((1.0 + ret_acum) ** (self.DIAS_UTEIS_MES / max(n_dias, 1)) - 1) * 100
        ret_anual = self.rentabilidade_anualizada(ret_acum, n_dias) * 100
        vol = self.volatilidade_anual(serie) * 100
        sharpe = self.sharpe_ratio(serie)
        sortino = self.sortino_ratio(serie)
        mdd = self.max_drawdown(serie) * 100
        var95 = self.var_historico(serie) * 100
        correlacoes = self.matriz_correlacao(retornos_map)

        detalhes: Dict[str, Dict[str, float]] = {}
        for ticker, ativo in self.ativos.items():
            detalhes[ticker] = {
                "peso": self.pesos.get(ticker, 0.0) * 100,
                "valor": ativo.valor_posicao,
                "classe": ativo.classe,
                "resultado_abs": ativo.resultado,
                "resultado_pct": (
                    (ativo.resultado / max(ativo.valor_posicao - ativo.resultado, 1e-9)) * 100
                    if ativo.custo_medio > 0
                    else 0.0
                ),
            }

        return MetricasCarteira(
            rentabilidade_diaria=ret_diaria,
            rentabilidade_mensal=ret_mensal,
            rentabilidade_anual=ret_anual,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=mdd,
            volatilidade_anual=vol,
            var_95_diario=var95,
            correlacoes=correlacoes,
            detalhes_ativos=detalhes,
        )

    def formatar_relatorio(self, metricas: MetricasCarteira) -> str:
        """Formata as metricas como relatorio legivel."""
        linhas: List[str] = []
        linhas.append("=" * 60)
        linhas.append("        RELATORIO DE ANALISE DA CARTEIRA")
        linhas.append("=" * 60)
        linhas.append("")
        linhas.append("--- Composicao da Carteira ---")
        for ticker, det in metricas.detalhes_ativos.items():
            ativo = self.ativos[ticker]
            linhas.append(
                f"  {ticker:<12} | {det['classe']:<12} "
                f"| Peso: {det['peso']:6.1f}% | "
                f"Valor: R$ {det['valor']:>12,.2f} | "
                f"P&L: R$ {det['resultado_abs']:>10,.2f} ({det['resultado_pct']:+.1f}%)"
            )
        linhas.append("")
        linhas.append("--- Metricas de Retorno ---")
        linhas.append(f"  Rentabilidade Diaria:      {metricas.rentabilidade_diaria:+.3f}%")
        linhas.append(f"  Rentabilidade Mensal:      {metricas.rentabilidade_mensal:+.3f}%")
        linhas.append(f"  Rentabilidade Anual:       {metricas.rentabilidade_anual:+.3f}%")
        linhas.append("")
        linhas.append("--- Metricas de Risco ---")
        linhas.append(f"  Volatilidade Anual:        {metricas.volatilidade_anual:.3f}%")
        linhas.append(f"  Indice de Sharpe:          {metricas.sharpe_ratio:.3f}")
        linhas.append(f"  Indice de Sortino:         {metricas.sortino_ratio:.3f}")
        linhas.append(f"  Maximo Drawdown:           {metricas.max_drawdown:.3f}%")
        linhas.append(f"  VaR Historico (95%):       {metricas.var_95_diario:.3f}%")
        linhas.append("")
        linhas.append("--- Matriz de Correlacao ---")
        tickers = sorted(self.ativos.keys())
        header = f"{'':>10}" + "".join(f"{t:>10}" for t in tickers)
        linhas.append(header)
        for t1 in tickers:
            row = f"{t1:>10}"
            for t2 in tickers:
                corr = metricas.correlacoes.get((t1, t2), 0.0)
                row += f"{corr:>10.3f}"
            linhas.append(row)
        linhas.append("")
        linhas.append("=" * 60)
        return "\n".join(linhas)


# ──────────────────────────────────────────────────────────────
#  Demo
# ──────────────────────────────────────────────────────────────
def _gerar_retornos_demo() -> Tuple[List[Ativo], RetornosMap]:
    """
    Gera dados demo de retornos diarios simulados para ativos
    brasileiros tipicos.
    """
    import random

    random.seed(42)
    n_dias = 252  # 1 ano util

    # Retornos medios diarios e volatilidades aproximadas
    params: Dict[str, Tuple[float, float, str]] = {
        "PETR4":      (0.0006, 0.022, "acoes"),       # Petrobras ON
        "VALE3":      (0.0004, 0.025, "acoes"),       # Vale ON
        "ITUB4":      (0.0005, 0.018, "acoes"),       # Itau PN
        "BBDC4":      (0.0003, 0.020, "acoes"),       # Bradesco PN
        "ABEV3":      (0.0002, 0.015, "acoes"),       # Ambev ON
        "TesouroIPCA":(0.0003, 0.006, "renda_fixa"),  # Tesouro IPCA+
        "CDB_120":    (0.0004, 0.003, "renda_fixa"),  # CDB 120% CDI
        "LCI_95":     (0.00035, 0.002, "renda_fixa"), # LCI 95% CDI
        "HGLG11":     (0.0003, 0.010, "fii"),         # FII HGLG11
        "MXRF11":     (0.0002, 0.008, "fii"),         # FII MXRF11
    }

    ativos = []
    retornos_map: RetornosMap = {}
    precos: Dict[str, float] = {
        "PETR4": 38.50, "VALE3": 62.30, "ITUB4": 33.80,
        "BBDC4": 14.90, "ABEV3": 13.20, "TesouroIPCA": 1050.00,
        "CDB_120": 100.0, "LCI_95": 100.0, "HGLG11": 101.50, "MXRF11": 10.30,
    }
    custos: Dict[str, float] = {
        "PETR4": 35.20, "VALE3": 58.00, "ITUB4": 31.50,
        "BBDC4": 15.10, "ABEV3": 12.80, "TesouroIPCA": 1020.00,
        "CDB_120": 100.0, "LCI_95": 100.0, "HGLG11": 98.00, "MXRF11": 10.10,
    }
    quantidades: Dict[str, float] = {
        "PETR4": 200, "VALE3": 100, "ITUB4": 150,
        "BBDC4": 300, "ABEV3": 200, "TesouroIPCA": 5,
        "CDB_120": 10, "LCI_95": 10, "HGLG11": 50, "MXRF11": 200,
    }

    for ticker, (mu, sigma, classe) in params.items():
        retornos = [random.gauss(mu, sigma) for _ in range(n_dias)]
        retornos_map[ticker] = retornos
        ativos.append(Ativo(
            ticker=ticker,
            preco_atual=precos[ticker],
            quantidade=quantidades[ticker],
            classe=classe,
            retornos_diarios=retornos,
            custo_medio=custos[ticker],
        ))

    return ativos, retornos_map


def main() -> None:
    """Demonstracao do analisador de carteiras com dados simulados."""
    print()
    print("  Gestora de Investimentos - Analisador de Carteiras")
    print("  " + "-" * 52)
    print()

    ativos, retornos_map = _gerar_retornos_demo()

    # Pesos fixos para a demo
    pesos: PesoMap = {
        "PETR4":       0.12,
        "VALE3":       0.10,
        "ITUB4":       0.12,
        "BBDC4":       0.08,
        "ABEV3":       0.06,
        "TesouroIPCA": 0.18,
        "CDB_120":     0.12,
        "LCI_95":      0.08,
        "HGLG11":      0.08,
        "MXRF11":      0.06,
    }

    analyzer = PortfolioAnalyzer(ativos=ativos, pesos=pesos)
    metricas = analyzer.analizar(retornos_map)
    relatorio = analyzer.formatar_relatorio(metricas)

    print(relatorio)

    # Interpretacao rapida
    print()
    print("--- Interpretacao Rapida ---")
    if metricas.sharpe_ratio > 1.0:
        print("  [BOM] Sharpe > 1.0: relacao retorno/risco adequada.")
    elif metricas.sharpe_ratio > 0.5:
        print("  [MEDIO] Sharpe entre 0.5 e 1.0: pode melhorar.")
    else:
        print("  [ATENCAO] Sharpe < 0.5: retorno nao compensa o risco.")

    if metricas.sortino_ratio > metricas.sharpe_ratio:
        print("  O Sortino maior que Sharpe indica que o risco "
              "concentra-se em movimientos positivos.")
    else:
        print("  Sortino <= Sharpe indica riscos de queda consistentes.")

    if metricas.max_drawdown > -15:
        print("  Drawdown controlado (< 15%).")
    elif metricas.max_drawdown > -30:
        print("  Drawdown moderado (15-30%). Atencao com alavancagem.")
    else:
        print("  Drawdown severo (>30%). Revisao de alocacao recomendada.")

    print()


if __name__ == "__main__":
    main()
