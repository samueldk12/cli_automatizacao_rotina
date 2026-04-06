"""
Estatisticas de Atleta - Sports Performance Tracker
Tracks goals, assists, matches, cards, per-game averages,
form tracking, efficiency ratings, player comparison.
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PartidaStats:
    data: str
    adversario: str
    gols: int = 0
    assistencias: int = 0
    cartoes_amarelos: int = 0
    cartoes_vermelhos: int = 0
    minutos_jogados: int = 0
    passes_completos: int = 0
    passes_tentados: int = 0
    finalicoes: int = 0
    finalicoes_gol: int = 0
    desarmes: int = 0
    interceptacoes: int = 0
    @property
    def passe_precision(self) -> float:
        return (self.passes_completos/self.passes_tentados*100) if self.passes_tentados else 0.0
    @property
    def avaliacao(self) -> float:
        nota = 5.0 + self.gols*1.5 + self.assistencias*1.0 + self.desarmes*0.2 + self.interceptacoes*0.2
        if self.passes_tentados > 0:
            nota += (self.passe_precision/100)*0.5
        nota -= self.cartoes_amarelos*0.5 + self.cartoes_vermelhos*2.0
        return round(min(10.0, max(0.0, nota)), 1)

@dataclass
class EstatisticasTemporada:
    atleta: str
    time: str
    posicao: str
    temporada: str
    partidas_jogadas: int = 0
    minutos_totais: int = 0
    gols: int = 0
    assistencias: int = 0
    cartoes_amarelos: int = 0
    cartoes_vermelhos: int = 0
    passes_completos: int = 0
    passes_tentados: int = 0
    finalicoes: int = 0
    finalicoes_gol: int = 0
    desarmes: int = 0
    interceptacoes: int = 0
    partidas: list[PartidaStats] = field(default_factory=list)
    @property
    def gols_por_jogo(self): return round(self.gols/self.partidas_jogadas,2) if self.partidas_jogadas else 0.0
    @property
    def assist_por_jogo(self): return round(self.assistencias/self.partidas_jogadas,2) if self.partidas_jogadas else 0.0
    @property
    def min_por_gol(self): return round(self.minutos_totais/self.gols,1) if self.gols else 0.0
    @property
    def passe_precision(self): return round((self.passes_completos/self.passes_tentados)*100,1) if self.passes_tentados else 0.0
    @property
    def aprov_finalicoes(self): return round((self.finalicoes_gol/self.finalicoes)*100,1) if self.finalicoes else 0.0
    @property
    def nota_media(self): return round(sum(p.avaliacao for p in self.partidas)/len(self.partidas),1) if self.partidas else 0.0
    @property
    def forma_5jogos(self):
        ultimas = self.partidas[-5:]
        r = []
        for p in ultimas:
            if p.avaliacao >= 8.0: r.append("E")
            elif p.avaliacao >= 6.0: r.append("B")
            elif p.avaliacao >= 4.5: r.append("R")
            else: r.append("F")
        return r
    def add_partida(self, p):
        self.partidas.append(p)
        self.partidas_jogadas += 1; self.minutos_totais += p.minutos_jogados
        self.gols += p.gols; self.assistencias += p.assistencias
        self.cartoes_amarelos += p.cartoes_amarelos; self.cartoes_vermelhos += p.cartoes_vermelhos
        self.passes_completos += p.passes_completos; self.passes_tentados += p.passes_tentados
        self.finalicoes += p.finalicoes; self.finalicoes_gol += p.finalicoes_gol
        self.desarmes += p.desarmes; self.interceptacoes += p.interceptacoes
    def relatorio(self) -> str:
        forma = " -> ".join(self.forma_5jogos) if self.forma_5jogos else "N/A"
        lines = [
            "="*60, f" ESTATISTICAS DO ATLETA - {self.atleta}", "="*60,
            f"Time: {self.time} | Posicao: {self.posicao} | Temporada: {self.temporada}",
            f"Partidas: {self.partidas_jogadas} | Minutos: {self.minutos_totais}", "",
            "--- OFENSIVO ---",
            f"Gols: {self.gols} ({self.gols_por_jogo}/jogo)",
            f"Assistencias: {self.assistencias} ({self.assist_por_jogo}/jogo)",
            f"Min/Gol: {self.min_por_gol:.1f}" if self.gols else "Min/Gol: N/A",
            f"Finalizacoes: {self.finalicoes_gol}/{self.finalicoes} ({self.aprov_finalicoes}%)", "",
            "--- PASSES ---",
            f"Passes: {self.passes_completos}/{self.passes_tentados} ({self.passe_precision}%)", "",
            "--- DEFENSIVO ---",
            f"Desarmes: {self.desarmes} | Interceptacoes: {self.interceptacoes}", "",
            "--- DISCIPLINA ---",
            f"Amarelos: {self.cartoes_amarelos} | Vermelhos: {self.cartoes_vermelhos}", "",
            "--- AVALIACAO ---",
            f"Nota Media: {self.nota_media}/10", f"Forma (ult 5): {forma}",
        ]
        return "\n".join(lines)

def comparar_atletas(a1, a2) -> str:
    lines = ["="*60, " COMPARACAO DE ATLETAS", "="*60,
             f"  {'Estatistica':20s}: {a1.atleta:20s} | {a2.atleta:20s}", "-"*60,
             f"  {'Partidas':20s}: {a1.partidas_jogadas:20d} | {a2.partidas_jogadas:20d}",
             f"  {'Gols':20s}: {a1.gols:20d} | {a2.gols:20d}",
             f"  {'Gols/Jogo':20s}: {a1.gols_por_jogo:20.2f} | {a2.gols_por_jogo:20.2f}",
             f"  {'Assistencias':20s}: {a1.assistencias:20d} | {a2.assistencias:20d}",
             f"  {'Passe %':20s}: {a1.passe_precision:20.1f} | {a2.passe_precision:20.1f}",
             f"  {'Nota Media':20s}: {a1.nota_media:20.1f} | {a2.nota_media:20.1f}",
             f"  {'Forma':20s}: {'-'.join(a1.forma_5jogos):20s} | {'-'.join(a2.forma_5jogos):20s}",
             ]
    return "\n".join(lines)

def main():
    print("="*60)
    print(" ESTATISTICAS DE ATLETA - MYC Esporte")
    print("="*60)
    e1 = EstatisticasTemporada("Gabriel Silva", "FC Paulista", "Atacante", "2024")
    for j in [
        {"data":"2024-03-01","adversario":"Santos","gols":2,"assistencias":1,"minutos_jogados":90,"passes_completos":32,"passes_tentados":41,"finalicoes":5,"finalicoes_gol":3,"desarmes":1},
        {"data":"2024-03-08","adversario":"Corinthians","gols":0,"assistencias":0,"minutos_jogados":75,"passes_completos":18,"passes_tentados":30,"finalicoes":2,"finalicoes_gol":0},
        {"data":"2024-03-15","adversario":"Palmeiras","gols":1,"assistencias":1,"minutos_jogados":90,"passes_completos":40,"passes_tentados":48,"finalicoes":4,"finalicoes_gol":2,"desarmes":2},
        {"data":"2024-03-22","adversario":"Sao Paulo","gols":3,"assistencias":0,"minutos_jogados":88,"passes_completos":25,"passes_tentados":35,"finalicoes":6,"finalicoes_gol":4,"desarmes":1},
        {"data":"2024-03-29","adversario":"Flamengo","gols":1,"assistencias":2,"minutos_jogados":90,"passes_completos":38,"passes_tentados":45,"finalicoes":3,"finalicoes_gol":1,"desarmes":3},
    ]:
        e1.add_partida(PartidaStats(**j))
    print(e1.relatorio())
    e2 = EstatisticasTemporada("Ricardo Santos", "Botafogo FC", "Meia", "2024")
    for j in [
        {"data":"2024-03-01","adversario":"Vasco","gols":1,"assistencias":2,"minutos_jogados":90,"passes_completos":65,"passes_tentados":72,"finalicoes":2,"finalicoes_gol":1,"desarmes":4,"interceptacoes":3},
        {"data":"2024-03-08","adversario":"Fluminense","gols":0,"assistencias":1,"minutos_jogados":85,"passes_completos":58,"passes_tentados":68,"desarmes":5,"interceptacoes":2},
        {"data":"2024-03-15","adversario":"Gremio","gols":2,"assistencias":0,"minutos_jogados":90,"passes_completos":50,"passes_tentados":60,"finalicoes":3,"finalicoes_gol":2,"desarmes":3,"interceptacoes":1},
        {"data":"2024-03-22","adversario":"Inter","gols":1,"assistencias":3,"minutos_jogados":90,"passes_completos":72,"passes_tentados":78,"finalicoes":2,"finalicoes_gol":1,"desarmes":6,"interceptacoes":4},
    ]:
        e2.add_partida(PartidaStats(**j))
    print("\n\n" + e2.relatorio())
    print("\n\n" + comparar_atletas(e1, e2))

if __name__ == "__main__":
    main()
