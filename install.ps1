# ============================================================
# MYC - My Commands  |  Script de Instalação (PowerShell)
# ============================================================
# Execução: .\install.ps1
# Requer: Python 3.9+ instalado

param(
    [switch]$Force   # Reinstala mesmo se já instalado
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  MYC - My Commands  |  Instalador" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ── Verifica Python ──────────────────────────────────────
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERRO: Python nao encontrado no PATH." -ForegroundColor Red
    Write-Host "Instale Python 3.9+ em https://python.org" -ForegroundColor Yellow
    exit 1
}

$pyVersion = & python --version 2>&1
Write-Host "Python encontrado: $pyVersion" -ForegroundColor Green

# ── Instala o pacote ─────────────────────────────────────
Write-Host ""
Write-Host "Instalando dependencias..." -ForegroundColor Cyan
Set-Location $scriptDir

try {
    & python -m pip install -e . --quiet
    Write-Host "Pacote instalado com sucesso." -ForegroundColor Green
} catch {
    Write-Host "ERRO na instalacao: $_" -ForegroundColor Red
    exit 1
}

# ── Configura PATH e gera scripts ────────────────────────
Write-Host ""
Write-Host "Configurando PATH e gerando scripts..." -ForegroundColor Cyan

try {
    & python -m myc setup --auto
} catch {
    Write-Host "AVISO: Nao foi possivel configurar o PATH automaticamente." -ForegroundColor Yellow
    Write-Host "Execute manualmente: myc setup --auto" -ForegroundColor Yellow
}

# ── Conclusao ────────────────────────────────────────────
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Instalacao concluida!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Reinicie o terminal (para o PATH ter efeito)" -ForegroundColor White
Write-Host "  2. Execute: myc add" -ForegroundColor White
Write-Host "     para cadastrar seu primeiro comando" -ForegroundColor White
Write-Host ""
Write-Host "Comandos disponiveis:" -ForegroundColor Cyan
Write-Host "  myc add               - Adicionar novo comando" -ForegroundColor White
Write-Host "  myc list              - Listar comandos" -ForegroundColor White
Write-Host "  myc tui               - Navegacao visual" -ForegroundColor White
Write-Host "  myc monitors          - Ver monitores" -ForegroundColor White
Write-Host "  myc run <grupo> <cmd> - Executar diretamente" -ForegroundColor White
Write-Host ""
