"""
Gerenciador de Editoria - Noticias e Midia
============================================
Organiza redacao: gerencia secoes, atribui reportagens,
acompanha pipelines de story e calendario editorial.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class StatusStory(Enum):
    """Status de uma reportagem no pipeline."""
    PAUTA = "Pauta"
    APURANDO = "Apurando"
    ESCREVENDO = "Escrevendo"
    REVISAO = "Revisao"
    APROVADO = "Aprovado"
    PUBLICADO = "Publicado"
    ARQUIVADO = "Arquivado"


class Secao(Enum):
    """Secoes editoriais."""
    POLITICA = "Politica"
    ECONOMIA = "Economia"
    ESPORTES = "Esportes"
    CULTURA = "Cultura"
    TECNOLOGIA = "Tecnologia"
    SAUDE = "Saude"
    EDUCACAO = "Educacao"
    INTERNACIONAL = "Internacional"
    COTIDIANO = "Cotidiano"


@dataclass
class Reportagem:
    """Uma reportagem/story no pipeline editorial."""
    titulo: str
    secao: Secao
    status: StatusStory = StatusStory.PAUTA
    responsavel: str = ""
    editor: str = ""
    palavra_chave: str = ""
    data_pauta: date = field(default_factory=date.today)
    data_publicacao: Optional[date] = None
    data_limite: Optional[date] = None
    estimativa_palavras: int = 1200
    palavras_escritas: int = 0
    observacoes: str = ""
    tags: list[str] = field(default_factory=list)
    _id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def avancar_pipeline(self) -> Optional[str]:
        """Avanca para o proximo status. Retorna novo status ou None."""
        ordem = [
            StatusStory.PAUTA,
            StatusStory.APURANDO,
            StatusStory.ESCREVENDO,
            StatusStory.REVISAO,
            StatusStory.APROVADO,
            StatusStory.PUBLICADO,
        ]

        idx = 0
        try:
            idx = ordem.index(self.status)
        except ValueError:
            return None

        if idx < len(ordem) - 1:
            self.status = ordem[idx + 1]

            if self.status == StatusStory.PUBLICADO:
                self.data_publicacao = date.today()

            return self.status.value
        return None

    def progresso_escrita(self) -> float:
        """Retorna percentual de progresso da escrita (0-100)."""
        if self.estimativa_palavras <= 0:
            return 0.0
        return min(
            100.0,
            (self.palavras_escritas / self.estimativa_palavras) * 100,
        )

    def esta_atrasada(self) -> bool:
        """Verifica se a reportagem esta atrasada (passou da data limite)."""
        if self.data_limite is None:
            return False
        if self.status in (StatusStory.PUBLICADO, StatusStory.ARQUIVADO):
            return False
        return date.today() > self.data_limite

    def __str__(self) -> str:
        atraso = " [ATRASADA]" if self.esta_atrasada() else ""
        progresso = self.progresso_escrita()

        pub_str = ""
        if self.data_publicacao:
            pub_str = f" | Pub: {self.data_publicacao.strftime('%d/%m')}"

        return (
            f"[{self._id}] {self.titulo} | {self.secao.value} | "
            f"{self.status.value}{atraso} | {progresso:.0f}% escrito"
            f"{pub_str}"
        )


@dataclass
class Editor:
    """Editor da redacao."""
    nome: str
    email: str
    secoes_responsaveis: list[Secao] = field(default_factory=list)
    reportagens_ativas: list[Reportagem] = field(default_factory=list)

    def reportagens_por_status(self) -> dict[str, int]:
        """Conta reportagens por status."""
        contagem = {}
        for r in self.reportagens_ativas:
            status = r.status.value
            contagem[status] = contagem.get(status, 0) + 1
        return contagem


class EditoriaManager:
    """Gerenciador de editoria da redacao."""

    def __init__(self) -> None:
        self.secoes: list[Secao] = list(Secao)
        self.reportagens: list[Reportagem] = []
        self.editores: list[Editor] = []
        self.jornalistas: list[str] = []

    def adicionar_jornalista(self, nome: str) -> None:
        """Adiciona jornalista a lista."""
        if nome not in self.jornalistas:
            self.jornalistas.append(nome)

    def criar_pauta(
        self,
        titulo: str,
        secao: Secao,
        responsavel: str = "",
        editor: str = "",
        data_limite: Optional[date] = None,
        palavras: int = 1200,
        tags: Optional[list[str]] = None,
    ) -> Reportagem:
        """Cria nova pauta/reportagem."""
        if responsavel and responsavel not in self.jornalistas:
            self.adicionar_jornalista(responsavel)

        reportagem = Reportagem(
            titulo=titulo,
            secao=secao,
            responsavel=responsavel,
            editor=editor,
            data_limite=data_limite,
            estimativa_palavras=palavras,
            tags=tags or [],
        )

        self.reportagens.append(reportagem)

        # Associar ao editor se existir
        if editor:
            ed = self._buscar_editor(editor)
            if ed and reportagem not in ed.reportagens_ativas:
                ed.reportagens_ativas.append(reportagem)

        return reportagem

    def _buscar_editor(self, nome: str) -> Optional[Editor]:
        for ed in self.editores:
            if ed.nome == nome:
                return ed
            return None

        return None

    def adicionar_editor(
        self,
        nome: str,
        email: str,
        secoes: Optional[list[Secao]] = None,
    ) -> Editor:
        """Adiciona um editor a redacao."""
        editor = Editor(
            nome=nome,
            email=email,
            secoes_responsaveis=secoes or [],
        )
        self.editores.append(editor)
        return editor

    def listar_por_secao(self, secao: Secao) -> list[Reportagem]:
        """Lista todas as reportagens de uma secao."""
        return [r for r in self.reportagens if r.secao == secao]

    def listar_atrasadas(self) -> list[Reportagem]:
        """Lista todas as reportagens atrasadas."""
        return [r for r in self.reportagens if r.esta_atrasada()]

    def resumo_editorial(self) -> str:
        """Gera resumo editorial completo."""
        linhas = [
            "=" * 60,
            f"RESUMO EDITORIAL - {date.today().strftime('%d/%m/%Y')}",
            "=" * 60,
        ]

        # Contagem por status
        status_count: dict[str, int] = {}
        for r in self.reportagens:
            status = r.status.value
            status_count[status] = status_count.get(status, 0) + 1

        linhas.append("Status:")
        for status, count in sorted(status_count.items()):
            linhas.append(f"  {status}: {count}")

        # Contagem por secao
        linhas.append("\nPor secao:")
        secao_count: dict[str, int] = {}
        for r in self.reportagens:
            secao = r.secao.value
            secao_count[secao] = secao_count.get(secao, 0) + 1

        for secao, count in sorted(secao_count.items()):
            linhas.append(f"  {secao}: {count}")

        # Atrasadas
        atrasadas = self.listar_atrasadas()
        if atrasadas:
            linhas.append(f"\nAtrasadas: {len(atrasadas)}")
            for r in atrasadas:
                linhas.append(f"  - {r.titulo} ({r.data_limite})")

        # Jornalistas
        linhas.append(f"\nJornalistas: {len(self.jornalistas)}")
        for j in self.jornalistas:
            reportagens_jorn = [
                r for r in self.reportagens
                if r.responsavel == j and r.status != StatusStory.ARQUIVADO
            ]
            linhas.append(f"  {j}: {len(reportagens_jorn)} ativas")

        return "\n".join(linhas)

    def exportar_calendario(
        self,
        data_inicio: date,
        data_fim: date,
    ) -> list[Reportagem]:
        """Exporta calendario editorial para um periodo."""
        resultado = []
        for r in self.reportagens:
            if r.status in (StatusStory.ARQUIVADO, StatusStory.PUBLICADO):
                pub = r.data_publicacao
                if pub and data_inicio <= pub <= data_fim:
                    resultado.append(r)
            else:
                if r.data_limite and data_inicio <= r.data_limite <= data_fim:
                    resultado.append(r)

        return sorted(resultado, key=lambda x: x.data_limite or date.max)


def main() -> None:
    """Demonstracao do Gerenciador de Editoria."""
    print("=" * 60)
    print("GERENCIADOR DE EDITORIA - Noticias e Midia")
    print("=" * 60)

    editoria = EditoriaManager()

    # Adicionar pessoal
    editoria.adicionar_jornalista("Maria Santos")
    editoria.adicionar_jornalista("Joao Oliveira")
    editoria.adicionar_jornalista("Ana Costa")
    editoria.adicionar_editor("Pedro Lima", "pedro@redacao.com.br", [Secao.POLITICA, Secao.ECONOMIA])

    # Criar pautas
    print("\n--- Criando Pautas ---")
    editoria.criar_pauta(
        "Reforma tributaria avanca no Senado",
        Secao.POLITICA,
        responsavel="Maria Santos",
        editor="Pedro Lima",
        tags=["politica", "economia", "senado"],
    )
    editoria.criar_pauta(
        "IBGE divulga dados de inflacao",
        Secao.ECONOMIA,
        responsavel="Joao Oliveira",
        tags=["economia", "IBGE", "inflacao"],
    )
    editoria.criar_pauta(
        "Flamengo vence classico no Maracana",
        Secao.ESPORTES,
        responsavel="Ana Costa",
    )

    # Avançar pipeline
    print("\n--- Avancando Pipeline ---")
    for r in editoria.reportagens:
        r.avancar_pipeline()
        print(f"  {r}")

    # Simular escrita
    editoria.reportagens[0].palavras_escritas = 900
    editoria.reportagens[0].data_limite = date(2026, 4, 10)
    editoria.reportagens[0].avancar_pipeline()  # Avanca para Escrito

    print(editoria.reportagens[0])

    # Resumo
    print("\n--- Resumo Editorial ---")
    print(editoria.resumo_editorial())

    # Calendario
    print("\n--- Calendario (Abril/2026) ---")
    calendario = editoria.exportar_calendario(
        date(2026, 4, 1),
        date(2026, 4, 30),
    )
    for r in calendario:
        print(f"  {r.data_limite}: {r.titulo}")

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
