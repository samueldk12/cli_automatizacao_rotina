"""
Company Memory — Memória compartilhada entre agentes de uma empresa.

Cada empresa tem sua propria memoria persistida em:
  ~/.myc/company_memory/<company_id>/

Operacoes:
  - save(key, value) — salva um dado na memoria da empresa
  - get(key) — recupera
  - list() — lista todas as keys
  - delete(key) — apaga
  - append(key, value) — append em lista
  - share(from_dept, to_dept, key) — compartilha dado entre depts

A memoria permite que o output de um agente seja reused
por outro departamento na fase seguinte.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

MEMORY_BASE = Path.home() / ".myc" / "company_memory"
MEMORY_BASE.mkdir(parents=True, exist_ok=True)


def _company_path(company_id: str) -> Path:
    """Diretorio de memoria de uma empresa."""
    p = MEMORY_BASE / company_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _index_path(company_id: str) -> Path:
    """Indice da memoria da empresa."""
    return _company_path(company_id) / "index.json"


def _load_index(company_id: str) -> dict[str, dict]:
    """Carrega indice de keys da empresa."""
    idx = _index_path(company_id)
    if idx.exists():
        try:
            return json.loads(idx.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_index(company_id: str, index: dict) -> None:
    """Salva indice."""
    _index_path(company_id).write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save(company_id: str, key: str, value: Any,
         dept: str = "", source: str = "") -> str:
    """Salva dado na memoria da empresa.

    Args:
        company_id: ID da empresa
        key: identificador unico
        value: valor (serializavel para JSON)
        dept: departamento que salvou
        source: contexto adicional (ex: specialist name)

    Returns:
        Path do arquivo salvo.
    """
    company_dir = _company_path(company_id)
    file_path = company_dir / f"{key}.json"

    data = {
        "key": key,
        "value": value,
        "department": dept,
        "source": source,
        "company_id": company_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Atualiza indice
    index = _load_index(company_id)
    index[key] = {
        "department": dept,
        "source": source,
        "file": f"{key}.json",
        "created_at": data["created_at"],
        "summary": _truncate(str(value)) if isinstance(value, str) else str(value)[:80],
    }
    _save_index(company_id, index)

    return str(file_path)


def get(company_id: str, key: str) -> Any | None:
    """Recupera dado da memoria da empresa."""
    company_dir = _company_path(company_id)
    file_path = company_dir / f"{key}.json"
    if file_path.exists():
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return data.get("value")
        except Exception:
            pass
    return None


def get_full(company_id: str, key: str) -> dict | None:
    """Recupera dado completo com metadados."""
    company_dir = _company_path(company_id)
    file_path = company_dir / f"{key}.json"
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def delete(company_id: str, key: str) -> bool:
    """Apaga dado da memoria."""
    company_dir = _company_path(company_id)
    file_path = company_dir / f"{key}.json"
    if file_path.exists():
        file_path.unlink()
        index = _load_index(company_id)
        index.pop(key, None)
        _save_index(company_id, index)
        return True
    return False


def list_keys(company_id: str) -> list[dict]:
    """Lista todos os itens de memoria da empresa."""
    index = _load_index(company_id)
    return [
        {
            "key": k,
            "department": v.get("department", ""),
            "source": v.get("source", ""),
            "created_at": v.get("created_at", ""),
            "summary": v.get("summary", ""),
        }
        for k, v in index.items()
    ]


def append(company_id: str, key: str, value: Any,
           dept: str = "") -> str:
    """Append em uma lista existente (ou cria nova)."""
    existing = get(company_id, key)
    if existing is None:
        return save(company_id, key, [value], dept=dept)

    if isinstance(existing, list):
        existing.append(value)
        return save(company_id, key, existing, dept=dept)
    else:
        # Converte em lista
        return save(company_id, key, [existing, value], dept=dept)


def share(company_id: str, key: str, to_dept: str) -> bool:
    """Compartilha um dado de memoria com outro departamento."""
    data = get_full(company_id, key)
    if not data:
        return False

    data["shared_with"] = data.get("shared_with", [])
    if to_dept not in data["shared_with"]:
        data["shared_with"].append(to_dept)
    data["updated_at"] = datetime.now().isoformat()

    company_dir = _company_path(company_id)
    (company_dir / f"{key}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return True


def get_for_department(company_id: str, dept: str) -> list[dict]:
    """Recupera todos os dados que um departamento pode acessar.

    Inclui dados criados pelo proprio departamento mais dados
    compartilhados de outros departamentos.
    """
    all_keys = list_keys(company_id)
    result = []

    for item in all_keys:
        if item["department"] == dept:
            result.append(item)
        else:
            # Verifica se esta compartilhado
            full = get_full(company_id, item["key"])
            if full and dept in full.get("shared_with", []):
                result.append(item)

    return result


def _truncate(text: str, maxlen: int = 120) -> str:
    if len(text) > maxlen:
        return text[:maxlen] + "..."
    return text


def show_memory_table(company_id: str) -> None:
    """Mostra memoria da empresa em tabela."""
    from rich.table import Table

    items = list_keys(company_id)
    if not items:
        console = Console()
        console.print(f"[yellow]Nenhuma memoria para empresa '{company_id}'.[/yellow]")
        return

    table = Table(title=f"Memoria: {company_id}")
    table.add_column("Key", style="cyan")
    table.add_column("Departamento", style="yellow")
    table.add_column("Criado", style="dim")
    table.add_column("Resumo", style="green")
    table.add_column("Compartilhado", style="magenta")

    for item in items:
        full = get_full(company_id, item["key"])
        shared = ", ".join(full.get("shared_with", [])) if full else "-"
        table.add_row(
            item["key"],
            item["department"] or "-",
            (item["created_at"] or "")[:19],
            item["summary"][:50],
            shared or "-",
        )

    from rich.console import Console
    Console().print(table)
