<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    L'Assistant IA de Bureau Invisible, Ultra-léger et 100% Hors Ligne
    /`---'\
   /       \    [ 100% Privé • Dynamic VRAM Juggler • Zero-DB RAG • Compagnon Casper ]
  (_/^\_/\_/^)
```

# 👻 GhostOS
### L'Assistant IA de Bureau Ultra-léger et Hors Ligne

<p align="center">
  <b>🌐 Choix de la langue / Language Select:</b><br>
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

[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Auteur: KIB.best](https://img.shields.io/badge/Auteur-KIB.best-8A2BE2.svg)](https://github.com/GhostOS-ai/GhostOS)
[![Email](https://img.shields.io/badge/Contact-GhostOS%40kib.best-0071e3.svg)](mailto:GhostOS@kib.best)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Plateforme](https://img.shields.io/badge/plateforme-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![RAM au repos](https://img.shields.io/badge/RAM%20au%20repos-%3C35%20Mo-success.svg)]()
[![VRAM max](https://img.shields.io/badge/VRAM%20max-%E2%89%A43.5%20Go-blueviolet.svg)]()
[![Confidentialité](https://img.shields.io/badge/Confidentialit%C3%A9-100%25%20Hors%20Ligne-orange.svg)]()

**Conçu spécifiquement pour les ordinateurs modestes et les Mac Apple Silicon (4 Go–8 Go de RAM) sans plantages de mémoire (OOM).**

</div>

---

### 💡 Pourquoi GhostOS ?

Faire tourner une IA locale aujourd'hui est souvent lourd et fastidieux :
1. **Surcharge de mémoire Electron :** La plupart des applications consomment **800 Mo à 1,2 Go de RAM** rien que pour l'interface avant de charger le moindre modèle.
2. **Le piège OOM multi-modèles :** Exécuter un LLM (3 Go) + un modèle visuel (2 Go) + Whisper (1 Go) fait planter tout système de 4 Go à 8 Go de RAM.
3. **Piles RAG surdimensionnées :** Les outils de discussion documentaire imposent Docker, de lourdes bases de données vectorielles et des gigaoctets de dépendances.

**GhostOS réinvente l'approche :**
- **Compagnon Casper et HUD Natif :** Utilise les moteurs web natifs du système (WebKit sur macOS, Edge WebView2 sur Windows, WebKitGTK sur Linux) pour consommer seulement **~35 Mo de RAM**.
- **Dynamic VRAM Juggler :** Bascule à chaud entre LLM, Vision et Whisper en moins de 150 ms. L'utilisation maximale de VRAM ne dépasse jamais **3,5 Go**.
- **Zero-DB RAG :** Glissez des fichiers sur Casper — indexation instantanée via **SQLite FTS5** pur sans bases de données externes.
- **100% Local et Privé :** Zéro télémétrie, zéro dépendance cloud. Fonctionne parfaitement sans connexion internet.

---

### ✨ Fonctionnalités Exclusives

- **Ghostwriter :** Réécriture, correction et traduction intelligente directement dans le presse-papiers de toutes vos applications.
- **Memory Vault :** Graphe contextuel à long terme dans SQLite avec zéro surcharge de VRAM.
- **Terminal Sandbox Lens :** Surveillance en temps réel des commandes terminal destructrices (`rm -rf`, `DROP TABLE`, `mkfs`) avec alertes claires.
- **Daily Standup & Commit Crafter :** Transforme automatiquement vos diffs git et votre activité en commits conventionnels et bilans quotidiens.
- **Auto-Minutes :** Transcription et synthèse de réunions avec plan d'action immédiat.

---

### 🚀 Démarrage Rapide

```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
pip install -e .

# Lancer le compagnon de bureau Casper
ghost pet
```

---

### 📄 Licence et Auteur

- **Auteur :** [KIB.best](https://github.com/GhostOS-ai/GhostOS)
- **Contact :** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **Licence :** MIT License © 2026 KIB.best.
