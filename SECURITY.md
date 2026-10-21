# Security Policy

## 🔒 Supported Versions

We provide security patches and updates for the following versions of GhostOS:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

---

## 🛡️ Reporting a Vulnerability

The GhostOS project takes privacy and security seriously. 

If you discover a potential security vulnerability, memory leak, or unsafe command execution issue in GhostOS:

1. **Do NOT open a public GitHub issue.**
2. Send an email to our core team at:
   📧 **[GhostOS@kib.best](mailto:GhostOS@kib.best)**
3. Please include:
   - Type of vulnerability / issue
   - Step-by-step instructions or minimal script to reproduce
   - Potential impact on the host system or offline environment
   - Suggested remediation (if known)

### Response Timeline
- **Initial acknowledgment:** Within 24–48 hours.
- **Triage & fix development:** Within 3–7 business days depending on severity.
- **Public release & disclosure:** Once a patched release is published on PyPI and GitHub.

---

## 🔐 The GhostOS Privacy & Air-Gap Pledge

GhostOS is architected from day one under paranoid privacy standards:
- **Zero Telemetry**: No analytical trackers, usage pings, or IP logging.
- **Local-Only Storage**: All vector embeddings (SQLite FTS5), chat histories, and configurations remain strictly on your local disk in `~/.ghost/`.
- **Sandbox Lens**: Destructive shell operations are proactively checked before terminal dispatch to prevent accidental data loss.
