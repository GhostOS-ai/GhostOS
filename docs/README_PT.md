<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S   v 2 . 1
     \  -  /    Copiloto de IA de Cérebro Híbrido e Estúdio GhostCode
    /`---'\
   /       \    [ 100% Privado • Cérebro Híbrido Local & Nuvem • Estúdio ChatGPT • <35MB RAM ]
  (_/^\_/\_/^)
```

# 👻 GhostOS v2.1
### Assistente de IA de desktop ultraleve e estúdio autônomo (Hybrid Brain)

<p align="center">
  <b>🌐 Seleção de idioma / Language Select / Выбор языка / Тілді таңдау:</b><br>
  <a href="../README.md"><b>English</b></a> •
  <a href="README_RU.md"><b>Русский</b></a> •
  <a href="README_KK.md"><b>Қазақша</b></a> •
  <a href="README_ZH.md"><b>简体中文</b></a> •
  <a href="README_ES.md"><b>Español</b></a> •
  <a href="README_DE.md"><b>Deutsch</b></a> •
  <a href="README_FR.md"><b>Français</b></a> •
  <a href="README_JA.md"><b>日本語</b></a> •
  <a href="README_PT.md"><b>Português</b></a> •
  <a href="README_AR.md"><b>العربية</b></a> •
  <a href="README_HI.md"><b>हिन्दी</b></a>
</p>

[![Versão PyPI](https://img.shields.io/pypi/v/ghostos-ai.svg?color=blue)](https://pypi.org/project/ghostos-ai/)
[![Lançamento GitHub](https://img.shields.io/github/v/release/GhostOS-ai/GhostOS?color=blue&label=release)](https://github.com/GhostOS-ai/GhostOS/releases/latest)
[![Product Hunt](https://img.shields.io/badge/Product%20Hunt-Upcoming%20Launch-da552f?logo=producthunt&logoColor=white)](https://www.producthunt.com/products/ghostos?launch=ghostos)
[![Estrelas GitHub](https://badgen.net/github/stars/GhostOS-ai/GhostOS?icon=github&color=yellow)](https://github.com/GhostOS-ai/GhostOS)
[![Licença: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Autor: KIB.best](https://img.shields.io/badge/Autor-KIB.best-8A2BE2.svg)](https://github.com/GhostOS-ai/GhostOS)
[![Email](https://img.shields.io/badge/Contato-GhostOS%40kib.best-0071e3.svg)](mailto:GhostOS@kib.best)
[![Plataforma](https://img.shields.io/badge/plataforma-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![RAM em repouso](https://img.shields.io/badge/RAM%20em%20repouso-%3C35%20MB-success.svg)]()
[![Pico de VRAM](https://img.shields.io/badge/Pico%20de%20VRAM-%E2%89%A43.5%20GB-blueviolet.svg)]()
[![Privacidade](https://img.shields.io/badge/Privacidade-100%25%20Offline-orange.svg)]()

**O assistente autônomo de desktop com IA projetado para notebooks modestos e computadores básicos (4–8 GB de RAM) sem travamentos por falta de memória (OOM).**

[Início rápido](#-início-rápido) • [Recursos exclusivos](#-recursos-exclusivos) • [Comparativo](#-por-que-o-ghostos-em-vez-de-outros) • [Arquitetura](#-arquitetura) • [Comandos CLI](#-comandos-cli-e-atalhos) • [Garantia de privacidade](#-100-garantia-de-privacidade)

</div>

---

### 💡 Por que o GhostOS?

Executar IA local hoje em dia enfrenta 3 grandes obstáculos:
1. **Consumo excessivo do Electron:** A maioria das ferramentas de desktop (LM Studio, Jan, AnythingLLM) consome entre **800 e 1200 MB de RAM** antes mesmo de carregar qualquer peso de rede neural.
2. **A armadilha de múltiplos modelos (OOM):** Manter simultaneamente um modelo de linguagem (3 GB) + modelo de visão (2 GB) + Whisper (1 GB) trava e encerra qualquer máquina com 4–8 GB de memória.
3. **Pilhas RAG inchadas:** Para pesquisar em alguns documentos, exigem contêineres Docker, bancos de dados vetoriais pesados (Chroma) e gigabytes de dependências externas.

**O GhostOS soluciona esses problemas de raiz:**
- **Mascote Casper e HUD nativos:** Desenvolvidos sobre os motores nativos do sistema operacional (WebKit no macOS, WebView2 no Windows, WebKitGTK no Linux), consumindo apenas **~35 MB de RAM** em repouso.
- **VRAM Juggler dinâmico:** Alterna modelos (texto, visão, voz) em tempo real em menos de 150 ms. O consumo máximo de VRAM **nunca excede 3.5 GB**.
- **Zero-DB RAG:** Basta arrastar qualquer arquivo para o Casper; a indexação ocorre em milissegundos através de **SQLite FTS5** puro, sem bancos de dados externos.
- **100% Privado:** Sem telemetria, sem servidores em nuvem e sem envio de logs. Funciona perfeitamente mesmo com a internet desconectada.

---

### ✨ Recursos exclusivos

#### 🌟 NOVO na v2.1: Cérebro Híbrido (Hybrid Brain) & Hub de Provedores de IA
* **Alternador unificado de modelos e provedores em nuvem:** Alterne sem esforço entre:
  * 👻 **Motor Integrado Ghost:** 100% offline, zero configuração, menos de 35 MB de RAM.
  * 🦙 **Ollama Local:** Detecção automática de `qwen2.5:1.5b`, `qwen2.5-coder:7b`, `llama3.2:3b`, `deepseek-r1:1.5b`, `mistral`.
  * ✨ **Google Gemini:** Conexão nativa REST com `gemini-2.5-flash`, `gemini-1.5-flash` e `gemini-1.5-pro` (plano gratuito generoso no Google AI Studio, altíssima velocidade).
  * 🧠 **OpenAI Cloud:** Suporte a `gpt-4o`, `gpt-4o-mini`, `o1` e `o3-mini` com chaves armazenadas localmente de forma criptografada.
  * ⚡ **DeepSeek AI:** Suporte nativo para `deepseek-chat` (V3) e `deepseek-reasoner` (R1 com raciocínio lógico).
  * 🟣 **Anthropic Claude:** Integração direta com `claude-3-5-sonnet` e `claude-3-5-haiku`.
  * 🖥️ **Personalizado / LM Studio:** Qualquer endpoint compatível com OpenAI (`http://localhost:1234/v1`, vLLM, LocalAI).
* **Botão de atalho `[ ⚙️ API ]` na barra superior:** Janela modal de 1 clique para configurar chaves de API, trocar modelos e testar conexão em tempo real.
* **Histórico de conversas multissessão estilo ChatGPT:**
  * Histórico de chats salvo automaticamente em `~/.ghostos/studio_sessions.json`.
  * Barra lateral com conversas reais, títulos automáticos, datas e exclusão em 1 clique.
* **Personas de IA Especializadas (1 clique):**
  * 👻 **Casper:** Companheiro de desktop espirituoso, conciso e privativo.
  * 💻 **GhostCode:** Engenheiro de software sênior para arquitetura, código limpo e testes.
  * ✍️ **Ghostwriter:** Mestre de redação para documentação, e-mails e comunicação.
  * 🧠 **Deep Think:** Modo analítico com raciocínio lógico passo a passo.
  * 🌐 **Web Live:** Assistente conectado à web em tempo real (clima, cotações, buscas).
* **Cartões retráteis de raciocínio profundo (CoT):**
  * Renderização nativa dos tokens `<think>...</think>` (DeepSeek-R1, OpenAI reasoning) em elegantes cartões foscos com efeito luminoso.

#### 0. ⚡ GhostCode: Agente autônomo de programação e estúdio estilo ChatGPT (v2.0)
* **Loop autônomo de engenharia de software:** A alternativa 100% offline e privada ao Claude Code e ao Cursor. O GhostCode formula planos passo a passo, inspeciona repositórios, lê e edita arquivos com precisão através de **Unified Diffs**, executa testes unitários e comandos de terminal seguros, e rastreia o histórico do Git.
* **Scaffolding de projetos prontos para produção em 1 clique:**
  * `FastAPI`: API assíncrona de alto desempenho com validação Pydantic, middleware CORS e testes unitários (`TestClient`).
  * `Telegram Bot`: Aplicação assíncrona moderna com `python-telegram-bot`, roteadores de comandos e arquitetura limpa.
  * `HTML / React Landing`: Landing page responsiva e elegante com design glassmorphism moderno.
  * `Ferramenta CLI Python`: Utilitário de linha de comando estruturado com parser de argumentos e suite de testes.
* **Estúdio de desktop estilo ChatGPT & Cursor (`ghost studio`):**
  * **Barra lateral esquerda recolhível:** Histórico de sessões e projetos («Hoje», «Ontem», «Projetos»), alternância direta entre `Ghost Chat` (assistente de IA geral) e `GhostCode` (programador autônomo), Zero-DB RAG, ferramentas do sistema e monitor VRAM.
  * **Fluxo de execução do agente:** Painel esquerdo com streaming dos pensamentos, chamadas de ferramentas e ações do GhostCode em tempo real.
  * **Tela interativa (Canvas):** Painel direito equipado com **Explorador de arquivos do projeto** (1 clique para abrir qualquer arquivo), **Editor de código em tempo real** (com salvamento direto em disco), **Visualizador de Unified Diff** (código adicionado e removido destacado) e **Terminal interativo de trabalho (`zsh`)**.
* **Transição instantânea:** Retorne ao mascote flutuante Casper a qualquer momento pelo botão `◀ В питомца` ou inicie-o do terminal com `ghost studio` ou `ghost code "tarefa"`.

#### 1. 👻 Mascote de desktop interativo Casper
* Um fantasma translúcido e elegante que flutua suavemente sobre a sua área de trabalho.
* **«Casper devora arquivos»:** Arraste qualquer arquivo PDF, código-fonte, registro ou anotação diretamente para o Casper. Ele abre a boca, engole o arquivo e o indexa imediatamente na base RAG (+25 XP!).
* **Estados e reações:**
  * 💤 `Repouso`: Flutuação suave, 0% de uso de CPU.
  * 🔮 `Pensando`: Brilho suave de safira durante a geração local de respostas.
  * 🎧 `Ouvindo`: Coloca fones brilhantes para transcrever reuniões.
  * 🍕 `Comendo`: Animação interativa de mastigação e ganho de experiência RPG.
  * ⚠️ `Alerta`: Aviso visual instantâneo se detectar comandos perigosos no terminal.
* Um clique dispara frases interativas; um clique duplo ou o atalho `Cmd+Shift+Space` / `Ctrl+Shift+Space` abre o painel de controle completo (**Spotlight HUD**).

#### 2. ✍️ «Ghostwriter» (Assistente de escrita global em qualquer aplicativo)
* Selecione texto em qualquer programa (Word, Telegram, navegador, VS Code, terminal) $\rightarrow$ pressione o atalho $\rightarrow$ transforme o texto em 1 segundo:
  * ✨ `polish`: Torna a redação impecável, clara e profissional.
  * 🤝 `polite`: Converte para um tom diplomático e corporativo.
  * 📝 `grammar`: Corrige erros gramaticais e ortográficos instantaneamente.
  * 🎯 `summarize`: Sintetiza em 2 a 3 pontos essenciais.
  * 🌐 `translate`: Tradução instantânea para múltiplos idiomas.
  * 🛠️ `code_fix`: Localiza e corrige falhas em trechos de código.
* Execução pelo terminal: `ghost write --mode polite "mensagem"` ou processamento automático da área de transferência!

#### 3. 🧠 «Memory Vault» (Grafo de memória persistente a longo prazo)
* Armazenamento de contexto pessoal persistente em SQLite sem requerer bancos vetoriais.
* Lembra suas preferências técnicas, seu nome e estilo de resposta entre inicializações.
* Adiciona contexto com **0 KB de consumo extra de VRAM** e impacto nulo de CPU em segundo plano.
* Comandos: `ghost vault list`, `ghost vault remember tech_stack "Python, Rust, Apple Silicon"`.

#### 4. 🛡️ «Terminal Sandbox Lens» (Escudo contra comandos perigosos)
* Verificação aprofundada de comandos de terminal antes de sua execução.
* Intercepta e barra operações destrutivas (`rm -rf /`, `mkfs`, `dd` direto, `DROP DATABASE`, `format C:`).
* Explica os riscos em linguagem simples e sugere alternativas seguras.
* Teste: `ghost sandbox "rm -rf /"`.

#### 5. 📅 «Daily Standup & Commit Crafter»
* Analisa as alterações do dia, git diff e histórico de comandos da sessão.
* Gera relatórios de standup prontos para Slack / Teams (*«O que fiz hoje», «No que estou trabalhando», «Impedimentos»*).
* Redige mensagens semânticas de commit seguindo o padrão Conventional Commits (`feat(...)`, `fix(...)`).
* Invocação: `ghost standup`.

#### 6. 🎙️ «Auto-Minutes Meeting Copilot»
* Secretário 100% offline para reuniões no Zoom, Google Meet e notas de voz.
* Estrutura atas completas: **Resumo executivo**, **Decisões-chave** e **Plano de ação (Action Items) com responsáveis**.
* O modelo Whisper é acionado pelo VRAM Juggler por apenas 5 segundos durante o áudio e descarregado em seguida.

#### 7. 🦎 «Memory Chameleon» (Perfis adaptativos de energia)
* Monitora automaticamente a bateria e a pressão na memória RAM:
  * 🍃 **ECO:** Ativado na bateria ou se a RAM ultrapassar 82%. Contexto de 1024 tokens, 2 threads de CPU, suspensão após 60s.
  * ⚖️ **Equilibrado:** Contexto de 2048 tokens, 4 threads, suspensão após 180s.
  * ⚡ **Performance:** Conectado à tomada com memória livre. Contexto de 4096 tokens, aceleração total de GPU.

#### 8. 🎮 Sistema de progressão RPG do Casper
* Seu mascote evolui conforme o seu ritmo diário de trabalho:
  * Ganho de XP por alimentar arquivos (+25 XP), concluir tarefas (+25 XP), interagir (+10 XP).
  * Desbloqueia temas visuais e acessórios (visor cyberpunk, grimório de magia, coroa real).

#### 9. 🎨 Guarda-roupa do Casper (Skins e temas visuais)
* Escolha entre 4 visuais elegantes pensados para modo escuro:
  * 💎 `glass`: Acabamento translúcido em porcelana branca estilo Apple Glass.
  * ⚡ `cyberpunk`: Ciano neon vibrante com aura magenta radiante.
  * 👑 `gold`: Brilho nobre em ouro real.
  * 🟢 `matrix`: Verde fósforo clássico de terminal hacker.
* Iniciar: `ghost pet --skin cyberpunk` ou altere com 1 clique pela barra de menus!

#### 10. 🍕 Casper Feeder (Alimentação física por arrastar e soltar)
* Arraste qualquer arquivo de código (`.py`, `.js`, `.ts`, `.json`), log ou PDF diretamente para o Casper.
* Ativa uma animação animada de mastigação (`@keyframes ghostChewWobble`) e balões de pensamento alegres.
* Incorpora os dados ao Zero-DB RAG sem telas ou modais de upload.

#### 11. 👻 Controlador nativo na barra de menus do macOS
* Ícone leve na barra de status superior desenvolvido com Cocoa `NSStatusBar` nativo (`ghost bar` ou `ghost pet --tray`).
* 1 clique para exibir/ocultar o Casper, trocar de skin, escolher o modelo ativo e limpar a VRAM com **0 KB de consumo em segundo plano**.

#### 12. 🔍 Barra de comando rápida Spotlight HUD
* Barra de entrada flutuante centralizada (`ghost spot`) no estilo Raycast/Spotlight para consultas sem distrações. Pressione `Esc` para fechar imediatamente.

#### 13. 🤖 Catálogo de modelos locais e aceleração de hardware
* Analisa seu ambiente local Ollama, lista modelos instalados com tamanho em GB, identifica o nível de hardware (**Apple Silicon Metal MPS**, **NVIDIA CUDA** ou **CPU**) e recomenda modelos ideais para dispositivos com 4GB–8GB de RAM (`ghost models`).

#### 14. 💎 Interface Apple Glassmorphism e Blocos de Código em 1 Clique (v1.3.0)
* **Navegação Unificada em 4 Abas:** Simplificação de 9 abas dispersas em 4 espaços organizados: `💬 Chat`, `📚 Conhecimento (RAG)`, `🛠️ Ferramentas SO` (com subferramentas: Agente SO, Captura de Tela, Área de Transferência, Autopiloto de Terminal, Diário Standup) e `🧠 VRAM`.
* **Seletor de Temas e Visuais em Tempo Real:** Alterne entre os temas Glass, Cyberpunk, Gold e Matrix diretamente no cabeçalho com persistência imediata.
* **Botões de Sugestão Rápida:** Ações úteis em 1 clique (`👋 O que você pode fazer?`, `🌤️ Clima`, `📂 Abrir Downloads`, `📸 Capturar tela`, `📋 Inspecionar área de transferência`).
* **Blocos de Código com Botão de Cópia Rápida:** Destaque de sintaxe escuro com identificação de linguagem e botão para copiar para a área de transferência em 1 clique.
* **Arrastar e Soltar Universal em Toda a Janela:** Solte arquivos sobre o Casper ou qualquer área do HUD para indexar no RAG local em milissegundos (+25 XP!).
* **Ícone Nativo Apple Retina no Dock:** Ícone oficial em alta resolução `.icns` integrado ao Dock do macOS e ao `/Applications/GhostOS.app`.

---

### 📊 Por que o GhostOS em vez de outros?

| Funcionalidade | GhostOS 👻 | Jan.ai / LM Studio | Ollama | AnythingLLM |
| :--- | :---: | :---: | :---: | :---: |
| **Consumo de RAM da interface** | **~35 MB** (Motor nativo) | ~850 MB (Electron) | Nenhuma (Apenas CLI) | ~1.1 GB (Electron + BD) |
| **Agente de código autônomo (GhostCode)** | **Sim (Integrado v2.0)** | ❌ Não | ❌ Não | ❌ Não |
| **Estúdio estilo ChatGPT & Cursor** | **Sim (1120x740)** | ❌ Não | ❌ Não | ❌ Não |
| **Mascote interativo de desktop** | **Sim (Casper RPG)** | ❌ Não | ❌ Não | ❌ Não |
| **RAG arrastando arquivos** | **Sim (Soltar no mascote)**| ❌ Upload manual | ❌ Importação manual | ❌ Upload manual |
| **Troca dinâmica de modelos** | **Sim (VRAM Juggler)** | ❌ Falha OOM em pouca VRAM| ❌ Manual via CLI | ❌ Falha OOM em pouca VRAM |
| **Congelamento de KV-Cache em disco**| **Sim (0 MB VRAM ocioso)**| ❌ Não | ❌ Não | ❌ Não |
| **Compressão de contexto (Vacuum)** | **Sim (Economiza 40-60%)**| ❌ Não | ❌ Não | ❌ Não |
| **Perfis inteligentes de bateria** | **Sim (Modo Chameleon)**| ❌ Não | ❌ Não | ❌ Não |
| **Reescrita global de texto** | **Sim (Em qualquer app)** | ❌ Não | ❌ Não | ❌ Não |
| **Proteção de segurança no terminal**| **Sim (Protege contra rm -rf)**| ❌ Não | ❌ Não | ❌ Não |
| **Gerador de standup e commits** | **Sim (Integrado)** | ❌ Não | ❌ Não | ❌ Não |
| **Banco de dados externo necessário**| **Zero (SQLite FTS5)** | Varia | Nenhum | Requer Chroma / Vector DB |
| **Suporte multiplataforma** | **macOS / Windows / Linux** | Sim | Sim | Sim |
| **Operação 100% offline** | **Sim** | Sim | Sim | Parcialmente |

---

### 🚀 Início rápido

#### 1. Instalação instantânea

**macOS e Linux (Instalador em 1 linha de terminal):**
```bash
curl -fsSL https://raw.githubusercontent.com/GhostOS-ai/GhostOS/main/install.sh | bash
```
*(No macOS, registra automaticamente o `/Applications/GhostOS.app` com o ícone Retina do Casper no Launchpad e Spotlight).*

**Ou através do Python pip:**
```bash
pip install --upgrade ghostos-ai
```

#### 2. Iniciar o Casper e a interface
```bash
ghost pet
```
*Ou no macOS: inicie o `GhostOS` diretamente pelo Spotlight (`Cmd + Espaço`), Launchpad ou clicando duas vezes em `/Applications/GhostOS.app`!*

#### 3. Uso direto pelo terminal (CLI)
```bash
# Iniciar o estúdio completo ChatGPT & GhostCode (1120x740)
ghost studio

# Tarefa de engenharia de software autônoma com GhostCode CLI
ghost code "crie um projeto fastapi chamado my_service"
ghost code "execute os testes e corrija as falhas"

# Pergunta instantânea para o modelo local
ghost "Qual a diferença entre processos e threads em Python?"

# Iniciar o mascote Casper (com tema cyberpunk e ícone na barra de menus)
ghost pet --skin cyberpunk --tray

# Abrir a barra de pesquisa rápida Spotlight HUD
ghost spot

# Iniciar o controlador da barra de menus do macOS
ghost bar

# Consultar modelos instalados e aceleração de hardware
ghost models

# Ensinar um arquivo ou pasta para o Casper (Zero-DB RAG)
ghost eat ~/Documents/minhas_notas.txt
ghost eat ./src/

# Assistente de escrita Ghostwriter
ghost write --mode polite "por favor analise este código com brevidade"
ghost write --mode grammar

# Cofre de memória de longo prazo Memory Vault
ghost vault remember tech_stack "Python, Rust, Apple Silicon"
ghost vault list

# Relatório diário de standup e mensagem semântica de commit
ghost standup

# Verificação de segurança de comandos de terminal
ghost sandbox "rm -rf /"

# Pesquisa na base de conhecimento
ghost rag search "migração de banco de dados"

# Análise visual da tela ativa
ghost screen

# Execução segura de tarefas no sistema operacional
ghost exec "encontre todos os arquivos maiores que 100MB"

# Diagnóstico de memória VRAM e processador
ghost status
```

---

### ⌨️ Comandos CLI e atalhos

| Atalho | Ação |
| :--- | :--- |
| `Cmd + Shift + Space` / `Ctrl + Shift + Space` | Alternar entre o Casper e a barra Spotlight HUD |
| `Clique simples no mascote` | Frase interativa / reação espontânea |
| `Clique duplo no mascote` | Abrir o painel de controle completo |
| `Escape` | Recolher o painel de volta ao pequeno mascote |
| `Enter` | Enviar comando |
| `Arrastar arquivo` | Alimentar o Casper com o documento (RAG instantâneo) |

---

### 💻 Programação local 100% gratuita com Ollama (Sem chaves API e Offline)

O GhostOS transforma seu Mac ou PC em um ambiente de desenvolvimento autônomo com IA **100% offline, gratuito e com privacidade total**. Sem assinaturas, sem cartões e sem limites de API.

#### 1. Configuração rápida em 2 minutos:
1. **Instalar o Ollama:**
   - macOS: `brew install ollama` (ou baixe em [ollama.com](https://ollama.com))
   - Windows/Linux: baixe em [ollama.com](https://ollama.com)
2. **Baixar um modelo de programação:**
   ```bash
   # 🏆 Melhor modelo compacto de código do mundo (recomendado para 16GB RAM):
   ollama run qwen2.5-coder:7b

   # 🍃 Modelo ultraleve (para máquinas com 4GB–8GB RAM, apenas ~1.8GB no disco):
   ollama run qwen2.5-coder:1.5b

   # 🧠 Modelo de raciocínio profundo com reflexão <think>:
   ollama run deepseek-r1:7b
   ```
3. **Iniciar o GhostOS:** O Casper detecta automaticamente o Ollama em execução (`http://localhost:11434`) e gera código local com aceleração Metal no Apple Silicon!

#### 2. Exemplos práticos no GhostOS:

| Tarefa de desenvolvimento | O que pedir ao Casper / GhostCode | O que o GhostOS entrega |
| :--- | :--- | :--- |
| **Criação completa de projeto** | *«Crie uma API REST com FastAPI, autenticação JWT e SQLite»* | Estrutura completa com modelos, rotas, schemas Pydantic e dependências. |
| **Correção de bugs e otimização** | *«Encontre vazamentos de memória e condições de corrida neste código»* | Explica a causa e entrega código limpo, tipado e de alto desempenho. |
| **Geração de interface web** | *«Construa um painel responsivo moderno em HTML, Tailwind CSS e JS puro»* | Entrega componentes prontos para produção com visual moderno. |
| **Geração de testes unitários** | *«Escreva casos de teste completos com pytest para este módulo»* | Suite de testes abrangente com fixtures, mocks e asserções. |
| **Automação segura no terminal** | *«Encontre todos os logs com mais de 7 dias e compacte-os em zip»* | Valida a segurança no Sandbox Lens e executa a tarefa com segurança. |

---

### 🏗️ Arquitetura

```mermaid
flowchart TD
    User([Usuário]) -->|Arrastar arquivo / Clique| Pet["👻 Mascote Casper (Motor nativo)"]
    User -->|Atalho Cmd+Shift+Space| HUD["🔮 Painel Spotlight HUD"]
    User -->|Terminal| CLI["💻 ghost CLI (rich)"]

    Pet --> Bridge["Ponte Python <-> JS Bridge API"]
    HUD --> Bridge
    CLI --> Core["Núcleo central GhostOS"]
    Bridge --> Core

    subgraph Memória ["🧠 VRAM Juggler & Memory Chameleon"]
        Core --> Juggler["Gerenciador de memória Juggler"]
        Juggler -->|Alternância <= 3.5GB| M1["Qwen 2.5 / Llama 3.2 (LLM)"]
        Juggler -->|Alternância <= 2.0GB| M2["Moondream2 / MiniCPM (Visão)"]
        Juggler -->|Alternância <= 0.6GB| M3["Whisper (Voz)"]
    end

    subgraph BaseConhecimento ["📂 Zero-DB Storage & Vault"]
        Core --> RAG["Índice de busca SQLite FTS5"]
        Core --> Vault["🧠 Memory Vault (Memória permanente)"]
        RAG --> Docs[("Documentos / Código / Notas")]
    end

    subgraph IntegraçãoSistema ["⚡ Integração com o SO"]
        Core --> Screen["Inspeção visual da tela"]
        Core --> Pilot["Piloto automático seguro do terminal"]
        Core --> Lens["🛡️ Lente de segurança Sandbox Lens"]
        Core --> Writer["✍️ Reescritor de texto Ghostwriter"]
    end
```

---

### 🔒 100% Garantia de privacidade

O GhostOS foi projetado para assegurar confidencialidade absoluta:
- **Zero telemetria:** Sem contadores analíticos ou coleta de padrões de uso.
- **Sem conexões com a nuvem:** Todas as computações ocorrem estritamente no seu hardware local (Apple Silicon MPS / NVIDIA / CPU).
- **Pronto para Air-Gap:** Funciona plenamente mesmo em ambientes completamente desconectados da internet.

---

### 📄 Licença e autoria

- **Autor:** [KIB.best](https://github.com/GhostOS-ai/GhostOS)
- **Email:** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **Licença:** MIT License © 2026 KIB.best. Gratuito para uso pessoal e comercial.
