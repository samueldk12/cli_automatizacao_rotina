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

---

## Licença

MIT
