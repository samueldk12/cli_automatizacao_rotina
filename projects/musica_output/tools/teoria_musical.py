"""
Conservatorio Musical - Utilitario de Teoria Musical
Departamento: Ensino (Professor Teoria)

Identifica escalas, construo acordes, navega pelo ciclo das quintas,
consulta armaduras de clave e analisa progresoes harmonicas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# --- Constantes Musicais ---

NOTAS_NATURAIS: list[str] = ["C", "D", "E", "F", "G", "A", "B"]

# Mapeamento de notas com seus intervalos em semitons (C = 0)
NOTA_PARA_SEMITOM: dict[str, int] = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4,
    "E#": 5, "F": 5,
    "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11,
}

SEMITOM_PARA_NOTA: dict[int, list[str]] = {}
for _nota, _semi in NOTA_PARA_SEMITOM.items():
    SEMITOM_PARA_NOTA.setdefault(_semi, []).append(_nota)

NOMES_INTERVALOS: dict[int, str] = {
    0: "Unisono",
    1: "Segunda menor",
    2: "Segunda maior",
    3: "Terca menor",
    4: "Terca maior",
    5: "Quarta justa",
    6: "Tritono",
    7: "Quinta justa",
    8: "Sexta menor",
    9: "Sexta maior",
    10: "Setima menor",
    11: "Setima maior",
}


class TipoEscala(Enum):
    MAIOR_NATURAL = "Maior Natural"
    MENOR_NATURAL = "Menor Natural"
    MENOR_HARMONICA = "Menor Harmonica"
    MENOR_MELODICA = "Menor Melodica (ascendente)"
    PENTATONICA_MAIOR = "Pentatonica Maior"
    PENTATONICA_MENOR = "Pentatonica Menor"
    BLUES = "Blues"
    DIMINUTA_TOM_SEMITOM = "Diminuta (Tom-Semitom)"
    DIMINUTA_SEMITOM_TOM = "Diminuta (Semitom-Tom)"
    CROMATICA = "Cromatica"
    DORICA = "Dorica"
    FRIGIA = "Frigia"
    LIDIA = "Lidia"
    MIXOLIDIA = "Mixolidia"
    EOLIA = "Eolia"
    LOCRIA = "Locria"


class QualidadeAcorde(Enum):
    MAIOR = "maior"
    MENOR = "menor"
    DIMINUTO = "diminuto"
    AUMENTADO = "aumentado"
    SUSPENSO_2 = "suspenso (sus2)"
    SUSPENSO_4 = "suspenso (sus4)"
    SEXTA = "sexta"
    SEXTA_MENOR = "sexta menor"
    POWER = "power chord"


class Grau(Enum):
    I = 1
    II = 2
    III = 3
    IV = 4
    V = 5
    VI = 6
    VII = 7


# --- Estruturas de Dados ---

@dataclass
class Escala:
    """Representa uma escala musical com suas notas e propriedades."""
    tipo: TipoEscala
    tonica: str
    notas: list[str]
    intervalos: list[int]


@dataclass
class Acorde:
    """Representa um acorde construido a partir de notas."""
    nota_raiz: str
    qualidade: QualidadeAcorde
    simbolo: str
    notas: list[str]
    intervalos: list[int]
    notacao_brasileira: str = ""


@dataclass
class ArmaduraClave:
    """Informacao sobre uma armadura de clave."""
    tonalidade: str
    modo: str
    sostenidos: int = 0
    bemois: int = 0
    notas_alteradas: list[str] = field(default_factory=list)


@dataclass
class AnaliseProgresao:
    """Resultado da analise de uma progressao harmonica."""
    tonalidade: str
    acordes: list[Acorde]
    graus_identificados: list[tuple[int, str]]
    cadencias: list[str]
    descricao: str


# --- Dicionarios de Escalas (padroes de intervalos em semitons) ---

PADROES_ESCALAS: dict[TipoEscala, list[int]] = {
    TipoEscala.MAIOR_NATURAL: [2, 2, 1, 2, 2, 2, 1],
    TipoEscala.MENOR_NATURAL: [2, 1, 2, 2, 1, 2, 2],
    TipoEscala.MENOR_HARMONICA: [2, 1, 2, 2, 1, 3, 1],
    TipoEscala.MENOR_MELODICA: [2, 1, 2, 2, 2, 2, 1],
    TipoEscala.PENTATONICA_MAIOR: [2, 2, 3, 2, 3],
    TipoEscala.PENTATONICA_MENOR: [3, 2, 2, 3, 2],
    TipoEscala.BLUES: [3, 2, 1, 1, 3, 2],
    TipoEscala.DIMINUTA_TOM_SEMITOM: [2, 1, 2, 1, 2, 1, 2, 1],
    TipoEscala.DIMINUTA_SEMITOM_TOM: [1, 2, 1, 2, 1, 2, 1, 2],
    TipoEscala.CROMATICA: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    TipoEscala.DORICA: [2, 1, 2, 2, 2, 1, 2],
    TipoEscala.FRIGIA: [1, 2, 2, 2, 1, 2, 2],
    TipoEscala.LIDIA: [2, 2, 2, 1, 2, 2, 1],
    TipoEscala.MIXOLIDIA: [2, 2, 1, 2, 2, 1, 2],
    TipoEscala.EOLIA: [2, 1, 2, 2, 1, 2, 2],
    TipoEscala.LOCRIA: [1, 2, 2, 1, 2, 2, 2],
}


# --- Funcionalidades Principais ---

def construir_escala(tonica: str, tipo: TipoEscala) -> Escala:
    """
    Constroi uma escala a partir da tonica e tipo especificados.

    Argumentos:
        tonica: Nota raiz da escala (ex: 'C', 'F#', 'Bb').
        tipo: Tipo da escala via enum TipoEscala.

    Retorna:
        Escala com notas e intervalos calculados.

    Excecoes:
        ValueError se a tonica nao for reconhecida.
    """
    if tonica not in NOTA_PARA_SEMITOM:
        raise ValueError(
            f"Tonica '{tonica}' nao reconhecida. "
            f"Notas validas: {list(NOTA_PARA_SEMITOM.keys())}"
        )

    tom_inicio = NOTA_PARA_SEMITOM[tonica]
    intervalos = PADROES_ESCALAS[tipo]
    notas: list[str] = [tonica]
    tom_atual = tom_inicio

    for i, intervalo in enumerate(intervalos):
        tom_atual = (tom_atual + intervalo) % 12
        # Se for o ultimo passo, volta a tonica
        if i == len(intervalos) - 1:
            notas.append(tonica)
        else:
            candidatos = SEMITOM_PARA_NOTA.get(tom_atual, [])
            nota_escolhida = _escolher_notacao(tom_atual, tonica, notas)
            notas.append(nota_escolhida)

    return Escala(
        tipo=tipo,
        tonica=tonica,
        notas=notas,
        intervalos=intervalos,
    )


def construir_acorde(
    raiz: str,
    qualidade: QualidadeAcorde,
    adicionar: list[int] | None = None,
) -> Acorde:
    """
    Constroi um acorde a partir da nota raiz e qualidade.

    Argumentos:
        raiz: Nota fundamental do acorde (ex: 'C', 'G#', 'Eb').
        qualidade: Qualidade do acorde via enum QualidadeAcorde.
        adicionar: Intervalos extras para acordes estendidos
                   (ex: [9, 11, 13] para C13).

    Retorna:
        Acorde com notas e simbolo.

    Excecoes:
        ValueError se a raiz nao for reconhecida.
    """
    if raiz not in NOTA_PARA_SEMITOM:
        raise ValueError(
            f"Raiz '{raiz}' nao reconhecida. "
            f"Notas validas: {list(NOTA_PARA_SEMITOM.keys())}"
        )

    # Padrões: lista de intervalos em semitons
    padroes_acordes: dict[QualidadeAcorde, tuple[list[int], str]] = {
        QualidadeAcorde.MAIOR: ([0, 4, 7], ""),
        QualidadeAcorde.MENOR: ([0, 3, 7], "m"),
        QualidadeAcorde.DIMINUTO: ([0, 3, 6], "dim"),
        QualidadeAcorde.AUMENTADO: ([0, 4, 8], "aug"),
        QualidadeAcorde.SUSPENSO_2: ([0, 2, 7], "sus2"),
        QualidadeAcorde.SUSPENSO_4: ([0, 5, 7], "sus4"),
        QualidadeAcorde.SEXTA: ([0, 4, 7, 9], "6"),
        QualidadeAcorde.SEXTA_MENOR: ([0, 3, 7, 9], "m6"),
        QualidadeAcorde.POWER: ([0, 7], "5"),
    }

    intervalos_base, sufixo = padroes_acordes[qualidade]
    tom_inicio = NOTA_PARA_SEMITOM[raiz]
    notas: list[str] = []

    for intervalo in intervalos_base:
        tom = (tom_inicio + intervalo) % 12
        nota = _escolher_notacao(tom, raiz, notas)
        notas.append(nota)

    # Acordes com setima e estendidos
    if adicionar:
        mapa_extensoes: dict[int, int] = {
            7: 10,   # 7 (menor) = 10 semitons
            7M: 11,  # 7M (maior) = 11 semitons
            8: 12,   # Oitava
            9: 14,   # Nona
            11: 17,  # Undecima
            13: 21,  # Tercecima
        }
        for ext in adicionar:
            intervalo_semi = mapa_extensoes.get(ext)
            if intervalo_semi is not None:
                tom = (tom_inicio + intervalo_semi) % 12
                nota = _escolher_notacao(tom, raiz, notas)
                notas.append(nota)

    # Constroi simbolo
    simbolo = f"{raiz}{sufixo}"
    if adicionar:
        for ext in adicionar:
            if ext == 7:
                simbolo += "7"
            elif ext == 7M:
                if qualidade == QualidadeAcorde.MAIOR:
                    simbolo = f"{raiz}maj7"
                elif qualidade == QualidadeAcorde.MENOR:
                    simbolo = f"{raiz}m7M"
            else:
                simbolo += str(ext)

    notacao_br = _notacao_brasileira(raiz)

    return Acorde(
        nota_raiz=raiz,
        qualidade=qualidade,
        simbolo=simbolo,
        notas=notas,
        intervalos=intervalos_base + [mapa_extensoes.get(e, e) for e in (adicionar or [])],
        notacao_brasileira=notacao_br,
    )


def ciclo_das_quintas(direcao: str = "quintas", inicio: str = "C") -> list[str]:
    """
    Navega pelo ciclo das quintas.

    Argumentos:
        direcao: 'quintas' (sobe quintas) ou 'quartas' (sobe quartas).
        inicio: Nota inicial para o ciclo.

    Retorna:
        Lista de 12 notas percorrendo o ciclo.
    """
    if direcao == "quintas":
        salto = 7  # quinta justa = 7 semitons
    elif direcao == "quartas":
        salto = 5  # quarta justa = 5 semitons
    else:
        raise ValueError("direcao deve ser 'quintas' ou 'quartas'")

    tom_atual = NOTA_PARA_SEMITOM[inicio]
    resultado: list[str] = []

    for _ in range(12):
        nota = SEMITOM_PARA_NOTA[tom_atual][0]
        resultado.append(nota)
        tom_atual = (tom_atual + salto) % 12

    return resultado


def consultar_armadura_clave(tonalidade: str, modo: str = "maior") -> ArmaduraClave:
    """
    Consulta a armadura de clave de uma tonalidade.

    Argumentos:
        tonalidade: Nota da tonalidade (ex: 'G', 'Eb', 'F#').
        modo: 'maior' ou 'menor'.

    Retorna:
        ArmaduraClave com numero de alteracoes e notas alteradas.
    """
    # Ordem dos sostenidos: F C G D A E B
    ordem_sostenidos = ["F", "C", "G", "D", "A", "E", "B"]
    # Ordem dos bemois: B E A D G C F (inverso)
    ordem_bemois = list(reversed(ordem_sostenidos))

    # Tonalidades maiores com seus sostenidos
    tonalidades_sostenidos: dict[str, int] = {
        "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5,
        "F#": 6, "C#": 7,
    }
    # Tonalidades maiores com bemois
    tonalidades_bemois: dict[str, int] = {
        "F": 1, "Bb": 2, "Eb": 3, "Ab": 4, "Db": 5,
        "Gb": 6, "Cb": 7,
    }

    # Para modo menor, usa relativa maior (menor = maior um tom e meio abaixo)
    def relativa_maior(tom: str, modo_str: str) -> tuple[str, str]:
        if modo_str == "menor":
            tom_semi = NOTA_PARA_SEMITOM[tom]
            maior_semi = (tom_semi + 3) % 12
            maior_nota = SEMITOM_PARA_NOTA[maior_semi][0]
            return maior_nota, "menor"
        return tom, "maior"

    tom_ref, modo_ref = relativa_maior(tonalidade, modo)

    notas_alteradas: list[str] = []

    if tom_ref in tonalidades_sostenidos:
        num = tonalidades_sostenidos[tom_ref]
        notas_alteradas = [f"{n}#" for n in ordem_sostenidos[:num]]
        return ArmaduraClave(
            tonalidade=tonalidade,
            modo=modo,
            sostenidos=num,
            bemois=0,
            notas_alteradas=notas_alteradas,
        )
    elif tom_ref in tonalidades_bemois:
        num = tonalidades_bemois[tom_ref]
        notas_alteradas = [f"{n}b" for n in ordem_bemois[:num]]
        return ArmaduraClave(
            tonalidade=tonalidade,
            modo=modo,
            sostenidos=0,
            bemois=num,
            notas_alteradas=notas_alteradas,
        )
    else:
        return ArmaduraClave(
            tonalidade=tonalidade,
            modo=modo,
            sostenidos=0,
            bemois=0,
            notas_alteradas=[],
        )


def analisar_progresao(
    simbolos: list[str],
    tonalidade: str = "C",
    modo: str = "maior",
) -> AnaliseProgresao:
    """
    Analisa uma progressao harmonica identificando graus e cadencias.

    Argumentos:
        simbolos: Lista de simbolos de acordes (ex: ['C', 'Am', 'F', 'G']).
        tonalidade: Tonalidade de referencia.
        modo: 'maior' ou 'menor'.

    Retorna:
        AnaliseProgresao com graus, cadencias e descricao.
    """
    # Acordes diatonicos para tonalidade maior
    acordes_diatonicos_maior: dict[str, int] = {}
    acordes_diatonicos_menor: dict[str, int] = {}

    escala_maior = construir_escala(tonalidade, TipoEscala.MAIOR_NATURAL)
    for i, nota in enumerate(escala_maior.notas[:7]):
        nota_base = nota
        acordes_diatonicos_maior[nota_base] = i + 1
        # Adiciona variante menor (para graus ii, iii, vi)
        if i in [1, 2, 5]:
            acordes_diatonicos_maior[f"{nota_base}m"] = i + 1
        # Adiciona dim (para vii)
        if i == 6:
            acordes_diatonicos_maior[f"{nota_base}dim"] = i + 1

    # Constroi acordes para a progressao
    acordes: list[Acorde] = []
    graus_identificados: list[tuple[int, str]] = []

    for simbolo in simbolos:
        # Tenta identificar o acorde
        acorde = _parsear_acorde(simbolo)
        acordes.append(acorde)

        # Tenta encontrar o grau
        grau = acordes_diatonicos_maior.get(simbolo, 0)
        if grau == 0:
            nota = simbolo.rstrip("m #b dim aug sus2 sus4 5 6 7 9 11 13").rstrip()
            if nota in [n for n in escala_maior.notas]:
                idx = escala_maior.notas.index(nota)
                grau = idx + 1
        graus_identificados.append((grau, simbolo))

    # Identifica cadencias
    cadencias = _identificar_cadencias(graus_identificados)

    descricao = _gerar_descricao_progresao(simbolos, graus_identificados, cadencias)

    return AnaliseProgresao(
        tonalidade=f"{tonalidade} {modo}",
        acordes=acordes,
        graus_identificados=graus_identificados,
        cadencias=cadencias,
        descricao=descricao,
    )


# --- Funcoes Auxiliares ---

def _escolher_notacao(tom: int, referencia: str, notas_previas: list[str]) -> str:
    """Escolhe a notacao mais adequada para um semitom."""
    candidatos = SEMITOM_PARA_NOTA.get(tom, [f"tom{tom}"])
    if len(candidatos) == 1:
        return candidatos[0]
    # Preferencia por sustenidos se a referencia tem sustain
    preferencia_sustenido = "#" in referencia
    for nota in candidatos:
        if preferencia_sustenido and "#" in nota:
            return nota
        if not preferencia_sustenido and "#" not in nota:
            return nota
    return candidatos[0]


def _notacao_brasileira(nota: str) -> str:
    """Converte notacao americana para notacao brasileira (C->Do, etc.)."""
    mapa: dict[str, str] = {
        "C": "Do", "D": "Re", "E": "Mi", "F": "Fa",
        "G": "Sol", "A": "La", "B": "Si",
    }
    base = nota.rstrip("#b")
    accid = nota[len(base):]
    nome = mapa.get(base, base)
    if accid:
        if accid == "#":
            nome += " sustenido"
        elif accid == "b":
            nome += " bemol"
    return nome


def _identificar_cadencias(graus: list[tuple[int, str]]) -> list[str]:
    """Identifica tipos de cadencias na progressao."""
    cadencias: list[str] = []
    for i in range(len(graus) - 1):
        g1, s1 = graus[i]
        g2, s2 = graus[i + 1]

        if g1 == 5 and g2 == 1:
            cadencias.append(f"Cadencia autentica (V -> I)")
        elif g1 == 4 and g2 == 1:
            cadencias.append(f"Cadencia plagal (IV -> I) - 'Amem'")
        elif g1 == 5 and g2 == 6:
            cadencias.append(f"Cadencia de engano (V -> VI)")
        elif g1 == 1 and g2 == 5:
            cadencias.append(f"Cadencia (I -> V)")
    return cadencias


def _gerar_descricao_progresao(
    simbolos: list[str],
    graus: list[tuple[int, str]],
    cadencias: list[str],
) -> str:
    """Gera descricao textual da progressao."""
    partes: list[str] = []
    partes.append(f"Progressao com {len(simbolos)} acordes: {' -> '.join(simbolos)}")

    if graus:
        partes_str = []
        for grau, simbolo in graus:
            if grau > 0:
            partes_str.append(f"{simbolo} (grau {grau})")
            else:
            partes_str.append(f"{simbolo} (grau N/A - possivel modulo)")
        partes.append("Grados: " + ", ".join(partes_str))

    if cadencias:
        partes.append("Cadencias encontradas:")
        partes.extend(f"  - {c}" for c in cadencias)

    return "\n".join(partes)


def _parsear_acorde(simbolo: str) -> Acorde:
    """Converte simbolo de acorde em objeto Acorde."""
    s = simbolo.strip()

    # Extrai nota raiz
    raiz_end = 2 if len(s) > 1 and (s[1] == '#' or s[1] == 'b') else 1
    raiz = s[:raiz_end]
    resto = s[raiz_end:]

    # Determina qualidade
    if resto.startswith('m') and not resto.startswith('maj'):
        qualidade = QualidadeAcorde.MENOR
        resto = resto[1:]
    elif resto.startswith('dim'):
        qualidade = QualidadeAcorde.DIMINUTO
        resto = resto[3:]
    elif resto.startswith('aug') or resto.startswith('+'):
        qualidade = QualidadeAcorde.AUMENTADO
        resto = resto[3:]
    elif resto.startswith('sus2'):
        qualidade = QualidadeAcorde.SUSPENSO_2
        resto = resto[4:]
    elif resto.startswith('sus4') or resto.startswith('sus'):
        qualidade = QualidadeAcorde.SUSPENSO_4
        resto = resto[4:] if resto.startswith('sus4') else resto[3:]
    elif resto.startswith('5'):
        qualidade = QualidadeAcorde.POWER
        resto = resto[1:]
    elif resto.startswith('6'):
        qualidade = QualidadeAcorde.SEXTA
        resto = resto[1:]
    else:
        qualidade = QualidadeAcorde.MAIOR

    adicionar: list[int] = []
    if '7M' in resto or 'maj7' in resto or 'Δ' in resto:
        adicionar.append(7M)
    elif '7' in resto:
        adicionar.append(7)
    for ext in ['13', '11', '9']:
        if ext in resto:
            adicionar.append(int(ext))

    return construir_acorde(raiz, qualidade, adicionar if adicionar else None)


# --- Classe Principal ---

class TeoriaMusical:
    """
    Classe principal para operacoes de teoria musical.

    Fornece metodos para consultar escalas, construir acordes,
    navegar pelo ciclo das quintas, consultar armaduras de clave
    e analisar progresoes harmonicas.
    """

    def listar_escalas_disponiveis(self) -> list[TipoEscala]:
        """Lista todos os tipos de escala suportados."""
        return list(TipoEscala)

    def identificar_escala(self, notas: list[str]) -> list[Escala]:
        """
        Identifica quais escalas contem as notas fornecidas.

        Argumentos:
            notas: Lista de notas para identificar a escala.

        Retorna:
            Lista de escalas correspondentes.
        """
        resultado: list[Escala] = []
        for tipo in TipoEscala:
            for nota in NOTA_PARA_SEMITOM:
                try:
                    escala = construir_escala(nota, tipo)
                    notas_set = set(escala.notas[:len(escala.notas)-1])
                    notas_input = set(notas)
                    if notas_input.issubset(notas_set):
                        resultado.append(escala)
                except ValueError:
                    continue
        return resultado

    def construir_e_exibir_escala(
        self, tonica: str, tipo: TipoEscala
    ) -> Escala:
        """Constroi e imprime informacoes da escala."""
        escala = construir_escala(tonica, tipo)
        print(f"Escala: {tipo.value} de {_notacao_brasileira(tonica)} ({tonica})")
        print(f"  Notas: {' - '.join(escala.notas)}")
        print(f"  Intervalos: {escala.intervalos}")
        return escala

    def construir_e_exibir_acorde(
        self,
        nota_raiz: str,
        qualidade: QualidadeAcorde,
        extensoes: list[int] | None = None,
    ) -> Acorde:
        """Constroi e imprime informacoes do acorde."""
        acorde = construir_acorde(nota_raiz, qualidade, extensoes)
        print(f"Acorde: {acorde.simbolo} ({acorde.notacao_brasileira} {acorde.qualidade.value})")
        print(f"  Notas: {' - '.join(acorde.notas)}")
        return acorde

    def exibir_ciclo_quintas(self, inicio: str = "C") -> None:
        """Exibe o ciclo das quintas a partir de uma nota."""
        print("\n=== Ciclo das Quintas ===")
        print(f"Iniciando em {inicio}:")
        ciclo = ciclo_das_quintas("quintas", inicio)
        print(f"  Quintas: {' -> '.join(ciclo)}")
        ciclo_q = ciclo_das_quintas("quartas", inicio)
        print(f"  Quartas: {' -> '.join(ciclo_q)}")

    def exibir_armadura(self, tonalidade: str, modo: str = "maior") -> ArmaduraClave:
        """Exibe informacoes da armadura de clave."""
        armadura = consultar_armadura_clave(tonalidade, modo)
        nota_br = _notacao_brasileira(tonalidade)
        print(f"\nArmadura de Clave: {nota_br} {modo}")
        if armadura.sostenidos > 0:
            print(f"  {armadura.sostenidos} sostenido(s): {', '.join(armadura.notas_alteradas)}")
        elif armadura.bemois > 0:
            print(f"  {armadura.bemois} bemol(is): {', '.join(armadura.notas_alteradas)}")
        else:
            print("  Sem alteracoes")
        return armadura

    def exibir_analise_progresao(
        self, simbolos: list[str], tonalidade: str = "C"
    ) -> AnaliseProgresao:
        """Analisa e exibe uma progressao harmonica."""
        resultado = analisar_progresao(simbolos, tonalidade)
        print(f"\n{'='*50}")
        print(f"Analise de Progressao - {resultado.tonalidade}")
        print(f"{'='*50}")
        print(resultado.descricao)
        return resultado


def main() -> None:
    """Funcao de demonstracao do modulo de Teoria Musical."""
    print("=" * 60)
    print("  Conservatorio Musical - Teoria Musical")
    print("  Departamento: Ensino | Professor Teoria")
    print("=" * 60)

    teoria = TeoriaMusical()

    # 1. Escalas
    print("\n--- Escalas ---")
    print("\nEscalas disponiveis:")
    for e in teoria.listar_escalas_disponiveis():
        print(f"  - {e.value}")

    escala_d_maior = teoria.construir_e_exibir_escala("D", TipoEscala.MAIOR_NATURAL)
    escala_am_harm = teoria.construir_e_exibir_escala("A", TipoEscala.MENOR_HARMONICA)
    teoria.construir_e_exibir_escala("Bb", TipoEscala.PENTATONICA_MAIOR)

    # 2. Acordes
    print("\n--- Acordes ---")
    teoria.construir_e_exibir_acorde("C", QualidadeAcorde.MAIOR)
    teoria.construir_e_exibir_acorde("Am", QualidadeAcorde.MENOR)
    teoria.construir_e_exibir_acorde("G", QualidadeAcorde.MAIOR, [7])
    teoria.construir_e_exibir_acorde("C", QualidadeAcorde.MAIOR, [7M])
    teoria.construir_e_exibir_acorde("F", QualidadeAcorde.MAIOR, [9, 13])
    teoria.construir_e_exibir_acorde("B", QualidadeAcorde.DIMINUTO)
    teoria.construir_e_exibir_acorde("E", QualidadeAcorde.POWER)

    # 3. Ciclo das Quintas
    teoria.exibir_ciclo_quintas("C")

    # 4. Armaduras de Clave
    teoria.exibir_armadura("G", "maior")
    teoria.exibir_armadura("Eb", "maior")
    teoria.exibir_armadura("A", "menor")

    # 5. Analise de Progressao
    teoria.exibir_analise_progresao(["C", "Am", "F", "G"], "C")
    teoria.exibir_analise_progresao(["Dm7", "G7", "Cmaj7", "Am7", "Dm7", "G7", "Cmaj7"], "C")
    teoria.exibir_analise_progresao(["Em7", "A7", "Dm7", "G7", "Cmaj7", "F#m7b5", "B7", "Em7"], "C")

    # 6. Identificar escala por notas
    print("\n--- Identificar Escala ---")
    encontradas = teoria.identificar_escala(["C", "E", "G", "B", "D"])
    print(f"Escalas que contem as notas C, E, G, B, D:")
    for esc in encontradas[:5]:
        print(f"  {esc.tipo.value}: {esc.tonica} -> {' '.join(esc.notas[:-1])}")
    if len(encontradas) > 5:
        print(f"  ... e {len(encontradas) - 5} mais")


if __name__ == "__main__":
    main()
