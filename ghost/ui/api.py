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
        """User asks a question from HUD or Pet: auto-routes to Agent, Web, RAG, or LLM."""
        # 1. Desktop OS task check
        from ghost.core.agent import GhostOSAgent
        from ghost.core.rpg import CasperRPG
        from ghost.core.voice import VoiceEngine

        agent_res = GhostOSAgent.execute_intent(prompt)
        if agent_res.get("handled"):
            CasperRPG.add_xp(25, "exec")
            VoiceEngine().speak(agent_res["output"], async_mode=True)
            return {
                "success": True,
                "response": agent_res["output"],
                "citations": []
            }

        # 2. Live Web search check (weather, currency, search)
        p_lower = prompt.lower()
        if any(w in p_lower for w in ["погода", "weather", "курс", "доллар", "евро", "валют", "найди в интернете"]):
            from ghost.core.web_search import WebSearchEngine
            web_res = WebSearchEngine.search_web(prompt)
            if web_res.get("content"):
                CasperRPG.add_xp(15, "web")
                VoiceEngine().speak(web_res["content"], async_mode=True)
                return {
                    "success": True,
                    "response": web_res["content"],
                    "citations": [web_res.get("source", "Internet")]
                }

        # 3. Check Memory Vault (Long-Term Facts) & Zero-DB RAG
        from ghost.core.memory_vault import MemoryVault
        vault = MemoryVault()
        vault.auto_extract_facts(prompt)
        vault_ctx = vault.get_context_block()

        docs = self.rag.search(prompt, top_k=2)
        doc_ctx = ""
        cited_files = []
        if docs:
            doc_ctx = "\n\n".join([f"[{d['filename']}]: {d['content']}" for d in docs])
            cited_files = list(set([d["filename"] for d in docs]))

        # Greetings and small talk should not be tainted by vault context
        p_clean = prompt.lower().strip()
        is_small_talk = any(w in p_clean for w in ["привет", "салам", "hello", "hi", "хай", "здравствуй", "как дела", "кто ты", "что ты умеешь", "помощь"])
        if is_small_talk:
            combined_context = None
        elif doc_ctx:
            combined_context = f"{vault_ctx}\n\n{doc_ctx}".strip()
        elif vault_ctx:
            combined_context = vault_ctx
        else:
            combined_context = None

        # 4. Neural LLM / Smart Assistant
        reply = self.engine.ask(prompt, context=combined_context)
        CasperRPG.add_xp(10, "chat")
        VoiceEngine().speak(reply, async_mode=True)
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
        from ghost.core.rpg import CasperRPG
        temp_file = GHOST_CACHE_DIR / filename
        try:
            temp_file.write_text(content, encoding="utf-8")
            res = self.rag.ingest_file(str(temp_file))
            if res.get("success"):
                CasperRPG.add_xp(25, "eat")
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def ingest_dropped_file_base64(self, filename: str, base64_data: str) -> Dict[str, Any]:
        """Ghost eats binary dropped file (e.g. PDF, image) via Base64 data URL."""
        import base64
        from ghost.config import GHOST_CACHE_DIR
        from ghost.core.rpg import CasperRPG
        temp_file = GHOST_CACHE_DIR / filename
        try:
            if "," in base64_data:
                base64_data = base64_data.split(",", 1)[1]
            file_bytes = base64.b64decode(base64_data)
            temp_file.write_bytes(file_bytes)
            res = self.rag.ingest_file(str(temp_file))
            if res.get("success"):
                CasperRPG.add_xp(35, "eat")
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
        Smoothly resize window between Pet (240x280), HUD (760x580), and Studio (1160x780).
        """
        import webview
        self.current_mode = target_mode
        if self.window:
            if target_mode == "studio":
                try:
                    if not hasattr(self, '_pet_x') or self._pet_x is None:
                        self._pet_x = self.window.x
                        self._pet_y = self.window.y
                    screens = webview.screens
                    if screens:
                        s = screens[0]
                        w_x = max(20, (s.width - 1160) // 2)
                        w_y = max(20, (s.height - 780) // 2)
                        self.window.resize(1160, 780)
                        self.window.move(w_x, w_y)
                    else:
                        self.window.resize(1160, 780)
                except Exception:
                    pass
            elif target_mode == "hud":
                try:
                    self._pet_x = self.window.x
                    self._pet_y = self.window.y
                    screens = webview.screens
                    if screens:
                        s = screens[0]
                        hud_x = max(20, (s.width - 760) // 2)
                        hud_y = max(20, (s.height - 580) // 3)
                        self.window.resize(760, 580)
                        self.window.move(hud_x, hud_y)
                    else:
                        self.window.resize(760, 580)
                except Exception:
                    pass
            else:
                try:
                    self.window.resize(240, 280)
                    if hasattr(self, '_pet_x') and self._pet_x is not None:
                        self.window.move(self._pet_x, self._pet_y)
                except Exception:
                    pass
        return {"mode": self.current_mode}

    def get_system_locale(self) -> Dict[str, str]:
        """Detect system language locale for automatic translation."""
        import locale
        import subprocess
        try:
            proc = subprocess.run(["defaults", "read", "-g", "AppleLanguages"], capture_output=True, text=True, timeout=1)
            if proc.returncode == 0 and proc.stdout:
                m = re.search(r'"([a-z]{2})(?:-[A-Za-z]+)?"', proc.stdout)
                if m:
                    return {"locale": m.group(1).lower()}
        except Exception:
            pass

        try:
            loc = locale.getlocale()[0] or os.environ.get("LANG", "en")
            if loc:
                return {"locale": loc.split('_')[0].lower()}
        except Exception:
            pass
        return {"locale": "en"}

    def set_locale(self, lang_code: str) -> Dict[str, Any]:
        """Set active interface language."""
        self.locale = lang_code.lower()
        return {"locale": self.locale}

    def toggle_wandering(self) -> Dict[str, Any]:
        """Toggle Casper gently wandering / floating across the desktop."""
        if getattr(self, '_wandering', False):
            self._wandering = False
            return {"wandering": False}

        self._wandering = True
        import threading
        import time
        import math
        import random

        def _wander_loop():
            step = 0
            while getattr(self, '_wandering', False) and self.current_mode == "pet":
                try:
                    if self.window:
                        cur_x = self.window.x
                        cur_y = self.window.y
                        dx = int(math.sin(step * 0.1) * 3 + random.choice([-1, 0, 1]))
                        dy = int(math.cos(step * 0.08) * 3 + random.choice([-1, 0, 1]))
                        new_x = max(30, cur_x + dx)
                        new_y = max(30, cur_y + dy)
                        self.window.move(new_x, new_y)
                        step += 1
                except Exception:
                    break
                time.sleep(0.12)
            self._wandering = False

        t = threading.Thread(target=_wander_loop, daemon=True)
        t.start()
        return {"wandering": True}

    def quick_open_folder(self) -> Dict[str, Any]:
        """Quick 1-click open project folder in macOS Finder."""
        from ghost.core.agent import GhostOSAgent
        return GhostOSAgent.execute_intent("открой папку")

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

    # ==================== EXCLUSIVE KILLER SUITE ====================
    def ghostwrite(self, text: str, mode: str = "polish") -> Dict[str, Any]:
        """Ghostwriter: Inline text rewrite & transformation."""
        from ghost.core.ghostwriter import Ghostwriter
        return Ghostwriter(self.engine).rewrite_text(text, mode=mode)

    def ghostwrite_clipboard(self, mode: str = "polish") -> Dict[str, Any]:
        """Ghostwriter: Read clipboard, transform, and write back."""
        from ghost.core.ghostwriter import Ghostwriter
        return Ghostwriter(self.engine).rewrite_clipboard(mode=mode)

    def get_memory_vault_facts(self) -> Dict[str, Any]:
        """Memory Vault: Get all remembered cross-session user facts."""
        from ghost.core.memory_vault import MemoryVault
        return {"facts": MemoryVault().get_all_facts()}

    def add_memory_vault_fact(self, key: str, value: str, category: str = "general") -> Dict[str, Any]:
        """Memory Vault: Add or update a personal user fact."""
        from ghost.core.memory_vault import MemoryVault
        success = MemoryVault().remember(key, value, category)
        return {"success": success}

    def forget_memory_vault_fact(self, key: str) -> Dict[str, Any]:
        """Memory Vault: Delete a fact from long-term memory."""
        from ghost.core.memory_vault import MemoryVault
        success = MemoryVault().forget(key)
        return {"success": success}

    def get_daily_standup(self) -> Dict[str, Any]:
        """Daily Standup & Commit Crafter: Generate ready-to-share standup."""
        from ghost.core.time_machine import GhostTimeMachine
        return {"standup": GhostTimeMachine.generate_daily_standup()}

    def sandbox_check_command(self, command: str) -> Dict[str, Any]:
        """Terminal Sandbox Lens: Deep safety inspection of shell commands."""
        from ghost.core.lens import GhostLens
        return GhostLens.verify_and_patch(command)

    def set_skin(self, skin: str) -> Dict[str, Any]:
        """Changes the active Casper theme/skin."""
        self.skin = skin
        return {"success": True, "skin": skin}

    def clear_chat(self) -> Dict[str, Any]:
        """Clears active session memory and resets HUD chat."""
        return {"success": True}

    # ==================== GHOSTCODE & CHATGPT STUDIO METHODS ====================

    def get_coder(self):
        """Returns or initializes GhostCodeAgent."""
        if not hasattr(self, "_coder") or self._coder is None:
            from ghost.core.coder import GhostCodeAgent
            self._coder = GhostCodeAgent()
        return self._coder

    def get_workspace_info(self) -> Dict[str, Any]:
        """GhostCode: Return active workspace root, directory tree, and git status."""
        coder = self.get_coder()
        tree_res = coder.list_dir(max_depth=3)
        git = coder.git_status()
        tree = tree_res.get("tree", [])
        files = [item["path"] for item in tree if item.get("type") == "file"]
        return {
            "status": "ok",
            "success": True,
            "workspace": coder.workspace_dir,
            "tree": tree,
            "files": files,
            "git": git
        }

    def set_workspace_path(self, path: str) -> Dict[str, Any]:
        """GhostCode: Change active workspace directory."""
        res = self.get_coder().set_workspace(path)
        res["status"] = "ok" if res.get("success") else "error"
        return res

    def choose_workspace_folder(self) -> Dict[str, Any]:
        """GhostCode: Open native macOS folder chooser dialog to select workspace."""
        if self.window:
            try:
                import webview
                folders = self.window.create_file_dialog(webview.FOLDER_DIALOG)
                if folders and len(folders) > 0:
                    selected = folders[0]
                    self.get_coder().set_workspace(selected)
                    return {"status": "ok", "workspace": selected}
            except Exception as e:
                return {"status": "error", "error": str(e), "workspace": self.get_coder().workspace_dir}
        return {"status": "cancelled", "workspace": self.get_coder().workspace_dir}

    def run_code_task(self, prompt: str) -> Dict[str, Any]:
        """GhostCode: Execute autonomous software engineering task."""
        from ghost.core.rpg import CasperRPG
        res = self.get_coder().run_task(prompt)
        res["status"] = "ok" if res.get("success") else "error"
        CasperRPG.add_xp(35, "code_task")
        return res

    def read_code_file(self, relative_path: str) -> Dict[str, Any]:
        """GhostCode: Read file content for code editor / diff viewer."""
        res = self.get_coder().read_file(relative_path)
        res["status"] = "ok" if res.get("success") else "error"
        return res

    def save_code_file(self, relative_path: str, content: str) -> Dict[str, Any]:
        """GhostCode: Save edited file content from code editor."""
        res = self.get_coder().write_file(relative_path, content, overwrite=True)
        res["status"] = "ok" if res.get("success") else "error"
        res["bytes"] = res.get("bytes_written", len(content.encode("utf-8")))
        return res

    def scaffold_project_api(self, template: str, project_name: str) -> Dict[str, Any]:
        """GhostCode: Scaffold new project from template."""
        from ghost.core.rpg import CasperRPG
        res = self.get_coder().scaffold_project(template, project_name)
        res["status"] = "ok" if res.get("success") else "error"
        CasperRPG.add_xp(50, "scaffold")
        return res

    def get_git_details(self) -> Dict[str, Any]:
        """GhostCode: Get git branch and diff."""
        return self.get_coder().git_status()

    def run_studio_terminal(self, command: str) -> Dict[str, Any]:
        """GhostCode: Run shell command in workspace terminal."""
        res = self.get_coder().run_command(command)
        res["status"] = "ok" if res.get("success") else "error"
        res["output"] = res.get("stdout") or res.get("output", "")
        return res

    def get_saved_sessions(self) -> Dict[str, Any]:
        """ChatGPT Studio: Return list of saved chat and code sessions."""
        from ghost.config import GHOST_CACHE_DIR, ensure_dirs
        ensure_dirs()
        sessions_file = GHOST_CACHE_DIR / "studio_sessions.json"
        if not sessions_file.exists():
            return {"sessions": []}
        try:
            with open(sessions_file, "r", encoding="utf-8") as f:
                return {"sessions": json.load(f)}
        except Exception:
            return {"sessions": []}

    def save_studio_session(self, session_id: str, title: str, mode: str, messages: list) -> Dict[str, Any]:
        """ChatGPT Studio: Persist active chat/code session."""
        from ghost.config import GHOST_CACHE_DIR, ensure_dirs
        import time
        ensure_dirs()
        sessions_file = GHOST_CACHE_DIR / "studio_sessions.json"
        sessions = []
        if sessions_file.exists():
            try:
                with open(sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)
            except Exception:
                sessions = []

        existing = next((s for s in sessions if s.get("id") == session_id), None)
        if existing:
            existing["title"] = title
            existing["mode"] = mode
            existing["messages"] = messages
            existing["updated_at"] = int(time.time())
        else:
            sessions.insert(0, {
                "id": session_id,
                "title": title,
                "mode": mode,
                "messages": messages,
                "created_at": int(time.time()),
                "updated_at": int(time.time())
            })

        sessions = sessions[:50]
        try:
            with open(sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_studio_session(self, session_id: str) -> Dict[str, Any]:
        """ChatGPT Studio: Delete session by ID."""
        from ghost.config import GHOST_CACHE_DIR
        sessions_file = GHOST_CACHE_DIR / "studio_sessions.json"
        if not sessions_file.exists():
            return {"success": True}
        try:
            with open(sessions_file, "r", encoding="utf-8") as f:
                sessions = json.load(f)
            sessions = [s for s in sessions if s.get("id") != session_id]
            with open(sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
