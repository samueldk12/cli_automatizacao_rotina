"""
Calculadora de Prazos Processuais - Advocacia BR
==================================================
Calcula prazos processuais contando em dias uteis (uteis), excluindo
finais de semana e feriados, para tribunais TRT, STF e STJ.
"""

from __future__ import annotations

import datetime
import sys
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tribuna(Enum):
    """Tribunais suportados."""
    TRT = "TRT"      # Tribunal Regional do Trabalho
    STF = "STF"      # Supremo Tribunal Federal
    STJ = "STJ"      # Superior Tribunal de Justica


@dataclass
class Feriado:
    """Representa um feriado nacional ou forense."""
    data: datetime.date
    descricao: str
    ambito: str = "nacional"  # nacional, forense, estadual

# Feriados nacionais fixos (varia por ano)
def _feriados_nacionais(ano: int) -> list[datetime.date]:
    """Retorna lista de feriados nacionais para um determinado ano."""
    feriados = [
        datetime.date(ano, 1, 1),   # Confraternizacao Universal
        datetime.date(ano, 4, 21),  # Tiradentes
        datetime.date(ano, 5, 1),   # Dia do Trabalho
        datetime.date(ano, 9, 7),   # Independencia
        datetime.date(ano, 10, 12), # Nossa Sra. Aparecida
        datetime.date(ano, 11, 2),  # Finados
        datetime.date(ano, 11, 15), # Proclamacao da Republica
        datetime.date(ano, 11, 20), # Consciencia Negra
        datetime.date(ano, 12, 25), # Natal
    ]
    return feriados


# Feriados moveis (Pascoa-based) para 2026
def _feriados_moveis(ano: int) -> list[datetime.date]:
    """Retorna feriados moveis baseados na Pascoa (algoritmo de Meeus/Jones/Butcher)."""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    pascoa = datetime.date(ano, mes, dia)

    return [
        pascoa - datetime.timedelta(days=48),  # Carnaval (segunda-feira)
        pascoa - datetime.timedelta(days=47),  # Carnaval (terca-feira)
        pascoa - datetime.timedelta(days=2),   # Sexta-feira Santa
        pascoa,                                # Pascoa
        pascoa + datetime.timedelta(days=60),  # Corpus Christi
    ]


@dataclass
class PrazoProcessual:
    """Representa um prazo processual calculado."""
    data_inicio: datetime.date
    data_fim: datetime.date
    dias_uteis: int
    feriado_encontrados: list[str] = field(default_factory=list)
    justificativa: str = ""
    tribunal: Tribuna = Tribuna.STF

    def __str__(self) -> str:
        feriados_info = ""
        if self.feriado_encontrados:
            feriados_info = f"\n  Feriados no periodo: {', '.join(self.feriado_encontrados)}"
        return (
            f"Prazo: {self.dias_uteis} dias uteis\n"
            f"Inicio: {self.data_inicio.strftime('%d/%m/%Y')}\n"
            f"Vencimento: {self.data_fim.strftime('%d/%m/%Y')}{feriados_info}"
        )


class CalculadoraPrazos:
    """Calculadora de prazos processuais para tribunais brasileiros."""

    def __init__(self, tribunal: Tribuna = Tribuna.STF) -> None:
        self.tribunal = tribunal
        self.feriados_cache: dict[int, list[datetime.date]] = {}

    def _obter_feriados(self, ano: int) -> list[datetime.date]:
        """Obtem feriados para o ano, com cache."""
        if ano not in self.feriados_cache:
            self.feriados_cache[ano] = (
                _feriados_nacionais(ano) + _feriados_moveis(ano)
            )
            # Feriado forense: 11 de agosto - Dia do Advogado/SJurista
            self.feriados_cache[ano].append(datetime.date(ano, 8, 11))
            # Recesso forense (simplificado): 20/12 a 06/01
            self.feriados_cache[ano].append(datetime.date(ano, 12, 24))
            self.feriados_cache[ano].append(datetime.date(ano, 12, 31))
        return self.feriados_cache[ano]

    def _obter_todos_feriados(self) -> list[datetime.date]:
        """Obtem feriados relevantes para o calculo do prazo."""
        # Coleta feriados de 2+ anos para cobrir intervalos
        anos = set()
        # Usando 2026 como base
        for ano in range(2025, 2028):
            anos.add(ano)

        feriados_set: set[datetime.date] = set()
        for ano in anos:
            feriados_set.update(self._obter_feriados(ano))

        feriados_set.update(self.get_adiantados_tribunal())
        return sorted(feriados_set)

    def get_adiantados_tribunal(self) -> list[datetime.date]:
        """Retorna feriados/admissaveis especificos do tribunal."""
        if self.tribunal == Tribuna.TRT:
            # Dia do Trabalho ja incluido nos nacionais
            pass
        elif self.tribunal == Tribuna.STF:
            pass
        elif self.tribunal == Tribuna.STJ:
            pass
        return []

    def _e_dia_util(self, data: datetime.date) -> bool:
        """Verifica se a data e dia util (nao weekend, nao feriado)."""
        # Seg=0, Dom=6
        if data.weekday() >= 5:
            return False

        feriados = self._obter_feriados(data.year)
        if data in feriados:
            return False

        return True

    def calcular_prazo(
        self,
        data_inicio: datetime.date,
        dias_uteis: int,
        incluir_inicio: bool = False,
    ) -> PrazoProcessual:
        """
        Calcula a data final do prazo processual.

        Args:
            data_inicio: Data do termo a quo (cienciacao/intimacao).
            dias_uteis: Numero de dias uteis do prazo.
            incluir_inicio: Se True, conta o dia inicial como dia 1.
                            Segue o CPC (art. 224): exclui dia do inicio, inclui vencimento.

        Returns:
            PrazoProcessual com data final e detalhes.

        Nota:
            Conforme CPC/2015 art. 224: "Na contagem de prazo em dias uteis,
            excluira-se o dia do inicio e incluir-se-a o dia do vencimento."
        """
        feriado_encontrados: list[str] = []
        dias_uteis_contados = 0
        data_atual = data_inicio

        if not incluir_inicio:
            data_atual += datetime.timedelta(days=1)

        while dias_uteis_contados < dias_uteis:
            feriados_ano = self._obter_feriados(data_atual.year)

            if data_atual in feriados_ano:
                nome = feriado_para_descricao(data_atual)
                if nome:
                    feriado_encontrados.append(f"{data_atual.strftime('%d/%m')} - {nome}")
                data_atual += datetime.timedelta(days=1)
                continue

            if data_atual.weekday() >= 5:
                data_atual += datetime.timedelta(days=1)
                continue

            dias_uteis_contados += 1

            if dias_uteis_contados < dias_uteis:
                data_atual += datetime.timedelta(days=1)

        justificativa = ""
        if feriado_encontrados:
            justificativa = (
                f"Prazo de {dias_uteis} dias uteis com {len(feriado_encontrados)} "
                f"feriado(s) no periodo"
            )

        return PrazoProcessual(
            data_inicio=data_inicio,
            data_fim=data_atual,
            dias_uteis=dias_uteis,
            feriado_encontrados=feriado_encontrados,
            justificativa=justificativa,
            tribunal=self.tribunal,
        )

    def calcular_prazo_em_dias(
        self,
        data_inicio: datetime.date,
        data_fim: datetime.date,
    ) -> int:
        """
        Calcula quantos dias uteis existem entre duas datas.

        Args:
            data_inicio: Data inicial (inclusive).
            data_fim: Data final (inclusive).

        Returns:
            Numero de dias uteis entre as datas.
        """
        if data_fim < data_inicio:
            return 0

        count = 0
        feriados = self._obter_todos_feriados()
        data_atual = data_inicio

        while data_atual <= data_fim:
            if data_atual.weekday() < 5 and data_atual not in feriados:
                count += 1
            data_atual += datetime.timedelta(days=1)

        return count

    def verificar_urgencia(
        self,
        data_inicio: datetime.date,
        dias_uteis_total: int,
        data_referencia: Optional[datetime.date] = None,
    ) -> dict:
        """
        Verifica status de urgencia de um prazo.

        Args:
            data_inicio: Data de inicio do prazo.
            dias_uteis_total: Total de dias uteis do prazo.
            data_referencia: Data para verificar urgencia (hoje por padrao).

        Returns:
            Dict com dias restantes, percentual consumido e status.
        """
        if data_referencia is None:
            data_referencia = datetime.date.today()

        prazo = self.calcular_prazo(data_inicio, dias_uteis_total)
        dias_restantes = self.calcular_prazo_em_dias(data_referencia, prazo.data_fim)

        total_uteis = self.calcular_prazo_em_dias(data_inicio, prazo.data_fim)
        total_uteis = max(total_uteis, 1)
        consumido = total_uteis - dias_restantes
        percentual = (consumido / total_uteis) * 100

        if dias_restantes <= 0:
            status = "VENCIDO"
        elif dias_restantes <= 2:
            status = "URGENTE"
        elif dias_restantes <= 5:
            status = "ATENCAO"
        else:
            status = "NORMAL"

        return {
            "tribunal": self.tribunal.value,
            "data_inicio": data_inicio.strftime("%d/%m/%Y"),
            "data_vencimento": prazo.data_fim.strftime("%d/%m/%Y"),
            "dias_restantes": dias_restantes,
            "percentual_consumido": round(percentual, 1),
            "status": status,
        }


def feriado_para_descricao(data: datetime.date) -> Optional[str]:
    """Retorna descricao do feriado para uma data."""
    feriados_descricao = {
        (1, 1): "Confraternizacao Universal",
        (4, 21): "Tiradentes",
        (5, 1): "Dia do Trabalho",
        (9, 7): "Independencia do Brasil",
        (10, 12): "Nossa Sra. Aparecida",
        (11, 2): "Finados",
        (11, 15): "Proclamacao da Republica",
        (11, 20): "Consciencia Negra",
        (12, 25): "Natal",
        (8, 11): "Dia do Estudante de Direito",
        (12, 24): "Vispera de Natal",
        (12, 31): "Vispera de Ano Novo",
    }
    return feriados_descricao.get((data.month, data.day))


def main() -> None:
    """Demonstracao da Calculadora de Prazos Processuais."""
    print("=" * 60)
    print("CALCULADORA DE PRAZOS PROCESSUAIS - Advocacia BR")
    print("=" * 60)

    # Exemplo 1: Prazo de 8 dias uteis (STF) - contestacao trabalhista
    print("\n--- Exemplo 1: Prazo Trabalista (TRT) ---")
    calc_trt = CalculadoraPrazos(Tribuna.TRT)
    prazo = calc_trt.calcular_prazo(
        data_inicio=datetime.date(2026, 6, 1),
        dias_uteis=8,
    )
    print(prazo)

    # Exemplo 2: Prazo de 15 dias uteis (STJ)
    print("\n--- Exemplo 2: Recurso Especial (STJ) ---")
    calc_stj = CalculadoraPrazos(Tribuna.STJ)
    prazo2 = calc_stj.calcular_prazo(
        data_inicio=datetime.date(2026, 3, 2),
        dias_uteis=15,
    )
    print(prazo2)

    # Exemplo 3: Verificar urgencia
    print("\n--- Exemplo 3: Verificar Urgencia ---")
    urgencia = calc_trt.verificar_urgencia(
        data_inicio=datetime.date(2026, 6, 1),
        dias_uteis_total=8,
        data_referencia=datetime.date(2026, 6, 8),
    )
    print(f"Tribunal: {urgencia['tribunal']}")
    print(f"Vencimento: {urgencia['data_vencimento']}")
    print(f"Dias restantes: {urgencia['dias_restantes']}")
    print(f"Status: {urgencia['status']}")

    # Exemplo 4: Contar dias uteis entre datas
    print("\n--- Exemplo 4: Dias Uteis entre Datas ---")
    dias = calc_trt.calcular_prazo_em_dias(
        datetime.date(2026, 7, 1),
        datetime.date(2026, 7, 31),
    )
    print(f"Julho/2026: {dias} dias uteis")

    print("\n" + "=" * 60)
    print("Demonstracao concluida.")


if __name__ == "__main__":
    main()
