"""
Gerenciador de CRM Pipeline - Empresa de Vendas
==================================================
Rastreia negocios por estagio, calcula win rates,
deal size medio, velocidade de vendas e cobertura de pipeline.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class EstagioPipeline(Enum):
    """Estagios do pipeline de vendas."""
    LEAD = "Lead"
    QUALIFICACAO = "Qualificacao"
    PROPOSTA = "Proposta"
    NEGOCIACAO = "Negociacao"
    FECHADO_GANHO = "Fechado Ganhou"
    FECHADO_PERDEU = "Fechado Perdeu"

    @property
    def eh_fechado(self) -> bool:
        return self in (
            EstagioPipeline.FECHADO_GANHO,
            EstagioPipeline.FECHADO_PERDEU,
        )

    @property
    def eh_fechado_ganho(self) -> bool:
        return self == EstagioPipeline.FECHADO_GANHO

    @property
    def eh_ativo(self) -> bool:
        return not self.eh_fechado


@dataclass
class Contato:
    """Contato da empresa/pessoa."""
    nome: str
    email: str
    telefone: str = ""
    empresa: str = ""
    cargo: str = ""

    def __str__(self) -> str:
        return f"{self.nome} - {self.empresa} ({self.email})"


@dataclass
class Negocio:
    """Um negocio/deal no pipeline."""
    titulo: str
    contato: Contato
    valor: float
    estagio: EstagioPipeline = EstagioPipeline.LEAD
    probabilidade: float = 0.0  # 0-100
    data_criacao: date = field(default_factory=date.today)
    data_ultima_atualizacao: date = field(default_factory=date.today)
    data_fechamento: Optional[date] = None
    data_prevista_fechamento: Optional[date] = None
    nota_interna: str = ""
    proximo_passo: str = ""
    produtos_interessados: list[str] = field(default_factory=list)
    _id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    _historico_estagio: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self._historico_estagio:
            self._historico_estagio = [self.estagio.value]

    @property
    def valor_ponderado(self) -> float:
        """Valor ponderado pela probabilidade."""
        return self.valor * (self.probabilidade / 100)

    @property
    def dias_no_estagio(self) -> int:
        """Dias desde a ultima atualizacao de estagio."""
        return (date.today() - self.data_ultima_atualizacao).days

    @property
    def tempo_total_pipeline(self) -> int:
        """Dias desde criacao ate hoje ou fechamento."""
        data_fim = self.data_fechamento or date.today()
        return (data_fim - self.data_criacao).days

    def avancar_estagio(self, novo_estagio: EstagioPipeline) -> None:
        """Avanca negocio para novo estagio."""
        self._historico_estagio.append(self.estagio.value)
        self.estagio = novo_estagio
        self.data_ultima_atualizacao = date.today()

        if novo_estagio.eh_fechado:
            self.data_fechamento = date.today()

        # Atualiza probabilidade por estagio
        prob_map = {
            EstagioPipeline.LEAD: 15,
            EstagioPipeline.QUALIFICACAO: 35,
            EstagioPipeline.PROPOSTA: 60,
            EstagioPipeline.NEGOCIACAO: 80,
            EstagioPipeline.FECHADO_GANHO: 100,
            EstagioPipeline.FECHADO_PERDEU: 0,
        }
        self.probabilidade = prob_map.get(novo_estagio, 0)

    def __str__(self) -> str:
        status = ""
        if self.estagio.eh_fechado:
            if self.data_fechamento:
                status = f" | Fechado em {self.data_fechamento.strftime('%d/%m')}"
        return (
            f"[{self._id}] {self.titulo} | {self.contato.empresa} | "
            f"R$ {self.valor:,.2f} | {self.estagio.value} ({self.probabilidade:.0f}%)"
            f"{status}"
        )


@dataclass
class MetricasPipeline:
    """Metricas gerais do pipeline."""
    total_negocios: int = 0
    negocios_ativos: int = 0
    negocios_ganhos: int = 0
    negocios_perdidos: int = 0
    valor_total_pipeline: float = 0.0
    valor_ponderado_total: float = 0.0
    valor_ganho: float = 0.0
    valor_perdido: float = 0.0
    ticket_medio: float = 0.0
    ticket_medio_ganhos: float = 0.0
    win_rate: float = 0.0
    velocidade_vendas_dias: float = 0.0
    cobertura_pipeline: float = 0.0  # pipeline / meta
    por_estagio: dict[str, int] = field(default_factory=dict)
    valor_por_estagio: dict[str, float] = field(default_factory=dict)


class CRMPipeline:
    """Gerenciador de pipeline de CRM."""

    def __init__(self, meta_vendas: float = 0.0) -> None:
        self.negocios: list[Negocio] = []
        self.meta_vendas = meta_vendas
        self.historico_metricas: list[MetricasPipeline] = []

    def adicionar_negocio(
        self,
        titulo: str,
        contato: Contato,
        valor: float,
        estagio: EstagioPipeline = EstagioPipeline.LEAD,
        data_prevista: Optional[date] = None,
        produtos: Optional[list[str]] = None,
        nota: str = "",
    ) -> Negocio:
        """Adiciona novo negocio ao pipeline."""
        negocio = Negocio(
            titulo=titulo,
            contato=contato,
            valor=valor,
            estagio=estagio,
            data_prevista_fechamento=data_prevista,
            nota_interna=nota,
            produtos_interessados=produtos or [],
        )
        self.negocios.append(negocio)
        return negocio

    def avancar_negocio(
        self,
        negocio: Negocio,
        novo_estagio: EstagioPipeline,
    ) -> str:
        """Avanca negocio no pipeline."""
        negocio.avancar_estagio(novo_estagio)
        return f"{negocio.titulo} -> {novo_estagio.value}"

    def negocios_por_estagio(
        self,
        estagio: EstagioPipeline,
    ) -> list[Negocio]:
        """Lista negocios por estagio."""
        return [n for n in self.negocios if n.estagio == estagio]

    def negocios_ativos(self) -> list[Negocio]:
        """Lista apenas negocios ativos (nao fechados)."""
        return [n for n in self.negocios if n.estagio.eh_ativo]

    def negocios_atrasados(self) -> list[Negocio]:
        """Lista negocios com data prevista vencida e ainda abertos."""
        hoje = date.today()
        return [
            n for n in self.negocios
            if n.data_prevista_fechamento
            and n.data_prevista_fechamento < hoje
            and n.estagio.eh_ativo
        ]

    def calcular_metricas(self, meta: Optional[float] = None) -> MetricasPipeline:
        """Calcula metricas completas do pipeline."""
        m = MetricasPipeline()
        m.total_negocios = len(self.negocios)

        negocios_ativos = [n for n in self.negocios if n.estagio.eh_ativo]
        negocios_ganhos = [n for n in self.negocios if n.estagio.eh_fechado_ganho]
        negocios_perdidos = [n for n in self.negocios if n.estagio == EstagioPipeline.FECHADO_PERDEU]

        m.negocios_ativos = len(negocios_ativos)
        m.negocios_ganhos = len(negocios_ganhos)
        m.negocios_perdidos = len(negocios_perdidos)

        # Valores
        m.valor_total_pipeline = sum(n.valor for n in negocios_ativos)
        m.valor_ponderado_total = sum(
            n.valor_ponderado for n in negocios_ativos
        )
        m.valor_ganho = sum(n.valor for n in negocios_ganhos)
        m.valor_perdido = sum(n.valor for n in negocios_perdidos)

        # Ticket medio
        if negocios_ativos:
            m.ticket_medio = m.valor_total_pipeline / len(negocios_ativos)

        if negocios_ganhos:
            m.ticket_medio_ganhos = m.valor_ganho / len(negocios_ganhos)

        # Win rate (ganho / (ganho + perdido))
        total_fechados = m.negocios_ganhos + m.negocios_perdidos
        if total_fechados > 0:
            m.win_rate = (m.negocios_ganhos / total_fechados) * 100

        # Velocidade de vendas (dias medios ate fechamento ganho)
        if negocios_ganhos:
            dias_total = sum(n.tempo_total_pipeline for n in negocios_ganhos)
            m.velocidade_vendas_dias = dias_total / len(negocios_ganhos)

        # Cobertura de pipeline
        meta_atual = meta or self.meta_vendas
        if meta_atual > 0:
            m.cobertura_pipeline = m.valor_total_pipeline / meta_atual

        # Por estagio
        for n in self.negocios:
            estagio = n.estagio.value
            m.por_estagio[estagio] = m.por_estagio.get(estagio, 0) + 1
            if not n.estagio.eh_fechado:
                m.valor_por_estagio[estagio] = (
                    m.valor_por_estagio.get(estagio, 0) + n.valor
                )

        self.historico_metricas.append(m)
        return m

    def relatorio_pipeline(self) -> str:
        """Gera relatorio visual do pipeline."""
        m = self.calcular_metricas()

        linhas = [
            "=" * 60,
            "RELATORIO DE PIPELINE DE VENDAS - CRM",
            "=" * 60,
            f"Meta de vendas: R$ {self.meta_vendas:,.2f}" if self.meta_vendas > 0 else "Meta: nao definida",
            f"Total negocios: {m.total_negocios}",
            f"Ativos: {m.negocios_ativos} | Ganhos: {m.negocios_ganhos} | Perdidos: {m.negocios_perdidos}",
            "-" * 60,
            f"Valor no pipeline: R$ {m.valor_total_pipeline:,.2f}",
            f"Valor ponderado: R$ {m.valor_ponderado_total:,.2f}",
            f"Valor ganho: R$ {m.valor_ganho:,.2f}",
            f"Ticket medio (ativos): R$ {m.ticket_medio:,.2f}",
            f"Ticket medio (ganhos): R$ {m.ticket_medio_ganhos:,.2f}",
            "-" * 60,
            f"Win Rate: {m.win_rate:.1f}%",
            f"Velocidade vendas: {m.velocidade_vendas_dias:.1f} dias",
        ]

        if m.cobertura_pipeline > 0:
            linhas.append(
                f"Cobertura pipeline: {m.cobertura_pipeline:.1f}x "
                f"({m.cobertura_pipeline * 100:.0f}% da meta)"
            )

        # Pipeline visual por estagio
        linhas.append("\nPIPELINE por Estagio:")
        for estagio in EstagioPipeline:
            if estagio.eh_fechado:
                continue
            count = m.por_estagio.get(estagio.value, 0)
            valor = m.valor_por_estagio.get(estagio.value, 0)
            linhas.append(
                f"  {estagio.value:15s}: {count} negocios | R$ {valor:,.2f}"
            )

        # Negocios atrasados
        atrasados = self.negocios_atrasados()
        if atrasados:
            linhas.append(f"\nNEGOCIOS ATRASADOS: {len(atrasados)}")
            for n in atrasados:
                linhas.append(f"  {n.titulo} ({n.data_prevista_fechamento})")

        return "\n".join(linhas)


def main() -> None:
    """Demonstracao do CRM Pipeline."""
    print("=" * 60)
    print("CRM PIPELINE MANAGER - Empresa de Vendas")
    print("=" * 60)

    crm = CRMPipeline(meta_vendas=500_000.0)

    # Criar negocios
    print("\n--- Criando Negocios ---")
    n1 = crm.adicionar_negocio(
        "Implantacao ERP - TechCorp",
        Contato("Carlos CEO TechCorp", "carlos@techcorp.com", telefone="1111111111", empresa="TechCorp", cargo="CEO"),
        valor=150_000.0,
        estagio=EstagioPipeline.NEGOCIACAO,
        data_prevista=date(2026, 4, 30),
        produtos=["ERP", "Suporte Premium"],
    )
    print(f"  {n1}")

    n2 = crm.adicionar_negocio(
        "Site E-commerce - ModaLTDA",
        Contato(
            "Ana Diretora", "ana@modaltda.com",
            empresa="ModaLTDA", cargo="Diretora",
        ),
        valor=80_000.0,
        estagio=EstagioPipeline.PROPOSTA,
        data_prevista=date(2026, 5, 15),
    )
    print(f"  {n2}")

    n3 = crm.adicionar_negocio(
        "Consultoria Digital - Construtora",
        Contato(
            "Roberto Gerente", "roberto@construtora.com",
            empresa="Construtora ABC", cargo="Gerente TI",
        ),
        valor=45_000.0,
        estagio=EstagioPipeline.LEAD,
    )
    print(f"  {n3}")

    n4 = crm.adicionar_negocio(
        "App Mobile - SaúdeVida",
        Contato(
            "Juliana CTO", "juliana@saudevida.com",
            empresa="SaúdeVida", cargo="CTO",
        ),
        valor=120_000.0,
        estagio=EstagioPipeline.QUALIFICACAO,
        data_prevista=date(2026, 6, 1),
    )
    print(f"  {n4}")

    # Avancar alguns
    print("\n--- Avancando Pipeline ---")
    crm.avancar_negocio(n3, EstagioPipeline.QUALIFICACAO)
    print(f"  {n3.titulo} -> {n3.estagio.value}")

    # Simular fechamentos (direto para exemplo)
    n5 = crm.adicionar_negocio(
        "Projeto BI - DataCo",
        Contato(
            "Fernando Diretor", "fernando@dataco.com",
            empresa="DataCo", cargo="Diretor",
        ),
        valor=90_000.0,
        estagio=EstagioPipeline.FECHADO_GANHO,
    )
    print(f"  {n5}")

    n6 = crm.adicionar_negocio(
        "Migracao Cloud - Logistica",
        Contato(
            "Marcos IT", "marcos@log.com",
            empresa="Logistica Express", cargo="Coord. TI",
        ),
        valor=60_000.0,
        estagio=EstagioPipeline.FECHADO_PERDEU,
    )
    print(f"  {n6}")

    # Relatorio
    print("\n--- Relatorio Pipeline ---")
    print(crm.relatorio_pipeline())

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
