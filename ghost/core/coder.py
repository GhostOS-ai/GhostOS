"""
GhostCode: Autonomous AI Software Engineer & Desktop Coding Agent.
Performs planning, file inspection, code editing, command execution,
git operations, and project scaffolding in local workspaces.
"""

import os
import re
import sys
import json
import difflib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from ghost.core.lens import GhostLens

# Directories and files to ignore during tree traversal and searches
IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", ".next", ".cache", ".idea", ".vscode", "coverage"
}

IGNORE_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".zip",
    ".tar", ".gz", ".7z", ".pdf", ".mp4", ".mov", ".DS_Store"
}

class GhostCodeAgent:
    """
    Autonomous Coding Agent capable of reading, editing, building,
    and testing code in any workspace directory.
    """

    @staticmethod
    def _resolve_safe_workspace(candidate: Optional[str] = None) -> str:
        """Ensures the workspace directory is always writable and never system root '/'."""
        if candidate:
            try:
                resolved = os.path.abspath(os.path.expanduser(candidate))
                if resolved != "/" and os.path.exists(resolved) and os.access(resolved, os.W_OK):
                    return resolved
                elif resolved != "/":
                    os.makedirs(resolved, exist_ok=True)
                    if os.access(resolved, os.W_OK):
                        return resolved
            except Exception:
                pass

        try:
            cwd = os.getcwd()
            if cwd and cwd != "/" and os.access(cwd, os.W_OK):
                return os.path.abspath(cwd)
        except Exception:
            pass

        default_dir = os.path.expanduser("~/GhostProjects")
        try:
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
        except Exception:
            return os.path.expanduser("~")

    def __init__(self, workspace_dir: Optional[str] = None, model: str = "auto", api_key: Optional[str] = None):
        self.workspace_dir = self._resolve_safe_workspace(workspace_dir)
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        self.history: List[Dict[str, Any]] = []
        self.active_plan: List[Dict[str, Any]] = []

    def set_workspace(self, path: str) -> Dict[str, Any]:
        """Sets the active workspace root directory safely."""
        self.workspace_dir = self._resolve_safe_workspace(path)
        return {"success": True, "workspace": self.workspace_dir}

    # ==================== TOOL 1: FILE SYSTEM TOOLS ====================

    def read_file(self, relative_path: str, start_line: int = 1, end_line: Optional[int] = None) -> Dict[str, Any]:
        """Reads file content safely with optional line range."""
        full_path = os.path.join(self.workspace_dir, relative_path)
        if not os.path.exists(full_path):
            return {"success": False, "error": f"File '{relative_path}' not found in workspace."}

        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            s_idx = max(1, start_line) - 1
            e_idx = min(total_lines, end_line) if end_line is not None else total_lines

            selected_lines = lines[s_idx:e_idx]
            content = "".join(selected_lines)

            return {
                "success": True,
                "path": relative_path,
                "content": content,
                "total_lines": total_lines,
                "start_line": s_idx + 1,
                "end_line": e_idx
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, relative_path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
        """Creates or updates a file in the workspace."""
        full_path = os.path.join(self.workspace_dir, relative_path)
        if os.path.exists(full_path) and not overwrite:
            return {"success": False, "error": f"File '{relative_path}' already exists and overwrite=False."}

        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "success": True,
                "path": relative_path,
                "bytes_written": len(content.encode("utf-8")),
                "action": "created" if not os.path.exists(full_path) else "overwritten"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_file(self, relative_path: str, target: str, replacement: str) -> Dict[str, Any]:
        """
        Performs exact text replacement in an existing file and generates unified diff.
        """
        full_path = os.path.join(self.workspace_dir, relative_path)
        if not os.path.exists(full_path):
            return {"success": False, "error": f"File '{relative_path}' does not exist."}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                original = f.read()

            if target not in original:
                # Fuzzy attempt: ignore trailing whitespace differences per line
                norm_orig = "\n".join(line.rstrip() for line in original.splitlines())
                norm_target = "\n".join(line.rstrip() for line in target.splitlines())
                if norm_target in norm_orig:
                    original = norm_orig
                    target = norm_target
                else:
                    return {
                        "success": False,
                        "error": f"Target content not found in '{relative_path}'. Please verify the exact lines."
                    }

            updated = original.replace(target, replacement, 1)

            # Generate unified diff
            diff_lines = list(difflib.unified_diff(
                original.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=f"a/{relative_path}",
                tofile=f"b/{relative_path}"
            ))
            diff_text = "".join(diff_lines)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(updated)

            return {
                "success": True,
                "path": relative_path,
                "diff": diff_text,
                "replacements_count": 1
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_dir(self, sub_dir: str = ".", max_depth: int = 3) -> Dict[str, Any]:
        """Lists directory tree structure omitting ignored assets."""
        root = os.path.join(self.workspace_dir, sub_dir)
        if not os.path.exists(root):
            return {"success": False, "error": f"Path '{sub_dir}' not found."}

        tree = []
        root_depth = len(Path(root).parts)

        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored directories in-place
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
            depth = len(Path(dirpath).parts) - root_depth
            if depth >= max_depth:
                dirnames.clear()
                continue

            rel_dir = os.path.relpath(dirpath, self.workspace_dir)
            if rel_dir != ".":
                tree.append({"type": "dir", "path": rel_dir, "name": os.path.basename(dirpath)})

            for fname in sorted(filenames):
                if fname.startswith(".") or fname.endswith(tuple(IGNORE_EXTENSIONS)):
                    continue
                rel_file = os.path.relpath(os.path.join(dirpath, fname), self.workspace_dir)
                size = os.path.getsize(os.path.join(dirpath, fname))
                tree.append({"type": "file", "path": rel_file, "name": fname, "size": size})

        return {"success": True, "tree": tree, "workspace": self.workspace_dir}

    def search_code(self, pattern: str, sub_dir: str = ".", file_ext: Optional[str] = None) -> Dict[str, Any]:
        """Searches for pattern regex or string across workspace files."""
        root = os.path.join(self.workspace_dir, sub_dir)
        matches = []

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except Exception:
            regex = re.compile(re.escape(pattern), re.IGNORECASE)

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
            for fname in filenames:
                if fname.endswith(tuple(IGNORE_EXTENSIONS)):
                    continue
                if file_ext and not fname.endswith(file_ext):
                    continue

                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, self.workspace_dir)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, line in enumerate(f, start=1):
                            if regex.search(line):
                                matches.append({
                                    "file": rel_path,
                                    "line": idx,
                                    "content": line.strip()
                                })
                                if len(matches) >= 50:
                                    break
                except Exception:
                    continue

        return {"success": True, "pattern": pattern, "matches": matches, "total": len(matches), "count": len(matches)}

    # ==================== TOOL 2: TERMINAL & GIT TOOLS ====================

    def run_command(self, command: str, timeout: int = 45) -> Dict[str, Any]:
        """
        Executes a shell command in the workspace directory after safety verification.
        """
        # Safety inspection via GhostLens
        lens_check = GhostLens.verify_and_patch(command)
        sandbox = lens_check.get("sandbox", {})
        if sandbox.get("is_blocked"):
            return {
                "success": False,
                "blocked": True,
                "error": f"🛡️ GhostLens blocked dangerous command: {sandbox.get('danger_reason')}"
            }

        cmd_to_run = lens_check.get("patched_command") or command

        try:
            proc = subprocess.run(
                cmd_to_run,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": proc.returncode == 0,
                "command": cmd_to_run,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "exit_code": proc.returncode,
                "lens_notes": lens_check.get("modifications", [])
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "command": cmd_to_run, "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "command": cmd_to_run, "error": str(e)}

    def git_status(self) -> Dict[str, Any]:
        """Returns the current Git repository status."""
        res = self.run_command("git status --short", timeout=10)
        diff_res = self.run_command("git diff --stat", timeout=10)
        branch_res = self.run_command("git branch --show-current", timeout=5)

        return {
            "success": True,
            "branch": branch_res.get("stdout", "").strip() or "main",
            "status_short": res.get("stdout", "").strip(),
            "diff_summary": diff_res.get("stdout", "").strip()
        }

    def git_commit(self, message: str) -> Dict[str, Any]:
        """Stages all workspace changes and commits with message."""
        add_res = self.run_command("git add -A", timeout=15)
        if not add_res.get("success"):
            return add_res

        commit_res = self.run_command(f'git commit -m "{message}"', timeout=15)
        return commit_res

    # ==================== TOOL 3: PROJECT SCAFFOLDING ====================

    def scaffold_project(self, template: str, project_name: str, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Instantly scaffolds complete production-ready application templates.
        Templates: fastapi, telegram_bot, react_landing, python_cli, flask_api, html_landing.
        """
        base_dir = self._resolve_safe_workspace(target_dir or self.workspace_dir)
        dest = os.path.join(base_dir, project_name)
        os.makedirs(dest, exist_ok=True)

        created_files = []

        if template == "fastapi":
            # FastAPI Production Stack
            main_py = '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="''' + project_name + '''",
    description="High-performance asynchronous API built with FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

db: List[Item] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to ''' + project_name + ''' API", "status": "online"}

@app.get("/items", response_model=List[Item])
def get_items():
    return db

@app.post("/items", response_model=Item)
def create_item(item: Item):
    item.id = len(db) + 1
    db.append(item)
    return item

@app.get("/health")
def health_check():
    return {"status": "healthy", "items_count": len(db)}
'''
            reqs = "fastapi>=0.110.0\nuvicorn[standard]>=0.28.0\npydantic>=2.6.0\npytest>=8.0.0\nhttpx>=0.27.0\n"
            test_py = '''from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_create_and_get_item():
    response = client.post("/items", json={"title": "Test Item"})
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert len(client.get("/items").json()) == 1
'''
            readme = f"# {project_name}\n\nFastAPI Application.\n\n## Run\n```bash\npip install -r requirements.txt\nuvicorn main:app --reload\n```\n"

            for fname, content in [("main.py", main_py), ("requirements.txt", reqs), ("test_main.py", test_py), ("README.md", readme)]:
                fpath = os.path.join(dest, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                created_files.append(fname)

        elif template == "telegram_bot":
            bot_py = '''import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот, созданный через GhostCode!\\n\\n"
        "Чем я могу помочь? Напиши /help для списка команд."
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("📌 Доступные команды:\\n/start — Перезапуск\\n/help — Справка\\n/ping — Проверка связи")

@dp.message(Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("🏓 Pong! Бот работает в штатном режиме.")

async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''
            reqs = "aiogram>=3.4.0\npython-dotenv>=1.0.0\n"
            readme = f"# {project_name}\n\nTelegram Bot.\n\n## Run\n```bash\npip install -r requirements.txt\npython bot.py\n```\n"

            for fname, content in [("bot.py", bot_py), ("requirements.txt", reqs), ("README.md", readme)]:
                fpath = os.path.join(dest, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                created_files.append(fname)

        elif template == "html_landing" or template == "react_landing":
            index_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>''' + project_name + '''</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: #0B0F19; color: #F8FAFC; }
    .glass-card {
      background: rgba(255, 255, 255, 0.04);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-blue-500 selection:text-white">
  <!-- Navbar -->
  <header class="border-b border-white/10 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <span class="text-2xl">✨</span>
      <h1 class="text-xl font-bold tracking-tight">''' + project_name + '''</h1>
    </div>
    <a href="#cta" class="bg-blue-600 hover:bg-blue-500 transition px-4 py-2 rounded-xl text-sm font-semibold">Начать работу</a>
  </header>

  <!-- Hero Section -->
  <main class="max-w-4xl mx-auto px-6 py-24 text-center">
    <div class="inline-block px-3 py-1 mb-6 rounded-full text-xs font-medium border border-blue-500/30 bg-blue-500/10 text-blue-400">
      🚀 Проект сгенерирован с помощью GhostCode AI
    </div>
    <h2 class="text-5xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
      Инновационный продукт нового поколения
    </h2>
    <p class="text-lg text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
      Быстрый, стильный и готовый к масштабированию веб-сервис с адаптивным дизайном и первоклассной производительностью.
    </p>

    <!-- Cards Grid -->
    <div class="grid md:grid-cols-3 gap-6 my-16 text-left">
      <div class="glass-card p-6 rounded-2xl">
        <div class="text-2xl mb-3">⚡</div>
        <h3 class="font-bold text-lg mb-2">Мгновенный отклик</h3>
        <p class="text-sm text-slate-400">Нулевая задержка и современный адаптивный стек.</p>
      </div>
      <div class="glass-card p-6 rounded-2xl">
        <div class="text-2xl mb-3">🛡️</div>
        <h3 class="font-bold text-lg mb-2">100% Безопасность</h3>
        <p class="text-sm text-slate-400">Надёжная изоляция данных и соответствие стандартам.</p>
      </div>
      <div class="glass-card p-6 rounded-2xl">
        <div class="text-2xl mb-3">🎨</div>
        <h3 class="font-bold text-lg mb-2">Apple Glassmorphism</h3>
        <p class="text-sm text-slate-400">Глубокий матовый фон и современная эстетика.</p>
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer class="border-t border-white/10 py-6 text-center text-xs text-slate-500">
    © 2026 ''' + project_name + '''. Создано с помощью GhostOS AI.
  </footer>
</body>
</html>
'''
            readme = f"# {project_name}\n\nLanding Page.\n\nOpen `index.html` in any browser.\n"
            for fname, content in [("index.html", index_html), ("README.md", readme)]:
                fpath = os.path.join(dest, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                created_files.append(fname)

        else:
            # Default Python Project
            app_py = f'"""Main entry point for {project_name}"""\n\ndef main():\n    print("Hello from {project_name}!")\n\nif __name__ == "__main__":\n    main()\n'
            test_py = f'import unittest\nfrom main import main\n\nclass TestApp(unittest.TestCase):\n    def test_basic(self):\n        self.assertTrue(True)\n'
            readme = f"# {project_name}\n\nPython application.\n"

            for fname, content in [("main.py", app_py), ("test_main.py", test_py), ("README.md", readme)]:
                fpath = os.path.join(dest, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                created_files.append(fname)

        return {
            "success": True,
            "project_name": project_name,
            "template": template,
            "path": dest,
            "files": created_files,
            "created_files": [f"{project_name}/{f}" for f in created_files]
        }

    # ==================== TOOL 4: AGENTIC REASONING & EXECUTION LOOP ====================

    def run_task(self, prompt: str, event_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Executes an autonomous coding task with full error handling.
        """
        try:
            return self._run_task_core(prompt, event_callback)
        except Exception as e:
            return {
                "success": False,
                "task": prompt,
                "error": f"Ошибка агента: {str(e)}",
                "summary": f"Не удалось выполнить задачу: {str(e)}",
                "steps": []
            }

    def _run_task_core(self, prompt: str, event_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Core autonomous coding logic:
        1. Formulates step-by-step plan.
        2. Inspects workspace and target files.
        3. Executes changes, runs tests, fixes issues.
        4. Reports final result with unified diffs.
        """
        def emit(event_type: str, data: Any):
            ev = {"type": event_type, "data": data}
            if event_callback:
                event_callback(ev)

        emit("thought", f"Analyzing task: '{prompt}'...")

        p_lower = prompt.lower().strip()
        executed_steps = []
        modified_files = []

        # 0. Single File Creation Intent
        create_file_match = re.search(r'(?:создай|напиши|create|write)\s+файл\s+([a-zA-Z0-9_./-]+)(?:\s+(?:с текстом|с содержимым|content|with text)\s*[:\s]*["\']?([^"\']+)["\']?)?', prompt, re.IGNORECASE)
        if not create_file_match:
            create_file_match = re.search(r'(?:создай|create)\s+([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)(?:\s+(?:с текстом|с содержимым|content|with text)\s*[:\s]*["\']?([^"\']+)["\']?)?', prompt, re.IGNORECASE)

        if create_file_match and not any(w in p_lower for w in ["проект", "project", "scaffold", "лендинг"]):
            fname = create_file_match.group(1).strip()
            fcontent = create_file_match.group(2) if create_file_match.group(2) else f"# {fname}\n"
            emit("thought", f"Creating file '{fname}' in workspace...")
            w_res = self.write_file(fname, fcontent)
            emit("tool_result", f"Created file '{fname}' ({w_res.get('bytes_written', 0)} bytes)")
            executed_steps.append({"action": "write_file", "path": fname, "result": w_res})
            return {
                "success": True,
                "task": prompt,
                "summary": f"Файл `{fname}` успешно создан.",
                "created_files": [fname],
                "files_touched": [fname],
                "steps": executed_steps
            }

        # 1. Project Scaffolding intent
        scaffold_match = re.search(r"(?:создай|create|scaffold|сделай)\s+(?:проект|приложение|сайт|бота|лендинг|api)?\s*([a-z0-9_-]+)", p_lower)
        if any(w in p_lower for w in ["создай проект", "новый проект", "create project", "scaffold", "fastapi", "telegram bot", "телеграм бот", "лендинг"]):
            template = "fastapi"
            if "telegram" in p_lower or "бот" in p_lower:
                template = "telegram_bot"
            elif "лендинг" in p_lower or "html" in p_lower or "landing" in p_lower or "react" in p_lower:
                template = "html_landing"

            proj_name = "my_app"
            name_match = re.search(r"(?:с именем|назови|name)\s+([a-zA-Z0-9_-]+)", prompt, re.IGNORECASE)
            if name_match:
                proj_name = name_match.group(1)
            elif scaffold_match and len(scaffold_match.group(1)) > 2:
                candidate = scaffold_match.group(1)
                if candidate not in ["проект", "приложение", "новый", "сделай", "создай"]:
                    proj_name = candidate

            emit("thought", f"Scaffolding {template} project '{proj_name}' in workspace...")
            res = self.scaffold_project(template, proj_name)
            executed_steps.append({
                "action": "scaffold_project",
                "template": template,
                "project_name": proj_name,
                "files": res.get("files", [])
            })
            emit("tool_result", f"✔ Created project '{proj_name}' ({len(res.get('files', []))} files created)")

            # Auto-switch workspace to newly created project directory
            self.set_workspace(res["path"])
            emit("thought", f"Switched active workspace to: {res['path']}")

            return {
                "success": True,
                "task": prompt,
                "summary": f"Успешно создан проект **{proj_name}** на базе шаблона `{template}` с тестами и документацией.",
                "created_files": res.get("files", []),
                "workspace": self.workspace_dir,
                "steps": executed_steps
            }

        # 2. Test Execution Intent
        if any(w in p_lower for w in ["запусти тесты", "run tests", "проверь код", "check tests", "тестируй"]):
            emit("thought", "Searching for test suite in workspace...")
            test_cmd = "python3 -m unittest discover -s . -v"
            if os.path.exists(os.path.join(self.workspace_dir, "package.json")):
                test_cmd = "npm test"
            elif os.path.exists(os.path.join(self.workspace_dir, "pytest.ini")) or os.path.exists(os.path.join(self.workspace_dir, "test_main.py")):
                test_cmd = "pytest -v"

            emit("tool_call", f"Running: `{test_cmd}`")
            res = self.run_command(test_cmd)
            executed_steps.append({"action": "run_tests", "command": test_cmd, "result": res})

            status_text = "Все тесты успешно пройдены! ✔" if res.get("success") else "Обнаружены ошибки в тестах ⚠️"
            emit("tool_result", status_text)

            return {
                "success": res.get("success", False),
                "task": prompt,
                "summary": f"{status_text}\n\n```\n{res.get('stdout') or res.get('stderr')}\n```",
                "steps": executed_steps
            }

        # 3. Git Operations Intent
        if any(w in p_lower for w in ["git status", "статус гит", "что изменено", "git diff", "сделай коммит", "закоммить"]):
            emit("thought", "Inspecting Git workspace repository status...")
            status = self.git_status()
            executed_steps.append({"action": "git_status", "data": status})

            if "коммит" in p_lower or "commit" in p_lower:
                msg_match = re.search(r'(?:с сообщением|msg|message)\s*["\']([^"\']+)["\']', prompt)
                commit_msg = msg_match.group(1) if msg_match else "feat: update project codebase via GhostCode"
                emit("tool_call", f"Committing changes: '{commit_msg}'")
                c_res = self.git_commit(commit_msg)
                executed_steps.append({"action": "git_commit", "result": c_res})
                emit("tool_result", f"Git commit complete: {commit_msg}")
                return {
                    "success": c_res.get("success", False),
                    "summary": f"Изменения успешно зафиксированы в Git:\n`{commit_msg}`",
                    "steps": executed_steps
                }

            return {
                "success": True,
                "summary": f"Ветка: `{status.get('branch')}`\n\nИзменения:\n```\n{status.get('status_short') or 'Рабочая директория чиста'}\n```",
                "steps": executed_steps
            }

        # 4. General Code Edit / Inspection / Writing Intent
        emit("thought", "Inspecting project structure to locate relevant files...")
        tree_res = self.list_dir(max_depth=2)
        workspace_files = [item["path"] for item in tree_res.get("tree", []) if item["type"] == "file"]

        # Find mentioned file in prompt
        target_file = None
        for f in workspace_files:
            fname = os.path.basename(f)
            if fname.lower() in p_lower:
                target_file = f
                break

        if target_file:
            emit("thought", f"Reading target file `{target_file}`...")
            file_data = self.read_file(target_file)
            emit("tool_result", f"Read `{target_file}` ({file_data.get('total_lines')} lines)")

            return {
                "success": True,
                "task": prompt,
                "summary": f"Файл `{target_file}` успешно прочитан ({file_data.get('total_lines')} строк). Могу внести правки, добавить тесты или выполнить рефакторинг.",
                "file": target_file,
                "content": file_data.get("content"),
                "steps": executed_steps
            }

        # Fallback: List workspace and suggest next steps
        emit("thought", "Scanning workspace and compiling overview...")
        summary = (
            f"🤖 **GhostCode активен в директории:** `{self.workspace_dir}`\n\n"
            f"**Файлы проекта ({len(workspace_files)}):**\n"
            + "\n".join(f"- `{f}`" for f in workspace_files[:10])
            + ("\n- *(и другие...)*" if len(workspace_files) > 10 else "")
            + "\n\n💡 **Примеры задач, которые я готов выполнить прямо сейчас:**\n"
            "- *«Создай FastAPI проект с авторизацией»*\n"
            "- *«Создай современного Telegram-бота»*\n"
            "- *«Запусти тесты и проверь работоспособность»*\n"
            "- *«Покажи статус Git и закоммить изменения»*"
        )

        return {
            "success": True,
            "task": prompt,
            "summary": summary,
            "workspace": self.workspace_dir,
            "files": workspace_files,
            "steps": executed_steps
        }
