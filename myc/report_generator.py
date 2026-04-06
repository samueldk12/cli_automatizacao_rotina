"""
MYC Report Generator - HTML Report Generation for all plugins.
Gera relatorios HTML estilizados (dark theme, responsive) para todos os plugins.
"""
import os
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class ReportSection:
    title: str
    subtitle: str = ""
    metrics: list = field(default_factory=list)
    tables: list = field(default_factory=list)
    charts_data: list = field(default_factory=list)
    text: str = ""
    items: list = field(default_factory=list)


@dataclass
class ReportConfig:
    title: str
    subtitle: str = ""
    company_name: str = ""
    sections: list = field(default_factory=list)
    footer: str = ""


def gerar_relatorio_html(config, output_path=None):
    today = date.today().strftime("%d/%m/%Y")
    sections_html = ""
    for sec in config.sections:
        metrics_html = ""
        if sec.metrics:
            metrics_html = '<div class="metrics-grid">'
            for label, value, color in sec.metrics:
                metrics_html += f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="color:var(--accent-{color});">{value}</div></div>'
            metrics_html += '</div>'
        text_html = f'<div class="report-text">{sec.text}</div>' if sec.text else ""
        items_html = ""
        if sec.items:
            items_html = '<ul class="bullet-list">' + "".join(f"<li>{i}</li>" for i in sec.items) + '</ul>'
        tables_html = ""
        for tbl in sec.tables:
            hdr = "".join(f"<th>{h}</th>" for h in tbl.get("headers", []))
            rows = "".join(f"<tr>{''.join(f'<td>{c}</td>' for c in r)}</tr>" for r in tbl.get("rows", []))
            tables_html += f'<div class="table-container"><table><thead><tr>{hdr}</tr></thead><tbody>{rows}</tbody></table></div>'
        charts_html = ""
        for ch in sec.charts_data:
            bars = ""
            for lb, vl, cl in zip(ch.get("labels", []), ch.get("values", []), ch.get("colors", [])):
                bars += f'<div class="bar-row"><span class="bar-label">{lb}</span><div class="bar-container"><div class="bar" style="width:{vl}%;background:var(--accent-{cl})" title="{vl}%"></div></div><span class="bar-value">{vl}%</span></div>'
            charts_html += f'<div class="chart-container"><h4>{ch.get("title","")}</h4>{bars}</div>'
        sections_html += f'<section class="report-section"><h2>{sec.title}</h2><h3 class="section-subtitle">{sec.subtitle}</h3>{metrics_html}{text_html}{items_html}{tables_html}{charts_html}</section>'
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{config.title} - MYC Report</title>
<style>
:root{{--bg:#121218;--bg2:#1e1e28;--bg3:#282836;--bd:#3a3a4a;--tx:#e8e8f0;--tx2:#a0a0b8;--tx3:#6a6a7e;--green:#2ec453;--red:#dc3545;--yellow:#ffc107;--blue:#0d6efd;--cyan:#00d2d3;--purple:#a55eea;--orange:#fd7e14;--pink:#e83e8c}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--tx);line-height:1.6}}
.hdr{{background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);padding:40px 24px;text-align:center;border-bottom:3px solid var(--cyan)}}
.hdr h1{{font-size:2.2rem;font-weight:700;background:linear-gradient(135deg,var(--cyan),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hdr .sub{{color:var(--tx2);font-size:1.05rem;margin-top:8px}}
.hdr .dt{{color:var(--tx3);font-size:.85rem;margin-top:12px}}
.ctn{{max-width:1100px;margin:0 auto;padding:24px}}
.sec{{background:var(--bg3);border:1px solid var(--bd);border-radius:12px;padding:24px;margin-bottom:24px}}
.sec h2{{font-size:1.4rem;color:var(--cyan);margin-bottom:4px;border-bottom:2px solid var(--bd);padding-bottom:8px}}
.sec .sst{{color:var(--tx3);font-size:.9rem;margin-bottom:16px}}
.mg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}}
.mc{{background:var(--bg2);border:1px solid var(--bd);border-radius:8px;padding:16px;text-align:center}}
.mc .ml{{color:var(--tx2);font-size:.85rem;margin-bottom:8px}}
.mc .mv{{font-size:1.8rem;font-weight:700}}
.rt{{color:var(--tx2);margin-bottom:16px;line-height:1.7}}
.bl{{color:var(--tx2);padding-left:24px;margin-bottom:16px}}
.bl li{{margin-bottom:6px}}
.tc{{overflow-x:auto;margin:16px 0}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:10px 14px;text-align:left;border-bottom:1px solid var(--bd)}}
th{{background:var(--bg2);color:var(--cyan);font-weight:600;font-size:.85rem}}
td{{color:var(--tx2);font-size:.9rem}}
tr:hover td{{background:rgba(0,210,211,.05)}}
.cc{{margin:16px 0}}.cc h4{{color:var(--tx);margin-bottom:10px}}
.br{{display:flex;align-items:center;margin-bottom:8px}}
.blb{{width:140px;color:var(--tx2);font-size:.85rem;text-align:right;padding-right:12px}}
.bc{{flex:1;background:var(--bg2);border-radius:4px;height:24px;overflow:hidden}}
.bar{{height:100%;border-radius:4px}}
.bv{width:60px;text-align:right;color:var(--tx3);font-size:.85rem}
.ft{{text-align:center;padding:20px;color:var(--tx3);font-size:.8rem;border-top:1px solid var(--bd)}}
@media print{{body{{background:#fff;color:#1a1a2e}}.sec{{border:1px solid #ccc;background:#fff}}}}
@media(max-width:768px){.mg{grid-template-columns:1fr}.hdr h1{font-size:1.6rem}.blb{width:100px;font-size:.75rem}}
</style>
</head>
<body>
<div class="hdr">
<h1>{config.title}</h1>
{f'<div class="sub">{config.subtitle}</div>' if config.sub else ''}
<div class="dt">Gerado em {today} {f'- {config.company_name}' if config.company_name else ''}</div>
</div>
<div class="ctn">{sections_html}</div>
<div class="ft"><p>{config.footer or f'MYC - My Company Assistant | Gerado automaticamente em {today}'}</p></div>
</body>
</html>'''
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Relatorio HTML gerado: {output_path}")
    return html


def gerar_pdf(html_content, output_path):
    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(output_path)
        print(f"PDF gerado: {output_path}")
        return True
    except ImportError:
        print("Instale weasyprint para gerar PDF: pip install weasyprint")
        return False
