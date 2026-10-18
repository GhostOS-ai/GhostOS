"""
GhostOS Phantom Clipboard
Sub-millisecond pattern-matcher and instant action generator for clipboard snippets.
Zero memory overhead: analyzes content using native regex heuristics before touching any LLM.
"""
import re
import json
import subprocess
from typing import Dict, Any, Optional

class PhantomClipboard:
    """
    Monitors and inspects clipboard contents to offer contextual 1-click actions.
    """

    @staticmethod
    def get_clipboard_text() -> str:
        """Read system clipboard across macOS, Windows, and Linux."""
        import sys
        try:
            if sys.platform == "darwin":
                res = subprocess.run("pbpaste", shell=True, capture_output=True, text=True, timeout=2)
                return res.stdout.strip()
            elif sys.platform == "win32":
                res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True, timeout=2)
                return res.stdout.strip()
            else:
                for tool in ["xclip -selection clipboard -o", "xsel --clipboard --output", "wl-paste"]:
                    try:
                        res = subprocess.run(tool, shell=True, capture_output=True, text=True, timeout=1)
                        if res.returncode == 0:
                            return res.stdout.strip()
                    except Exception:
                        continue
        except Exception:
            pass
        return ""

    @staticmethod
    def set_clipboard_text(text: str) -> bool:
        """Write text to system clipboard across macOS, Windows, and Linux."""
        import sys
        try:
            if sys.platform == "darwin":
                proc = subprocess.Popen("pbcopy", shell=True, stdin=subprocess.PIPE, text=True)
                proc.communicate(text, timeout=2)
                return proc.returncode == 0
            elif sys.platform == "win32":
                proc = subprocess.Popen(["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value $input"], stdin=subprocess.PIPE, text=True)
                proc.communicate(text, timeout=2)
                return proc.returncode == 0
            else:
                for tool in ["xclip -selection clipboard", "xsel --clipboard --input", "wl-copy"]:
                    try:
                        proc = subprocess.Popen(tool, shell=True, stdin=subprocess.PIPE, text=True)
                        proc.communicate(text, timeout=2)
                        if proc.returncode == 0:
                            return True
                    except Exception:
                        continue
        except Exception:
            pass
        return False

    @classmethod
    def inspect(cls, custom_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze clipboard content and classify its intent.
        Returns suggested action, category, and instant preview.
        """
        text = custom_text if custom_text is not None else cls.get_clipboard_text()
        if not text:
            return {
                "detected": False,
                "category": "empty",
                "badge": "📋 Empty",
                "preview": "",
                "actions": []
            }

        preview = (text[:120] + "...") if len(text) > 120 else text

        # 1. Error / Traceback
        if any(marker in text for marker in ["Traceback (most recent call last):", "Error:", "Exception:", "fatal:", "panic:"]):
            return {
                "detected": True,
                "category": "error",
                "badge": "🚨 Stack Trace / Error",
                "preview": preview,
                "raw_text": text,
                "suggested_action": "diagnose_error",
                "action_title": "💡 Explain & Fix Error",
                "actions": ["Explain & Fix", "Summarize Traceback", "Copy Cleaned Error"]
            }

        # 2. JSON Snippet
        trimmed = text.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
            try:
                parsed = json.loads(trimmed)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                return {
                    "detected": True,
                    "category": "json",
                    "badge": "✨ JSON Data",
                    "preview": preview,
                    "raw_text": text,
                    "formatted_text": formatted,
                    "suggested_action": "format_json",
                    "action_title": "✨ Prettify & Validate JSON",
                    "actions": ["Prettify JSON", "Minify JSON", "Generate TypeScript Types"]
                }
            except Exception:
                pass

        # 3. SQL Query
        if re.search(r'\b(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE)\b', text, re.IGNORECASE):
            return {
                "detected": True,
                "category": "sql",
                "badge": "🔍 SQL Query",
                "preview": preview,
                "raw_text": text,
                "suggested_action": "explain_sql",
                "action_title": "🔍 Explain Query & Indexing",
                "actions": ["Explain Query", "Optimize SQL", "Convert to Python ORM"]
            }

        # 4. URL
        if re.match(r'^https?://[^\s]+$', trimmed):
            return {
                "detected": True,
                "category": "url",
                "badge": "🔗 Web Link",
                "preview": preview,
                "raw_text": text,
                "suggested_action": "open_link",
                "action_title": "🌐 Fetch & Summarize URL",
                "actions": ["Summarize Webpage", "Copy Clean URL"]
            }

        # 5. Code Snippet
        if re.search(r'\b(def |function |const |let |class |fn |impl |public static void)\b', text):
            return {
                "detected": True,
                "category": "code",
                "badge": "⚡ Code Snippet",
                "preview": preview,
                "raw_text": text,
                "suggested_action": "explain_code",
                "action_title": "⚡ Explain & Refactor Code",
                "actions": ["Explain Code", "Add Docstrings", "Refactor Clean Code"]
            }

        # Default text
        return {
            "detected": True,
            "category": "text",
            "badge": "📝 Text Selection",
            "preview": preview,
            "raw_text": text,
            "suggested_action": "improve_text",
            "action_title": "🌐 Translate / Polish Text",
            "actions": ["Translate to Russian", "Improve Grammar", "Summarize Key Points"]
        }
