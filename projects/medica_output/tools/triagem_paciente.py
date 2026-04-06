"""
Triagem de Pacientes – Clinica Medica

Classificacao de risco baseada em sinais vitais e sintomas.
Protocolo adaptado do Manchester Triage System.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NivelPrioridade(str, Enum):
    """Niveis de prioridade da triagem."""
    EMERGENCIA = "Emergencia"       # Vermelho – atendimento imediato
    MUITO_URGENTE = "Muito Urgente" # Laranja – ate 10 min
    URGENTE = "Urgente"             # Amarelo – ate 60 min
    POUCO_URGENTE = "Pouco Urgente" # Verde – ate 120 min
    NAO_URGENTE = "Nao Urgente"     # Azul – ate 240 min


class Sintoma(str, Enum):
    DOR_TORACICA = "dor_toracica"
    FALTA_AR = "falta_ar"
    FEBRE_ALTA = "febre_alta"
    SANGRAMENTO = "sangramento"
    CONFUSAO_MENTAL = "confusao_mental"
    DOR_MODERADA = "dor_moderada"
    FERIMENTO_LEVE = "ferimento_leve"
    DOR_CRONICA = "dor_cronica"
    CONSULTA_ROTINA = "consulta_rotina"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class SinaisVitais:
    """Sinais vitais do paciente no momento da triagem."""
    pressao_sistolica: int       # mmHg
    pressao_diastolica: int      # mmHg
    frequencia_cardiaca: int     # bpm
    temperatura: float           # °C
    frequencia_respiratoria: int # ipm
    saturacao_o2: float          # % SpO2
    dor_escala: int = 0          # 0-10

    @property
    def pressao_normal(self) -> bool:
        return 90 <= self.pressao_sistolica <= 140 and 60 <= self.pressao_diastolica <= 90

    @property
    def taquicardia(self) -> bool:
        return self.frequencia_cardiaca > 100

    @property
    def bradicardia(self) -> bool:
        return self.frequencia_cardiaca < 50

    @property
    def febre(self) -> bool:
        return self.temperatura >= 38.5

    @property
    def hipotermia(self) -> bool:
        return self.temperatura < 35.0

    @property
    def hipoxemia(self) -> bool:
        return self.saturacao_o2 < 92.0

    def resumo(self) -> str:
        """String formatada com os sinais vitais."""
        return (
            f"PA={self.pressao_sistolica}/{self.pressao_diastolica} mmHg | "
            f"FC={self.frequencia_cardiaca} bpm | "
            f"T={self.temperatura:.1f}°C | "
            f"FR={self.frequencia_respiratoria} ipm | "
            f"SpO2={self.saturacao_o2}% | "
            f"Dor={self.dor_escala}/10"
        )


@dataclass
class RegistroTriagem:
    """Resultado de uma triagem individual."""
    paciente_nome: str
    cpf: str
    sinais: SinaisVitais
    sintomas: list[Sintoma]
    prioridade: NivelPrioridade
    pontuacao_risco: int
    tempo_espera_estimado: str
    hora_entrada: datetime = field(default_factory=datetime.now)
    observacao: str = ""


# ---------------------------------------------------------------------------
# Classificador
# ---------------------------------------------------------------------------

# Tabela de pontuacao de sintomas
_PONTUACAO_SINTOMA: dict[Sintoma, int] = {
    Sintoma.DOR_TORACICA: 35,
    Sintoma.FALTA_AR: 30,
    Sintoma.SANGRAMENTO: 30,
    Sintoma.FEBRE_ALTA: 15,
    Sintoma.CONFUSAO_MENTAL: 25,
    Sintoma.DOR_MODERADA: 10,
    Sintoma.FERIMENTO_LEVE: 5,
    Sintoma.DOR_CRONICA: 5,
    Sintoma.CONSULTA_ROTINA: 0,
}


def _classificar_prioridade(pontuacao: int) -> NivelPrioridade:
    if pontuacao >= 70:
        return NivelPrioridade.EMERGENCIA
    if pontuacao >= 50:
        return NivelPrioridade.MUITO_URGENTE
    if pontuacao >= 30:
        return NivelPrioridade.URGENTE
    if pontuacao >= 15:
        return NivelPrioridade.POCO_URGENTE
    return NivelPrioridade.NAO_URGENTE


_TEMPO_ESPERA: dict[NivelPrioridade, str] = {
    NivelPrioridade.EMERGENCIA: "Imediato",
    NivelPrioridade.MUITO_URGENTE: "Ate 10 minutos",
    NivelPrioridade.URGENTE: "Ate 60 minutos",
    NivelPrioridade.POCO_URGENTE: "Ate 120 minutos",
    NivelPrioridade.NAO_URGENTE: "Ate 240 minutos",
}


def calcular_risco(
    sinais: SinaisVitais,
    sintomas: list[Sintoma],
) -> tuple[int, NivelPrioridade, str]:
    """
    Calcula pontuacao de risco, nivel de prioridade e tempo estimado.

    Retorna: (pontuacao, prioridade, tempo_espera_estimado)
    """
    pontos = 0

    # Sinais vitais anormais
    if sinais.pressao_sistolica < 90 or sinais.pressao_sistolica > 180:
        pontos += 20
    if sinais.pressao_diastolica > 110:
        pontos += 15
    if sinais.taquicardia:
        pontos += 10
    if sinais.bradicardia:
        pontos += 15
    if sinais.febre:
        pontos += 10
    if sinais.hipotermia:
        pontos += 20
    if sinais.hipoxemia:
        pontos += 25
    if sinais.dor_escala >= 8:
        pontos += 15
    elif sinais.dor_escala >= 5:
        pontos += 8

    # Sintomas
    for s in sintomas:
        pontos += _PONTUACAO_SINTOMA.get(s, 0)

    prioridade = _classificar_prioridade(pontos)
    tempo = _TEMPO_ESPERA[prioridade]
    return pontos, prioridade, tempo


# ---------------------------------------------------------------------------
# Sistema de Triagem (fila)
# ---------------------------------------------------------------------------

class SistemaTriagem:
    """Gerencia a fila de triagem da Clinica Medica."""

    def __init__(self) -> None:
        self._registros: list[RegistroTriagem] = []
        self._fila_espera: list[RegistroTriagem] = []

    def adicionar_paciente(
        self,
        paciente_nome: str,
        cpf: str,
        sinais: SinaisVitais,
        sintomas: list[Sintoma],
        observacao: str = "",
    ) -> RegistroTriagem:
        """Realiza a triagem e insere o paciente na fila."""
        pontos, prioridade, tempo = calcular_risco(sinais, sintomas)
        registro = RegistroTriagem(
            paciente_nome=paciente_nome,
            cpf=cpf,
            sinais=sinais,
            sintomas=sintomas,
            prioridade=prioridade,
            pontuacao_risco=pontos,
            tempo_espera_estimado=tempo,
            observacao=observacao,
        )
        self._registros.append(registro)
        self._inserir_na_fila(registro)
        return registro

    def _inserir_na_fila(self, registro: RegistroTriagem) -> None:
        """Insere na fila ordenada por prioridade (maior pontuacao primeiro)."""
        ordem = {
            NivelPrioridade.EMERGENCIA: 0,
            NivelPrioridade.MUITO_URGENTE: 1,
            NivelPrioridade.URGENTE: 2,
            NivelPrioridade.POCO_URGENTE: 3,
            NivelPrioridade.NAO_URGENTE: 4,
        }
        chave = (ordem[registro.prioridade], -registro.pontuacao_risco)
        # Insere mantendo a ordenacao
        for i, r in enumerate(self._fila_espera):
            chave_atual = (ordem[r.prioridade], -r.pontuacao_risco)
            if chave < chave_atual:
                self._fila_espera.insert(i, registro)
                return
        self._fila_espera.append(registro)

    def proximo_paciente(self) -> Optional[RegistroTriagem]:
        """Retorna e remove o proximo paciente da fila."""
        if not self._fila_espera:
            return None
        return self._fila_espera.pop(0)

    def tamanho_fila(self) -> int:
        return len(self._fila_espera)

    # -- Relatorios ----------------------------------------------------------

    def estatisticas_fila(self) -> dict:
        """Estatisticas gerais da fila de espera."""
        total = len(self._registros)
        na_fila = len(self._fila_espera)
        atendidos = total - na_fila

        por_prioridade: dict[str, int] = {}
        for r in self._registros:
            por_prioridade.setdefault(r.prioridade.value, 0)
            por_prioridade[r.prioridade.value] += 1

        pontuacao_media = (
            sum(r.pontuacao_risco for r in self._registros) / total if total else 0
        )

        return {
            "total_triagens": total,
            "na_fila_de_espera": na_fila,
            "atendidos": atendidos,
            "por_prioridade": por_prioridade,
            "pontuacao_media_risco": round(pontuacao_media, 1),
        }

    def relatorio_fila(self) -> str:
        """Gera relatorio formatado da fila de espera."""
        linhas = [
            "RELATORIO DA FILA DE TRIAGEM",
            "=" * 60,
            f"Horario: {self._registros[0].hora_entrada:%d/%m/%Y %H:%M}" if self._registros else "",
            f"Pacientes na fila: {self.tamanho_fila()}",
            "-" * 60,
        ]
        if not self._fila_espera:
            linhas.append("  Fila vazia.")
        else:
            for i, r in enumerate(self._fila_espera, 1):
                sintomas_str = ", ".join(s.value for s in r.sintomas)
                linhas.append(
                    f"  {i}. {r.paciente_nome} (CPF: {r.cpf})"
                )
                linhas.append(
                    f"     Prioridade: {r.prioridade.value} | "
                    f"Risco: {r.pontuacao_risco} pts | "
                    f"Espera: {r.tempo_espera_estimado}"
                )
                linhas.append(f"     Sintomas: {sintomas_str}")
                linhas.append(f"     Sinais: {r.sinais.resumo()}")
                if r.observacao:
                    linhas.append(f"     Obs: {r.observacao}")
                linhas.append("")

        stats = self.estatisticas_fila()
        linhas.append("ESTATISTICAS:")
        for k, v in stats.items():
            linhas.append(f"  {k}: {v}")

        return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main() -> None:
    """Demonstracao do Sistema de Triagem."""
    print("=" * 60)
    print("  CLINICA MEDICA – Triagem de Pacientes")
    print("=" * 60)

    st = SistemaTriagem()

    # Paciente 1 – emergencia (dor toracica, PA alta)
    p1 = st.adicionar_paciente(
        paciente_nome="Carlos Mendes",
        cpf="111.222.333-44",
        sinais=SinaisVitais(
            pressao_sistolica=190,
            pressao_diastolica=120,
            frequencia_cardiaca=115,
            temperatura=37.8,
            frequencia_respiratoria=24,
            saturacao_o2=89.0,
            dor_escala=9,
        ),
        sintomas=[Sintoma.DOR_TORACICA, Sintoma.FALTA_AR],
        observacao="Paciente sudoreico, palido.",
    )
    print(f"\nTriagem: {p1.paciente_nome} – {p1.prioridade.value} ({p1.pontuacao_risco} pts)")
    print(f"  Espera estimada: {p1.tempo_espera_estimado}")

    # Paciente 2 – urgente
    p2 = st.adicionar_paciente(
        paciente_nome="Ana Paula Ribeiro",
        cpf="555.666.777-88",
        sinais=SinaisVitais(
            pressao_sistolica=130,
            pressao_diastolica=85,
            frequencia_cardiaca=88,
            temperatura=39.2,
            frequencia_respiratoria=20,
            saturacao_o2=96.0,
            dor_escala=6,
        ),
        sintomas=[Sintoma.FEBRE_ALTA, Sintoma.DOR_MODERADA],
    )
    print(f"Triagem: {p2.paciente_nome} – {p2.prioridade.value} ({p2.pontuacao_risco} pts)")
    print(f"  Espera estimada: {p2.tempo_espera_estimado}")

    # Paciente 3 – nao urgente (consulta de rotina)
    p3 = st.adicionar_paciente(
        paciente_nome="Marcos Oliveira",
        cpf="999.888.777-66",
        sinais=SinaisVitais(
            pressao_sistolica=120,
            pressao_diastolica=80,
            frequencia_cardiaca=72,
            temperatura=36.6,
            frequencia_respiratoria=16,
            saturacao_o2=98.0,
            dor_escala=0,
        ),
        sintomas=[Sintoma.CONSULTA_ROTINA],
    )
    print(f"Triagem: {p3.paciente_nome} – {p3.prioridade.value} ({p3.pontuacao_risco} pts)")
    print(f"  Espera estimada: {p3.tempo_espera_estimado}")

    # Atender proximo (deve ser Carlos – emergencia)
    proximo = st.proximo_paciente()
    print(f"\nProximo paciente chamado: {proximo.paciente_nome}")

    # Relatorio
    print("\n" + st.relatorio_fila())


if __name__ == "__main__":
    main()
