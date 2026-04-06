"""
Faturamento Medico – Clinica Medica

Calculadora de contas medicas baseada na tabela CBHPM
(Classificacao Brasileira Hierarquizada de Procedimentos Medicos).
Controle de contas hospitalares, sinistros (glosas) e relatorios mensais.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumeracoes
# ---------------------------------------------------------------------------

class TipoProcedimento(str, Enum):
    CONSULTA = "consulta"
    EXAME_LABORATORIAL = "exame_laboratorial"
    EXAME_IMAGEM = "exame_imagem"
    PROCEDIMENTO = "procedimento"
    CIRURGIA = "cirurgia"
    DIARIA = "diaria_hospitalar"


class StatusGuia(str, Enum):
    SOLICITADA = "solicitada"
    AUTORIZADA = "autorizada"
    EXECUTADA = "executada"
    GLOSADA = "glosada"
    PAGA = "paga"


# ---------------------------------------------------------------------------
# Tabela CBHPM simplificada (valores ficticios em R$)
# ---------------------------------------------------------------------------

TABELA_CBHPM: dict[str, dict] = {
    # Consultas
    "10101012": {"descricao": "Consulta em consultorio (clinico geral)", "tipo": TipoProcedimento.CONSULTA, "valor": 180.00},
    "10101020": {"descricao": "Consulta em consultorio (especialista)", "tipo": TipoProcedimento.CONSULTA, "valor": 250.00},
    "10101039": {"descricao": "Retorno em consultorio", "tipo": TipoProcedimento.CONSULTA, "valor": 120.00},
    # Exames laboratoriais
    "40301013": {"descricao": "Hemograma completo", "tipo": TipoProcedimento.EXAME_LABORATORIAL, "valor": 85.00},
    "40301021": {"descricao": "Glicemia de jejum", "tipo": TipoProcedimento.EXAME_LABORATORIAL, "valor": 45.00},
    "40301030": {"descricao": "Colesterol total – LDL, HDL", "tipo": TipoProcedimento.EXAME_LABORATORIAL, "valor": 120.00},
    "40301048": {"descricao": "Creatinina", "tipo": TipoProcedimento.EXAME_LABORATORIAL, "valor": 55.00},
    "40301056": {"descricao": "TSH – Hormonio tireoestimulante", "tipo": TipoProcedimento.EXAME_LABORATORIAL, "valor": 65.00},
    # Exames de imagem
    "40601017": {"descricao": "Radiografia de torax", "tipo": TipoProcedimento.EXAME_IMAGEM, "valor": 90.00},
    "40601025": {"descricao": "Ultrassonografia abdominal", "tipo": TipoProcedimento.EXAME_IMAGEM, "valor": 200.00},
    "40601033": {"descricao": "Ecocardiograma", "tipo": TipoProcedimento.EXAME_IMAGEM, "valor": 350.00},
    "40601041": {"descricao": "Ressonancia magnetica (por segmento)", "tipo": TipoProcedimento.EXAME_IMAGEM, "valor": 800.00},
    "40601050": {"descricao": "Tomografia computadorizada", "tipo": TipoProcedimento.EXAME_IMAGEM, "valor": 600.00},
    # Procedimentos
    "30401011": {"descricao": "Eletrocardiograma de repouso", "tipo": TipoProcedimento.PROCEDIMENTO, "valor": 120.00},
    "30401020": {"descricao": "Teste ergometrico", "tipo": TipoProcedimento.PROCEDIMENTO, "valor": 280.00},
    "30401038": {"descricao": "Holter 24h", "tipo": TipoProcedimento.PROCEDIMENTO, "valor": 350.00},
    "30401046": {"descricao": "MAPA – Monitorizacao ambulatorial PA", "tipo": TipoProcedimento.PROCEDIMENTO, "valor": 320.00},
    # Cirurgias
    "20101010": {"descricao": "Apendicectomia", "tipo": TipoProcedimento.CIRURGIA, "valor": 1200.00},
    "20101028": {"descricao": "Colecistectomia videolaparoscopica", "tipo": TipoProcedimento.CIRURGIA, "valor": 2000.00},
    "20101036": {"descricao": "Herniorrafia", "tipo": TipoProcedimento.CIRURGIA, "valor": 1500.00},
    # Diarias
    "90101016": {"descricao": "Diaria enfermaria", "tipo": TipoProcedimento.DIARIA, "valor": 450.00},
    "90101024": {"descricao": "Diaria apartamento", "tipo": TipoProcedimento.DIARIA, "valor": 800.00},
    "90101032": {"descricao": "Diaria UTI", "tipo": TipoProcedimento.DIARIA, "valor": 2500.00},
}


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class ItemConta:
    """Um item (procedimento) na conta do paciente."""
    codigo_cbhpm: str
    quantidade: int = 1
    valor_unitario: float = 0.0
    glosado: bool = False
    motivo_glosa: str = ""

    @property
    def valor_total(self) -> float:
        if self.glosado:
            return 0.0
        return self.quantidade * self.valor_unitario

    @property
    def valor_glosa(self) -> float:
        if not self.glosado:
            return 0.0
        return self.quantidade * self.valor_unitario


@dataclass
class GuiaTiss:
    """Padrao TISS – Troca de Informacao em Saude Suplementar."""
    numero_guia: str
    paciente_nome: str
    paciente_cpf: str
    convenio: str
    procedimento_codigo: str
    procedimento_descricao: str
    quantidade: int
    valor_total: float
    status: StatusGuia = StatusGuia.SOLICITADA
    data_solicitacao: date = field(default_factory=date.today)
    data_execucao: Optional[date] = None
    motiva_glosa: str = ""


@dataclass
class ContaPaciente:
    """Conta acumulada de um paciente."""
    paciente_id: str
    paciente_nome: str
    paciente_cpf: str
    convenio: str
    itens: list[ItemConta] = field(default_factory=list)
    data_abertura: date = field(default_factory=date.today)
    data_fechamento: Optional[date] = None

    @property
    def valor_bruto(self) -> float:
        """Valor total sem considerar glosas."""
        return sum(item.quantidade * item.valor_unitario for item in self.itens)

    @property
    def valor_glosas(self) -> float:
        return sum(item.valor_glosa for item in self.itens)

    @property
    def valor_liquido(self) -> float:
        return self.valor_bruto - self.valor_glosas


# ---------------------------------------------------------------------------
# Calculadora de Faturamento
# ---------------------------------------------------------------------------

class FaturamentoMedico:
    """Gerencia o faturamento da Clinica Medica."""

    def __init__(self) -> None:
        self._contas: dict[str, ContaPaciente] = {}    # paciente_id -> Conta
        self._guias: list[GuiaTiss] = []

    # -- Contas --------------------------------------------------------------

    def abrir_conta(
        self,
        paciente_id: str,
        paciente_nome: str,
        paciente_cpf: str,
        convenio: str,
    ) -> ContaPaciente:
        """Abre uma nova conta para o paciente."""
        conta = ContaPaciente(
            paciente_id=paciente_id,
            paciente_nome=paciente_nome,
            paciente_cpf=paciente_cpf,
            convenio=convenio,
        )
        self._contas[paciente_id] = conta
        return conta

    def adicionar_item(
        self,
        paciente_id: str,
        codigo_cbhpm: str,
        quantidade: int = 1,
    ) -> bool:
        """Adiciona um procedimento a conta do paciente usando a tabela CBHPM."""
        conta = self._contas.get(paciente_id)
        tabela_info = TABELA_CBHPM.get(codigo_cbhpm)
        if conta is None or tabela_info is None:
            return False

        item = ItemConta(
            codigo_cbhpm=codigo_cbhpm,
            quantidade=quantidade,
            valor_unitario=tabela_info["valor"],
        )
        conta.itens.append(item)
        return True

    def gerar_glosa(self, paciente_id: str, item_index: int, motivo: str) -> bool:
        """Marca um item da conta como glosado."""
        conta = self._contas.get(paciente_id)
        if conta is None or item_index >= len(conta.itens):
            return False
        conta.itens[item_index].glosado = True
        conta.itens[item_index].motivo_glosa = motivo
        return True

    def fechar_conta(self, paciente_id: str) -> Optional[ContaPaciente]:
        conta = self._contas.get(paciente_id)
        if conta is None:
            return None
        conta.data_fechamento = date.today()
        return conta

    def conta_do_paciente(self, paciente_id: str) -> Optional[ContaPaciente]:
        return self._contas.get(paciente_id)

    # -- Guias TISS ----------------------------------------------------------

    def criar_guia(
        self,
        numero_guia: str,
        paciente_nome: str,
        paciente_cpf: str,
        convenio: str,
        codigo_cbhpm: str,
        quantidade: int = 1,
    ) -> Optional[GuiaTiss]:
        tabela_info = TABELA_CBHPM.get(codigo_cbhpm)
        if tabela_info is None:
            return None
        valor = tabela_info["valor"] * quantidade
        guia = GuiaTiss(
            numero_guia=numero_guia,
            paciente_nome=paciente_nome,
            paciente_cpf=paciente_cpf,
            convenio=convenio,
            procedimento_codigo=codigo_cbhpm,
            procedimento_descricao=tabela_info["descricao"],
            quantidade=quantidade,
            valor_total=valor,
        )
        self._guias.append(guia)
        return guia

    def glosar_guia(self, numero_guia: str, motivo: str) -> bool:
        for g in self._guias:
            if g.numero_guia == numero_guia:
                g.status = StatusGuia.GLOSADA
                g.motivo_glosa = motivo
                return True
        return False

    # -- Relatorios mensais --------------------------------------------------

    def relatorio_mensal(
        self, mes: int, ano: int
    ) -> dict:
        """
        Gera relatorio de faturamento para um mes/ano.

        Considera todas as guias e contas para estatisticas.
        """
        total_guias = len(self._guias)
        guias_glosadas = [g for g in self._guias if g.status == StatusGuia.GLOSADA]
        guias_pagas = [g for g in self._guias if g.status == StatusGuia.PAGA]

        faturamento_bruto = sum(g.valor_total * g.quantidade for g in self._guias)
        valor_glosas = sum(
            g.valor_total * g.quantidade for g in guias_glosadas
        )

        # Contas fechadas
        contas_fechadas = [
            c for c in self._contas.values()
            if c.data_fechamento is not None
        ]
        total_contas_glosas = sum(c.valor_glosas for c in contas_fechadas)

        taxa_glosa = (
            (valor_glosas / faturamento_bruto * 100)
            if faturamento_bruto > 0 else 0.0
        )

        # Agrupar por tipo de procedimento
        por_tipo: dict[str, dict] = {}
        for g in self._guias:
            info = TABELA_CBHPM.get(g.procedimento_codigo, {})
            tipo = info.get("tipo", "desconhecido")
            if isinstance(tipo, TipoProcedimento):
                tipo_str = tipo.value
            else:
                tipo_str = str(tipo)
            if tipo_str not in por_tipo:
                por_tipo[tipo_str] = {"quantidade": 0, "valor": 0.0}
            por_tipo[tipo_str]["quantidade"] += g.quantidade
            por_tipo[tipo_str]["valor"] += g.valor_total * g.quantidade

        # Agrupar por convenio
        por_convenio: dict[str, float] = {}
        for c in contas_fechadas:
            por_convenio.setdefault(c.convenio, 0.0)
            por_convenio[c.convenio] += c.valor_liquido

        return {
            "mes": mes,
            "ano": ano,
            "total_guias": total_guias,
            "guias_glosadas": len(guias_glosadas),
            "guias_pagas": len(guias_pagas),
            "faturamento_bruto_guias": round(faturamento_bruto, 2),
            "valor_glosas_guias": round(valor_glosas, 2),
            "total_contas_fechadas": len(contas_fechadas),
            "valor_glosas_contas": round(total_contas_glosas, 2),
            "taxa_glosa_percentual": round(taxa_glosa, 2),
            "por_tipo_procedimento": por_tipo,
            "por_convenio_contas": por_convenio,
        }

    def detalhe_conta(self, paciente_id: str) -> Optional[str]:
        """Gera string formatada com o detalhamento da conta."""
        conta = self._contas.get(paciente_id)
        if conta is None:
            return None

        linhas = [
            f"CONTA DO PACIENTE: {conta.paciente_nome} (CPF: {conta.paciente_cpf})",
            f"Convenio: {conta.convenio}",
            f"Abertura: {conta.data_abertura} | "
            f"Fechamento: {conta.data_fechamento or 'Aberta'}",
            "-" * 65,
            f"{'Codigo':<12} {'Descricao':<40} {'Qtd':>4} {'Unit( R$)':>10} {'Total(R$)':>10} {'Situacao':>10}",
            "-" * 65,
        ]

        for item in conta.itens:
            info = TABELA_CBHPM.get(item.codigo_cbhpm, {})
            desc = info.get("descricao", item.codigo_cbhpm)[:38]
            situacao = "GLOSADO" if item.glosado else "OK"
            linhas.append(
                f"{item.codigo_cbhpm:<12} {desc:<40} {item.quantidade:>4} "
                f"{item.valor_unitario:>10.2f} {item.valor_total:>10.2f} {situacao:>10}"
            )
            if item.motivo_glosa:
                linhas.append(f"             Motivo: {item.motivo_glosa}")

        linhas.append("-" * 65)
        linhas.append(
            f"  Valor Bruto: R$ {conta.valor_bruto:>12.2f}"
        )
        linhas.append(
            f"  Glosas:      R$ {conta.valor_glosas:>12.2f}"
        )
        linhas.append(
            f"  Valor Liquido: R$ {conta.valor_liquido:>12.2f}"
        )
        return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main() -> None:
    """Demonstracao do Faturamento Medico."""
    print("=" * 60)
    print("  CLINICA MEDICA – Faturamento Medico (CBHPM)")
    print("=" * 60)

    fm = FaturamentoMedico()

    # Abrir conta
    conta = fm.abrir_conta(
        paciente_id="P001",
        paciente_nome="Maria da Silva",
        paciente_cpf="123.456.789-00",
        convenio="Unimed",
    )
    print(f"\nConta aberta: {conta.paciente_nome}")

    # Adicionar itens
    itens = [
        ("10101020", 1),   # Consulta especialista
        ("40301013", 1),   # Hemograma
        ("40301030", 1),   # Colesterol
        ("40601025", 1),   # Ultrassonografia
        ("30401011", 1),   # ECG
        ("90101024", 2),   # Diaria apartamento x2
    ]
    for codigo, qtd in itens:
        fm.adicionar_item("P001", codigo, qtd)
        desc = TABELA_CBHPM[codigo]["descricao"]
        print(f"  + {desc} x{qtd}")

    # Simular glosa no hemograma (indice 1)
    fm.gerar_glosa("P001", item_index=1, motivo="Nao autorizado pelo convenio")
    print("\n  [!] Glosa aplicada ao Hemograma")

    # Detalhe da conta
    print("\n" + fm.detalhe_conta("P001"))

    # Criar guias TISS
    fm.criar_guia("G001", "Maria da Silva", "123.456.789-00", "Unimed", "10101020", 1)
    fm.criar_guia("G002", "Maria da Silva", "123.456.789-00", "Unimed", "40301013", 1)
    fm.criar_guia("G003", "Joao Souza", "987.654.321-00", "Bradesco Saude", "40601041", 1)
    fm.criar_guia("G004", "Joao Souza", "987.654.321-00", "Bradesco Saude", "30401038", 1)

    # Glosar guia
    fm.glosar_guia("G002", "Procedimento nao coberto pelo plano")

    # Abrir conta para Joao e fechar
    fm.abrir_conta("P002", "Joao Souza", "987.654.321-00", "Bradesco Saude")
    fm.adicionar_item("P002", "10101020", 1)
    fm.adicionar_item("P002", "40601041", 1)
    fm.fechar_conta("P002")

    fm.fechar_conta("P001")

    # Relatorio mensal
    rel = fm.relatorio_mensal(mes=4, ano=2026)
    print("\nRELATORIO MENSAL DE FATURAMENTO – Abril/2026")
    print("-" * 50)
    for k, v in rel.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
