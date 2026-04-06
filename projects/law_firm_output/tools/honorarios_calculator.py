"""
Calculadora de Honorarios Advocaticios - Advocacia BR
======================================================
Calcula honorarios com base nas tabelas OAB, contingencia,
custas processuais e gera relatorios de honorarios.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TipoHonorario(Enum):
    """Tipos de honorarios advocatícios."""
    PRO_LABORE = "Pro Labore"
    SUCUMBENCIA = "Sucumbencia"
    CONTINGENCIA = "Contingencia"
    CONSULTORIA = "Consultoria"
    ADMINISTRATIVO = "Administrativo"


@dataclass
class TabelaOAB:
    """Tabela de honorarios minimos da OAB (valores referenciais)."""
    ano: int
    estado: str
    # Valores em reais (referenciais, variam por seccional)
    consulta_juridica: float = 300.0
    peticao_inicial: float = 3300.0
    contestacao: float = 2200.0
    recurso: float = 2200.0
    audiencia: float = 1100.0
    contrato_simples: float = 1100.0
    contrato_complexo: float = 3300.0
    working_hour_advogado_junior: float = 150.0
    working_hour_advogado_senior: float = 350.0
    working_hour_advogado_pleno: float = 250.0


@dataclass
class CalculoHonorario:
    """Resultado de um calculo de honorarios."""
    tipo: TipoHonorario
    descricao: str
    valor_base: float
    valor_final: float
    percentual_aplicado: Optional[float] = None
    observacoes: str = ""

    def __str__(self) -> str:
        perc_str = ""
        if self.percentual_aplicado is not None:
            perc_str = f" ({self.percentual_aplicado}%)"
        return (
            f"{self.descricao}{perc_str}\n"
            f"  Valor base: R$ {self.valor_base:,.2f}\n"
            f"  Valor final: R$ {self.valor_final:,.2f}"
        )


@dataclass
class CustasProcessuais:
    """Custas e despesas processuais."""
    custas_iniciais: float = 0.0
    emolumentos: float = 0.0
    despesas_cart: float = 0.0
    pericia: float = 0.0
    tradutor_juramentado: float = 0.0
    outras: float = 0.0

    @property
    def total(self) -> float:
        return sum([
            self.custas_iniciais,
            self.emolumentos,
            self.despesas_cart,
            self.pericia,
            self.tradutor_juramentado,
            self.outras,
        ])


@dataclass
class RelatorioHonorarios:
    """Relatorio completo de honorarios."""
    advogado: str = ""
    cliente: str = ""
    numero_processo: str = ""
    calculos: list[CalculoHonorario] = field(default_factory=list)
    custas: CustasProcessuais = field(default_factory=CustasProcessuais)
    observacoes_gerais: str = ""

    @property
    def total_honorarios(self) -> float:
        return sum(c.valor_final for c in self.calculos)

    @property
    def total_geral(self) -> float:
        return self.total_honorarios + self.custas.total

    def gerar_relatorio(self) -> str:
        """Gera relatorio textual completo."""
        linhas = [
            "=" * 60,
            "RELATORIO DE HONORARIOS ADVOCATICIOS",
            "=" * 60,
            f"Advogado: {self.advogado}",
            f"Cliente: {self.cliente}",
            f"Processo: {self.numero_processo}",
            "-" * 60,
        ]

        if self.calculos:
            linhas.append("HONORARIOS:")
            for calc in self.calculos:
                perc = f" ({calc.percentual_aplicado}%)" if calc.percentual_aplicado is not None else ""
                linhas.append(
                    f"  {calc.descricao}{perc}: R$ {calc.valor_final:,.2f}"
                )
            linhas.append(f"  ---")
            linhas.append(
                f"  TOTAL HONORARIOS: R$ {self.total_honorarios:,.2f}"
            )

        linhas.append("")

        if self.custas.total > 0:
            linhas.append("CUSTAS E DESPESAS PROCESSUAIS:")
            linhas.append(f"  Custas iniciais: R$ {self.custas.custas_iniciais:,.2f}")
            linhas.append(f"  Emolumentos: R$ {self.custas.emolumentos:,.2f}")
            if self.custas.custas_iniciais:
                linhas.append(f"  Despesas cartoriais: R$ {self.custas.despesas_cart:,.2f}")
            if self.custas.pericia > 0:
                linhas.append(f"  Pericia: R$ {self.custas.pericia:,.2f}")
            if self.custas.tradutor_juramentado > 0:
                linhas.append(f"  Tradutor juramentado: R$ {self.custas.tradutor_juramentado:,.2f}")
            if self.custas.outras > 0:
                linhas.append(f"  Outras despesas: R$ {self.custas.outras:,.2f}")
                linhas.append(f"  ---")
            linhas.append(
                f"  TOTAL CUSTAS: R$ {self.custas.total:,.2f}"
            )

        linhas.append("")
        linhas.append("=" * 60)
        linhas.append(f"TOTAL GERAL: R$ {self.total_geral:,.2f}")
        linhas.append("=" * 60)

        return "\n".join(linhas)


class HonorariosCalculator:
    """Calculadora de honorarios advocatícios."""

    def __init__(self, tabela: Optional[TabelaOAB] = None) -> None:
        self.tabela = tabela or TabelaOAB(ano=2026, estado="SP")

    def calcular_pro_labore(
        self,
        servicos: list[tuple[str, float]],
        desconto: float = 0.0,
    ) -> list[CalculoHonorario]:
        """
        Calcula honorarios pro labore por servico.

        Args:
            servicos: Lista de (descricao, valor ou horas).
            desconto: Percentual de desconto (0-100).

        Returns:
            Lista de calculos pro labore.
        """
        resultados = []
        for descricao, valor in servicos:
            valor_final = valor * (1 - desconto / 100)
            resultados.append(
                CalculoHonorario(
                    tipo=TipoHonorario.PRO_LABORE,
                    descricao=descricao,
                    valor_base=valor,
                    valor_final=round(valor_final, 2),
                    percentual_aplicado=None,
                )
            )
        return resultados

    def calcular_contingencia(
        self,
        valor_causa: float,
        percentual: float = 30.0,
        minimo: Optional[float] = None,
        maximo: Optional[float] = None,
    ) -> CalculoHonorario:
        """
        Calcula honorarios por contingencia (exit).

        Args:
            valor_causa: Valor da causa ou valor obtido.
            percentual: Percentual de contingencia (padrao: 30%).
            minimo: Valor minimo de honorarios.
            maximo: Valor maximo de honorarios (teto).

        Returns:
            CalculoHonorario com o resultado.
        """
        valor = valor_causa * (percentual / 100)

        if minimo is not None and valor < minimo:
            valor = minimo
        if maximo is not None and valor > maximo:
            valor = maximo

        return CalculoHonorario(
            tipo=TipoHonorario.CONTINGENCIA,
            descricao=f"Honorarios contingencia ({percentual}%)",
            valor_base=valor_causa,
            valor_final=round(valor, 2),
            percentual_aplicado=percentual,
        )

    def calcular_sucumbencia(
        self,
        valor_condenacao: float,
        percentual: float = 10.0,
    ) -> CalculoHonorario:
        """
        Calcula honorarios de sucumbencia (art. 85 CPC/2015).

        Conforme CPC art. 85, os honorarios de sucumbencia
        variam entre 10% e 20% do valor da condenacao.

        Args:
            valor_condenacao: Valor da condenacao.
            percentual: Percentual (10-20%, padrao 10%).

        Returns:
            CalculoHonorario com o resultado.

        Raises:
            ValueError: Se percentual fora do range 10-20.
        """
        if not 10 <= percentual <= 20:
            raise ValueError(
                "Percentual de sucumbencia deve estar entre 10% e 20% (art. 85 CPC)"
            )

        valor = valor_condenacao * (percentual / 100)

        return CalculoHonorario(
            tipo=TipoHonorario.SUCUMBENCIA,
            descricao=f"Honorarios sucumbencia ({percentual}%)",
            valor_base=valor_condenacao,
            valor_final=round(valor, 2),
            percentual_aplicado=percentual,
            observacoes="Art. 85, 2, CPC/2015",
        )

    def calcular_servicos_tabela(
        self,
        servicos: list[str],
    ) -> list[CalculoHonorario]:
        """
        Calcula honorarios pela tabela OAB.

        Args:
            servicos: Lista de nomes de servicos conforme tabela.

        Returns:
            Lista de CalculoHonorario.
        """
        tabela_map = {
            "consulta": ("Consulta juridica", self.tabela.consulta_juridica),
            "peticao_inicial": ("Peticao inicial", self.tabela.peticao_inicial),
            "contestacao": ("Contestacao", self.tabela.contestacao),
            "recurso": ("Recurso", self.tabela.recurso),
            "audiencia": ("Audiencia", self.tabela.audiencia),
            "contrato_simples": ("Contrato simples", self.tabela.contrato_simples),
            "contrato_complexo": ("Contrato complexo", self.tabela.contrato_complexo),
        }

        resultados = []
        for servico in servicos:
            if servico in tabela_map:
                descricao, valor = tabela_map[servico]
                resultados.append(
                    CalculoHonorario(
                        tipo=TipoHonorario.ADMINISTRATIVO,
                        descricao=f"{descricao} (Tabela OAB {self.tabela.estado}/{self.tabela.ano})",
                        valor_base=valor,
                        valor_final=valor,
                    )
                )
        return resultados

    def gerar_relatorio(
        self,
        advogado: str,
        cliente: str,
        processo: str,
        calculos: list[CalculoHonorario],
        custas: Optional[CustasProcessuais] = None,
    ) -> RelatorioHonorarios:
        """
        Gera relatorio completo de honorarios.

        Args:
            advogado: Nome do advogado.
            cliente: Nome do cliente.
            processo: Numero do processo.
            calculos: Lista de calculos de honorarios.
            custas: Custas processuais (opcional).

        Returns:
            RelatorioHonorarios completo.
        """
        return RelatorioHonorarios(
            advogado=advogado,
            cliente=cliente,
            numero_processo=processo,
            calculos=calculos,
            custas=custas or CustasProcessuais(),
        )


def main() -> None:
    """Demonstracao da Calculadora de Honorarios."""
    print("=" * 60)
    print("CALCULADORA DE HONORARIOS ADVOCATICIOS - Advocacia BR")
    print("=" * 60)

    tabela_2026 = TabelaOAB(ano=2026, estado="SP")
    calc = HonorariosCalculator(tabela_2026)

    # Exemplo 1: Honorarios pela tabela OAB
    print("\n--- Exemplo 1: Servicos pela Tabela OAB ---")
    servicos = calc.calcular_servicos_tabela([
        "consulta",
        "peticao_inicial",
        "audiencia",
    ])
    for s in servicos:
        print(f"  {s.descricao}: R$ {s.valor_final:,.2f}")

    # Exemplo 2: Honorarios por contingencia
    print("\n--- Exemplo 2: Honorarios de Contingencia ---")
    conting = calc.calcular_contingencia(
        valor_causa=1_000_000.0,
        percentual=30.0,
        minimo=50_000.0,
        maximo=500_000.0,
    )
    print(conting)

    # Exemplo 3: Honorarios de sucumbencia
    print("\n--- Exemplo 3: Honorarios de Sucumbencia ---")
    suc = calc.calcular_sucumbencia(
        valor_condenacao=150_000.0,
        percentual=15.0,
    )
    print(suc)

    # Exemplo 4: Relatorio completo
    print("\n--- Exemplo 4: Relatorio Completo ---")
    todos_calculos = servicos + [conting, suc]
    custas = CustasProcessuais(
        custas_iniciais=532.50,
        emolumentos=85.00,
        despesas_cart=120.00,
    )
    relatorio = calc.gerar_relatorio(
        advogado="Dr. Silva",
        cliente="Joao da Silva S.A.",
        processo="0001234-56.2026.8.26.0100",
        calculos=todos_calculos,
        custas=custas,
    )
    print(relatorio.gerar_relatorio())

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
