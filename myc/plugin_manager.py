"""
Gerencia plugins de agentes — instalacao, criacao, e integracao com MYC.

Plugins sao instalados em ~/.myc/agents/plugins/ pelo MYC (specialists),
e em ~/.myc/agents/companies/ ficam os plugins de empresas.
"""

import json
import shutil
import sys
from pathlib import Path

from rich.console import Console

console = Console()

PLUGINS_DIR = Path.home() / ".myc" / "agents" / "plugins"
COMPANIES_DIR = Path.home() / ".myc" / "agents" / "companies"
PLUGIN_REGISTRY = Path.home() / ".myc" / "agents" / "plugin_registry.json"
MYC_PLUGINS_SPECIALISTS = Path(__file__).parent.parent / "plugins" / "specialists"
MYC_PLUGINS_COMPANIES = Path(__file__).parent.parent / "plugins" / "companies"


# ── Bundles de Specialists (conjuntos de plugins por area) ──

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


# ── Bundles de Empresas (conjuntos de sub-agentes por empresa) ──

COMPANY_BUNDLES = {
    "agencia_marketing_full": {
        "name": "Agencia Marketing Full",
        "description": "Equipe completa de marketing — social media, SEO, copy, campanhas",
        "specialists": ["social_media", "seo_analyst", "copywriter", "campaign_manager"],
        "company_context": "Voces sao uma agencia de marketing completa. Trabalhem em equipe cobrindo todas as areas de marketing digital.",
    },
    "dev_house_full": {
        "name": "Dev House",
        "description": "Equipe de desenvolvimento completa — frontend, backend, database, DevOps",
        "specialists": ["frontend_dev", "backend_dev", "database_designer", "devops_deploy"],
        "company_context": "Voces sao uma equipe de desenvolvimento full stack. Cada um cuida de sua area enquanto colabora com o todo.",
    },
    "security_team": {
        "name": "Equipe de Seguranca",
        "description": "Time completo de seguranca — auditoria, OWASP, pentest, hardening",
        "specialists": ["web_auditor", "owasp_checker", "pentest_helper", "hardening_guide"],
        "company_context": "Voces sao um time de seguranca ofensiva e defensiva. Cobram todas as camadas de seguranca do software.",
    },
}


# ── Instalacao de Bundles ──────────────────────────────────

def install_bundles(all_: bool = False, names: list[str] | None = None) -> None:
    """Instala todos os plugins de um ou mais bundles de specialists no diretorio do usuario."""
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
        console.print(f"\n[bold cyan]Instalando bundle de specialists: {bundle['name']}[/bold cyan]")

        for plugin_name in bundle["plugins"]:
            if install_plugin(plugin_name):
                installed_count += 1

    console.print(f"\n[green]{installed_count} plugins specialists instalados.[/green]")


def install_company_bundle(bundle_id: str) -> None:
    """Instala um bundle de empresa, criando o plugin company e seus specialists."""
    from myc.plugin_installer import install_plugin, install_company_plugin

    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)

    if bundle_id not in COMPANY_BUNDLES:
        console.print(f"[red]Bundle de empresa desconhecido: {bundle_id}[/red]")
        console.print("Disponiveis: " + ", ".join(COMPANY_BUNDLES.keys()))
        return

    bundle = COMPANY_BUNDLES[bundle_id]
    console.print(f"\n[bold cyan]Instalando empresa: {bundle['name']}[/bold cyan]")

    # Instala os specialists referenciados
    for sp_id in bundle["specialists"]:
        install_plugin(sp_id)

    # Gera o plugin de empresa
    _generate_company_plugin(bundle_id, bundle)


def _generate_company_plugin(bundle_id: str, bundle: dict) -> None:
    """Gera um plugin de empresa dinamicamente a partir de um bundle."""
    import json

    specialists_list = []
    for sp_id in bundle["specialists"]:
        # Tenta pegar nome e descricao do specialist
        try:
            from myc.plugin_installer import get_plugin_meta
            meta = get_plugin_meta(sp_id)
            sp_name = meta["name"] if meta else sp_id
        except Exception:
            sp_name = sp_id

        specialists_list.append({
            "id": sp_id,
            "name": sp_name,
            "role": f"Especialista em {sp_name}. Responsavel por todas as tarefas relacionadas a esta area dentro da empresa.",
            "specialists": [sp_id],  # referencia a si mesmo
        })

    ctx_lines = [bundle["company_context"]]
    ctx_lines.append("\nEspecialistas disponiveis nesta empresa:")
    for s in specialists_list:
        ctx_lines.append(f"  - {s['name']} (ID: {s['id']})")

    context_block = f'''
def COMPANY_CONTEXT():
    return """{"\n".join(ctx_lines)}"""
'''

    template = f'''"""
Empresa: {bundle['name']}
Descricao: {bundle['description']}
Gerada automaticamente via bundle: {bundle_id}
"""

NAME = "{bundle['name']}"
DESCRIPTION = "{bundle['description']}"

SPECIALISTS = {json.dumps(specialists_list, indent=4, ensure_ascii=False)}
{context_block}
'''

    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
    target = COMPANIES_DIR / f"{bundle_id}.py"
    target.write_text(template, encoding="utf-8")
    console.print(f"[green]Empresa '{bundle_id}' criada em {target}[/green]")


def register_bundle_install(bundle_id: str, agent_name: str) -> None:
    """Registra que um bundle de specialists foi instalado para um agente especifico."""
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
    """Lista todos os bundles de specialists disponiveis e status de instalacao."""
    from rich.table import Table
    from myc.plugin_installer import get_plugin_meta

    table = Table(title="Bundles de Specialists", show_lines=True)
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


def list_company_bundles() -> None:
    """Lista todos os bundles de empresas disponiveis."""
    from rich.table import Table

    table = Table(title="Bundles de Empresas", show_lines=True)
    table.add_column("Bundle", style="cyan")
    table.add_column("Nome", style="yellow")
    table.add_column("Descricao", style="green")
    table.add_column("Specialists", style="dim")

    for bid, bdata in COMPANY_BUNDLES.items():
        table.add_row(
            bid,
            bdata["name"],
            bdata["description"],
            ", ".join(bdata["specialists"]),
        )

    console.print(table)
