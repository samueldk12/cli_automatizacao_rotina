"""
Verificador de Fatos (Fact-Checker) - Noticias e Midia
========================================================
Cruzamento de informacoes contra fontes, acompanhamento
de status de verificacao e calculo de precisao por jornalista.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class StatusVerificacao(Enum):
    """Status da verificacao de fato."""
    PENDENTE = "Pendente"
    EM_ANALISE = "Em analise"
    VERDADEIRO = "Verdadeiro"
    FALSO = "Falso"
    ENGANOSO = "Enganoso"
    NAO_PODE_VERIFICAR = "Nao pode verificar"
    EXAGERADO = "Exagerado"
    SEM_CONTEXTO = "Sem contexto"


@dataclass
class Fonte:
    """Fonte de informacao para verificacao."""
    nome: str
    tipo: str = ""  # oficial, academico, dados, testemunhal, etc.
    url: str = ""
    confiabilidade: float = 1.0  # 0.0 a 1.0

    def __str__(self) -> str:
        return f"{self.nome} ({self.tipo}) [{self.confiabilidade:.1f}]"


@dataclass
class Afirmacao:
    """Uma afirmacao/claim a ser verificada."""
    texto: str
    autor_afirmacao: str = ""

    fontes_apoio: list[Fonte] = field(default_factory=list)
    fontes_contradicao: list[Fonte] = field(default_factory=list)
    status: StatusVerificacao = StatusVerificacao.PENDENTE
    observacoes: str = ""
    data_verificacao: Optional[date] = None


@dataclass
class Checagem:
    """Resultado completo de uma checagem de fato."""
    id: str = ""
    titulo: str = ""
    afirmacao: Optional[Afirmacao] = None
    jornalista_responsavel: str = ""
    editor_responsavel: str = ""
    data_criacao: date = field(default_factory=date.today)
    conclusao: str = ""
    nota_explicativa: str = ""
    _nota_interna: float = 0.0  # score automatizado

    @property
    def nota(self) -> float:
        """Retorna nota de precisao (0-100)."""
        status_score = {
            StatusVerificacao.VERDADEIRO: 100,
            StatusVerificacao.ENGANOSO: 25,
            StatusVerificacao.EXAGERADO: 40,
            StatusVerificacao.SEM_CONTEXTO: 50,
            StatusVerificacao.FALSO: 0,
            StatusVerificacao.NAO_PODE_VERIFICAR: 0,
            StatusVerificacao.PENDENTE: 0,
            StatusVerificacao.EM_ANALISE: 0,
        }
        if self.afirmacao and self.afirmacao.status != StatusVerificacao.PENDENTE:
            return float(status_score.get(self.afirmacao.status, 0))
        return 0.0

    def __str__(self) -> str:
        status = self.afirmacao.status.value if self.afirmacao else "N/A"
        return f"[{self.id}] {self.titulo} | {status} | Nota: {self.nota:.0f}"


@dataclass
class AvaliacaoJornalista:
    """Avaliacao de precisao de um jornalista."""
    nome: str
    total_checagens: int = 0
    verdadeiras: int = 0
    falsas: int = 0
    enganosas: int = 0
    nao_verificadas: int = 0

    @property
    def taxa_acerto(self) -> float:
        """Taxa de afirmacoes verdadeiras (%)."""
        if self.total_checagens == 0:
            return 0.0
        return (self.verdadeiras / self.total_checagens) * 100

    @property
    def taxa_erro(self) -> float:
        """Taxa de afirmacoes falsas ou enganosas (%)."""
        if self.total_checagens == 0:
            return 0.0
        return ((self.falsas + self.enganosas) / self.total_checagens) * 100


class FactChecker:
    """Sistema de verificacao de fatos para redacao."""

    def __init__(self) -> None:
        self.checagens: list[Checagem] = []
        self.fontes: list[Fonte] = []
        self.avaliacoes: dict[str, AvaliacaoJornalista] = {}

    def cadastrar_fonte(self, fonte: Fonte) -> None:
        """Registra uma fonte confiavel."""
        self.fontes.append(fonte)

    def _gerar_id(self) -> str:
        """Gera ID unico para checagem."""
        return f"FC-{len(self.checagens) + 1:04d}"

    def iniciar_checagem(
        self,
        titulo: str,
        texto_afirmacao: str,
        jornalista: str,
        editor: str = "",
        autor_afirmacao: str = "",
    ) -> Checagem:
        """Inicia uma nova checagem de fato."""
        afirm = Afirmacao(
            texto=texto_afirmacao,
            autor_afirmacao=autor_afirmacao,
        )

        checagem = Checagem(
            id=self._gerar_id(),
            titulo=titulo,
            afirmacao=afirm,
            jornalista_responsavel=jornalista,
            editor_responsavel=editor,
        )

        self.checagens.append(checagem)
        return checagem

    def adicionar_fonte_apoio(self, checagem: Checagem, fonte: Fonte) -> None:
        """Adiciona fonte que apoia a afirmacao."""
        if checagem.afirmacao and fonte not in checagem.afirmacao.fontes_apoio:
            checagem.afirmacao.fontes_apoio.append(fonte)

    def adicionar_fonte_contradicao(
        self,
        checagem: Checagem,
        fonte: Fonte,
    ) -> None:
        """Adiciona fonte que contradiz a afirmacao."""
        if checagem.afirmacao and fonte not in checagem.afirmacao.fontes_contradicacao:
            checagem.afirmacao.fontes_contradicacao.append(fonte)

    def definir_status(
        self,
        checagem: Checagem,
        status: StatusVerificacao,
        conclusao: str = "",
    ) -> None:
        """Define o status final de uma checagem."""
        if checagem.afirmacao:
            checagem.afirmacao.status = status
            checagem.afirmacao.data_verificacao = date.today()
            checagem.conclusao = conclusao

    def calcular_acuracidade(self, fonte: Fonte) -> float:
        """
        Calcula score de confiabilidade de uma fonte.

        Leva em conta historico de verificacoes onde a fonte foi utilizada.
        """
        apoio_count = 0
        contradi_count = 0

        for c in self.checagens:
            if c.afirmacao:
                if fonte in c.afirmacao.fontes_apoio:
                    if c.afirmacao.status == StatusVerificacao.VERDADEIRO:
                        apoio_count += 1
                    elif c.afirmacao.status == StatusVerificacao.FALSO:
                        contradi_count += 1
                if fonte in c.afirmacao.fontes_contradicacao:
                    if c.afirmacao.status == StatusVerificacao.FALSO:
                        apoio_count += 1
                    elif c.afirmacao.status == StatusVerificacao.VERDADEIRO:
                        contradi_count += 1

        total = apoio_count + contradi_count
        if total == 0:
            return fonte.confiabilidade

        return apoio_count / total

    def avaliacao_jornalista(self, jornalista: str) -> AvaliacaoJornalista:
        """
        Gera avaliacao de precisao para um jornalista.

        Analisa todas as checagens onde o jornalista foi responsavel.
        """
        aval = AvaliacaoJornalista(nome=jornalista)

        for c in self.checagens:
            if c.jornalista_responsavel != jornalista:
                continue

            aval.total_checagens += 1

            if c.afirmacao:
                status = c.afirmacao.status
                if status == StatusVerificacao.VERDADEIRO:
                    aval.verdadeiras += 1
                elif status == StatusVerificacao.FALSO:
                    aval.falsas += 1
                elif status == StatusVerificacao.ENGANOSO:
                    aval.enganosas += 1
                elif status == StatusVerificacao.NAO_PODE_VERIFICAR:
                    aval.nao_verificadas += 1

        self.avaliacoes[jornalista] = aval
        return aval

    def resumo_geral(self) -> str:
        """Gera resumo geral de fact-checking."""
        linhas = [
            "=" * 60,
            "RESUMO FACT-CHECKING",
            "=" * 60,
            f"Total de checagens: {len(self.checagens)}",
            f"Fontes cadastradas: {len(self.fontes)}",
        ]

        # Distribuicao por status
        status_count: dict[str, int] = {}
        for c in self.checagens:
            if c.afirmacao:
                status = c.afirmacao.status.value
                status_count[status] = status_count.get(status, 0) + 1

        linhas.append("\nDistribuicao por resultado:")
        for status, count in sorted(status_count.items()):
            linhas.append(f"  {status}: {count}")

        # Avaliacoes de jornalistas
        if self.avaliacoes:
            linhas.append("\nAvaliacao de Jornalistas:")
            for nome, aval in self.avaliacoes.items():
                linhas.append(
                    f"  {nome}: {aval.taxa_acerto:.1f}% acerto, "
                    f"{aval.taxa_erro:.1f}% erro "
                    f"({aval.total_checagens} checagens)"
                )

        return "\n".join(linhas)


def main() -> None:
    """Demonstracao do Fact-Checker."""
    print("=" * 60)
    print("VERIFICADOR DE FATOS - Noticias e Midia")
    print("=" * 60)

    checker = FactChecker()

    # Cadastrar fontes
    print("\n--- Cadastrando Fontes ---")
    fonte_ibge = Fonte("IBGE", "dados", "https://ibge.gov.br", 0.95)
    fonte_bcb = Fonte("Banco Central", "oficial", "https://bcb.gov.br", 0.92)
    fonte_governo = Fonte("Governo Federal", "oficial", "", 0.70)
    checker.cadastrar_fonte(fonte_ibge)
    checker.cadastrar_fonte(fonte_bcb)
    checker.cadastrar_fonte(fonte_governo)
    print(f"  Fonte: {fonte_ibge}")
    print(f"  Fonte: {fonte_bcb}")
    print(f"  Fonte: {fonte_governo}")

    # Iniciar checagens
    print("\n--- Iniciando Checagens ---")
    c1 = checker.iniciar_checagem(
        titulo="Inflacao atingiu 10% em 2025",
        texto_afirmacao="A inflacao acumulada em 2025 foi de 10%",
        jornalista="Maria Santos",
        autor_afirmacao="Deputado X",
    )
    checker.adicionar_fonte_apoio(c1, fonte_ibge)
    checker.adicionar_fonte_apoio(c1, fonte_bcb)
    checker.definir_status(c1, StatusVerificacao.ENGANOSO, "IBGE indica 4,68%")
    print(c1)

    c2 = checker.iniciar_checagem(
        titulo="PIB cresceu 3% no ultimo trimestre",
        texto_afirmacao="O PIB brasileiro cresceu 3% em relacao ao trimestre anterior",
        jornalista="Joao Oliveira",
        autor_afirmacao="Ministro da Economia",
    )
    checker.adicionar_fonte_apoio(c2, fonte_ibge)
    checker.definir_status(c2, StatusVerificacao.VERDADEIRO, "Confirmado pelo IBGE")
    print(c2)

    c3 = checker.iniciar_checagem(
        titulo="Desemprego em minima historica",
        texto_afirmacao="O desemprego atingiu a menor taxa da serie historica",
        jornalista="Maria Santos",
    )
    checker.adicionar_fonte_contradicao(c3, fonte_ibge)
    checker.definir_status(c3, StatusVerificacao.FALSO,
                          "IBGE mostra taxa acima de minimos")
    print(c3)

    # Avaliacoes
    print("\n--- Avaliacao de Jornalistas ---")
    for nome in ["Maria Santos", "Joao Oliveira"]:
        aval = checker.avaliacao_jornalista(nome)
        print(f"  {aval.nome}: {aval.taxa_acerto:.1f}% acerto / "
              f"{aval.taxa_erro:.1f}% erro ({aval.total_checagens} checagens)")

    # Resumo
    print("\n--- Resumo Geral ---")
    print(checker.resumo_geral())

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
