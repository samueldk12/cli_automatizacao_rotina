# MYC — My Commands

CLI para cadastrar e executar atalhos de sites e aplicativos diretamente do terminal, com suporte a **multi-monitor** e organização por **dia da semana**.

---

## Funcionalidades

- Cadastrar grupos de comandos (ex: `estudar`, `trabalhar`)
- Cada comando abre URLs e/ou aplicativos em monitores específicos
- Filtro por dia da semana (`segunda`, `terca`, `quarta`, `quinta`, `sexta`, `sabado`, `domingo`)
- Navegação visual interativa (TUI) com setas
- Scripts de atalho gerados automaticamente no PATH
- Reposicionamento de janelas via Win32 API

---

## Instalação

### Pré-requisitos

- Python 3.9+
- Windows 10 ou 11

### Via PowerShell

```powershell
git clone https://github.com/samueldk12/cli_automatizacao_rotina.git
cd cli_automatizacao_rotina
.\install.ps1
```

### Manual

```powershell
pip install -e .
myc setup --auto   # adiciona ~/.myc/bin ao PATH
# reinicie o terminal
```

---

## Uso rápido

### Adicionar um comando

```
myc add
```

Segue um wizard interativo:

```
Grupo       →  estudar
Subcomando  →  visao-computacional
Dias        →  Segunda, Quarta, Sexta
Ação 1      →  https://udemy.com/...  | Monitor 1 | Nova janela
Ação 2      →  https://colab.research.google.com  | Monitor 2 | Nova janela
```

### Executar um comando

```powershell
estudar visao-computacional            # executa direto
estudar segunda visao-computacional    # filtra pelo dia
estudar                                # abre TUI do grupo
```

### Navegação visual

```
myc tui
```

Opções de navegação:
- Por grupo de comandos
- Por dia da semana
- Grade semanal
- Busca por nome/descrição

---

## Comandos disponíveis

| Comando | Descrição |
|---------|-----------|
| `myc add` | Cadastra novo comando (wizard interativo) |
| `myc list` | Lista todos os comandos |
| `myc list -g estudar` | Lista comandos de um grupo |
| `myc run <grupo> <cmd>` | Executa um comando |
| `myc run <grupo> <dia> <cmd>` | Executa com filtro de dia |
| `myc tui` | Navegação visual interativa |
| `myc tui --group estudar` | TUI direto em um grupo |
| `myc edit <grupo> <cmd>` | Edita um comando existente |
| `myc delete <grupo> <cmd>` | Remove um subcomando |
| `myc delete <grupo>` | Remove um grupo inteiro |
| `myc monitors` | Lista monitores detectados |
| `myc setup` | Gera scripts de atalho |
| `myc setup --auto` | Gera scripts e adiciona ao PATH |
| `myc config` | Configura caminho do Chrome |
| `myc agent add` | Cria perfil de agente de IA (wizard) |
| `myc agent list` | Lista agentes configurados |
| `myc agent launch <nome>` | Lanca agente no diretorio atual |
| `myc agent delete <nome>` | Remove agente |
| `myc agent history` | Historico de lancamentos |
| `myc agent plugins` | Lista plugins instalados |
| `myc agent plugin-add` | Cria plugin customizado |
| `myc agent bundles` | Lista bundles disponiveis |
| `myc agent bundle-install --all` | Instala todos os bundles (64 plugins) |
| `myc agent bundle-install <id>` | Instala bundle especifico |
| `myc agent install-plugin <arquivo>` | Instala plugin de arquivo .py local |
| `myc automate <agente> --group X` | Lanca agente com contexto de rotinas MYC |

---

## Estrutura de configuração

A configuração fica em `~/.myc/config.json`:

```json
{
  "commands": {
    "estudar": {
      "description": "Comandos de estudo",
      "subcommands": {
        "visao-computacional": {
          "description": "Visão Computacional",
          "days": ["segunda", "quarta", "sexta"],
          "actions": [
            {
              "type": "browser",
              "url": "https://udemy.com/course/...",
              "monitor": 0,
              "new_window": true,
              "browser": "chrome"
            },
            {
              "type": "browser",
              "url": "https://colab.research.google.com",
              "monitor": 1,
              "new_window": true,
              "browser": "chrome"
            }
          ]
        }
      }
    }
  }
}
```

### Tipos de ação

| Tipo | Campos |
|------|--------|
| `browser` | `url`, `monitor` (0-based), `new_window`, `browser` (`chrome`/`edge`/`firefox`) |
| `app` | `path` (caminho do .exe), `args` (lista de argumentos) |

### Dias válidos

`segunda` · `terca` · `quarta` · `quinta` · `sexta` · `sabado` · `domingo`

> Lista vazia `[]` significa **todos os dias**.

---

## Scripts de atalho gerados

Após `myc setup`, para cada grupo é criado em `~/.myc/bin/`:

- `estudar.bat` — para CMD
- `estudar.ps1` — para PowerShell

O comportamento:
```
estudar                   →  myc tui --group estudar
estudar <subcomando>      →  myc run estudar <subcomando>
estudar <dia> <subcomando> →  myc run estudar <dia> <subcomando>
```

---

## Estrutura do projeto

```
cli_automatizacao_rotina/
├── myc/
│   ├── __init__.py
│   ├── __main__.py     # entry point
│   ├── cli.py          # comandos Click
│   ├── config.py       # leitura/escrita do config.json
│   ├── monitor.py      # detecção de monitores (screeninfo)
│   ├── runner.py       # execução de ações (browser/app)
│   └── tui.py          # navegação visual (rich + questionary)
├── pyproject.toml
├── requirements.txt
└── install.ps1
```

---

## Dependências

| Pacote | Uso |
|--------|-----|
| `click` | Framework CLI |
| `rich` | Output formatado e tabelas |
| `questionary` | Menus interativos com setas |
| `screeninfo` | Detecção de monitores |
| `pyinstaller` | Build de executavel .exe |

---

## Agente Padrao (sua maquina)

O agente `default` ja vem configurado com seu setup (OpenRouter + qwen3.6-plus).
Para lancar:

```powershell
myc agent launch default
```

## Bundles de Plugins (64 plugins, 16 areas)

| Bundle | ID | Plugins | Uso |
|--------|-----|---------|-----|
| Agencia de Marketing | `marketing` | 4 | Redes sociais, SEO, copywriting, campanhas |
| Estudio de Game Design | `gamedesign` | 4 | Level design, narrativa, mecanicas, UX |
| Escritorio de Advocacia (BR) | `advocacia` | 4 | Legislacao, contratos, peticoes, jurisprudencia |
| Redacao Jornalistica | `jornalismo` | 4 | Pautas, fact-checking, redacao, editorial |
| Inteligencia OSINT | `osint` | 4 | Coleta, fontes, pegada digital, correlacao |
| Seguranca Web | `seguranca_web` | 4 | Auditoria, OWASP, pentest, hardening |
| Bug Bounty Hunter | `bugbounty` | 4 | Recon, exploits, relatorios, triagem |
| Eng. de Visao Computacional | `visao_computacional` | 4 | Arquitetura, datasets, treino, deploy |
| Desenvolvimento Full Stack | `fullstack` | 4 | Frontend, backend, banco de dados, DevOps |
| Desenvolvimento de App Mobile | `app_mobile` | 4 | Arquitetura, UI, ponte nativa, loja |
| Gerador de Ideias | `ideias` | 4 | Brainstorm, design thinking, validacao, MVP |
| Vendas e Empreendedorismo | `vendas` | 4 | Pitch, funil, modelo de negocio, growth |
| Engenharia de Dados | `data_engineering` | 4 | ETL, pipelines, qualidade, data warehouse |
| Engenharia de Software | `software_engineering` | 4 | Arquitetura, code review, testes, CI/CD |
| Engenharia da Computacao | `computer_engineering` | 4 | Embarcados, IoT, redes, sistemas operacionais |
| Professor / Educador | `professor` | 4 | Planejamento, avaliacoes, didatica, conteudo |

### Exemplos de uso

```powershell
# Instala todos os plugins (64)
myc agent bundle-install --all

# Instala bundle especifico e vincula ao agente
myc agent bundle-install bugbounty --agent dev

# Lanca agente com plugins ativos
myc agent launch default

# Cria plugin customizado via wizard
myc agent plugin-add

# Lista historico de uso
myc agent history
```

### Criar plugins customizados

Adicione qualquer arquivo `.py` como plugin:

```powershell
myc agent install-plugin C:/path/to/meu_plugin.py
```

Ou crie via wizard interativo:

```powershell
myc agent plugin-add
```

## Build (executavel)

```powershell
python build_exe.py
# Gera: dist/myc.exe (~20MB)
```

## Licença

MIT
