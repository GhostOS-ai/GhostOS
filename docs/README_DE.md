<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    Der unsichtbare, federleichte Offline-Desktop-KI-Assistent
    /`---'\
   /       \    [ 100% Privat • Dynamic VRAM Juggler • Zero-DB RAG • Casper Desktop-Pet ]
  (_/^\_/\_/^)
```

# 👻 GhostOS
### Der federleichte, offline Desktop-KI-Assistent & Begleiter

<p align="center">
  <b>🌐 Sprachauswahl / Language Select:</b><br>
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

[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Autor: KIB.best](https://img.shields.io/badge/Autor-KIB.best-8A2BE2.svg)](https://kib.best)
[![Email](https://img.shields.io/badge/Kontakt-GhostOS%40kib.best-0071e3.svg)](mailto:GhostOS@kib.best)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Plattform](https://img.shields.io/badge/Plattform-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![Ruhe-RAM](https://img.shields.io/badge/Ruhe--RAM-%3C35%20MB-success.svg)]()
[![Spitzen-VRAM](https://img.shields.io/badge/Spitzen--VRAM-%E2%89%A43.5%20GB-blueviolet.svg)]()
[![Datenschutz](https://img.shields.io/badge/Datenschutz-100%25%20Offline-orange.svg)]()

**Speziell entwickelt für schwächere Laptops und Apple Silicon Macs (4GB–8GB RAM) – ohne Out-Of-Memory (OOM) Abstürze.**

</div>

---

### 💡 Warum GhostOS?

Lokale KI ist heutzutage oft überladen und ressourcenhungrig:
1. **Electron-RAM-Verschwendung:** Die meisten Desktop-Apps verbrauchen **800MB–1.2GB RAM** nur für die Benutzeroberfläche, bevor überhaupt ein Modell geladen wird.
2. **Die Multi-Modell OOM-Falle:** Das gleichzeitige Laden von LLM (3GB) + Vision (2GB) + Whisper (1GB) bringt Systeme mit 4GB–8GB RAM zum Absturz.
3. **Überkomplizierte RAG-Stacks:** Dokumenten-Chat-Tools erfordern oft Docker, schwere Vektordatenbanken und Gigabytes an Abhängigkeiten.

**GhostOS löst dies von Grund auf:**
- **Casper Desktop-Begleiter & HUD:** Verwendet native System-Web-Engines (WebKit unter macOS, Edge WebView2 unter Windows, WebKitGTK unter Linux) mit nur **~35MB RAM**.
- **Dynamic VRAM Juggler:** Schaltet in unter 150ms flexibel zwischen LLM, Vision und Whisper um. Der maximale VRAM-Bedarf übersteigt nie **3.5GB**.
- **Zero-DB RAG:** Ziehe Dokumente auf Casper – sekundenschnelle Indizierung über reines **SQLite FTS5** ohne externe Datenbanken.
- **100% Lokal & Privat:** Keine Telemetrie, keine Cloud-Abhängigkeiten. Funktioniert komplett ohne Internet.

---

### ✨ Exklusive Technologien

- **Ghostwriter:** Intelligente Textkorrektur, Zusammenfassung und Übersetzung direkt in der Zwischenablage jeder Anwendung.
- **Memory Vault:** Langzeit-Kontextgraph in SQLite ohne VRAM-Verbrauch.
- **Terminal Sandbox Lens:** Proaktiver Schutz vor destruktiven Terminalbefehlen (`rm -rf`, `DROP TABLE`, `mkfs`) mit verständlichen Hinweisen.
- **Daily Standup & Commit Crafter:** Verwandelt tägliche Aktivitäten und Git-Diffs automatisch in saubere Conventional Commits und Standup-Berichte.
- **Auto-Minutes:** Automatische Meeting-Transkription in Zusammenfassungen und Aufgabenlisten.

---

### 🚀 Schnellstart

```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
pip install -e .

# Casper Desktop-Begleiter starten
ghost pet
```

---

### 📄 Lizenz & Autor

- **Autor:** [KIB.best](https://kib.best)
- **Kontakt:** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **Lizenz:** MIT License © 2026 KIB.best.
