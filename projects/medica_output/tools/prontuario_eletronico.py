"""
Prontuario Eletronico do Paciente - Clinica Medica

Sistema de registro eletronico de pacientes, historico de consultas,
prescricoes, resultados de exames e agendamento.
"""

from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Especialidade(str, Enum):
    CLINICO_GERAL = "clinico_geral"
    CARDIOLOGISTA = "cardiologista"
    ENDOCRINOLOGISTA = "endocrinologista"
    DERMATOLOGISTA = "dermatologista"
    RADIOLOGISTA = "radiologista"
    PATOLOGISTA = "patologista"


class Sexo(str, Enum):
    MASCULINO = "masculino"
    FEMININO = "feminino"
    OUTRO = "outro"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class Prescricao:
    """Prescricao medica vinculada a uma consulta."""
    medicamento: str
    dosagem: str
    frequencia: str
    duracao_dias: int
    data_emissao: date = field(default_factory=date.today)


@dataclass
class ResultadoExame:
    """Resultado de exame laboratorial ou de imagem."""
    nome_exame: str
    tipo: str  # 'laboratorial' ou 'imagem'
    resultado: str
    data: date = field(default_factory=date.today)
    observacao: str = ""


@dataclass
class Consulta:
    """Registro de uma consulta realizada."""
    data: date
    especialidade: Especialidade
    medico: str
    diagnostico: str  # CID-10简写
    anotacoes: str = ""
    prescricoes: list[Prescricao] = field(default_factory=list)


@dataclass
class Paciente:
    """Ficha do paciente."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    nome: str = ""
    cpf: str = ""                       # XXX.XXX.XXX-XX
    data_nascimento: date = date(2000, 1, 1)
    sexo: Sexo = Sexo.OUTRO
    telefone: str = ""
    endereco: str = ""
    convenio: str = ""                  # Nome do plano de saude ou 'particular'
    consultas: list[Consulta] = field(default_factory=list)
    exames: list[ResultadoExame] = field(default_factory=list)
    data_cadastro: date = field(default_factory=date.today)

    @property
    def idade(self) -> int:
        hoje = date.today()
        return (
            hoje.year
            - self.data_nascimento.year
            - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        )


# ---------------------------------------------------------------------------
# Agendamento
# ---------------------------------------------------------------------------

@dataclass
class Agendamento:
    """Agendamento de consulta futuras."""
    paciente_id: str
    paciente_nome: str
    data: date
    hora: str
    especialidade: Especialidade
    medico: str
    confirmada: bool = False


# ---------------------------------------------------------------------------
# ProntuarioEletronico – repositorio principal
# ---------------------------------------------------------------------------

class ProntuarioEletronico:
    """Repositorio central de prontuarios da Clinica Medica."""

    def __init__(self) -> None:
        self._pacientes: dict[str, Paciente] = {}       # id -> Paciente
        self._agendamentos: list[Agendamento] = []

    # -- CRUD Paciente -------------------------------------------------------

    def cadastrar_paciente(
        self,
        nome: str,
        cpf: str,
        data_nascimento: date,
        sexo: Sexo,
        telefone: str,
        endereco: str,
        convenio: str,
    ) -> Paciente:
        """Cadastra um novo paciente e retorna o registro."""
        p = Paciente(
            nome=nome,
            cpf=cpf,
            data_nascimento=data_nascimento,
            sexo=sexo,
            telefone=telefone,
            endereco=endereco,
            convenio=convenio,
        )
        self._pacientes[p.id] = p
        return p

    def buscar_por_cpf(self, cpf: str) -> Optional[Paciente]:
        """Busca paciente pelo CPF."""
        for p in self._pacientes.values():
            if p.cpf == cpf:
                return p
        return None

    def buscar_por_nome(self, termo: str) -> list[Paciente]:
        """Busca pacientes por nome (parcial, sem distincao de maiusculas)."""
        termo_lower = termo.lower()
        return [p for p in self._pacientes.values() if termo_lower in p.nome.lower()]

    def obter_paciente(self, paciente_id: str) -> Optional[Paciente]:
        return self._pacientes.get(paciente_id)

    # -- Consultas -----------------------------------------------------------

    def registrar_consulta(
        self,
        paciente_id: str,
        data: date,
        especialidade: Especialidade,
        medico: str,
        diagnostico: str,
        anotacoes: str = "",
    ) -> Optional[Consulta]:
        p = self._pacientes.get(paciente_id)
        if p is None:
            return None
        c = Consulta(
            data=data, especialidade=especialidade, medico=medico,
            diagnostico=diagnostico, anotacoes=anotacoes,
        )
        p.consultas.append(c)
        return c

    def adicionar_prescricao(
        self,
        paciente_id: str,
        consulta_index: int,
        prescricao: Prescricao,
    ) -> bool:
        p = self._pacientes.get(paciente_id)
        if p is None or consulta_index >= len(p.consultas):
            return False
        p.consultas[consulta_index].prescricoes.append(prescricao)
        return True

    def adicionar_exame(
        self,
        paciente_id: str,
        exame: ResultadoExame,
    ) -> bool:
        p = self._pacientes.get(paciente_id)
        if p is None:
            return False
        p.exames.append(exame)
        return True

    # -- Agendamento ---------------------------------------------------------

    def agendar_consulta(
        self,
        paciente_id: str,
        paciente_nome: str,
        data: date,
        hora: str,
        especialidade: Especialidade,
        medico: str,
    ) -> Agendamento:
        a = Agendamento(
            paciente_id=paciente_id,
            paciente_nome=paciente_nome,
            data=data,
            hora=hora,
            especialidade=especialidade,
            medico=medico,
        )
        self._agendamentos.append(a)
        return a

    def listar_agendamentos(self, data: date | None = None) -> list[Agendamento]:
        """Lista agendamentos, opcionalmente filtrados por data."""
        if data is None:
            return self._agendamentos
        return [a for a in self._agendamentos if a.data == data]

    def confirmar_agendamento(self, agendamento: Agendamento) -> None:
        agendamento.confirmada = True

    # -- Estatisticas --------------------------------------------------------

    def estatisticas_especialidades(self) -> dict[str, int]:
        """Quantidade de consultas por especialidade."""
        contagem: Counter[str] = Counter()
        for p in self._pacientes.values():
            for c in p.consultas:
                contagem[c.especialidade.value] += 1
        return dict(contagem)

    def diagnosticos_mais_comuns(self, top: int = 10) -> list[tuple[str, int]]:
        """Lista os diagnosticos mais frequente."""
        contagem: Counter[str] = Counter()
        for p in self._pacientes.values():
            for c in p.consultas:
                contagem[c.diagnostico] += 1
        return contagem.most_common(top)

    def resumo_geral(self) -> dict:
        """Retorna um dicionario com resumo do sistema."""
        total_pacientes = len(self._pacientes)
        total_consultas = sum(len(p.consultas) for p in self._pacientes.values())
        total_exames = sum(len(p.exames) for p in self._pacientes.values())
        total_agendamentos = len(self._agendamentos)
        convenios: Counter[str] = Counter(
            p.convenio for p in self._pacientes.values() if p.convenio
        )
        return {
            "total_pacientes": total_pacientes,
            "total_consultas": total_consultas,
            "total_exames": total_exames,
            "agendamentos": total_agendamentos,
            "convenios": dict(convenios),
            "consultas_por_especialidade": self.estatisticas_especialidades(),
            "top_diagnosticos": self.diagnosticos_mais_comuns(5),
        }

    def historico_completo(self, paciente_id: str) -> Optional[str]:
        """Gera um texto formatado com o historico do paciente."""
        p = self._pacientes.get(paciente_id)
        if p is None:
            return None
        linhas = [
            f"Prontuario - {p.nome} (CPF: {p.cpf})",
            f"Idade: {p.idade} anos | Sexo: {p.sexo.value}",
            f"Convenio: {p.convenio}",
            "-" * 60,
            "CONSULTAS:",
        ]
        for i, c in enumerate(p.consultas, 1):
            linhas.append(
                f"  {i}. {c.data} – {c.especialidade.value} | Dr(a). {c.medico}"
            )
            linhas.append(f"     Diagnostico: {c.diagnostico}")
            linhas.append(f"     Anotacoes: {c.anotacoes or '-'}")
            if c.prescricoes:
                linhas.append("     Prescricoes:")
                for pres in c.prescricoes:
                    linhas.append(
                        f"       - {pres.medicamento} {pres.dosagem}, "
                        f"{pres.frequencia}, {pres.duracao_dias} dias"
                    )
        linhas.append("")
        linhas.append("EXAMES:")
        for e in p.exames:
            linhas.append(
                f"  - {e.nome_exame} ({e.tipo}) em {e.data}: {e.resultado}"
            )
            if e.observacao:
                linhas.append(f"    Obs: {e.observacao}")
        return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main() -> None:
    """Demonstracao do Prontuario Eletronico."""
    print("=" * 60)
    print("  CLINICA MEDICA – Prontuario Eletronico do Paciente")
    print("=" * 60)

    pe = ProntuarioEletronico()

    # Cadastrando pacientes
    maria = pe.cadastrar_paciente(
        nome="Maria da Silva",
        cpf="123.456.789-00",
        data_nascimento=date(1985, 3, 15),
        sexo=Sexo.FEMININO,
        telefone="(11) 99999-1234",
        endereco="Rua das Flores, 100",
        convenio="Unimed",
    )
    print(f"\nPaciente cadastrado: {maria.nome} (ID: {maria.id})")

    joao = pe.cadastrar_paciente(
        nome="Joao Souza",
        cpf="987.654.321-00",
        data_nascimento=date(1970, 11, 8),
        sexo=Sexo.MASCULINO,
        telefone="(11) 98888-5678",
        endereco="Av. Paulista, 500",
        convenio="particular",
    )
    print(f"Paciente cadastrado: {joao.nome} (ID: {joao.id})")

    # Busca
    resultados = pe.buscar_por_nome("maria")
    print(f"\nBusca por 'maria': {len(resultados)} resultado(s)")

    # Registrar consultas
    cx1 = pe.registrar_consulta(
        paciente_id=maria.id,
        data=date(2026, 3, 10),
        especialidade=Especialidade.CARDIOLOGISTA,
        medico="Dra. Helena Costa",
        diagnostico="I10 – Hipertensao essencial primaria",
        anotacoes="PA=150/95. Solicitar exames.",
    )
    print(f"\nConsulta registrada: {cx1.diagnostico}")

    pe.adicionar_prescricao(
        paciente_id=maria.id,
        consulta_index=0,
        prescricao=Prescricao(
            medicamento="Losartana",
            dosagem="50mg",
            frequencia="1x ao dia",
            duracao_dias=60,
        ),
    )
    print("Prescricao adicionada: Losartana 50mg")

    pe.adicionar_exame(
        paciente_id=maria.id,
        exame=ResultadoExame(
            nome_exame="Eletrocardiograma",
            tipo="imagem",
            resultado="Sem alteracoes significativas",
            data=date(2026, 3, 15),
        ),
    )

    pe.registrar_consulta(
        paciente_id=joao.id,
        data=date(2026, 3, 12),
        especialidade=Especialidade.EMDOCRINOLOGISTA,
        medico="Dr. Roberto Lima",
        diagnostico="E11 – Diabetes mellitus tipo 2",
        anotacoes="Glicemia de jejum = 140 mg/dL",
    )

    pe.registrar_consulta(
        paciente_id=maria.id,
        data=date(2026, 3, 20),
        especialidade=Especialidade.DERMATOLOGISTA,
        medico="Dra. Ana Beatriz",
        diagnostico="L70.0 – Acne vulgar",
    )

    # Agendamento
    pe.agendar_consulta(
        paciente_id=maria.id,
        paciente_nome=maria.nome,
        data=date(2026, 4, 15),
        hora="10:00",
        especialidade=Especialidade.CARDIOLOGISTA,
        medico="Dra. Helena Costa",
    )
    print("\nAgendamento realizado para 15/04/2026 as 10:00")

    # Estatisticas
    resumo = pe.resumo_geral()
    print(f"\n--- Resumo Geral ---")
    for k, v in resumo.items():
        print(f"  {k}: {v}")

    # Historico completo
    print("\n" + pe.historico_completo(maria.id))


if __name__ == "__main__":
    main()
