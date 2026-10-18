<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    O Assistente de IA de Desktop Invisível, Ultraleve e 100% Offline
    /`---'\
   /       \    [ 100% Privado • Dynamic VRAM Juggler • Zero-DB RAG • Pet Casper ]
  (_/^\_/\_/^)
```

# 👻 GhostOS
### O Assistente de IA de Desktop Ultraleve e Offline

<p align="center">
  <b>🌐 Seleção de idioma / Language Select:</b><br>
  <a href="../README.md"><b>English</b></a> •
  <a href="README_RU.md"><b>Русский</b></a> •
  <a href="README_KK.md"><b>Қазақша</b></a> •
  <a href="README_ZH.md"><b>简体中文</b></a> •
  <a href="README_ES.md"><b>Español</b></a> •
  <a href="README_DE.md"><b>Deutsch</b></a> •
  <a href="README_FR.md"><b>Français</b></a> •
  <a href="README_JA.md"><b>日本語</b></a> •
  <a href="README_PT.md"><b>Português</b></a>
</p>

[![Licença: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Autor: KIB.best](https://img.shields.io/badge/Autor-KIB.best-8A2BE2.svg)](https://kib.best)
[![Email](https://img.shields.io/badge/Contato-GhostOS%40kib.best-0071e3.svg)](mailto:GhostOS@kib.best)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Plataforma](https://img.shields.io/badge/plataforma-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![RAM ociosa](https://img.shields.io/badge/RAM%20ociosa-%3C35%20MB-success.svg)]()
[![VRAM máxima](https://img.shields.io/badge/VRAM%20m%C3%A1xima-%E2%89%A43.5%20GB-blueviolet.svg)]()
[![Privacidade](https://img.shields.io/badge/Privacidade-100%25%20Offline-orange.svg)]()

**Desenvolvido especificamente para computadores modestos e Macs com Apple Silicon básico (4GB–8GB RAM) sem travamentos por falta de memória (OOM).**

</div>

---

### 💡 Por que o GhostOS?

A maioria dos assistentes de IA locais atuais é pesada e ineficiente:
1. **Sobrecarga de RAM do Electron:** Vários aplicativos consomem **800MB a 1.2GB de RAM** apenas na interface gráfica antes de carregar qualquer modelo.
2. **Armadilha de OOM Multimodelo:** Executar LLM (3GB) + modelo de visão (2GB) + Whisper (1GB) simultaneamente derruba sistemas de 4GB a 8GB de RAM.
3. **Pilhas RAG Complexas:** Ferramentas de busca documental exigem Docker e bancos de dados vetoriais pesados.

**O GhostOS resolve isso na arquitetura:**
- **Pet Casper & HUD Nativo:** Renderizado com WebViews nativos do sistema operacional (WebKit no macOS, Edge WebView2 no Windows, WebKitGTK no Linux) consumindo apenas **~35MB de RAM**.
- **Dynamic VRAM Juggler:** Alterna entre LLM, Visão e Whisper sob demanda em menos de 150 ms. O consumo máximo de VRAM nunca ultrapassa **3.5GB**.
- **Zero-DB RAG:** Arraste arquivos para o Casper para indexá-los instantaneamente via **SQLite FTS5** puro, sem bancos de dados externos.
- **100% Local e Privado:** Zero telemetria, zero requisições em nuvem. Funciona perfeitamente desconectado da internet.

---

### ✨ Tecnologias Exclusivas

- **Ghostwriter:** Correção, resumo e tradução inteligente direto na área de transferência em qualquer aplicativo.
- **Memory Vault:** Grafo de contexto de longo prazo em SQLite com consumo zero de VRAM.
- **Terminal Sandbox Lens:** Monitor em tempo real de comandos perigosos no terminal (`rm -rf`, `DROP TABLE`, `mkfs`) com avisos claros.
- **Daily Standup & Commit Crafter:** Converte automaticamente atividades do dia e diffs de git em commits organizados e relatórios diários.
- **Auto-Minutes:** Transcrição de reuniões em resumos executivos e listas de tarefas.

---

### 🚀 Instalação Rápida

```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
pip install -e .

# Iniciar o pet de desktop Casper
ghost pet
```

---

### 📄 Licença e Autor

- **Autor:** [KIB.best](https://kib.best)
- **Contato:** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **Licença:** MIT License © 2026 KIB.best.
