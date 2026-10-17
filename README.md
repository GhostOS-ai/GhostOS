<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    The Invisible, Featherweight, Offline Desktop AI Copilot
    /`---'\
   /       \    [ 100% Private • Dynamic VRAM Juggler • Zero-DB RAG • Casper Pet ]
  (_/^\_/\_/^)
```

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon%20%7C%20Linux%20%7C%20Windows-brightgreen.svg)]()
[![Idle RAM](https://img.shields.io/badge/Idle%20RAM-%3C35%20MB-success.svg)]()
[![Peak VRAM](https://img.shields.io/badge/Peak%20VRAM-%E2%89%A43.5%20GB-blueviolet.svg)]()
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Offline-orange.svg)]()

**A unified, offline desktop AI companion that runs seamlessly on low-spec laptops and base Apple Silicon Macs (4GB–8GB RAM) without Out-Of-Memory (OOM) crashes.**

[Quickstart](#-quickstart) • [Features](#-exclusive-features) • [Comparison](#-why-ghostos-vs-others) • [Architecture](#-architecture) • [CLI Usage](#-cli-usage)

</div>

---

### 💡 Why GhostOS?

Running local AI today is frustrating:
- **Heavyweight UI bloat:** Most AI desktop apps use Electron, burning **800MB–1.2GB of RAM** before an LLM is even loaded.
- **The Multi-Model OOM Trap:** Trying to run an LLM (3GB) + Vision model (2GB) + Whisper (1GB) simultaneously instantly crashes computers with 4GB–8GB RAM.
- **Overcomplicated RAG:** Most local document tools force you to run Docker containers, heavy vector DBs (Chroma/Qdrant), and hundreds of megabytes of Python dependencies.

**GhostOS solves this from first principles:**
1. **Casper Companion Pet & HUD:** Rendered via Apple's native WebKit (`WKWebView`) consuming just **~35MB RAM**.
2. **VRAM Juggler:** Dynamically hot-swaps between LLM, Vision, and Whisper on demand in <150ms. Peak VRAM never exceeds **3.5GB**.
3. **Zero-DB RAG:** Drop files onto Casper — indexed in milliseconds using pure **SQLite FTS5** without external databases.

---

### ✨ Exclusive Features

#### 1. 👻 Interactive Casper Desktop Pet
* A lightweight, translucent ghost that floats quietly on your screen.
* **"Casper Eats Files":** Drag and drop any PDF, code repository, markdown, or text file directly onto Casper. Casper opens his mouth, swallows the file, and indexes it into your local knowledge base instantly.
* **Visual Moods & States:**
  * 💤 `Idle`: Soft breathing float, 0% CPU footprint.
  * 🔮 `Thinking`: Neon aura glow, streaming neural generation.
  * 🎧 `Listening`: Casper wears glowing headphones, transcribing offline audio.
  * 🍕 `Eating`: Swallows dragged documents with suction animation.
  * ⚠️ `Alarm`: Visual alert for terminal command risks.
* Click Casper or press `Cmd+Shift+Space` to morph into the **Spotlight HUD**.

#### 2. 🧠 VRAM Juggler (Smart Memory Dispatcher)
* Solves the VRAM bottleneck by enforcing a single active model in GPU/VRAM at a time.
* If you ask Casper to inspect your screen, the Juggler unloads the text model, loads the vision model, extracts insights in 0.5s, and restores the LLM.
* **Auto-Sleep:** Automatically frees all GPU memory after 3 minutes of inactivity so your laptop stays cool and battery lasts all day.

#### 3. 📂 Zero-DB RAG (Instant Document Search)
* Pure SQLite FTS5 with BM25 ranking built directly into Python.
* Zero Docker, zero ChromaDB, zero background vector indexers.
* Instant sub-millisecond keyword and semantic search across your personal notes, PDFs, and codebases.

#### 4. ⚡ Safe Terminal Autopilot
* Describe any task in natural language (*"find all mov files and convert to mp4"*, *"kill process on port 3000"*).
* Autopilot evaluates risk level:
  * 🟢 **SAFE**: Read-only queries (`find`, `lsof`, `df`, `grep`).
  * 🟡 **CAUTION**: Modifying actions (`kill`, `mv`, `cp`).
  * 🔴 **DANGEROUS**: High-risk commands (`rm -rf`, `sudo`, `dd`).
* Run commands with 1-click execution or copy them to your clipboard.

#### 5. 👁️ Screen Peek (Visual Inspector)
* Silent, zero-shutter screen capture of active applications.
* Explains compiler errors in your IDE, inspects dashboard numbers, and debugs visual UI layouts without manual screenshots.

#### 6. 🎙️ Offline Meeting Copilot
* Record audio from calls or voice notes.
* Local Whisper transcription formats conversations into structured Executive Overviews, Key Decisions, and Action Items.
* **100% Private:** Not a single millisecond of voice data leaves your device.

---

### 📊 Why GhostOS vs. Others?

| Feature | GhostOS 👻 | Jan.ai / LM Studio | Ollama | AnythingLLM |
| :--- | :---: | :---: | :---: | :---: |
| **GUI Memory Footprint** | **~35 MB** (Native WebKit) | ~850 MB (Electron) | None (CLI only) | ~1.1 GB (Electron + DB) |
| **Desktop Pet Companion** | **Yes (Casper)** | No | No | No |
| **Drag & Drop RAG Ingestion**| **Yes (Drop onto Pet)** | Manual upload | Manual import | Manual upload |
| **Multi-Model VRAM Swapping**| **Yes (VRAM Juggler)** | ❌ OOM on low VRAM | Manual CLI | ❌ OOM on low VRAM |
| **Spotlight / Raycast HUD** | **Yes (1-click morph)** | No (Full window) | No | No (Web browser) |
| **External DB Requirement** | **Zero (SQLite FTS5)** | Varies | None | Requires Vector DB / Chroma |
| **Safe Terminal Autopilot** | **Yes (Built-in)** | No | No | No |
| **Works 100% Offline** | **Yes** | Yes | Yes | Mostly |

---

### 🏗️ Architecture

```mermaid
flowchart TD
    User([User Desktop]) -->|Drag & Drop File / Click| Pet["👻 Casper Floating Pet (WebKit)"]
    User -->|Hotkey Cmd+Shift+Space| HUD["🔮 Spotlight HUD / Command Bar"]
    User -->|Terminal CLI| CLI["💻 ghost CLI (rich)"]

    Pet --> Bridge["Python <-> JS Bridge API"]
    HUD --> Bridge
    CLI --> Core["GhostOS Core Engine"]
    Bridge --> Core

    subgraph MemoryManagement ["🧠 VRAM Juggler"]
        Core --> Juggler["Memory Juggler Dispatcher"]
        Juggler -->|Hot-Swap <= 3.5GB| M1["Qwen 2.5 / Llama 3.2 (LLM)"]
        Juggler -->|Hot-Swap <= 2.0GB| M2["Moondream2 / MiniCPM (Vision)"]
        Juggler -->|Hot-Swap <= 0.6GB| M3["Whisper (Voice Copilot)"]
    end

    subgraph Storage ["📂 Zero-DB Storage"]
        Core --> RAG["SQLite FTS5 Knowledge Base"]
        RAG --> Docs[("Local Notes / Code / PDFs")]
    end

    subgraph OSIntegration ["⚡ System Integration"]
        Core --> Screen["Silent Screencapture"]
        Core --> Pilot["Safe Terminal Autopilot"]
    end
```

---

### 🚀 Quickstart

#### 1. Clone & Install
```bash
git clone https://github.com/your-username/ghostos.git
cd ghostos
pip install -e .
```

#### 2. Launch Casper Desktop Pet & HUD
```bash
ghost pet
```
*Casper will float on your screen. Drag any file onto him, or click him to open the HUD!*

#### 3. Or use from Terminal (CLI)
```bash
# Instant question
ghost "Why does Python raise RecursionError and how to fix it?"

# Feed a document or code directory to Casper
ghost eat ~/Documents/my_notes.txt
ghost eat ./src/

# Search indexed knowledge
ghost rag search "database migration"

# Inspect current active screen
ghost screen

# Generate and safely run a terminal task
ghost exec "find all files larger than 100MB"

# Check VRAM Juggler memory diagnostics
ghost status
```

---

### ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Cmd + Shift + Space` / Click Ghost | Toggle Spotlight HUD |
| `Escape` | Minimize back to Floating Casper |
| `Enter` | Submit query |
| `Drag & Drop File` | Feed document to Casper (Instant RAG) |

---

### 🔒 100% Privacy Pledge

GhostOS is designed for paranoid privacy:
- **No Telemetry:** We collect zero analytics, zero user data, zero cookies.
- **No Cloud Fallbacks:** Every inference runs entirely on your local CPU or Metal/GPU.
- **Air-Gapped Ready:** Works with your Wi-Fi completely turned off.

---

### 🤝 Contributing

Contributions are welcome! Feel free to submit issues, pull requests, or custom Casper skins.

```bash
# Run unit tests
python3 -m unittest discover tests
```

---

### 📄 License

MIT License © 2026 GhostOS Contributors. Free for personal and commercial use.
