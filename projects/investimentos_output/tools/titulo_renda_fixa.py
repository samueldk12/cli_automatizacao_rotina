"""
Calculadora de Titulos de Renda Fixa
======================================
Calcula rendimentos brutos e liquidos de titulos brasileiros considerando
IR (tabela regressiva), IOF e inflacao.

Departamentos: analise_mercado, gestao_portfolios.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from datetime import date
from typing import Dict, List, Optional, Tuple


# ------------------------------------------------------------------
#  Constantes fiscais
# ------------------------------------------------------------------

# Tabela regressiva de IR para renda fixa (exceto isentos)
#   ate 180 dias ........ 22.5%
#   181 a 360 dias ...... 20%
#   361 a 720 dias ...... 17.5%
#   acima de 720 dias ... 15%
TABELA_IR_REGRESSIVA: List[Tuple[int, float]] = [
    (180, 0.225),
    (360, 0.200),
    (720, 0.175),
    (99999, 0.150),
]

IOF_PONTO_BASE = 0.0038  # aliquota maxima D+1


def aliquota_ir_dias(dias_corridos: int) -> float:
    """Retorna aliquota de IR conforme dias corridos do investimento."""
    for limite, aliquota in TABELA_IR_REGRESSIVA:
        if dias_corridos <= limite:
            return aliquota
    return 0.15


def aliquota_iof_dias(dias_corridos: int) -> float:
    """IOF: decae linearmente entre D+1 e D+30, depois e zero."""
    if dias_corridos <= 0 or dias_corridos > 30:
        return 0.0
    return IOF_PONTO_BASE * (1.0 - (dias_corridos - 1) / 30.0)


# ------------------------------------------------------------------
#  Enumeracoes e dataclasses
# ------------------------------------------------------------------

class TipoTitulo(Enum):
    TESOURO_SELIC = "Tesouro Selic"
    TESOURO_PREFIXADO = "Tesouro Prefixado"
    TESOURO_IPCA = "Tesouro IPCA+"
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    DEBENTURE = "Debenture"
    CRI_CRA = "CRI/CRA"


@dataclass
class ResultadoCalculo:
    """Resultado do calculo de um titulo de renda fixa."""
    titulo: str
    tipo: TipoTitulo
    prazo_dias: int
    valor_aplicado: float
    rentabilidade_bruta: float
    valor_bruto_final: float
    desconto_iof: float
    aliquota_ir_percent: float
    desconto_ir: float
    valor_liquido_final: float
    rentabilidade_liquida_pct: float
    taxa_real_anual: Optional[float] = None
    observacoes: str = ""

    @property
    def imposto_total(self) -> float:
        return self.desconto_ir + self.desconto_iof

    @property
    def custo_tributario_pct(self) -> float:
        if self.rentabilidade_bruta <= 0:
            return 0.0
        return (self.imposto_total / self.rentabilidade_bruta) * 100


# ------------------------------------------------------------------
#  Classe principal
# ------------------------------------------------------------------

class RendaFixaCalculator:
    """
    Calculadora de rendimentos para titulos de renda fixa brasileiros.

    Considera IR regressivo, IOF (para os primeiros 30 dias) e
    inflacao (IPCA estimado) para calculo da taxa real.
    """

    # Isentos de IR: LCI, LCA, CRI/CRA
    ISENTOS_IR: set[TipoTitulo] = {TipoTitulo.LCI, TipoTitulo.LCA, TipoTitulo.CRI_CRA}

    def __init__(
        self,
        taxa_selic_anual: float = 0.1050,
        taxa_ipca_anual: float = 0.0450,
        data_base: Optional[date] = None,
    ) -> None:
        self.selic = taxa_selic_anual
        self.ipca = taxa_ipca_anual
        self.data_base = data_base or date.today()
        self._selic_di = (1.0 + self.selic) ** (1.0 / 252) - 1.0

    # ── Conversoes de taxa ──────────────────────────────────
    @staticmethod
    def taxa_anual_para_diaria(taxa_anual: float) -> float:
        """Converte taxa anual para diaria (base 252 dias uteis)."""
        return (1.0 + taxa_anual) ** (1.0 / 252) - 1.0

    @staticmethod
    def taxa_para_dias(taxa_anual: float, dias_corridos: int) -> float:
        """Rendimento acumulado (fator-1) para N dias corridos."""
        if dias_corridos == 0:
            return 0.0
        dias_uteis = int(dias_corridos / 365 * 252)
        if dias_uteis == 0:
            dias_uteis = 1
        return (1.0 + taxa_anual) ** (dias_uteis / 252) - 1.0

    def _isento_ir(self, tipo: TipoTitulo) -> bool:
        return tipo in self.ISENTOS_IR

    # ── Calculos individuais ────────────────────────────────
    def _calcular_bruto(
        self,
        tipo: TipoTitulo,
        valor: float,
        dias: int,
        taxa: float,
        taxa_ipca: float,
    ) -> float:
        """Calcula o rendimento bruto conforme tipo de titulo."""
        if tipo == TipoTitulo.TESOURO_SELIC:
            fator = (1.0 + self.selic) ** (dias / 252)
            return valor * fator - valor

        elif tipo == TipoTitulo.TESOURO_PREFIXADO:
            fator = (1.0 + taxa) ** (dias / 252)
            return valor * fator - valor

        elif tipo == TipoTitulo.TESOURO_IPCA:
            selic_f = (1.0 + self.selic) ** (dias / 252)
            ipca_f = (1.0 + taxa_ipca) ** (dias / 365)
            fator = selic_f * ipca_f
            return valor * fator - valor

        elif tipo in (TipoTitulo.CDB,):
            # taxa e o percentual do CDI/SELIC (ex: 120% = 1.2)
            taxa_efetiva = taxa * self.selic
            fator = (1.0 + taxa_efetiva) ** (dias / 252)
            return valor * fator - valor

        elif tipo == TipoTitulo.DEBENTURE:
            fator = (1.0 + taxa) ** (dias / 252)
            return valor * fator - valor

        else:
            # LCI, LCA, CRI/CRA: taxa direta
            fator = (1.0 + taxa) ** (dias / 252)
            return valor * fator - valor

    def calcular(
        self,
        tipo: TipoTitulo,
        valor: float,
        dias: int,
        taxa: float = 0.0,
        taxa_ipca: Optional[float] = None,
        descricao: str = "",
    ) -> ResultadoCalculo:
        """
        Calcula rendimento bruto e liquido de um titulo.

        Parametros:
            tipo         – TipoTitulo
            valor        – Valor aplicado (R$)
            dias         – Prazo em dias corridos
            taxa         – Taxa anual ou multiplicador do CDI (para CDB)
            taxa_ipca    – IPCA anual estimado (usado apenas Tesouro IPCA+)
            descricao    – Rotulo legivel
        """
        ipca_usado = taxa_ipca if taxa_ipca is not None else self.ipca

        if tipo in (TipoTitulo.TESOURO_IPCA, TipoTitulo.DEBENTURE):
            if taxa == 0:
                raise ValueError("Informe a taxa para este tipo de titulo.")
        desc = descricao or tipo.value

        bruto = self._calcular_bruto(tipo, valor, dias, taxa, ipca_usado)
        valor_bruto = valor + bruto

        # IOF (somente nos primeiros 30 dias, nao se aplica a LCI/LCA/CRI/CRA)
        iof = 0.0
        if not self._isento_ir(tipo):
            iof_rate = aliquota_iof_dias(dias)
            if iof_rate > 0:
                iof = bruto * iof_rate
        bruto_apos_iof = bruto - iof

        # IR
        aliquota = 0.0
        ir = 0.0
        if not self._isento_ir(tipo):
            aliquota = aliquota_ir_dias(dias)
            ir = bruto_apos_iof * aliquota

        valor_liquido = valor_bruto - iof - ir
        ret_liquid_pct = ((valor_liquido - valor) / valor) * 100 if valor > 0 else 0.0

        # Taxa real (descontando inflacao)
        taxa_real = None
        if ipca_usado > 0:
            fator_bruto = valor_bruto / valor if valor > 0 else 1.0
            fator_inflacao = (1.0 + ipca_usado) ** (dias / 365)
            if fator_inflacao > 0:
                taxa_real = ((fator_bruto / fator_inflacao) - 1) * 100

        observacoes = ""
        if self._isento_ir(tipo):
            observacoes = "Isento de IR"

        return ResultadoCalculo(
            titulo=desc,
            tipo=tipo,
            prazo_dias=dias,
            valor_aplicado=valor,
            rentabilidade_bruta=bruto,
            valor_bruto_final=valor_bruto,
            desconto_iof=iof,
            aliquota_ir_percent=aliquota * 100,
            desconto_ir=ir,
            valor_liquido_final=valor_liquido,
            rentabilidade_liquida_pct=ret_liquid_pct,
            taxa_real_anual=taxa_real,
            observacoes=observacoes,
        )

    # ── Comparacao entre opcoes ─────────────────────────────
    def comparar_opcoes(
        self,
        valor: float,
        dias: int,
        opcoes: List[Dict],
    ) -> List[ResultadoCalculo]:
        """
        Compara varias opcoes de investimento.

        Cada opcao e um dicionario com:
            tipo, taxa, descricao (opcional), taxa_ipca (opcional)

        Exemplo:
            {"tipo": TipoTitulo.CDB, "taxa": 1.15, "descricao": "CDB 115% CDI"}
        """
        resultados = []
        for op in opcoes:
            r = self.calcular(
                tipo=op["tipo"],
                valor=valor,
                dias=dias,
                taxa=op.get("taxa", self.selic),
                taxa_ipca=op.get("taxa_ipca"),
                descricao=op.get("descricao", ""),
            )
            resultados.append(r)
        return resultados

    @staticmethod
    def formatar_relatorio_comparativo(resultados: List[ResultadoCalculo]) -> str:
        """Formata comparacao entre opcoes como tabela legivel."""
        linhas: List[str] = []
        linhas.append("")
        linhas.append("=" * 95)
        linhas.append(f"  {'Tipo/Titulo':<28} {'Bruto(R$)':>12} {'IR%':>6} {'IR(R$)':>10} "
                      "{'Liq(R$)':>12} {'Liq%':>8} {'TaxaReal%':>10}")
        linhas.append("  " + "-" * 93)

        for r in sorted(resultados, key=lambda x: x.valor_liquido_final, reverse=True):
            aliq = f"{r.aliquota_ir_percent:.1f}" if r.desconto_ir > 0 else "ISENTO"
            real = f"{r.taxa_real_anual:+.2f}" if r.taxa_real_anual is not None else "N/A"
            linhas.append(
                f"  {r.titulo:<28} {r.valor_bruto_final:>12,.2f} {aliq:>6s} "
                f"{r.desconto_ir:>10,.2f} {r.valor_liquido_final:>12,.2f} "
                f"{r.rentabilidade_liquida_pct:>7.2f}% {real:>10s}"
            )
        linhas.append("  " + "-" * 93)

        if resultados:
            melhor = max(resultados, key=lambda x: x.valor_liquido_final)
            linhas.append(f"\n  >>> Melhor opcao: {melhor.titulo} "
                          f"(R$ {melhor.valor_liquido_final:,.2f} liquido)")
        linhas.append("=" * 95)
        return "\n".join(linhas)

    def formatar_detalhe(self, r: ResultadoCalculo) -> str:
        """Detalhamento individual de um titulo."""
        linhas = [
            "",
            f"  Titulo: {r.titulo}",
            f"  Valor aplicado:      R$ {r.valor_aplicado:>12,.2f}",
            f"  Prazo:                {r.prazo_dias} dias corridos",
            f"  Rend. bruto:         R$ {r.rentabilidade_bruta:>12,.2f}",
            f"  Valor bruto:         R$ {r.valor_bruto_final:>12,.2f}",
        ]
        if r.desconto_iof > 0:
            linhas.append(f"  IOF:                 R$ {r.desconto_iof:>12,.2f}")
        if r.desconto_ir > 0:
            linhas.append(f"  IR ({r.aliquota_ir_percent:.1f}%):       R$ {r.desconto_ir:>12,.2f}")
        linhas.append(f"  Valor liquido final: R$ {r.valor_liquido_final:>12,.2f}")
        linhas.append(f"  Rentabilidade liq:   {r.rentabilidade_liquida_pct:+.2f}%")
        if r.taxa_real_anual is not None:
            linhas.append(f"  Taxa real (vs IPCA): {r.taxa_real_anual:+.2f}%")
        if r.observacoes:
            linhas.append(f"  Obs: {r.observacoes}")
        return "\n".join(linhas)


# ------------------------------------------------------------------
#  Demo
# ------------------------------------------------------------------

def main() -> None:
    """Demonstracao com comparacao de opcoes de renda fixa."""
    print()
    print("  Gestora de Investimentos - Calculadora Renda Fixa")
    print("  " + "-" * 50)
    print()

    calc = RendaFixaCalculator(
        taxa_selic_anual=0.1050,   # Selic 10.50% a.a.
        taxa_ipca_anual=0.0450,    # IPCA estimado 4.50% a.a.
    )

    valor = 50_000.0
    dias = 720  # ~2 anos

    opcoes = [
        {"tipo": TipoTitulo.TESOURO_SELIC,
         "descricao": "Tesouro Selic 2029"},
        {"tipo": TipoTitulo.TESOURO_PREFIXADO,
         "taxa": 0.115,
         "descricao": "Tesouro Prefixado 2029 (11.5%)"},
        {"tipo": TipoTitulo.TESOURO_IPCA,
         "taxa": 0.055,
         "descricao": "Tesouro IPCA+ 2029 (IPCA+5.5%)"},
        {"tipo": TipoTitulo.CDB,
         "taxa": 1.25,
         "descricao": "CDB 125% CDI"},
        {"tipo": TipoTitulo.CDB,
         "taxa": 1.00,
         "descricao": "CDB 100% CDI"},
        {"tipo": TipoTitulo.LCI,
         "taxa": 0.090,
         "descricao": "LCI 90% CDI (isenta IR)"},
        {"tipo": TipoTitulo.LCA,
         "taxa": 0.092,
         "descricao": "LCA 92% CDI (isenta IR)"},
        {"tipo": TipoTitulo.DEBENTURE,
         "taxa": 0.130,
         "descricao": "Debenture Incentivada IPCA+6%"},
    ]

    resultados = calc.comparar_opcoes(valor=valor, dias=dias, opcoes=opcoes)
    texto = calc.formatar_relatorio_comparativo(resultados)
    print(texto)

    # Detalhe do Tesouro IPCA+
    ipc_res = calc.calcular(
        tipo=TipoTitulo.TESOURO_IPCA,
        valor=valor,
        dias=dias,
        taxa=0.055,
        descricao="Tesouro IPCA+ 2029",
    )
    print("\n  Detalhe — Tesouro IPCA+ 2029")
    print(calc.formatar_detalhe(ipc_res))

    # Detalhe da LCI
    lci_res = calc.calcular(
        tipo=TipoTitulo.LCI,
        valor=valor,
        dias=dias,
        taxa=0.090,
        descricao="LCI 90% CDI",
    )
    print("\n  Detalhe — LCI 90% CDI")
    print(calc.formatar_detalhe(lci_res))

    print()


if __name__ == "__main__":
    main()
