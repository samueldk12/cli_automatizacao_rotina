"""
Portfolio Manager - Digital Art Portfolio
Organizes artworks by project/tags/medium, tracks creation stats,
manages client commissions with pricing, and revenue analytics.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import Optional


class ArtworkStatus(Enum):
    EM_PROGRESS = "Em Progresso"
    CONCLUIDO = "Concluido"
    ARQUIVADO = "Arquivado"
    VENDIDO = "Vendido"


@dataclass
class Artwork:
    title: str
    medium: str
    tags: list[str] = field(default_factory=list)
    project: str = ""
    status: ArtworkStatus = ArtworkStatus.EM_PROGRESS
    created_date: Optional[date] = None
    completed_date: Optional[date] = None
    price: float = 0.0
    hours_spent: float = 0.0

    @property
    def is_sold(self) -> bool:
        return self.status == ArtworkStatus.VENDIDO

    def mark_completed(self):
        self.status = ArtworkStatus.CONCLUIDO
        self.completed_date = date.today()

    def mark_sold(self, sale_price: float):
        self.status = ArtworkStatus.VENDIDO
        self.price = sale_price


@dataclass
class Commission:
    client_name: str
    client_email: str
    description: str
    budget: float = 0.0
    deposit: float = 0.0
    status: str = "pending"
    deadline: Optional[date] = None
    revisions_left: int = 3

    @property
    def remaining_balance(self) -> float:
        return self.budget - self.deposit


class PortfolioManager:
    """Manages a digital art portfolio with commissions and stats."""

    def __init__(self, artist_name: str, hourly_rate: float = 50.0):
        self.artist_name = artist_name
        self.hourly_rate = hourly_rate
        self.artworks: list[Artwork] = []
        self.commissions: list[Commission] = []

    def add_artwork(self, artwork: Artwork):
        self.artworks.append(artwork)

    def add_commission(self, commission: Commission):
        self.commissions.append(commission)

    def find_by_tag(self, tag: str) -> list[Artwork]:
        return [a for a in self.artworks if tag.lower() in [t.lower() for t in a.tags]]

    def find_by_project(self, project: str) -> list[Artwork]:
        return [a for a in self.artworks if a.project.lower() == project.lower()]

    def commission_price(self, hours_estimate: float, materials_cost: float = 0.0, complexity_factor: float = 1.0) -> float:
        """Precifica comissao: valor_hora * horas * complexidade + materiais."""
        return (self.hourly_rate * hours_estimate * complexity_factor) + materials_cost

    def stats(self) -> str:
        total = len(self.artworks)
        sold = sum(1 for a in self.artworks if a.is_sold)
        in_progress = sum(1 for a in self.artworks if a.status == ArtworkStatus.EM_PROGRESS)
        completed = sum(1 for a in self.artworks if a.status == ArtworkStatus.CONCLUIDO)
        total_revenue = sum(a.price for a in self.artworks if a.is_sold)
        total_hours = sum(a.hours_spent for a in self.artworks)
        avg_price = total_revenue / sold if sold > 0 else 0.0

        mediums: dict[str, int] = {}
        for a in self.artworks:
            mediums[a.medium] = mediums.get(a.medium, 0) + 1

        tag_counts: dict[str, int] = {}
        for a in self.artworks:
            for t in a.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        paid_comm = sum(1 for c in self.commissions if c.status == "paid")
        pending_comm = sum(1 for c in self.commissions if c.status in ("pending", "in_progress"))
        comm_revenue = sum(c.budget for c in self.commissions if c.status == "paid")

        lines = [
            "=" * 60,
            f" ESTATISTICAS DO PORTFOLIO - {self.artist_name}",
            "=" * 60,
            f"Total de obras: {total}",
            f"  Em progresso: {in_progress}",
            f"  Concluidas: {completed}",
            f"  Vendidas: {sold}",
            f"Horas totais trabalhadas: {total_hours:.1f}h",
            f"Receita de vendas: R$ {total_revenue:,.2f}",
            f"Preco medio por obra vendida: R$ {avg_price:,.2f}",
            "",
            "Por meio:",
        ]
        for med, cnt in sorted(mediums.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {med:15s}: {cnt} obras")
        lines.append("\nTop 5 tags:")
        for tag, count in top_tags:
            lines.append(f"  #{tag}: {count}")
        lines.append(f"\nComissoes: {len(self.commissions)}")
        lines.append(f"  Pagas: {paid_comm}")
        lines.append(f"  Pendentes: {pending_comm}")
        lines.append(f"  Receita de comissoes: R$ {comm_revenue:,.2f}")
        lines.append(f"  Receita total: R$ {total_revenue + comm_revenue:,.2f}")
        return "\n".join(lines)


def main():
    print("=" * 60)
    print(" GERENCIADOR DE PORTFOLIO - MYC Producao Artistica")
    print("=" * 60)

    manager = PortfolioManager("Ana Oliveira", hourly_rate=75.0)

    manager.add_artwork(Artwork("Floresta Digital", "Digital Art",
        tags=["natureza", "fantasia", "paisagem"], project="Natureza Digital",
        status=ArtworkStatus.CONCLUIDO, hours_spent=12.5))
    manager.add_artwork(Artwork("Cyberpunk City", "Digital Art",
        tags=["scifi", "cidade", "cyberpunk"], project="Futuro",
        status=ArtworkStatus.VENDIDO, price=2500.0, hours_spent=20.0))
    manager.add_artwork(Artwork("Retrato Abstrato", "Oleo sobre tela",
        tags=["retrato", "abstrato"], status=ArtworkStatus.VENDIDO,
        price=3200.0, hours_spent=15.0))
    manager.add_artwork(Artwork("Aquarela do Brasil", "Aquarela",
        tags=["natureza", "brasil"], project="Brasil Series",
        status=ArtworkStatus.EM_PROGRESS, hours_spent=8.0))
    manager.add_artwork(Artwork("Portal Dimensional", "Digital Art",
        tags=["fantasia", "scifi"], project="Futuro",
        status=ArtworkStatus.EM_PROGRESS, hours_spent=5.0))

    # Commission pricing
    comm_price = manager.commission_price(hours_estimate=25, materials_cost=150.0, complexity_factor=1.3)
    print(f"\nPreco comissao (25h, materiais R$150, complexidade 1.3x): R$ {comm_price:,.2f}")

    manager.add_commission(Commission(
        client_name="Carlos Mendes", client_email="carlos@email.com",
        description="Ilustracao para capa de livro de fantasia",
        budget=comm_price, deposit=comm_price * 0.5, status="in_progress",
        deadline=date(2024, 3, 15),
    ))

    print(manager.stats())

    # Search examples
    print("\n--- Obras com tag 'natureza' ---")
    for a in manager.find_by_tag("natureza"):
        print(f"  {a.title} ({a.medium})")

    print("\n--- Projeto 'Futuro' ---")
    for a in manager.find_by_project("Futuro"):
        print(f"  {a.title} - {a.status.value}")


if __name__ == "__main__":
    main()
