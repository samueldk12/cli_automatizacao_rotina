"""
Rastreador de Recrutamento - RH Company
==========================================
Gerencia vagas, pipeline de candidatos, metricas de tempo
e taxas de conversao por etapa do processo seletivo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class EtapaCandidato(Enum):
    """Etapas do processo seletivo."""
    INSCRITO = "Inscrito"
    TRIAGEM = "Triagem"
    ENTREVISTA_RH = "Entrevista RH"
    ENTREVISTA_TECNICA = "Entrevista tecnica"
    TESTE_PRACTICO = "Teste pratico"
    PROPOSTA = "Proposta"
    CONTRATADO = "Contratado"
    REPROVADO = "Reprovado"
    DESISTENTE = "Desistente"

    @property
    def eh_final(self) -> bool:
        return self in (
            EtapaCandidato.CONTRATADO,
            EtapaCandidato.REPROVADO,
            EtapaCandidato.DESISTENTE,
        )


@dataclass
class Candidato:
    """Representa um candidato no processo."""
    nome: str
    email: str
    telefone: str = ""
    linkedin: str = ""
    vaga_id: str = ""
    etapa_atual: EtapaCandidato = EtapaCandidato.INSCRITO
    data_inscricao: date = field(default_factory=date.today)
    data_ultima_etapa: Optional[date] = None
    data_contratacao: Optional[date] = None
    salario_esperado: float = 0.0
    observacoes: str = ""
    documentos: list[str] = field(default_factory=list)
    avaliacoes: dict[str, float] = field(default_factory=dict)

    @property
    def tempo_no_processo(self) -> int:
        """Dias desde a inscricao ate hoje ou contratacao."""
        data_fim = self.data_contratacao or date.today()
        return (data_fim - self.data_inscricao).days

    def avancar(self, nova_etapa: EtapaCandidato) -> None:
        """Avanca candidato para nova etapa."""
        self.etapa_atual = nova_etapa
        self.data_ultima_etapa = date.today()

        if nova_etapa == EtapaCandidato.CONTRATADO:
            self.data_contratacao = date.today()

    def __str__(self) -> str:
        dias = self.tempo_no_processo
        return (
            f"{self.nome} | {self.etapa_atual.value} | "
            f"{dias} dias no processo"
        )


@dataclass
class Vaga:
    """Vaga de emprego."""
    titulo: str
    departamento: str
    nivel: str = ""  # junior, pleno, senior, gestor
    tipo_contrato: str = "CLT"
    faixa_salarial: str = ""
    descricao: str = ""
    habilidades_requisitas: list[str] = field(default_factory=list)
    data_abertura: date = field(default_factory=date.today)
    data_fechamento: Optional[date] = None
    candidatos: list[Candidato] = field(default_factory=list)
    responsavel: str = ""
    status: str = "Aberta"
    _id: str = ""

    @property
    def num_candidatos(self) -> int:
        return len(self.candidatos)

    @property
    def dias_aberta(self) -> int:
        data_fim = self.data_fechamento or date.today()
        return (data_fim - self.data_abertura).days

    def adicionar_candidato(self, candidato: Candidato) -> None:
        candidato.vaga_id = self._id or self.titulo
        candidato.data_inscricao = date.today()
        self.candidatos.append(candidato)

    def estatisticas_vaga(self) -> dict:
        """Obtem estatisticas da vaga."""
        stats = {
            "total_candidatos": len(self.candidatos),
            "por_etapa": {},
            "contratados": 0,
            "tempo_medio": 0,
        }

        for cand in self.candidatos:
            etapa = cand.etapa_atual.value
            stats["por_etapa"][etapa] = stats["por_etapa"].get(etapa, 0) + 1

            if cand.etapa_atual == EtapaCandidato.CONTRATADO:
                stats["contratados"] += 1

            stats["tempo_medio"] += cand.tempo_no_processo

        if self.candidatos:
            stats["tempo_medio"] /= len(self.candidatos)
            stats["tempo_medio"] = round(stats["tempo_medio"], 1)

        return stats


class RecrutamentoTracker:
    """Sistema de rastreamento de recrutamento."""

    def __init__(self) -> None:
        self.vagas: list[Vaga] = []
        self.candidatos_todos: list[Candidato] = []
        self._vaga_counter = 0
        self._candidato_counter = 0

    def criar_vaga(
        self,
        titulo: str,
        departamento: str,
        nivel: str = "",
        faixa_salarial: str = "",
        descricao: str = "",
        habilidades: Optional[list[str]] = None,
        responsavel: str = "",
    ) -> Vaga:
        """Cria nova vaga no sistema."""
        self._vaga_counter += 1
        vaga = Vaga(
            titulo=titulo,
            departamento=departamento,
            nivel=nivel,
            faixa_salarial=faixa_salarial,
            descricao=descricao,
            habilidades_requisitas=habilidades or [],
            responsavel=responsavel,
            _id=f"VAGA-{self._vaga_counter:04d}",
        )
        self.vagas.append(vaga)
        return vaga

    def adicionar_candidato(
        self,
        nome: str,
        email: str,
        vaga: Vaga,
        telefone: str = "",
        salario_esperado: float = 0.0,
    ) -> Candidato:
        """Adiciona candidato a uma vaga."""
        self._candidato_counter += 1
        candidato = Candidato(
            nome=nome,
            email=email,
            telefone=telefone,
            salario_esperado=salario_esperado,
            vaga_id=vaga._id,
        )
        vaga.adicionar_candidato(candidato)
        self.candidatos_todos.append(candidato)
        return candidato

    def avancar_candidato(
        self,
        candidato: Candidato,
        nova_etapa: EtapaCandidato,
    ) -> str:
        """Avanca candidato para proxima etapa."""
        candidato.avancar(nova_etapa)
        return f"{candidato.nome} movido para {nova_etapa.value}"

    def converter_etapa(
        self,
        etapa_origem: EtapaCandidato,
        etapa_destino: EtapaCandidato,
    ) -> float:
        """
        Calcula taxa de conversao entre duas etapas.

        Returns:
            Taxa de conversao (0-100).
        """
        origem_count = sum(
            1 for c in self.candidatos_todos
            if c.etapa_atual == etapa_origem
        )

        # Candidatos que passaram pela origem e chegaram no destino
        destino_count = sum(
            1 for c in self.candidatos_todos
            if c.etapa_atual == etapa_destino
        )

        if origem_count == 0:
            return 0.0

        return (destino_count / origem_count) * 100

    def tempo_medio_contratacao(self) -> float:
        """Calcula tempo medio de contratacao (dias) para os contratados."""
        contratados = [
            c for c in self.candidatos_todos
            if c.etapa_atual == EtapaCandidato.CONTRATADO
        ]

        if not contratados:
            return 0.0

        tempo_total = sum(c.tempo_no_processo for c in contratados)
        return round(tempo_total / len(contratados), 1)

    def taxa_conversao_geral(self) -> float:
        """Calcula taxa geral de conversao (inscritos -> contratados)."""
        total = len(self.candidatos_todos)
        if total == 0:
            return 0.0

        contratados = sum(
            1 for c in self.candidatos_todos
            if c.etapa_atual == EtapaCandidato.CONTRATADO
        )

        return round((contratados / total) * 100, 1)

    def relatorio_gerencial(self) -> str:
        """Gera relatorio gerencial de recrutamento."""
        linhas = [
            "=" * 60,
            "RELATORIO GERENCIAL DE RECRUTAMENTO",
            "=" * 60,
            f"Vagas ativas: {sum(1 for v in self.vagas if v.status == 'Aberta')}",
            f"Total de vagas: {len(self.vagas)}",
            f"Total de candidatos: {len(self.candidatos_todos)}",
            f"Taxa de conversao geral: {self.taxa_conversao_geral()}%",
            f"Tempo medio contratacao: {self.tempo_medio_contratacao()} dias",
            "-" * 60,
        ]

        # Distribuicao por etapa
        etapas_count: dict[str, int] = {}
        for c in self.candidatos_todos:
            etapa = c.etapa_atual.value
            etapas_count[etapa] = etapas_count.get(etapa, 0) + 1

        linhas.append("Candidatos por etapa:")
        for etapa, count in sorted(etapas_count.items()):
            total = len(self.candidatos_todos) or 1
            pct = (count / total) * 100
            linhas.append(f"  {etapa}: {count} ({pct:.1f}%)")

        # Por vaga
        linhas.append("\nDetalhamento por vaga:")
        for vaga in self.vagas:
            stats = vaga.estatisticas_vaga()
            linhas.append(
                f"  {vaga._id} | {vaga.titulo} | {vaga.departamento} | "
                f"{stats['total_candidatos']} candidatos | "
                f"Tempo medio: {stats['tempo_medio']} dias"
            )

        return "\n".join(linhas)


def main() -> None:
    """Demonstracao do Recrutamento Tracker."""
    print("=" * 60)
    print("RASTREAMENTO DE RECRUTAMENTO - RH Company")
    print("=" * 60)

    tracker = RecrutamentoTracker()

    # Criar vagas
    print("\n--- Criando Vagas ---")
    vaga1 = tracker.criar_vaga(
        titulo="Desenvolvedor Python Senior",
        departamento="Tecnologia",
        nivel="Senior",
        faixa_salarial="R$ 12.000 - R$ 18.000",
        descricao="Desenvolvedor Python para equipe de backend",
        habilidades=["Python", "FastAPI", "PostgreSQL", "Docker"],
        responsavel="Ana RH",
    )
    print(f"  Criada: {vaga1._id} - {vaga1.titulo}")

    vaga2 = tracker.criar_vaga(
        titulo="Analista Financeiro",
        departamento="Financeiro",
        nivel="Pleno",
        faixa_salarial="R$ 6.000 - R$ 9.000",
        responsavel="Carlos RH",
    )
    print(f"  Criada: {vaga2._id} - {vaga2.titulo}")

    # Adicionar candidatos
    print("\n--- Adicionando Candidatos ---")
    c1 = tracker.adicionar_candidato(
        "Joao Silva", "joao@email.com", vaga1,
        salario_esperado=15000.0,
    )
    c2 = tracker.adicionar_candidato(
        "Maria Santos", "maria@email.com", vaga1,
        salario_esperado=14000.0,
    )
    c3 = tracker.adicionar_candidato(
        "Pedro Oliveira", "pedro@email.com", vaga1,
    )
    c4 = tracker.adicionar_candidato(
        "Ana Costa", "ana@email.com", vaga2,
        salario_esperado=8000.0,
    )

    for c in [c1, c2, c3, c4]:
        print(f"  {c}")

    # Avançar candidates no pipeline
    print("\n--- Avancando Pipeline ---")
    tracker.avancar_candidato(c1, EtapaCandidato.ENTREVISTA_RH)
    tracker.avancar_candidato(c1, EtapaCandidato.ENTREVISTA_TECNICA)
    tracker.avancar_candidato(c1, EtapaCandidato.TESTE_PRACTICO)
    tracker.avancar_candidato(c1, EtapaCandidato.CONTRATADO)

    print(f"  {c1.nome}: {c1.etapa_atual.value} ({c1.tempo_no_processo} dias)")

    tracker.avancar_candidato(c2, EtapaCandidato.TRIAGEM)
    tracker.avancar_candidato(c2, EtapaCandidato.ENTREVISTA_RH)

    print(f"  {c2.nome}: {c2.etapa_atual.value} ({c2.tempo_no_processo} dias)")

    tracker.avancar_candidato(c3, EtapaCandidato.TRIAGEM)
    tracker.avancar_candidato(c3, EtapaCandidato.REPROVADO)

    print(f"  {c3.nome}: {c3.etapa_atual.value}")

    tracker.avancar_candidato(c4, EtapaCandidato.TRIAGEM)
    tracker.avancar_candidato(c4, EtapaCandidato.ENTREVISTA_RH)
    tracker.avancar_candidato(c4, EtapaCandidato.ENTREVISTA_TECNICA)

    print(f"  {c4.nome}: {c4.etapa_atual.value} ({c4.tempo_no_processo} dias)")

    # Metrics
    print(f"\n--- Metricas ---")
    print(f"Tempo medio contratacao: {tracker.tempo_medio_contratacao()} dias")
    print(f"Taxa conversao geral: {tracker.taxa_conversao_geral()}%")
    print(f"Conversao Triagem -> Entrevista RH: {tracker.converter_etapa(EtapaCandidato.TRIAGEM, EtapaCandidato.ENTREVISTA_RH):.1f}%")

    # Relatorio
    print("\n--- Relatorio Gerencial ---")
    print(tracker.relatorio_gerencial())

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
