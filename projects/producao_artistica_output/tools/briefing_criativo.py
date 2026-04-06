"""
Briefing Criativo - Creative Brief Generator
Generates structured creative briefs for clients, tracks project
requirements, manages deliverables, timeline, revisions and approvals.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import Optional


class BriefingStatus(Enum):
    RASCUNHO = "Rascunho"
    AGUARDANDO_APROVACAO = "Aguardando Aprovacao"
    APROVADO = "Aprovado"
    EM_EXECUCAO = "Em Execucao"
    EM_REVISAO = "Em Revisao"
    FINALIZADO = "Finalizado"
    CANCELADO = "Cancelado"


class Prioridade(Enum):
    BAIXA = "Baixa"
    MEDIA = "Media"
    ALTA = "Alta"
    URGENTE = "Urgente"


@dataclass
class Entrega:
    nome: str
    descricao: str
    formato: str
    quantidade: int = 1


@dataclass
class Revisao:
    versao: int
    data: date
    notas: str
    aprovada: bool = False


@dataclass
class BriefingCriativo:
    project_id: str
    cliente: str
    contato: str
    titulo: str
    descricao: str
    objetivo: str = ""
    publico_alvo: str = ""
    referencia_estilo: str = ""
    orcamento: float = 0.0
    prioridade: Prioridade = Prioridade.MEDIA
    status: BriefingStatus = BriefingStatus.RASCUNHO
    deadline: Optional[date] = None
    entregas: list[Entrega] = field(default_factory=list)
    revisoes: list[Revisao] = field(default_factory=list)
    observacoes: str = ""

    def add_entrega(self, nome: str, descricao: str, formato: str, qtd: int = 1):
        self.entregas.append(Entrega(nome=nome, descricao=descricao, formato=formato, quantidade=qtd))

    def add_revisao(self, notas: str, aprovada: bool = False):
        self.revisoes.append(Revisao(versao=len(self.revisoes) + 1, data=date.today(), notas=notas, aprovada=aprovada))

    @property
    def dias_restantes(self) -> Optional[int]:
        if self.deadline:
            return (self.deadline - date.today()).days
        return None

    def texto_completo(self) -> str:
        lines = [
            "=" * 50,
            f"BRIEFING CRIATIVO - {self.titulo}",
            "=" * 50,
            f"ID: {self.project_id} | Status: {self.status.value} | Prioridade: {self.prioridade.value}",
            f"Cliente: {self.cliente} | Contato: {self.contato}",
            f"Objetivo: {self.objetivo}",
            f"Publico-alvo: {self.publico_alvo}",
            f"Referencia: {self.referencia_estilo}",
            f"Orcamento: R$ {self.orcamento:,.2f}",
            "",
            f"Descricao:\n  {self.descricao}",
            "",
            f"Entregaveis ({len(self.entregas)}):",
        ]
        for e in self.entregas:
            lines.append(f"  - {e.nome} ({e.formato}, qtd:{e.quantidade}): {e.descricao}")

        dias = self.dias_restantes
        prazo = f"Prazo: {self.deadline} ({dias} dias)" if dias is not None else "Prazo: N/A"
        lines.append(f"\n{prazo}")

        if self.revisoes:
            lines.append(f"\nRevisoes ({len(self.revisoes)}):")
            for r in self.revisoes:
                st = "APROVADA" if r.aprovada else "PENDENTE"
                lines.append(f"  v{r.versao} ({r.data}): {st} - {r.notas}")

        if self.observacoes:
            lines.append(f"\nObs: {self.observacoes}")
        return "\n".join(lines)


class BriefingManager:
    """Gerencia todos os briefings criativos de um studio."""

    def __init__(self, studio_name: str):
        self.studio_name = studio_name
        self.briefings: list[BriefingCriativo] = []
        self._counter = 0

    def criar_briefing(self, **kwargs) -> BriefingCriativo:
        self._counter += 1
        bf = BriefingCriativo(project_id=f"BRF-{self._counter:04d}", **kwargs)
        self.briefings.append(bf)
        return bf

    def por_status(self, status: BriefingStatus) -> list[BriefingCriativo]:
        return [b for b in self.briefings if b.status == status]

    def dashboard(self) -> str:
        total = len(self.briefings)
        by_status: dict[str, int] = {}
        for b in self.briefings:
            by_status[b.status.value] = by_status.get(b.status.value, 0) + 1
        orcamento_total = sum(b.orcamento for b in self.briefings)

        lines = [
            f"DASHBOARD - {self.studio_name}",
            f"Total: {total} briefings | Orcamento total: R$ {orcamento_total:,.2f}",
            "Por status:",
        ]
        for st, cnt in sorted(by_status.items()):
            lines.append(f"  {st:25s}: {cnt}")
        urg = sum(1 for b in self.briefings if b.prioridade == Prioridade.URGENTE)
        lines.append(f"Urgentes: {urg}")
        return "\n".join(lines)


def main():
    print("=" * 60)
    print(" BRIEFING CRIATIVO - MYC Producao Artistica")
    print("=" * 60)

    mgr = BriefingManager("Studio Ana Oliveira")

    b1 = mgr.criar_briefing(
        cliente="Tech Startup LTDA", contato="ceo@techstartup.com",
        titulo="Logo TechStart",
        descricao="Criacao de logotipo e identidade visual para startup de tecnologia.",
        objetivo="Identidade visual moderna que comunique inovacao.",
        publico_alvo="Empresas B2B de tecnologia",
        referencia_estilo="Minimalista, cores tech",
        orcamento=5000.0, prioridade=Prioridade.ALTA,
        deadline=date(2024, 3, 15),
    )
    b1.add_entrega("Logo principal", "Logo em vetor", "SVG")
    b1.add_entrega("Brand book", "Manual da marca", "PDF")
    b1.add_revisao("Primeira versao entregue")

    b2 = mgr.criar_briefing(
        cliente="Restaurante Sabor BR", contato="maria@saborbr.com",
        titulo="Posts Instagram", descricao="20 artes para Instagram",
        objetivo="Aumentar engagement", publico_alvo="Jovens 18-35",
        orcamento=3000.0, prioridade=Prioridade.MEDIA, deadline=date(2024, 3, 30),
    )
    b2.add_entrega("Posts Feed", "1080x1080", "PNG", 15)
    b2.add_entrega("Stories", "1080x1920", "PNG", 5)

    b3 = mgr.criar_briefing(
        cliente="Evento Corp SP", contato="eventos@corpsp.com",
        titulo="Banner Conferencia", descricao="Banner para exposicao",
        objetivo="Banner impactante para stand",
        orcamento=800.0, prioridade=Prioridade.URGENTE, deadline=date(2024, 3, 10),
    )
    b3.add_entrega("Banner impresso", "2m x 1m", "PDF")

    print(b1.texto_completo())
    print("\n\n")
    print(b2.texto_completo())
    print("\n\n")
    print(mgr.dashboard())


if __name__ == "__main__":
    main()
