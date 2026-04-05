"""
Gerencia plugins de agentes — instalacao, criacao, e integracao com MYC.

Plugins sao instalados em ~/.myc/agents/plugins/ pelo MYC,
e em ~/.myc/agents/plugins/bundles/ ficam "bundles" de plugins por area.
"""

import json
import shutil
import sys
from pathlib import Path

from rich.console import Console

console = Console()

PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"
BUNDLES_DIR = Path.home() / ".myc" / "agents" / "bundles"
PLUGIN_REGISTRY = Path.home() / ".myc" / "agents" / "plugin_registry.json"
MYC_PLUGINS_BUILTIN = Path(__file__).parent.parent / "plugins" / "bundles"


# ── Bundles (conjuntos de plugins por area) ─────────────────

BUNDLES = {
    # ─── Marketing ─────────────────────────────────────────
    "marketing": {
        "name": "Agencia de Marketing",
        "description": "Redes sociais, SEO, copywriting, campanhas, analytics",
        "plugins": ["social_media", "seo_analyst", "copywriter", "campaign_manager"],
        "icon": "Megafone",
    },
    # ─── Game Design ───────────────────────────────────────
    "gamedesign": {
        "name": "Estudio de Game Design",
        "description": "Level design, narrativa interativa, mecanicas, balanco, UX de jogo",
        "plugins": ["level_designer", "game_narrative", "mechanics_balancer", "game_ux"],
        "icon": "Gamepad",
    },
    # ─── Advocacia Brasileira ──────────────────────────────
    "advocacia": {
        "name": "Escritorio de Advocacia (BR)",
        "description": "Legislacao brasileira, contratos, peticoes, jurisprudencia",
        "plugins": ["legislacao_br", "contratos_br", "peticoes", "jurisprudencia"],
        "icon": "Martelo",
    },
    # ─── Jornalismo ────────────────────────────────────────
    "jornalismo": {
        "name": "Redacao Jornalistica",
        "description": "Pautas, reportagens, fact-checking, redacao, editoriais",
        "plugins": ["pauta_journal", "fact_checker", "redacao_news", "editorial"],
        "icon": "Noticia",
    },
    # ─── OSINT ─────────────────────────────────────────────
    "osint": {
        "name": "Inteligencia OSINT",
        "description": "Investigacao digital, fonte aberta, analise de dados publicos",
        "plugins": ["osint_collector", "source_analyzer", "digital_footprint", "data_correlator"],
        "icon": "Lupa",
    },
    # ─── Seguranca Web ────────────────────────────────────
    "seguranca_web": {
        "name": "Seguranca Web",
        "description": "Auditoria web, OWASP, pentest, hardening",
        "plugins": ["web_auditor", "owasp_checker", "pentest_helper", "hardening_guide"],
        "icon": "Escudo",
    },
    # ─── Bug Bounty ───────────────────────────────────────
    "bugbounty": {
        "name": "Bug Bounty Hunter",
        "description": "Recon, exploit writing, report, triagem",
        "plugins": ["recon", "exploit_writer", "bounty_report", "vuln_triage"],
        "icon": "Inseto",
    },
    # ─── Visao Computacional ──────────────────────────────
    "visao_computacional": {
        "name": "Engenharia de Visao Computacional",
        "description": "CNN, deteccao de objetos, segmentacao, OpenCV, PyTorch",
        "plugins": ["cv_architect", "dataset_builder", "model_trainer", "cv_deployer"],
        "icon": "Olho",
    },
    # ─── Full Stack ───────────────────────────────────────
    "fullstack": {
        "name": "Desenvolvimento Full Stack",
        "description": "Frontend, backend, banco de dados, deploy, DevOps",
        "plugins": ["frontend_dev", "backend_dev", "database_designer", "devops_deploy"],
        "icon": "Codigo",
    },
    # ─── App Mobile ───────────────────────────────────────
    "app_mobile": {
        "name": "Desenvolvimento de App Mobile",
        "description": "React Native, Flutter, iOS, Android, UI/UX mobile",
        "plugins": ["mobile_architect", "ui_mobile", "native_bridge", "app_store_prep"],
        "icon": "Smartphone",
    },
    # ─── Ideias / Brainstorming ───────────────────────────
    "ideias": {
        "name": "Gerador de Ideias",
        "description": "Brainstorming, design thinking, validacao, prototipagem rapida",
        "plugins": ["brainstorm", "design_thinking", "idea_validator", "mvp_builder"],
        "icon": "Lampada",
    },
    # ─── Vendas / Empreendedorismo ────────────────────────
    "vendas": {
        "name": "Vendas e Empreendedorismo",
        "description": "Pitch, funil de vendas, modelo de negocio, growth hacking",
        "plugins": ["sales_pitch", "sales_funnel", "business_model", "growth_hacker"],
        "icon": "Dolar",
    },
    # ─── Engenharia de Dados ──────────────────────────────
    "data_engineering": {
        "name": "Engenharia de Dados",
        "description": "ETL, pipelines, data warehouse, Spark, Airflow",
        "plugins": ["etl_builder", "pipeline_designer", "data_quality", "warehouse_architect"],
        "icon": "Banco de dados",
    },
    # ─── Engenharia de Software ───────────────────────────
    "software_engineering": {
        "name": "Engenharia de Software",
        "description": "Arquitetura, clean code, design patterns, testes, CI/CD",
        "plugins": ["software_architect", "code_reviewer", "test_engineer", "ci_cd_expert"],
        "icon": "Engrenagem",
    },
    # ─── Engenharia da Computacao ─────────────────────────
    "computer_engineering": {
        "name": "Engenharia da Computacao",
        "description": "Sistemas embarcados, IoT, redes, sistemas operacionais, hardware",
        "plugins": ["embedded_dev", "iot_engineer", "network_analyzer", "os_internals"],
        "icon": "Chip",
    },
    # ─── Professor (multi-area) ───────────────────────────
    "professor": {
        "name": "Professor / Educador",
        "description": "Planejamento de aula, avaliacoes, didatica, conteudo educativo",
        "plugins": ["lesson_planner", "exam_creator", "didatica", "content_creator_edu"],
        "icon": "Livro",
    },
}


def install_bundles(all_: bool = False, names: list[str] | None = None) -> None:
    """Instala todos os plugins de um ou mais bundles no diretorio do usuario."""
    from myc.plugin_installer import install_plugin

    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

    targets = []
    if all_:
        targets = list(BUNDLES.keys())
    elif names:
        targets = names
    else:
        # Mostra lista e pergunta
        from rich.table import Table
        table = Table(title="Bundles Disponiveis", show_lines=True)
        table.add_column("ID", style="cyan", width=25)
        table.add_column("Nome", style="yellow", width=30)
        table.add_column("Descrição", style="green")
        table.add_column("Plugins", style="dim")
        for bid, bdata in BUNDLES.items():
            table.add_row(
                bid,
                bdata["name"],
                bdata["description"],
                str(len(bdata["plugins"])),
            )
        console.print(table)
        return

    installed_count = 0
    for bundle_id in targets:
        if bundle_id not in BUNDLES:
            console.print(f"[red]Bundle desconhecido: {bundle_id}[/red]")
            continue

        bundle = BUNDLES[bundle_id]
        console.print(f"\n[bold cyan]Instalando bundle: {bundle['name']}[/bold cyan]")

        for plugin_name in bundle["plugins"]:
            if install_plugin(plugin_name):
                installed_count += 1

    console.print(f"\n[green]{installed_count} plugins instalados.[/green]")


def register_bundle_install(bundle_id: str, agent_name: str) -> None:
    """Registra que um bundle foi instalado para um agente especifico."""
    from myc.agent import _load_agents, _save_agents

    agents = _load_agents()
    if agent_name not in agents:
        console.print(f"[yellow]Agente '{agent_name}' nao existe. Criando...[/yellow]")
        agents[agent_name] = {
            "name": agent_name,
            "platform": "openclaude",
            "env": {},
            "cwd": None,
            "initial_context": "",
            "custom_command": None,
            "plugins": [],
            "linked_routines": [],
            "created_at": str(__import__("datetime").datetime.now().isoformat()),
        }

    bundle = BUNDLES.get(bundle_id)
    if not bundle:
        console.print(f"[red]Bundle '{bundle_id}' nao encontrado.[/red]")
        return

    profile = agents[agent_name]
    existing = set(profile.get("plugins", []))
    new_plugins = set(bundle["plugins"]) - existing
    profile.setdefault("plugins", []).extend(new_plugins)
    _save_agents(agents)

    if new_plugins:
        console.print(f"[green]{len(new_plugins)} plugins do bundle '{bundle_id}' vinculados ao agente '{agent_name}'.[/green]")
    else:
        console.print(f"[dim]Todos os plugins do bundle ja estavam vinculados.[/dim]")


def list_bundles() -> None:
    """Lista todos os bundles disponiveis e status de instalacao."""
    from rich.table import Table
    from myc.plugin_installer import get_plugin_meta

    table = Table(title="Bundles de Plugins", show_lines=True)
    table.add_column("Bundle", style="cyan")
    table.add_column("Nome", style="yellow")
    table.add_column("Plugins", style="green")
    table.add_column("Instalados", style="dim")

    for bid, bdata in BUNDLES.items():
        installed = 0
        for pname in bdata["plugins"]:
            if get_plugin_meta(pname):
                installed += 1
        status = f"{installed}/{len(bdata['plugins'])}"
        table.add_row(bid, bdata["name"], str(len(bdata["plugins"])), status)

    console.print(table)
