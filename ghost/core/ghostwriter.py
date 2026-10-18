"""
GhostOS Ghostwriter
Inline AI text transformation and rewriter engine operating across all desktop apps via clipboard.
Zero RAM bloat: processes text on demand and immediately releases model memory.
"""
import sys
import subprocess
from typing import Dict, Any, Optional

from ghost.core.clipboard import PhantomClipboard
from ghost.core.engine import GhostEngine

class Ghostwriter:
    """
    Transforms any selected text in Word, Telegram, browsers, IDEs, or notes.
    """

    TRANSFORMATIONS = {
        "polish": {
            "title": "✨ Polish & Refine",
            "prompt": "Rewrite the following text to make it clear, concise, and professional, preserving its original meaning:\n\n{text}"
        },
        "polite": {
            "title": "🤝 Professional & Polite",
            "prompt": "Rewrite the following text with a diplomatic, respectful, and friendly business tone:\n\n{text}"
        },
        "grammar": {
            "title": "📝 Fix Spelling & Grammar",
            "prompt": "Fix all typos, punctuation errors, and grammatical mistakes in the following text. Do not add conversational commentary:\n\n{text}"
        },
        "summarize": {
            "title": "🎯 Executive Summary",
            "prompt": "Summarize the key points of the following text into 2-3 bullet points:\n\n{text}"
        },
        "translate_en": {
            "title": "🇺🇸 Translate to English",
            "prompt": "Translate the following text into natural, fluent English:\n\n{text}"
        },
        "translate_ru": {
            "title": "🇷🇺 Translate to Russian",
            "prompt": "Переведи следующий текст на естественный грамотный русский язык:\n\n{text}"
        },
        "code_explain": {
            "title": "⚡ Explain Code",
            "prompt": "Explain what this code does in 2 concise sentences:\n\n{text}"
        },
        "code_fix": {
            "title": "🛠️ Fix Code Bug",
            "prompt": "Analyze this code for bugs, fix them, and provide the clean corrected code:\n\n{text}"
        }
    }

    def __init__(self, engine: Optional[GhostEngine] = None):
        self.engine = engine or GhostEngine()

    def rewrite_text(self, text: str, mode: str = "polish") -> Dict[str, Any]:
        """
        Transform given text based on specified mode.
        """
        clean_text = text.strip()
        if not clean_text:
            return {"success": False, "error": "No text provided to rewrite."}

        trans = self.TRANSFORMATIONS.get(mode, self.TRANSFORMATIONS["polish"])
        prompt = trans["prompt"].format(text=clean_text)

        try:
            result = self.engine.ask(prompt)
            return {
                "success": True,
                "mode": mode,
                "title": trans["title"],
                "original": clean_text,
                "result": result.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def rewrite_clipboard(self, mode: str = "polish") -> Dict[str, Any]:
        """
        Read system clipboard, rewrite text, and write transformed result back to clipboard.
        Allows instant paste with Cmd+V / Ctrl+V in any application!
        """
        current_text = PhantomClipboard.get_clipboard_text()
        if not current_text:
            return {"success": False, "error": "Clipboard is empty. Copy some text first!"}

        res = self.rewrite_text(current_text, mode=mode)
        if res.get("success"):
            PhantomClipboard.set_clipboard_text(res["result"])
            res["copied_to_clipboard"] = True

        return res
