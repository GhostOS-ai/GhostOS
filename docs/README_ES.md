<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    El Asistente de IA de Escritorio Invisible, Ultraligero y 100% Offline
    /`---'\
   /       \    [ 100% Privado • Dynamic VRAM Juggler • Zero-DB RAG • Mascota Casper ]
  (_/^\_/\_/^)
```

# 👻 GhostOS
### El Asistente de IA de Escritorio Ultraligero y Offline

<p align="center">
  <b>🌐 Selección de idioma / Language Select:</b><br>
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

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Autor: KIB.best](https://img.shields.io/badge/Autor-KIB.best-8A2BE2.svg)](https://kib.best)
[![Email](https://img.shields.io/badge/Contacto-GhostOS%40kib.best-0071e3.svg)](mailto:GhostOS@kib.best)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Plataforma](https://img.shields.io/badge/plataforma-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![RAM en reposo](https://img.shields.io/badge/RAM%20en%20reposo-%3C35%20MB-success.svg)]()
[![VRAM máximo](https://img.shields.io/badge/VRAM%20máximo-%E2%89%A43.5%20GB-blueviolet.svg)]()
[![Privacidad](https://img.shields.io/badge/Privacidad-100%25%20Offline-orange.svg)]()

**Diseñado específicamente para portátiles modestos y Macs con Apple Silicon básico (4GB–8GB RAM) sin bloqueos por falta de memoria (OOM).**

</div>

---

### 💡 ¿Por qué GhostOS?

Ejecutar IA local hoy en día suele ser pesado e ineficiente:
1. **Exceso de RAM en Electron:** La mayoría de las aplicaciones de escritorio consumen entre **800MB y 1.2GB de RAM** solo para la interfaz antes de cargar cualquier modelo.
2. **Trampa de OOM Multimodelo:** Ejecutar un LLM (3GB) + modelo de visión (2GB) + Whisper (1GB) simultáneamente satura cualquier equipo con 4GB–8GB de RAM.
3. **Pilas RAG Sobredimensionadas:** Herramientas de chat con documentos requieren Docker, pesadas bases vectoriales y gigabytes de dependencias.

**GhostOS soluciona esto desde el diseño:**
- **Mascota Casper y HUD Nativo:** Renderizado con motores web del sistema operativo (WebKit en macOS, Edge WebView2 en Windows, WebKitGTK en Linux) consumiendo solo **~35MB de RAM**.
- **Dynamic VRAM Juggler:** Intercambia en caliente entre LLM, Visión y Whisper en menos de 150 ms. El uso máximo de VRAM nunca supera los **3.5GB**.
- **Zero-DB RAG:** Arrastra archivos a Casper para indexarlos al instante usando **SQLite FTS5** puro, sin bases de datos pesadas.
- **100% Privado y Autónomo:** Cero telemetría, cero llamadas a la nube. Funciona completamente aislado de internet.

---

### ✨ Tecnologías Exclusivas

- **Ghostwriter:** Corrección, resumen y traducción inteligente directo en tu portapapeles en cualquier aplicación del sistema.
- **Memory Vault:** Grafo de conocimiento de contexto a largo plazo en SQLite sin consumir memoria VRAM.
- **Terminal Sandbox Lens:** Detector proactivo de comandos peligrosos en consola (`rm -rf`, `DROP TABLE`, `mkfs`) con advertencias en lenguaje natural.
- **Daily Standup & Commit Crafter:** Convierte automáticamente la actividad de tu día y los diffs de git en resúmenes diarios y commits limpios.
- **Auto-Minutes:** Transcripción y resumen ejecutivo de reuniones con lista de tareas pendientes.

---

### 🚀 Instalación Rápida

```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
pip install -e .

# Iniciar la mascota de escritorio Casper
ghost pet
```

---

### 📄 Licencia y Autoría

- **Autor:** [KIB.best](https://kib.best)
- **Contacto:** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **Licencia:** MIT License © 2026 KIB.best.
