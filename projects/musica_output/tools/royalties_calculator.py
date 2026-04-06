"""
Calculadora de Royalties para Streaming de Musica - Brasil.

Estima ganhos do Spotify (~$0.004/stream), Apple Music, YouTube Music,
Deezer, calcula splits de compositor/editora (50/50 PRO), distribuicao
ECAD e gera relatorios de royalties.
"""

from __future__ import annotations

import dataclasses
from datetime import date
from enum import Enum
from typing import Optional

# Dolar para Real (aproximado)
USD_BRL = 5.0


# ---------------------------------------------------------------------------
# Enums & Dataclasses
# ---------------------------------------------------------------------------

class Plataforma(str, Enum):
    SPOTIFY = "Spotify"
    APPLE_MUSIC = "Apple Music"
    YOUTUBE_MUSIC = "YouTube Music"
    DEEZER = "Deezer"
    AMAZON_MUSIC = "Amazon Music"
    TIDAL = "Tidal"


@dataclasses.dataclass
class ObraMusical:
    """Representa uma obra musical."""
    titulo: str
    artistas: list[str] = dataclasses.field(default_factory=list)
    compositor: str = ""
    editora: str = ""
    isrc: str = ""
    duracao_segundos: int = 0


@dataclasses.dataclass
class StreamsEstimativa:
    """Estimativa de streams por plataforma."""
    obra: ObraMusical
    periodo: str  # ex: "2024-Q1"
    streams: dict[Plataforma, int] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class RoyaltyPlataforma:
    """Detalhamento de royalties por plataforma."""
    plataforma: Plataforma
    streams: int
    valor_por_stream: float
    total_bruto: float
    total_bruto_brl: float


@dataclasses.dataclass
class DistribuicaoECAD:
    """Distribuicao de royalties ECAD."""
    total: float
    percentual_autor: float = 50.0
    percentual_editora: float = 50.0
    valor_autor: float = 0.0
    valor_editora: float = 0.0


@dataclasses.dataclass
class RelatorioRoyalties:
    """Relatorio completo de royalties."""
    obra: ObraMusical
    periodo: str
    detalhamento_plataformas: list[RoyaltyPlataforma]
    distribuicao_ecad: DistribuicaoECAD
    total_streams: int
    total_bruto: float
    total_bruto_brl: float
    total_autor_brl: float
    total_editora_brl: float


# ---------------------------------------------------------------------------
# Valores por stream (em USD)
# ---------------------------------------------------------------------------

VALOR_POR_STREAM: dict[Plataforma, float] = {
    Plataforma.SPOTIFY: 0.004,
    Plataforma.APPLE_MUSIC: 0.008,
    Plataforma.YOUTUBE_MUSIC: 0.002,
    Plataforma.DEEZER: 0.005,
    Plataforma.AMAZON_MUSIC: 0.004,
    Plataforma.TIDAL: 0.013,
}


# ---------------------------------------------------------------------------
# Calculos
# ---------------------------------------------------------------------------

def calcular_royalty_plataforma(plataforma: Plataforma, streams: int) -> RoyaltyPlataforma:
    """Calcula royalties de uma plataforma especifica."""
    valor = VALOR_POR_STREAM.get(plataforma, 0.003)
    total = streams * valor
    return RoyaltyPlataforma(
        plataforma=plataforma,
        streams=streams,
        valor_por_stream=valor,
        total_bruto=round(total, 2),
        total_bruto_brl=round(total * USD_BRL, 2),
    )


def estimar_ecad(royalties_brl: float, percentual_autor: float = 50.0) -> DistribuicaoECAD:
    """Calcula a distribuicao ECAD autor/editora."""
    pct_autor = percentual_autor / 100
    pct_editora = 1.0 - pct_autor
    return DistribuicaoECAD(
        total=royalties_brl,
        percentual_autor=pct_autor * 100,
        percentual_editora=pct_editora * 100,
        valor_autor=round(royalties_brl * pct_autor, 2),
        valor_editora=round(royalties_brl * pct_editora, 2),
    )


def gerar_relatorio(obra: ObraMusical, periodo: str,
                    streams_estimativa: dict[Plataforma, int],
                    percentual_autor: float = 50.0) -> RelatorioRoyalties:
    """Gera relatorio completo de royalties."""
    detalhamento: list[RoyaltyPlataforma] = []
    total_streams = 0
    total_bl = 0.0
    total_brl = 0.0

    for plat, streams in streams_estimativa.items():
        rp = calcular_royalty_plataforma(plat, streams)
        detalhamento.append(rp)
        total_streams += rp.streams
        total_bl += rp.total_bruto
        total_brl += rp.total_bruto_brl

    distribuicao = estimar_ecad(round(total_brl, 2), percentual_autor)

    return RelatorioRoyalties(
        obra=obra,
        periodo=periodo,
        detalhamento_plataformas=detalhamento,
        distribuicao=distribuicao,
        total_streams=total_streams,
        total_bruto=round(total_bl, 2),
        total_bruto_brl=round(total_brl, 2),
        total_autor_brl=distribuicao.valor_autor,
        total_editora_brl=distribuicao.valor_editora,
    )


def comparar_plataformas(streams_base: int) -> str:
    """Compara ganhos estimados entre plataformas para o mesmo numero de streams."""
    linhas = ["\n  COMPARATIVO DE PLATAFORMAS:"]
    for plat in Plataforma:
        rp = calcular_royalty_plataforma(plat, streams_base)
        linhas.append(
            f"    {plat.value:20s}: R${rp.total_bruto_brl:>10.2f} "
            f"(R${rp.valor_por_stream * USD_BRL:.5f}/stream)"
        )
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Formatar
# ---------------------------------------------------------------------------

def formatar_relatorio(rel: RelatorioRoyalties) -> str:
    """Formata o relatorio de royalties como texto."""
    linhas = ["=" * 60]
    linhas.append(f"  RELATORIO DE ROYALTIES - {rel.obra.titulo}")
    linhas.append("=" * 60)
    if rel.obra.compositor:
        linhas.append(f"  Compositor: {rel.obra.compositor}")
    if rel.obra.editora:
        linhas.append(f"  Editora: {rel.obra.editora}")
    if rel.obra.isrc:
        linhas.append(f"  ISRC: {rel.obra.isrc}")
    linhas.append(f"  Periodo: {rel.periodo}")
    linhas.append(f"  Total Streams: {rel.total_streams:,}")
    linhas.append("")
    linhas.append("  DETALHAMENTO POR PLATAFORMA:")
    for rp in rel.detalhamento_plataformas:
        linhas.append(
            f"    {rp.plataforma.value:20s}: {rp.streams:>10,} streams | "
            f"R${rp.total_bruto_brl:>10.2f} (R${rp.valor_por_stream * USD_BRL:.5f}/stream)"
        )
    linhas.append("")
    linhas.append("-" * 60)
    linhas.append(f"  Total Bruto (USD): ${rel.total_bruto:,.2f}")
    linhas.append(f"  Total Bruto (BRL): R${rel.total_bruto_brl:,.2f}")
    linhas.append("")
    d = rel.distribuicao_ecad
    linhas.append(f"  Distribuicao ECAD ({d.percentual_autor:.0f}/{d.percentual_editora:.0f}):")
    linhas.append(f"    Autor (Compositor):    R${d.valor_autor:,.2f}")
    linhas.append(f"    Editora (Publicadora): R${d.valor_editora:,.2f}")
    linhas.append("=" * 60)
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main() -> None:
    """Demonstracao da calculadora de royalties."""
    print("\n>>> CALCULADORA DE ROYALTIES MUSICAIS\n")

    obra1 = ObraMusical(
        titulo="Saudade de Verao",
        artistas=["Ana Clara"],
        compositor="Ana Clara",
        editora="Som Brasil Musicas",
        isrc="BRUMG2400001",
        duracao_segundos=205,
    )

    # Exemplo 1: Musica popular (100k streams no Spotify, 30k Apple, 15k YT Music, 8k Deezer)
    rel1 = gerar_relatorio(
        obra=obra1,
        periodo="2024-Q1",
        streams_estimativa={
            Plataforma.SPOTIFY: 100_000,
            Plataforma.APPLE_MUSIC: 30_000,
            Plataforma.YOUTUBE_MUSIC: 15_000,
            Plataforma.DEEZER: 8_000,
        },
    )
    print(formatar_relatorio(rel1))
    print(comparar_plataformas(100_000))

    print("\n")

    # Exemplo 2: Musica viral (1 milhoes de streams)
    obra2 = ObraMusical(
        titulo="Hit do Verao 2024",
        artistas=["MC Funk Carioca", "DJ Beats"],
        compositor="MC Funk Carioca",
        editora="Funk Records",
        isrc="BRFRG2400099",
        duracao_segundos=155,
    )
    rel2 = gerar_relatorio(
        obra=obra2,
        periodo="2024-Q2",
        streams_estimativa={
            Plataforma.SPOTIFY: 500_000,
            Plataforma.APPLE_MUSIC: 100_000,
            Plataforma.YOUTUBE_MUSIC: 200_000,
            Plataforma.DEEZER: 50_000,
            Plataforma.AMAZON_MUSIC: 30_000,
        },
        percentual_autor=50.0,
    )
    print(formatar_relatorio(rel2))

    # Exemplo 3: Split diferente (artista independente fica com 100%)
    obra3 = ObraMusical(
        titulo="Indie Acustico #5",
        artistas=["Luis Independente"],
        compositor="Luis Independente",
        editora="Auto-publicado",
    )
    rel3 = gerar_relatorio(
        obra=obra3,
        periodo="2024-Q3",
        streams_estimativa={
            Plataforma.SPOTIFY: 50_000,
            Plataforma.YOUTUBE_MUSIC: 10_000,
        },
        percentual_autor=100.0,
    )
    print(formatar_relatorio(rel3))


if __name__ == "__main__":
    main()
