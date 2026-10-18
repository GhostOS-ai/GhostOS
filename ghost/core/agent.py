"""
GhostOS Desktop & File System Agent
Executes system tasks (find files via Apple Spotlight mdfind, create folders, organize desktop)
with 0 MB extra RAM overhead using native OS calls.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

class GhostOSAgent:
    """
    Local OS task assistant for macOS file system operations.
    """

    @staticmethod
    def find_files(query: str, search_dir: Optional[str] = None, max_results: int = 15) -> List[Dict[str, Any]]:
        """
        Fast file search across macOS using Apple Spotlight indexer (mdfind).
        Runs in ~0.02s without scanning the disk manually.
        """
        target_dir = Path(search_dir).expanduser() if search_dir else Path.home()
        clean_query = query.strip()

        # Build mdfind command
        # E.g. mdfind -onlyin <dir> "kMDItemDisplayName == '*query*'c"
        escaped = clean_query.replace('"', '\\"')
        cmd = f'mdfind -onlyin "{target_dir}" "kMDItemDisplayName == \'*{escaped}*\'c"'

        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
            results = []
            if res.returncode == 0 and lines:
                for path_str in lines[:max_results]:
                    p = Path(path_str)
                    if p.exists():
                        results.append({
                            "name": p.name,
                            "path": str(p),
                            "is_dir": p.is_dir(),
                            "size_bytes": p.stat().st_size if not p.is_dir() else 0
                        })
                return results
        except Exception:
            pass

        # Fallback to standard fast os.walk
        results = []
        try:
            for root, _, files in os.walk(target_dir):
                if len(results) >= max_results:
                    break
                for f in files:
                    if clean_query.lower() in f.lower():
                        full_path = Path(root) / f
                        results.append({
                            "name": f,
                            "path": str(full_path),
                            "is_dir": False,
                            "size_bytes": full_path.stat().st_size
                        })
        except Exception:
            pass
        return results

    @staticmethod
    def create_folder(folder_path_str: str) -> Dict[str, Any]:
        """Safely create a folder anywhere in user directory."""
        path = Path(folder_path_str).expanduser()
        try:
            path.mkdir(parents=True, exist_ok=True)
            return {
                "success": True,
                "path": str(path),
                "message": f"📁 Folder successfully created at: {path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def organize_files(source_dir_str: str, pattern_ext: str, target_dir_str: str) -> Dict[str, Any]:
        """Move matching files from source folder into destination folder."""
        source = Path(source_dir_str).expanduser()
        target = Path(target_dir_str).expanduser()

        if not source.exists() or not source.is_dir():
            return {"success": False, "error": f"Source directory does not exist: {source}"}

        target.mkdir(parents=True, exist_ok=True)
        moved = []

        clean_ext = pattern_ext.lower().strip()
        if not clean_ext.startswith("."):
            clean_ext = "." + clean_ext

        for item in source.iterdir():
            if item.is_file() and item.suffix.lower() == clean_ext:
                dest = target / item.name
                shutil.move(str(item), str(dest))
                moved.append(item.name)

        return {
            "success": True,
            "moved_count": len(moved),
            "files": moved,
            "target_dir": str(target),
            "message": f"Organized {len(moved)} files into '{target.name}'"
        }

    @classmethod
    def execute_intent(cls, prompt: str) -> Dict[str, Any]:
        """
        Heuristic natural language parser for desktop actions.
        Matches intent without invoking heavy LLMs.
        """
        p = prompt.lower().strip()

        # 1. Intent: Find files
        # e.g.: "найди все pdf на рабочем столе", "find report.docx in downloads", "жұмыс үстелінен pdf тап"
        if any(trigger in p for trigger in ["найди", "поиск", "где лежит", "find files", "find file", "find", "search for", "search", "тап", "ізде", "查找", "搜索", "buscar"]):
            # Detect target folder
            search_folder = None
            if "рабоч" in p or "desktop" in p or "үстел" in p or "桌面" in p or "escritorio" in p:
                search_folder = str(Path.home() / "Desktop")
            elif "загруз" in p or "download" in p or "жүктеу" in p or "下载" in p or "descargas" in p:
                search_folder = str(Path.home() / "Downloads")
            elif "документ" in p or "document" in p or "құжат" in p or "文档" in p:
                search_folder = str(Path.home() / "Documents")

            # Extract search query
            clean = p
            for prefix in ["найди все файлы", "найди файлы", "найди файл", "найди все", "найди", "поиск", "где лежит", 
                           "find files", "find file", "find", "search for", "search", "ізде", "查找", "搜索", "buscar"]:
                if clean.startswith(prefix):
                    clean = clean[len(prefix):].strip()
                    break

            # Strip trailing verbs (for SOV languages like Kazakh: "pdf файлдарын тап", "файлдарды тап")
            for suffix in ["файлдарды тап", "файлдарды ізде", "файлды тап", "файл тап", "тап", "ізде"]:
                if clean.endswith(suffix):
                    clean = clean[:-len(suffix)].strip()
                    break

            query = re.sub(r'\s*(на рабочем столе|в загрузках|в документах|on desktop|in downloads|жұмыс үстелінен|жүктеулерден)\s*', '', clean).strip()
            if not query:
                query = "pdf"

            files = cls.find_files(query, search_dir=search_folder)
            if not files:
                return {
                    "handled": True,
                    "action": "find_files",
                    "output": f"🔍 Ничего не найдено по запросу `{query}` в {search_folder or 'домашней папке'}."
                }

            lines = [f"🔍 **Найдено файлов: {len(files)}**\n"]
            for f in files[:8]:
                size_kb = round(f["size_bytes"] / 1024, 1)
                lines.append(f"• `{f['name']}` ({size_kb} KB) — `{f['path']}`")

            return {
                "handled": True,
                "action": "find_files",
                "output": "\n".join(lines),
                "results": files
            }

        # 2. Intent: Create folder
        # e.g.: "создай папку Проект в Загрузках", "create folder Test on desktop", "папка жаса"
        if any(trigger in p for trigger in ["создай папку", "сделай директорию", "create folder", "make folder", "mkdir", "папка жаса", "бума жаса", "新建文件夹", "创建文件夹", "crear carpeta"]):
            match = re.search(r'(создай папку|сделай директорию|create folder|make folder|mkdir|папка жаса|бума жаса|新建文件夹|创建文件夹|crear carpeta)\s+([^\s]+)', p)
            folder_name = match.group(2) if match else "New_Folder"

            base_dir = Path.home()
            if "загруз" in p or "download" in p or "жүктеу" in p or "下载" in p:
                base_dir = Path.home() / "Downloads"
            elif "рабоч" in p or "desktop" in p or "үстел" in p or "桌面" in p:
                base_dir = Path.home() / "Desktop"
            elif "документ" in p or "document" in p:
                base_dir = Path.home() / "Documents"

            target_path = base_dir / folder_name
            res = cls.create_folder(str(target_path))
            return {
                "handled": True,
                "action": "create_folder",
                "output": f"📁 Папка создана: `{target_path}`" if res["success"] else f"Ошибка: {res['error']}"
            }

        # 3. Intent: Organize files
        # e.g.: "перемести скриншоты в папку Скрины на рабочем столе"
        if any(w in p for w in ["перемести", "organize", "move", "жылжыт", "移动"]):
            if "скриншот" in p or "screenshot" in p or "png" in p:
                desktop = Path.home() / "Desktop"
                target = desktop / "Screenshots"
                res = cls.organize_files(str(desktop), ".png", str(target))
                return {
                    "handled": True,
                    "action": "organize_files",
                    "output": f"📦 Перемещено {res['moved_count']} скриншотов в `{target}`."
                }

        # 4. Intent: Open Folder in Finder
        # e.g.: "открой папку", "открой загрузки", "открой рабочий стол", "open downloads", "папканы аш"
        if any(trigger in p for trigger in ["открой папку", "открой директорию", "открой finder", "открой загрузки", "открой рабочий", "открой проекты", 
                                            "open folder", "open directory", "open downloads", "open desktop", "open finder", "open project",
                                            "папканы аш", "жүктеулерді аш", "打开文件夹", "打开访达", "abrir carpeta"]):
            target_path = Path.home()
            folder_title = "домашнюю папку"

            if "загруз" in p or "download" in p:
                target_path = Path.home() / "Downloads"
                folder_title = "Загрузки"
            elif "рабоч" in p or "desktop" in p:
                target_path = Path.home() / "Desktop"
                folder_title = "Рабочий стол"
            elif "документ" in p or "document" in p:
                target_path = Path.home() / "Documents"
                folder_title = "Документы"
            elif "проект" in p or "project" in p:
                target_path = Path.home() / "Downloads" / "Мой проект"
                folder_title = "Мой проект"
            elif "finder" in p:
                target_path = Path.home()
                folder_title = "Finder"
            else:
                # Check if specific folder name followed
                match = re.search(r'(открой папку|открой)\s+([^\s]+)', p)
                if match:
                    specific = match.group(2)
                    candidate = Path.home() / specific
                    if candidate.exists():
                        target_path = candidate
                        folder_title = specific
                    else:
                        target_path = Path.cwd()
                        folder_title = target_path.name
                else:
                    target_path = Path.cwd()
                    folder_title = target_path.name

            try:
                import sys
                if sys.platform == "darwin":
                    subprocess.run(f"open '{target_path}'", shell=True, check=True)
                elif sys.platform == "win32":
                    os.startfile(str(target_path))
                else:
                    subprocess.run(["xdg-open", str(target_path)], check=True)
                return {
                    "handled": True,
                    "action": "open_folder",
                    "output": f"📂 Открыл {folder_title} (`{target_path}`)!"
                }
            except Exception as e:
                return {
                    "handled": True,
                    "action": "open_folder",
                    "output": f"Не удалось открыть папку: {e}"
                }

        return {"handled": False}
