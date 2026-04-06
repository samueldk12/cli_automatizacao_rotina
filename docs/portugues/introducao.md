# Introducao ao MYC

## O que e o MYC?

MYC (My Commands) e uma ferramenta de linha de comando que resolve dois problemas:

1. **Automacao de Rotinas** — Cadastre grupos de aplicativos, URLs e abas do navegador organizados por dia da semana, execute com um unico comando e posicione janelas em multiplos monitores.
2. **Sistema de Agentes IA** — Implante um sistema modular de plugins com 65 especialistas, 27 empresas, 13 departamentos e 8 middlewares que transformam um LLM em uma equipe de agentes especializados.

## Instalacao

### Pre-requisitos

- Python 3.9+
- Windows 10 ou 11
- npm (para plataforma OpenClaude, opcional)

### Instalacao Rapida

```powershell
git clone https://github.com/samueldk12/cli_automatizacao_rotina.git
cd cli_automatizacao_rotina
.\install.ps1
```

### Instalacao Manual

```powershell
pip install -e .
myc setup --auto   # adiciona ~/.myc/bin ao PATH
# reinicie o terminal
```

## Configuracao

### Passo 1: Configurar OpenClaude (Plataforma IA)

```powershell
myc install openclaude
```

Isso guiara voce por:
1. Instalar OpenClaude via npm (se ainda nao estiver)
2. Inserir sua chave de API do OpenRouter
3. Selecionar um modelo (padrao: `qwen/qwen3.6-plus:free`)

> Nao tem uma chave do OpenRouter? Obtenha uma em [openrouter.ai](https://openrouter.ai/)

### Passo 2: Instalar Bundles de Plugins

```powershell
# Instalar todos os bundles de especialistas (65 plugins)
myc agent bundle-install --all

# Instalar um bundle especifico
myc agent bundle-install fullstack
myc agent bundle-install marketing
myc agent bundle-install professor
```

### Passo 3: Verificar Instalacao

```powershell
# Listar agentes configurados
myc agent list

# Listar empresas disponiveis
myc agent-company dev_agency

# Listar middlewares disponiveis
myc agent middleware --list

# Lancar seu agente
myc agent launch default
```

## Sua Primeira Rotina

```powershell
# Criar um novo grupo de comandos
myc add

# O wizard vai perguntar:
# 1. Nome do grupo (ex: "trabalhar")
# 2. Nome do subcomando (ex: "daily")
# 3. Dias da semana
# 4. Acoes (URLs para abrir, apps para executar)

# Executar a rotina
trabalhar daily

# Ou via TUI
myc tui
```

## Sua Primeira Consulta com IA

```powershell
# Consultar um especialista diretamente
myc agent-specialist frontend_dev "crie componente de dashboard responsivo"

# Usar uma empresa (organizacao multi-agente)
myc agent-company dev_agency tech_lead "arquitete backend em microservicos"

# Adicionar middlewares para saida aprimorada
myc agent-specialist backend_dev -o prompt_enhancer -o code_quality "implemente autenticacao JWT"
```

## Referencia Rapida de Comandos

| Comando | Descricao |
|---------|-----------|
| `myc add` | Criar novo comando de rotina |
| `myc list` | Listar todos os comandos |
| `myc tui` | Abrir navegacao visual no terminal |
| `myc monitors` | Listar monitores detectados |
| `myc setup --auto` | Gerar atalhos e adicionar ao PATH |
| `myc config-html` | Abrir dashboard web (localhost:8787) |
| `myc install openclaude` | Instalar e configurar plataforma IA |
| `myc agent add` | Criar perfil de agente |
| `myc agent list` | Listar agentes configurados |
| `myc agent launch <nome>` | Lancar um agente |
| `myc agent-specialist <nome> "consulta"` | Consultar especialista |
| `myc agent-company <empresa> [sub] "consulta"` | Consultar sub-agente de empresa |
| `myc agent-department <dept> "consulta"` | Consultar departamento |
| `myc agent middleware --list` | Listar middlewares disponiveis |
| `myc agent bundle-install --all` | Instalar todos os bundles |

## Proximos Passos

- Leia a arquitetura completa: [ARCHITECTURE.md](../ARCHITECTURE.md)
- Consulte a referencia de plugins: [../plugins/README.md](../plugins/README.md)
- Veja casos de uso reais: [casos_de_uso.md](./casos_de_uso.md)
