"""
Tax Calculator for Brazilian Tax System
Calculates IRPF, IRPJ, CSLL, PIS, COFINS, ICMS, and ISS
Supports Simples Nacional, Lucro Presumido, and Lucro Real regimes.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import date


class TaxRegime(Enum):
    SIMPLES_NACIONAL = "Simples Nacional"
    LUCRO_PRESUMIDO = "Lucro Presumido"
    LUCRO_REAL = "Lucro Real"


class PessoaType(Enum):
    PESSOA_FISICA = "Pessoa Fisica"
    PESSOA_JURIDICA = "Pessoa Juridica"


@dataclass
class TaxBracket:
    min_income: float
    max_income: float
    rate: float
    deduction: float


@dataclass
class TaxResult:
    tax_name: str
    base_calculation: float
    rate: float
    amount: float
    description: str


@dataclass
class TaxSummary:
    company_name: str
    regime: TaxRegime
    reference_month: str
    gross_revenue: float
    taxes: list = field(default_factory=list)
    total_taxes: float = 0.0
    effective_rate: float = 0.0

    def add_tax(self, tax: TaxResult):
        self.taxes.append(tax)
        self.total_taxes = sum(t.amount for t in self.taxes)
        self.effective_rate = (self.total_taxes / self.gross_revenue * 100) if self.gross_revenue > 0 else 0

    def to_dict(self) -> dict:
        return {
            "empresa": self.company_name,
            "regime": self.regime.value,
            "mes_referencia": self.reference_month,
            "receita_bruta": f"R$ {self.gross_revenue:,.2f}",
            "total_impostos": f"R$ {self.total_taxes:,.2f}",
            "aliquota_efetiva": f"{self.effective_rate:.2f}%",
            "impostos": [
                {
                    "nome": t.tax_name,
                    "base_calculo": f"R$ {t.base_calculation:,.2f}",
                    "aliquota": f"{t.rate:.2f}%",
                    "valor": f"R$ {t.amount:,.2f}",
                    "descricao": t.description,
                }
                for t in self.taxes
            ],
        }


# IRPF 2024 table (monthly)
IRPF_BRACKETS = [
    TaxBracket(0, 2259.20, 0.0, 0.0),
    TaxBracket(2259.21, 2826.65, 0.075, 169.44),
    TaxBracket(2826.66, 3751.05, 0.15, 381.44),
    TaxBracket(3751.06, 4664.68, 0.225, 662.77),
    TaxBracket(4664.69, float("inf"), 0.275, 896.00),
]

# IRPJ - Lucro Presumido rates
IRPJ_RATE = 0.15
IRPJ_ADDITIONAL_RATE = 0.10
IRPJ_ADDITIONAL_THRESHOLD = 20000.0  # per month

# CSLL rate
CSLL_RATE = 0.09

# PIS rate (Lucro Presumido/Real - cumulativo vs nao-cumulativo)
PIS_CUMULATIVE = 0.0065
PIS_NON_CUMULATIVE = 0.0165

# COFINS rates
COFINS_CUMULATIVE = 0.03
COFINS_NON_CUMULATIVE = 0.076

# Presumed profit margins for Lucro Presumido
PRESUMED_MARGIN_SERVICES = 0.32
PRESUMED_MARGIN_COMMERCE = 0.08
PRESUMED_MARGIN_INDUSTRY = 0.08


class TaxCalculator:
    """Calculates all Brazilian taxes based on regime and revenue."""

    def __init__(
        self,
        company_name: str,
        regime: TaxRegime,
        gross_revenue: float,
        activity_type: str = "servicos",
        reference_month: Optional[str] = None,
    ):
        self.company_name = company_name
        self.regime = regime
        self.gross_revenue = gross_revenue
        self.activity_type = activity_type
        self.reference_month = reference_month or date.today().strftime("%B/%Y")
        self.summary = TaxSummary(
            company_name=company_name,
            regime=regime,
            reference_month=self.reference_month,
            gross_revenue=gross_revenue,
        )

    def calculate_all(self) -> TaxSummary:
        if self.regime == TaxRegime.LUCRO_PRESUMIDO:
            self._calc_lucro_presumido()
        elif self.regime == TaxRegime.LUCRO_REAL:
            self._calc_lucro_real()
        elif self.regime == TaxRegime.SIMPLES_NACIONAL:
            self._calc_simples_nacional()
        return self.summary

    def _calc_lucro_presumido(self):
        presumed_margin = (
            PRESUMED_MARGIN_SERVICES
            if self.activity_type == "servicos"
            else PRESUMED_MARGIN_COMMERCE
        )
        presumed_profit = self.gross_revenue * presumed_margin

        # IRPJ (15%)
        irpj_base = presumed_profit
        irpj = irpj_base * IRPJ_RATE
        additional = max(0, (presumed_profit - IRPJ_ADDITIONAL_THRESHOLD)) * IRPJ_ADDITIONAL_RATE
        irpj += additional
        self.summary.add_tax(TaxResult(
            tax_name="IRPJ",
            base_calculation=irpj_base,
            rate=IRPJ_RATE * 100 + (10.0 if additional > 0 else 0),
            amount=irpj,
            description=f"IR sobre lucro presumido (margem {presumed_margin*100:.0f}%) + adicional",
        ))

        # CSLL (9%)
        csll = presumed_profit * CSLL_RATE
        self.summary.add_tax(TaxResult(
            tax_name="CSLL",
            base_calculation=presumed_profit,
            rate=CSLL_RATE * 100,
            amount=csll,
            description="Contribuicao Social sobre o Lucro Liquido",
        ))

        # PIS cumulativo (0.65%)
        pis = self.gross_revenue * PIS_CUMULATIVE
        self.summary.add_tax(TaxResult(
            tax_name="PIS",
            base_calculation=self.gross_revenue,
            rate=PIS_CUMULATIVE * 100,
            amount=pis,
            description="Programa de Integracao Social (cumulativo)",
        ))

        # COFINS cumulativa (3%)
        cofins = self.gross_revenue * COFINS_CUMULATIVE
        self.summary.add_tax(TaxResult(
            tax_name="COFINS",
            base_calculation=self.gross_revenue,
            rate=COFINS_CUMULATIVE * 100,
            amount=cofins,
            description="Contribuicao para Financiamento da Seguridade Social (cumulativa)",
        ))

        # ISS (municipal - varies 2-5%, using 5% as worst case)
        iss = self.gross_revenue * 0.05
        self.summary.add_tax(TaxResult(
            tax_name="ISS",
            base_calculation=self.gross_revenue,
            rate=5.0,
            amount=iss,
            description="Imposto Sobre Servicos (aliquota municipal)",
        ))

    def _calc_lucro_real(self):
        # In real scenario, actual expenses would be deducted
        estimated_expenses = self.gross_revenue * 0.60
        real_profit = self.gross_revenue - estimated_expenses

        irpj = real_profit * IRPJ_RATE
        additional = max(0, (real_profit - IRPJ_ADDITIONAL_THRESHOLD)) * IRPJ_ADDITIONAL_RATE
        irpj += additional
        self.summary.add_tax(TaxResult(
            tax_name="IRPJ",
            base_calculation=real_profit,
            rate=IRPJ_RATE * 100,
            amount=irpj,
            description="IR sobre lucro real apos deducao de despesas",
        ))

        csll = real_profit * CSLL_RATE
        self.summary.add_tax(TaxResult(
            tax_name="CSLL",
            base_calculation=real_profit,
            rate=CSLL_RATE * 100,
            amount=csll,
            description="CSLL sobre lucro real",
        ))

        pis = self.gross_revenue * PIS_NON_CUMULATIVE
        self.summary.add_tax(TaxResult(
            tax_name="PIS",
            base_calculation=self.gross_revenue,
            rate=PIS_NON_CUMULATIVE * 100,
            amount=pis,
            description="PIS nao-cumulativo (com credito de insumos)",
        ))

        cofins = self.gross_revenue * COFINS_NON_CUMULATIVE
        self.summary.add_tax(TaxResult(
            tax_name="COFINS",
            base_calculation=self.gross_revenue,
            rate=COFINS_NON_CUMULATIVE * 100,
            amount=cofins,
            description="COFINS nao-cumulativa (com credito de insumos)",
        ))

    def _calc_simples_nacional(self):
        # Annex-based rates (simplified)
        if self.activity_type == "servicos":
            annex = "Anexo III ou V"
            rate = 0.06  # Approximate starting rate
        else:
            annex = "Anexo I ou II"
            rate = 0.04

        simples = self.gross_revenue * rate
        self.summary.add_tax(TaxResult(
            tax_name="DAS (Simples Nacional)",
            base_calculation=self.gross_revenue,
            rate=rate * 100,
            amount=simples,
            description=f"Documento de Arrecadacao Simples - {annex}. "
                        f"Inclui IRPJ, CSLL, PIS, COFINS, ISS/ICMS, CPP em guia unica.",
        ))

    @staticmethod
    def calculate_irpf(monthly_income: float) -> dict:
        """Calculate IRPF (Individual Income Tax) for a given monthly income."""
        for bracket in IRPF_BRACKETS:
            if monthly_income <= bracket.max_income:
                tax = max(0, monthly_income * bracket.rate - bracket.deduction)
                effective = (tax / monthly_income * 100) if monthly_income > 0 else 0
                return {
                    "base_calculo": monthly_income,
                    "aliquota_nominal": bracket.rate * 100,
                    "deducao": bracket.deduction,
                    "irpf_devido": tax,
                    "aliquota_efetiva": effective,
                    "faixa": f"R$ {bracket.min_income:,.2f} - R$ {bracket.max_income:,.2f}",
                }
        return {"error": "Income exceeds defined brackets"}


def main():
    """Demo: Calculate taxes for sample companies."""
    print("=" * 70)
    print(" CALCULADORA DE IMPOSTOS BRASILEIROS - MYC Accounting Firm")
    print("=" * 70)

    # Company 1: Lucro Presumido - Services
    calc1 = TaxCalculator(
        "TechConsult LTDA",
        TaxRegime.LUCRO_PRESUMIDO,
        gross_revenue=150000.00,
        activity_type="servicos",
    )
    result1 = calc1.calculate_all()
    print(f"\n {result1.company_name}")
    print(f" Regime: {result1.regime.value}")
    print(f" Receita Bruta: R$ {result1.gross_revenue:,.2f}")
    for tax in result1.taxes:
        print(f"  {tax.tax_name:10s}: R$ {tax.amount:>12,.2f}  ({tax.rate:.2f}%)")
    print(f"  {'TOTAL':10s}: R$ {result1.total_taxes:>12,.2f}  ({result1.effective_rate:.2f}% efetiva)")

    # Company 2: Simples Nacional - Commerce
    calc2 = TaxCalculator(
        "Mercearia do Ze ME",
        TaxRegime.SIMPLES_NACIONAL,
        gross_revenue=45000.00,
        activity_type="comercio",
    )
    result2 = calc2.calculate_all()
    print(f"\n {result2.company_name}")
    print(f" Regime: {result2.regime.value}")
    print(f" Receita Bruta: R$ {result2.gross_revenue:,.2f}")
    for tax in result2.taxes:
        print(f"  {tax.tax_name:10s}: R$ {tax.amount:>12,.2f}  ({tax.rate:.2f}%)")
    print(f"  {'TOTAL':10s}: R$ {result2.total_taxes:>12,.2f}  ({result2.effective_rate:.2f}% efetiva)")

    # IRPF Example
    print("\n--- IRPF Example ---")
    salaries = [2500, 5000, 10000, 25000]
    for sal in salaries:
        irpf = TaxCalculator.calculate_irpf(sal)
        if "error" not in irpf:
            print(f"  R$ {sal:>8,.2f}/mes: IRPF R$ {irpf['irpf_devido']:>8,.2f} (aliquota efetiva: {irpf['aliquota_efetiva']:.1f}%)")


if __name__ == "__main__":
    main()
