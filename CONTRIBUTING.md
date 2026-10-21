# Contributing to GhostOS

Thank you for your interest in contributing to GhostOS! 👻

GhostOS is a featherweight, 100% offline, privacy-first desktop AI companion engineered for low-spec hardware and base laptops. We welcome contributions from developers worldwide.

---

## 🛠️ Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/GhostOS-ai/GhostOS.git
cd GhostOS
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install in editable mode with development dependencies
```bash
pip install -e .
pip install flake8 mypy build twine
```

---

## 🧪 Running Tests

We maintain a strict zero-regression policy. Before submitting any changes, ensure all tests pass cleanly:

```bash
python3 -m unittest discover tests
```

To run a specific test suite:
```bash
python3 -m unittest tests/test_model_catalog.py
```

---

## 📐 Core Architectural Principles

When contributing to GhostOS, please keep our core tenets in mind:

1. **Zero Bloat (<35MB RAM idle)**: Never introduce heavy Electron runtimes or monolithic web servers. We rely on native OS webviews (`pywebview` / WebKit / WebView2).
2. **100% Offline & Private**: Absolutely no telemetry, tracking pings, or cloud phone-home calls. Air-gapped readiness is mandatory.
3. **Hardware Friendliness**: Code should run smoothly on 4GB–8GB RAM machines without memory leaks or unmanaged thread pools.
4. **Clean Dependencies**: Prefer Python standard library modules (`sqlite3`, `urllib`, `dataclasses`, `subprocess`) wherever possible.

---

## 🚀 Submitting a Pull Request (PR)

1. **Fork the repository** on GitHub.
2. **Create a topic branch** from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   ```
3. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "feat: add support for new Casper theme"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feat/my-new-feature
   ```
5. **Open a Pull Request** against `GhostOS-ai/GhostOS:main`.
6. Ensure all unit tests pass in your branch.

---

## 💬 Community & Help

- **Issues & Discussions**: Feel free to open a [GitHub Issue](https://github.com/GhostOS-ai/GhostOS/issues) to discuss ideas before writing large features.
- **Security Inquiries**: For sensitive vulnerability reports, please email [GhostOS@kib.best](mailto:GhostOS@kib.best).
- **Code of Conduct**: All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
