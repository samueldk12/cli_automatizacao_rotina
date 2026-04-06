"""
Gerenciador de Campeonato - Empresa Esportiva
===============================================
Gerencia tabela de classificacao de ligas, agenda jogos,
calcula desempates e gerencia competicoes esportivas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Time:
    """Time/participante do campeonato."""
    nome: str
    cidade: str = ""
    tecnico: str = ""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Time):
            return self.nome == other.nome
        return False

    def __hash__(self) -> int:
        return hash(self.nome)

    def __repr__(self) -> str:
        return self.nome


@dataclass
class Jogo:
    """Um jogo/partida do campeonato."""
    rodada: int
    mandante: Time
    visitante: Time
    gols_mandante: Optional[int] = None
    gols_visitante: Optional[int] = None
    data: str = ""
    local: str = ""

    @property
    def realizado(self) -> bool:
        return self.gols_mandante is not None and self.gols_visitante is not None

    @property
    def vencedor(self) -> Optional[Time]:
        if not self.realizado:
            return None
        if self.gols_mandante > self.gols_visitante:
            return self.mandante
        elif self.gols_visitante > self.gols_mandante:
            return self.visitante
        else:
            return None  # Empate

    def definir_placar(self, gols_mandante: int, gols_visitante: int) -> None:
        """Define o placar do jogo."""
        self.gols_mandante = gols_mandante
        self.gols_visitante = gols_visitante

    def __str__(self) -> str:
        placar = f"{self.gols_mandante} x {self.gols_visitante}" if self.realizado else "x"
        return (
            f"Rodada {self.rodada}: {self.mandante} {placar} {self.visitante}"
        )


@dataclass
class ClassificacaoTime:
    """Posicao na tabela de classificacao."""
    time: Time
    posicao: int = 0
    pontos: int = 0
    jogos: int = 0
    vitorias: int = 0
    empates: int = 0
    derrotas: int = 0
    gols_pro: int = 0
    gols_contra: int = 0
    saldo_gols: int = 0
    aproveitamento: float = 0.0
    campanha: str = ""

    def atualizar(self, jogo: Jogo, time: Time) -> None:
        """Atualiza stats baseado em um jogo."""
        self.jogos += 1

        if jogo.mandante == time:
            self.gols_pro += jogo.gols_mandante or 0
            self.gols_contra += jogo.gols_visitante or 0
        else:
            self.gols_pro += jogo.gols_visitante or 0
            self.gols_contra += jogo.gols_mandante or 0

        self.saldo_gols = self.gols_pro - self.gols_contra

        if jogo.vencedor == time:
            self.vitorias += 1
            self.pontos += 3
        elif jogo.vencedor is None:  # Empate
            self.empates += 1
            self.pontos += 1
        else:
            self.derrotas += 1

        self._calcular_aproveitamento()

    def _calcular_aproveitamento(self) -> None:
        """Calcula % de aproveitamento."""
        if self.jogos > 0:
            possiveis = self.jogos * 3
            self.aproveitamento = (self.pontos / possiveis) * 100


class CampeonatoManager:
    """Gerenciador de campeonato/liga."""

    def __init__(
        self,
        nome_campeonato: str,
        pontos_vitoria: int = 3,
        pontos_empate: int = 1,
        pontos_derrota: int = 0,
    ) -> None:
        self.nome_campeonato = nome_campeonato
        self.pontos_vitoria = pontos_vitoria
        self.pontos_empate = pontos_empate
        self.pontos_derrota = pontos_derrota
        self.times: list[Time] = []
        self.jogos: list[Jogo] = []
        self.rodada_atual = 0

    def adicionar_time(self, time: Time) -> None:
        """Adiciona time ao campeonato."""
        self.times.append(time)

    def gerar_rodada(self, rodada: int) -> list[Jogo]:
        """
        Gera jogos de uma rodada (todos-contra-todos).

        Usa algoritmo round-robin simplificado.
        """
        if len(self.times) % 2 != 0:
            # Adiciona 'bye' se numero impar
            times_rodada = self.times + [Time("BYE")]
        else:
            times_rodada = list(self.times)

        n = len(times_rodada)
        jogos_rodada = []

        for i in range(n // 2):
            mandante = times_rodada[i]
            visitante = times_rodada[n - 1 - i]

            if mandante.nome == "BYE" or visitante.nome == "BYE":
                continue

            jogo = Jogo(
                rodada=rodada,
                mandante=mandante,
                visitante=visitante,
            )
            jogos_rodada.append(jogo)
            self.jogos.append(jogo)

        self.rodada_atual = rodada
        return jogos_rodada

    def gerar_campeonato(self) -> list[list[Jogo]]:
        """
        Gera todas as rodadas do campeonato (turno).

        Returns:
            Lista de rodadas, cada uma com lista de jogos.
        """
        n = len(self.times)
        if n < 2:
            return []

        # Round-robin com algoritmo padrao
        times_rodada = list(self.times)
        if len(times_rodada) % 2 != 0:
            times_rodada.append(Time("BYE"))

        n_times = len(times_rodada)
        num_rodadas = n_times - 1
        todas_rodadas: list[list[Jogo]] = []

        for rodada in range(1, num_rodadas + 1):
            jogos_rodada = []
            for i in range(n_times // 2):
                mandante = times_rodada[i]
                visitante = times_rodada[n_times - 1 - i]

                if mandante.nome == "BYE" or visitante.nome == "BYE":
                    continue

                jogo = Jogo(
                    rodada=rodada,
                    mandante=mandante,
                    visitante=visitante,
                )
                jogos_rodada.append(jogo)
                self.jogos.append(jogo)

            todas_rodadas.append(jogos_rodada)

            # Rotacao round-robin
            times_rodada.insert(1, times_rodada.pop())

        return todas_rodadas

    def _gerar_classificacao(self) -> list[ClassificacaoTime]:
        """Calcula tabela de classificacao completa."""
        classificacao: dict[str, ClassificacaoTime] = {}

        for time in self.times:  # Inicializa todos
            classificacao[time.nome] = ClassificacaoTime(time=time)

        for jogo in self.jogos:
            if not jogo.realizado:
                continue

            # Atualiza mandante
            if jogo.mandante.nome in classificacao:
                classificacao[jogo.mandante.nome].atualizar(jogo, jogo.mandante)

            # Atualiza visitante (se nao for BYE)
            if jogo.visitante.nome != "BYE" and jogo.visitante.nome in classificacao:
                classificacao[jogo.visitante.nome].atualizar(
                    jogo, jogo.visitante
                )

        # Ordena por pontos, depois saldo de gols, depois gols pro
        lista = list(classificacao.values())
        lista.sort(
            key=lambda x: (x.pontos, x.saldo_gols, x.gols_pro),
            reverse=True,
        )

        # Define posicoes
        for i, c in enumerate(lista, 1):
            c.posicao = i

        return lista

    def tabela_classificacao(self) -> list[ClassificacaoTime]:
        """Retorna tabela de classificacao."""
        return self._gerar_classificacao()

    def exibir_tabela(self) -> str:
        """Exibe tabela de classificacao formatada."""
        classificacao = self._gerar_classificacao()

        linhas = [
            "=" * 70,
            f"TABELA - {self.nome_campeonato}",
            "=" * 70,
            (
                f"{'#':3s} {'Time':<20s} {'P':3s} {'J':3s} {'V':3s} "
                f"{'E':3s} {'D':3s} {'GP':3s} {'GC':3s} {'SG':3s} {'%':6s}"
            ),
            "-" * 70,
        ]

        for c in classificacao:
            linhas.append(
                f"{c.posicao:3d} {c.time.nome:<20s} {c.pontos:3d} {c.jogos:3d} "
                f"{c.vitorias:3d} {c.empates:3d} {c.derrotas:3d} "
                f"{c.gols_pro:3d} {c.gols_contra:3d} {c.saldo_gols:3d} "
                f"{c.aproveitamento:5.1f}%"
            )

        return "\n".join(linhas)

    def artilharia_simulada(self) -> dict[str, int]:
        """Simulacao de artilharia do campeonato por time."""
        gols: dict[str, int] = {}
        for jogo in self.jogos:
            if jogo.realizado:
                gols[jogo.mandante.nome] = gols.get(
                    jogo.mandante.nome, 0
                ) + (jogo.gols_mandante or 0)
                if jogo.visitante.nome != "BYE":
                    gols[jogo.visitante.nome] = gols.get(
                        jogo.visitante.nome, 0
                    ) + (jogo.gols_visitante or 0)
        return gols

    def resumo(self) -> str:
        """Resumo do campeonato."""
        jogos_realizados = [j for j in self.jogos if j.realizado]
        total_gols = sum(
            (j.gols_mandante or 0) + (j.gols_visitante or 0)
            for j in jogos_realizados
        )

        linhas = [
            "=" * 60,
            f"RESUMO - {self.nome_campeonato}",
            "=" * 60,
            f"Times: {len(self.times)}",
            f"Jogos realizados: {len(jogos_realizados)}/{len(self.jogos)}",
            f"Total de gols: {total_gols}",
        ]

        if jogos_realizados:
            media = total_gols / len(jogos_realizados)
            linhas.append(f"Media de gols por jogo: {media:.2f}")

        # Maior goleada
        if jogos_realizados:
            maior = max(
                jogos_realizados,
                key=lambda j: abs((j.gols_mandante or 0) - (j.gols_visitante or 0)),
            )
            linhas.append(
                f"Maior goleada: {maior.mandante} {maior.gols_mandante} x "
                f"{maior.gols_visitante} {maior.visitante}"
            )

        return "\n".join(linhas)


def main() -> None:
    """Demonstracao do Campeonato Manager."""
    print("=" * 60)
    print("GERENCIADOR DE CAMPEONATO - Empresa Esportiva")
    print("=" * 60)

    camp = CampeonatoManager("Campeonato Brasileiro Demo 2026")

    # Adicionar times
    print("\n--- Times Participantes ---")
    times_nomes = [
        "Flamengo", "Palmeiras", "Corinthians", "Sao Paulo",
        "Santos", "Gremio", "Internacional", "Atletico-MG",
    ]
    times = []
    for nome in times_nomes:
        t = Time(nome=nome)
        times.append(t)
        camp.adicionar_time(t)
        print(f"  {t}")

    # Gerar campeonato
    print("\n--- Gerando Campeonato ---")
    rodadas = camp.gerar_campeonato()
    print(f"Total de rodadas: {len(rodadas)}")
    print(f"Total de jogos: {len(camp.jogos)}")

    # Simular resultados
    print("\n--- Simulando Resultados ---")
    import random
    random.seed(42)

    for jogo in camp.jogos:
        gols_m = random.randint(0, 4)
        gols_v = random.randint(0, 4)
        jogo.definir_placar(gols_m, gols_v)

    print(f"Jogos simulados: {len(camp.jogos)}")

    # Tabela
    print("\n--- Tabela de Classificacao ---")
    print(camp.exibir_tabela())

    # Resumo
    print("\n--- Resumo ---")
    print(camp.resumo())

    # Artilharia
    print("\n--- Artilharia por Time ---")
    art = camp.artilharia_simulada()
    for time, gols in sorted(art.items(), key=lambda x: -x[1]):
        print(f"  {time}: {gols} gols")

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
