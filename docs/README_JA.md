<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    不可視で超軽量、完全オフラインで動作するデスクトップAIコパイロット
    /`---'\
   /       \    [ 100% プライベート • 動的VRAMジャグラー • Zero-DB RAG • デスクトップペット Casper ]
  (_/^\_/\_/^)
```

# 👻 GhostOS
### 超軽量・完全オフライン動作のデスクトップAIアシスタント＆コンパニオン

<p align="center">
  <b>🌐 言語を選択 / Language Select:</b><br>
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

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Author: KIB.best](https://img.shields.io/badge/Author-KIB.best-8A2BE2.svg)](https://github.com/GhostOS-ai/GhostOS)
[![Email](https://img.shields.io/badge/Contact-GhostOS%40kib.best-0071e3.svg)](mailto:GhostOS@kib.best)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![アイドル時RAM](https://img.shields.io/badge/待機RAM-%3C35%20MB-success.svg)]()
[![最大VRAM](https://img.shields.io/badge/最大VRAM-%E2%89%A43.5%20GB-blueviolet.svg)]()
[![プライバシー](https://img.shields.io/badge/プライバシー-100%25%20オフライン-orange.svg)]()

**低スペックPCや標準的なApple Silicon Mac（4GB〜8GBメモリ）でもメモリ不足（OOM）でクラッシュせずに快適動作。**

</div>

---

### 💡 なぜ GhostOS なのか？

現在のローカルAI環境が抱える課題：
1. **Electronによるメモリ肥大化:** 多くのアプリはAIモデルを読み込む前のUIだけで **800MB〜1.2GB** のメモリを浪費します。
2. **複数モデルによるOOMトラップ:** LLM（3GB）＋ 画像認識（2GB）＋ Whisper（1GB）を同時に起動すると、4GB〜8GBのマシンは即座に停止します。
3. **過剰に複雑なRAG:** ドキュメント検索にDockerや重量級のベクトルDBを要求され、設定が困難です。

**GhostOS のアプローチ:**
- **Casper デスクトップペット & HUD:** OS標準の軽量WebViewエンジン（macOS WebKit、Windows Edge WebView2、Linux WebKitGTK）を採用し、待機時わずか **~35MB RAM** で動作。
- **動的VRAMジャグラー (VRAM Juggler):** LLM、画像認識、音声認識を150ミリ秒で必要に応じてオンデマンド切り替え。最大VRAM使用量は **3.5GB以下** に抑制。
- **Zero-DB RAG:** ファイルをCasperにドラッグ＆ドロップするだけで、**SQLite FTS5** による超高速全文検索を実現。外部DBは不要。
- **100% 完全オフライン・プライベート:** テレメトリなし、クラウド送信なし。LANケーブルを抜いた環境でも完全に機能します。

---

### ✨ 独自機能

- **Ghostwriter:** あらゆるアプリ上で、選択したテキストをクリップボード経由で即座にAI校正・翻訳・要約。
- **Memory Vault:** VRAMを消費しないSQLiteベースの長期コンテキストグラフ。
- **Terminal Sandbox Lens:** 危険なコマンド（`rm -rf`, `DROP TABLE`, `mkfs` など）をリアルタイムに検知し警告。
- **Daily Standup & Commit Crafter:** 日々のGit変更履歴から自動的にコミットメッセージや日報を作成。
- **Auto-Minutes:** 音声会議のリアルタイム文字起こしとアクションプラン作成。

---

### 🚀 クイックスタート

```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
pip install -e .

# Casper デスクトップペットを起動
ghost pet
```

---

### 📄 ライセンスと開発者

- **開発者:** [KIB.best](https://github.com/GhostOS-ai/GhostOS)
- **連絡先:** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **ライセンス:** MIT License © 2026 KIB.best.
