<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    隐形、超轻量、纯离线的桌面 AI 助手与伴侣
    /`---'\
   /       \    [ 100% 隐私保护 • 动态显存调度 • Zero-DB RAG • Casper 桌面小幽灵 ]
  (_/^\_/\_/^)
```

# 👻 GhostOS
### 超轻量、纯离线运行的桌面 AI 助手与代码伴侣

<p align="center">
  <b>🌐 语言选择 / Language Select:</b><br>
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
[![空闲内存](https://img.shields.io/badge/待机内存-%3C35%20MB-success.svg)]()
[![显存峰值](https://img.shields.io/badge/显存峰值-%E2%89%A43.5%20GB-blueviolet.svg)]()
[![隐私保护](https://img.shields.io/badge/隐私-100%25%20离线-orange.svg)]()

**专为低配置笔记本与标准 Apple Silicon Mac (4GB–8GB 统一内存) 设计，杜绝内存溢出 (OOM) 崩溃，无需联网即可流畅运行的桌面智能助手。**

---

### 💡 为什么选择 GhostOS？

当今本地 AI 客户端的通病：
1. **Electron 内存巨兽：** LM Studio、Jan 或 AnythingLLM 等客户端在加载任何模型之前，界面就已占满 **800MB–1.2GB** 系统内存。
2. **多模型显存陷阱 (OOM)：** 同时运行语言模型 (3GB) + 视觉模型 (2GB) + 语音模型 (1GB) 会瞬间挤爆 4GB–8GB 显存造成死机。
3. **过于臃肿的知识库体系：** 大多数本地文档对话工具强制要求配置 Docker 与重型向量数据库（如 Chroma、Qdrant）。

**GhostOS 给出创新解决方案：**
- **原生极轻量桌面宠物与 HUD：** 采用操作系统原生 WebView 渲染（macOS WebKit、Windows Edge WebView2、Linux WebKitGTK），界面待机仅需 **~35MB 内存**。
- **显存调度器 (VRAM Juggler)：** 在 150 毫秒内按需热切换不同功能模型，显存占用永远锁定在 **3.5GB 以内**。
- **Zero-DB 本地知识库：** 拖拽 PDF、代码或笔记投喂给 Casper 桌面幽灵，即可基于纯 **SQLite FTS5** 瞬间检索，无需外部数据库。
- **100% 绝对隐私：** 无数据外发、无云端中转，完全支持拔网线物理隔离运行。

---

### 🚀 极速安装与启动

```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
pip install -e .

# 启动 Casper 桌面小幽灵与控制台
ghost pet
```

---

### 📄 开源许可证与作者信息

- **作者:** [KIB.best](https://github.com/GhostOS-ai/GhostOS)
- **邮箱:** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **许可证:** MIT License © 2026 KIB.best. 免费供个人与商业使用。
