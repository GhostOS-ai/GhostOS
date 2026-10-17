"""
GhostOS UI JavaScript API Bridge
Provides Python methods callable from the WKWebView frontend (Pet & HUD).
"""
import os
import json
from typing import Dict, Any, Optional

from ghost.core.engine import GhostEngine
from ghost.core.rag import ZeroDbRAG
from ghost.core.vision import ScreenInspector
from ghost.core.autopilot import TerminalAutopilot
from ghost.core.audio import MeetingCopilot
from ghost.core.memory_juggler import MemoryJuggler

class GhostBridgeAPI:
    """
    Bridge exposed to window.pywebview.api.
    """

    def __init__(self, window=None):
        self.window = window
        self.engine = GhostEngine()
        self.rag = ZeroDbRAG()
        self.vision = ScreenInspector()
        self.autopilot = TerminalAutopilot()
        self.meeting = MeetingCopilot()
        self.juggler = MemoryJuggler()
        self.current_mode = "pet"  # "pet" or "hud"

    def set_window(self, window):
        self.window = window

    def ask(self, prompt: str) -> Dict[str, Any]:
        """User asks a question from HUD."""
        # Check local docs first
        docs = self.rag.search(prompt, top_k=2)
        context = ""
        cited_files = []
        if docs:
            context = "\n\n".join([f"[{d['filename']}]: {d['content']}" for d in docs])
            cited_files = list(set([d["filename"] for d in docs]))

        reply = self.engine.ask(prompt, context=context)
        return {
            "success": True,
            "response": reply,
            "citations": cited_files
        }

    def eat_file_path(self, path: str) -> Dict[str, Any]:
        """Ghost eats a file via drag-and-drop file path."""
        res = self.rag.ingest_file(path)
        return res

    def ingest_dropped_content(self, filename: str, content: str) -> Dict[str, Any]:
        """Ghost eats raw dropped text/file from web drag-and-drop."""
        from ghost.config import GHOST_CACHE_DIR
        temp_file = GHOST_CACHE_DIR / filename
        try:
            temp_file.write_text(content, encoding="utf-8")
            res = self.rag.ingest_file(str(temp_file))
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def peek_screen(self) -> Dict[str, Any]:
        """Analyze current frontmost screen."""
        return self.vision.analyze_screen()

    def generate_autopilot_command(self, task: str) -> Dict[str, Any]:
        """Translate request into a shell command with safety score."""
        return self.autopilot.generate_command(task)

    def execute_terminal(self, command: str) -> Dict[str, Any]:
        """Execute approved terminal command."""
        return self.autopilot.execute_command(command)

    def get_memory_stats(self) -> Dict[str, Any]:
        """Return real-time VRAM Juggler diagnostics."""
        return self.juggler.get_memory_status()

    def get_indexed_documents(self) -> Dict[str, Any]:
        """Return list of all indexed files."""
        return {"documents": self.rag.list_documents()}

    def toggle_mode(self, target_mode: str) -> Dict[str, Any]:
        """
        Smoothly resize window between Pet mode (220x240) and HUD mode (680x520).
        """
        self.current_mode = target_mode
        if self.window:
            if target_mode == "hud":
                self.window.resize(680, 540)
            else:
                self.window.resize(220, 240)
        return {"mode": self.current_mode}

    def minimize_pet(self) -> None:
        """Minimize or hide window."""
        if self.window:
            self.window.minimize()

    # ==================== NEW KILLER FEATURES ====================
    def get_rpg_status(self) -> Dict[str, Any]:
        """Fetch Casper RPG level, title, accessory, and XP."""
        from ghost.core.rpg import CasperRPG
        return CasperRPG.get_full_status()

    def inspect_clipboard(self) -> Dict[str, Any]:
        """Phantom Clipboard: Inspect system clipboard and categorize."""
        from ghost.core.clipboard import PhantomClipboard
        return PhantomClipboard.inspect()

    def apply_clipboard_action(self, action: str, text: str) -> Dict[str, Any]:
        """Execute selected clipboard transformation."""
        from ghost.core.clipboard import PhantomClipboard
        from ghost.core.rpg import CasperRPG
        CasperRPG.add_xp(10, "clipboard")

        if action == "format_json":
            try:
                parsed = json.loads(text)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                PhantomClipboard.set_clipboard_text(formatted)
                return {"success": True, "result": formatted, "copied": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif action == "diagnose_error":
            res = self.engine.ask(f"Explain this error and give the exact fix:\n\n{text}")
            return {"success": True, "result": res, "copied": False}

        elif action == "explain_sql":
            res = self.engine.ask(f"Explain what this SQL query does and how to optimize it:\n\n{text}")
            return {"success": True, "result": res, "copied": False}

        else:
            res = self.engine.ask(f"Process this text ({action}):\n\n{text}")
            return {"success": True, "result": res, "copied": False}

    def get_time_machine_summary(self) -> Dict[str, Any]:
        """Fetch daily developer session timeline and git commit suggestions."""
        from ghost.core.time_machine import GhostTimeMachine
        return GhostTimeMachine.generate_session_summary()

    def get_chameleon_profile(self) -> Dict[str, Any]:
        """Fetch current hardware and power adaptive profile."""
        from ghost.core.chameleon import MemoryChameleon
        return MemoryChameleon.get_profile()

    def set_chameleon_mode(self, mode: str) -> Dict[str, Any]:
        """Manually set Chameleon mode: 'eco', 'balanced', 'performance', or null for auto."""
        from ghost.core.chameleon import MemoryChameleon
        MemoryChameleon.set_override(mode if mode != "auto" else None)
        return MemoryChameleon.get_profile()

    # ==================== VOICE, AGENT & WEB SEARCH ====================
    def toggle_voice(self, state: Optional[bool] = None) -> Dict[str, Any]:
        """Toggle native text-to-speech output."""
        from ghost.core.voice import VoiceEngine
        new_state = VoiceEngine().toggle(state)
        return {"voice_enabled": new_state}

    def speak_text(self, text: str) -> Dict[str, Any]:
        """Speak arbitrary text aloud using native say synthesizer."""
        from ghost.core.voice import VoiceEngine
        success = VoiceEngine().speak(text)
        return {"success": success}

    def execute_agent_task(self, prompt: str) -> Dict[str, Any]:
        """Execute a desktop OS file management task."""
        from ghost.core.agent import GhostOSAgent
        from ghost.core.rpg import CasperRPG
        res = GhostOSAgent.execute_intent(prompt)
        if res.get("handled"):
            CasperRPG.add_xp(25, "exec")
        return res

    def search_web(self, query: str) -> Dict[str, Any]:
        """Fetch live web search context."""
        from ghost.core.web_search import WebSearchEngine
        return WebSearchEngine.search_web(query)
