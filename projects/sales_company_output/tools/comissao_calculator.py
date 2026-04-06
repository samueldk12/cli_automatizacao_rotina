"""
Calculadora de Comissoes - Empresa de Vendas
===============================================
Calcula comissoes de vendas com taxas tieradas, bonus
de equipes, metas mensais/trimestrais e aceleradores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Periodicidade(Enum):
    """Periodo de calculo da comissao."""
    MENSAL = "Mensal"
    TRIMESTRAL = "Trimestral"
    ANUAL = "Anual"


@dataclass
class Venda:
    """Representa uma venda individual."""
    id_venda: str
    vendedor: str
    valor: float
    data_venda: str = ""
    produto: str = ""
    margem: float = 0.0  # percentual de margem
    custo: float = 0.0

    @property
    def lucro(self) -> float:
        return self.valor - self.custo

    def __str__(self) -> str:
        return (
            f"[{self.id_venda}] R$ {self.valor:,.2f} | "
            f"{self.vendedor} | {self.produto}"
        )


@dataclass
class TierComissao:
    """Faixa (tier) de calculo de comissao."""
    limite_minimo: float
    limite_maximo: float  # None = sem limite
    percentual: float  # taxa de comissao
    descricao: str = ""


@dataclass
class ResultadoComissao:
    """Resultado do calculo de comissao para um vendedor."""
    vendedor: str
    periodo: str = ""
    vendas: list[Venda] = field(default_factory=list)
    total_vendas: float = 0.0
    meta: float = 0.0
    atingimento_meta: float = 0.0
    comissao_base: float = 0.0
    comissao_acelerador: float = 0.0
    bonus_equipe: float = 0.0
    comissao_total: float = 0.0
    detalhamento: list[str] = field(default_factory=list)

    def resumo(self) -> str:
        """Gera resumo da comissao."""
        linhas = [
            f"Vendedor: {self.vendedor}",
            f"Periodo: {self.periodo}",
            f"Total vendas: R$ {self.total_vendas:,.2f}",
            f"Meta: R$ {self.meta:,.2f}",
            f"Atingimento: {self.atingimento_meta:.1f}%",
            f"Comissao base: R$ {self.comissao_base:,.2f}",
            f"Acelerador: R$ {self.comissao_acelerador:,.2f}",
            f"Bonus equipe: R$ {self.bonus_equipe:,.2f}" if self.bonus_equipe > 0 else "",
            f"TOTAL COMISSAO: R$ {self.comissao_total:,.2f}",
        ]
        if self.detalhamento:
            linhas.append("\nDetalhamento:")
            for d in self.detalhamento:
                linhas.append(f"  {d}")

        return "\n".join(linha for linha in linhas if linha)


@dataclass
class ConfigComissao:
    """Configuracao do plano de comissoes."""
    tiers: list[TierComissao] = field(default_factory=lambda: [
        TierComissao(0, 50_000, 0.05, "Ate R$ 50k - 5%"),
        TierComissao(50_000, 100_000, 0.08, "R$ 50k-100k - 8%"),
        TierComissao(100_000, float("inf"), 0.12, "Acima de R$ 100k - 12%"),
    ])
    meta_mensal: float = 100_000.0
    meta_trimestral: float = 300_000.0
    taxa_acelerador: float = 1.5  # multiplicador acima de 100% da meta
    bonus_equipe_percentual: float = 0.02  # bonus se equipe toda bater meta
    minimo_venda: float = 0.0  # comissao minima por venda

    def adicionar_tier(
        self,
        min_valor: float,
        max_valor: float,
        percentual: float,
        descricao: str = "",
    ) -> None:
        self.tiers.append(
            TierComissao(
                limite_minimo=min_valor,
                limite_maximo=max_valor,
                percentual=percentual,
                descricao=descricao,
            )
        )

    def get_tier_ativo(self, valor_acumulado: float) -> TierComissao:
        """Retorna o tier ativo baseado no valor acumulado."""
        tiers_ordenados = sorted(self.tiers, key=lambda t: t.limite_minimo)

        for tier in tiers_ordenados:
            if tier.limite_minimo <= valor_acumulado < tier.limite_maximo:
                return tier

        # Se passou de todos os limites, retorna o ultimo tier
        return tiers_ordenados[-1]


class ComissaoCalculator:
    """Calculadora de comissoes de vendas."""

    def __init__(self, config: Optional[ConfigComissao] = None) -> None:
        self.config = config or ConfigComissao()
        self.vendas: list[Venda] = []
        self.resultados: list[ResultadoComissao] = []

    def registrar_venda(self, venda: Venda) -> None:
        """Registra uma nova venda."""
        self.vendas.append(venda)

    def calcular_comissao_tierada(self, vendedor: str) -> float:
        """
        Calcula comissao por faixas (tiers).

        Exemplo:
        - 5% nas primeiras R$ 50k
        - 8% de R$ 50k ate R$ 100k
        - 12% acima de R$ 100k
        """
        vendas_vendedor = [v for v in self.vendas if v.vendedor == vendedor]
        total = sum(v.valor for v in vendas_vendedor)

        comissao = 0.0
        tiers_ordenados = sorted(self.config.tiers, key=lambda t: t.limite_minimo)

        valor_restante = total

        for i, tier in enumerate(tiers_ordenados):
            if valor_restante <= 0:
                break

            faixa_tier = tier.limite_maximo - tier.limite_minimo

            if i == 0:
                # Primeira faixa: calcula do zero
                valor_na_faixa = min(valor_restante, tier.limite_maximo)
            else:
                # Facas subsequentes: calcula ate o limite da faixa
                anterior = tiers_ordenados[i - 1].limite_maximo
                if total <= anterior:
                    break
                valor_na_faixa = min(valor_restante, faixa_tier)

            comissao += valor_na_faixa * tier.percentual
            valor_restante -= valor_na_faixa

            # Debug
            if tier.limite_maximo == float("inf"):
                faixa_str = f"Acima de {tier.limite_minimo:,.0f}"
            else:
                faixa_str = f"{tier.limite_minimo:,.0f} - {tier.limite_maximo:,.0f}"

        return comissao

    def calcular_acelerador(self, vendedor: str) -> float:
        """
        Calcula bonus acelerador para vendas acima da meta.

        Se o vendedor atingiu 100%+ da meta, as vendas acima
        recebem taxa acelerada (ex: 1.5x a taxa base).
        """
        vendas_vendedor = [v for v in self.vendas if v.vendedor == vendedor]
        total = sum(v.valor for v in vendas_vendedor)
        meta = self.config.meta_mensal

        if total <= meta:
            return 0.0

        # Valor acima da meta
        excedente = total - meta

        # Encontra taxa do tier onde esta o excedente
        tier = self.config.get_tier_ativo(meta)
        comissao_extra = excedente * tier.percentual

        # Aplica acelerador
        acelerador = comissao_extra * (self.config.taxa_acelerador - 1)

        return acelerador

    def calcular_bonus_equipe(self, vendedores: list[str]) -> dict[str, float]:
        """
        Calcula bonus de equipe se todos baterem a meta.

        Returns:
            Dict {vendedor: valor_bonus}
        """
        todos_na_meta = True
        vendas_por_vendedor: dict[str, float] = {}

        for vendedor in vendedores:
            total = sum(
                v.valor for v in self.vendas if v.vendedor == vendedor
            )
            vendas_por_vendedor[vendedor] = total

            if total < self.config.meta_mensal:
                todos_na_meta = False

        if not todos_na_meta:
            return {v: 0.0 for v in vendedores}

        # Bonus: percentual sobre vendas de cada um
        return {
            v: vendas * self.config.bonus_equipe_percentual
            for v, vendas in vendas_por_vendedor.items()
        }

    def calcular_comissao_completa(
        self,
        vendedor: str,
        periodo: str = "",
    ) -> ResultadoComissao:
        """
        Calcula comissao completa com tiers, acelerador e bonus.

        Args:
            vendedor: Nome/Codigo do vendedor.
            periodo: Identificacao do periodo.

        Returns:
            ResultadoComissao com calculo completo.
        """
        vendas_vendedor = [v for v in self.vendas if v.vendedor == vendedor]

        total_vendas = sum(v.valor for v in vendas_vendedor)
        meta = self.config.meta_mensal
        atingimento = (total_vendas / meta) * 100 if meta > 0 else 0

        # Comissao base (tierada)
        comissao_base = self.calcular_comissao_tierada(vendedor)

        # Acelerador
        acelerador = self.calcular_acelerador(vendedor)

        resultado = ResultadoComissao(
            vendedor=vendedor,
            periodo=periodo,
            vendas=vendas_vendedor,
            total_vendas=total_vendas,
            meta=meta,
            atingimento_meta=atingimento,
            comissao_base=round(comissao_base, 2),
            comissao_acelerador=round(acelerador, 2),
            comissao_total=round(comissao_base + acelerador, 2),
            detalhamento=[
                f"Vendas registradas: {len(vendas_vendedor)}",
                f"Meta atingida: {atingimento:.1f}%",
                f"Comissao tierada: R$ {comissao_base:,.2f}",
                f"Bonus acelerador: R$ {acelerador:,.2f}",
            ],
        )

        self.resultados.append(resultado)
        return resultado

    def ranking_vendedores(self) -> list[ResultadoComissao]:
        """Ranking de vendedores por comissao total."""
        # Agrupa por vendedor
        vendedores_set = set(v.vendedor for v in self.vendas)

        resultados = []
        for vendedor in vendedores_set:
            resultado = self.calcular_comissao_completa(vendedor)
            resultados.append(resultado)

        return sorted(resultados, key=lambda r: r.comissao_total, reverse=True)

    def relatorio_comissoes(self) -> str:
        """Relatorio completo de comissoes."""
        if not self.vendas:
            return "Nenhuma venda registrada."

        linhas = [
            "=" * 60,
            "RELATORIO DE COMISSOES",
            "=" * 60,
            f"Total de vendas: {len(self.vendas)}",
            f"Valor total vendido: R$ {sum(v.valor for v in self.vendas):,.2f}",
            "-" * 60,
        ]

        vendedores_set = set(v.vendedor for v in self.vendas)
        for vendedor in sorted(vendedores_set):
            vendas_vendedor = [
                v for v in self.vendas if v.vendedor == vendedor
            ]
            total = sum(v.valor for v in vendas_vendedor)
            meta = self.config.meta_mensal
            pct = (total / meta) * 100 if meta > 0 else 0

            barras = "#" * min(int(pct / 2), 50)
            linhas.append(
                f"  {vendedor}: R$ {total:,.2f} ({pct:.0f}% da meta) {barras}"
            )

        linhas.append("-" * 60)
        linhas.append("\nDETALHAMENTO INDIVIDUAL:")

        for res in self.ranking_vendedores():
            linhas.append(f"\n  {res.resumo()}")

        return "\n".join(linhas)


def main() -> None:
    """Demonstracao da Calculadora de Comissoes."""
    print("=" * 60)
    print("CALCULADORA DE COMISSOES - Empresa de Vendas")
    print("=" * 60)

    # Configuracao personalizada
    config = ConfigComissao(
        meta_mensal=100_000.0,
        taxa_acelerador=1.5,
        bonus_equipe_percentual=0.02,
    )
    config.tiers = [
        TierComissao(0, 30_000, 0.05, "Ate R$ 30k - 5%"),
        TierComissao(30_000, 70_000, 0.08, "R$ 30k-70k - 8%"),
        TierComissao(70_000, float("inf"), 0.12, "Acima de R$ 70k - 12%"),
    ]

    calc = ComissaoCalculator(config)

    # Registrar vendas
    print("\n--- Registrando Vendas ---")
    vendas = [
        Venda("V001", "Joao Silva", 25_000.0, produto="ERP Basico"),
        Venda("V002", "Maria Santos", 45_000.0, produto="CRM Premium"),
        Venda("V003", "Joao Silva", 35_000.0, produto="Suporte Anual"),
        Venda("V004", "Pedro Costa", 30_000.0, produto="Consultoria"),
        Venda("V005", "Maria Santos", 55_000.0, produto="ERP Completo"),
        Venda("V006", "Maria Santos", 40_000.0, produto="Treinamento"),
        Venda("V007", "Pedro Costa", 25_000.0, produto="Modulo BI"),
        Venda("V008", "Joao Silva", 50_000.0, produto="Projeto Custom"),
    ]

    for venda in vendas:
        calc.registrar_venda(venda)
        print(f"  {venda}")

    # Calculos individuais
    print("\n--- Comissoes Individuais ---")
    for vendedor in ["Joao Silva", "Maria Santos", "Pedro Costa"]:
        resultado = calc.calcular_comissao_completa(vendedor, "Abril/2026")
        print(f"\n{resultado.resumo()}")

    # Bonus de equipe
    print("\n--- Bonus de Equipe ---")
    bonus = calc.calcular_bonus_equipe([
        "Joao Silva", "Maria Santos", "Pedro Costa"
    ])
    for vendedor, valor in bonus.items():
        if valor > 0:
            print(f"  {vendedor}: R$ {valor:,.2f} (bonus equipe)")
        else:
            print(f"  {vendedor}: Sem bonus de equipe")

    # Ranking
    print("\n--- Ranking por Comissao ---")
    for i, res in enumerate(calc.ranking_vendedores(), 1):
        print(f"  {i}o lugar: {res.vendedor} - R$ {res.comissao_total:,.2f}")

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
