<div align="center">

```
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    Көрінбейтін, аса жеңіл, дербес жергілікті AI-көмекші
    /`---'\
   /       \    [ 100% Құпия • VRAM Juggler • Zero-DB RAG • Каспер көмекшісі ]
  (_/^\_/\_/^)
```

# 👻 GhostOS
### Компьютерге арналған аса жеңіл, оффлайн AI-көмекші және десктоп серігі

<p align="center">
  <b>🌐 Тілді таңдау / Language Select:</b><br>
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

[![Лицензия: MIT](https://img.shields.io/badge/Лицензия-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Автор: KIB.best](https://img.shields.io/badge/Автор-KIB.best-8A2BE2.svg)](https://github.com/GhostOS-ai/GhostOS)
[![Email](https://img.shields.io/badge/Байланыс-GhostOS%40kib.best-0071e3.svg)](mailto:GhostOS@kib.best)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Платформа](https://img.shields.io/badge/платформа-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![Тыныш кездегі RAM](https://img.shields.io/badge/RAM-%3C35%20МБ-success.svg)]()
[![Ең жоғарғы VRAM](https://img.shields.io/badge/VRAM-%E2%89%A43.5%20ГБ-blueviolet.svg)]()
[![Құпиялылық](https://img.shields.io/badge/Құпиялылық-100%25%20Оффлайн-orange.svg)]()

**Қуаты аз ноутбуктер мен қарапайым компьютерлерде (4–8 ГБ RAM) жады жетпей тоқтап қалмай (OOM), толық жергілікті жұмыс істейтін AI-көмекші.**

---

### 💡 Неліктен GhostOS?

Қазіргі дербес AI бағдарламаларының негізгі кемшіліктері:
1. **Electron жадысының ауырлығы:** Көптеген қосымшалар (LM Studio, Jan, AnythingLLM) нейрожеліні жүктемей тұрып-ақ **800–1200 МБ жедел жадты** босқа жалмап қояды.
2. **Бірнеше модель тұзағы (OOM):** Тілдік модельді (3 ГБ) + көру моделін (2 ГБ) + Whisper (1 ГБ) бір уақытта қосқанда 4–8 ГБ жады бар компьютер бірден қатып қалады.
3. **Күрделі дерекқорлар:** Құжаттармен жұмыс істеу үшін Docker мен ауыр векторлық базаларды (Chroma) орнатуды талап етеді.

**GhostOS бұл мәселені түбегейлі шешеді:**
- **Каспер және HUD интерфейсі:** Жүйенің нативті компоненттерінде жұмыс істейді және бар болғаны **~35 МБ RAM** жұмсайды.
- **VRAM Juggler:** Модельдерді бір-бірімен 150 миллисекунд ішінде ауыстырып отырады. Бейнежад шығыны ешқашан **3.5 ГБ-тан аспайды**.
- **Zero-DB RAG:** Файлды Касперге тастасаңыз жеткілікті — таза **SQLite FTS5** арқылы лезде іздеу базасына қосылады.
- **100% Құпия:** Ешқандай бұлтты серверлерге дерек кетпейді, интернетсіз толық жұмыс істейді.

---

### 🚀 Жылдам орнату және іске қосу

```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
pip install -e .

# Каспер көмекшісін іске қосу
ghost pet
```

---

### 📄 Лицензия және авторлық құқық

- **Автор:** [KIB.best](https://github.com/GhostOS-ai/GhostOS)
- **Email:** [GhostOS@kib.best](mailto:GhostOS@kib.best)
- **Лицензия:** MIT License © 2026 KIB.best. Жеке және коммерциялық мақсатта қолдану тегін.
