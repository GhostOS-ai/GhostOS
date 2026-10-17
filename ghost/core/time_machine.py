"""
GhostOS Time Machine
Lightweight session journal that reconstructs daily work context and generates
instant git commit messages without heavy background tracking.
"""
import os
import datetime
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

class GhostTimeMachine:
    """
    Analyzes local developer activity, modified files, and git diffs
    to provide session recall and automated summaries.
    """

    @staticmethod
    def get_git_status(repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Fetch git status and list of modified/untracked files."""
        cwd = repo_path or os.getcwd()
        try:
            res = subprocess.run(
                "git status --porcelain",
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=3
            )
            if res.returncode != 0:
                return {"is_git": False, "files": [], "error": "Not a git repository."}

            files = []
            for line in res.stdout.splitlines():
                if len(line) >= 4:
                    status = line[:2].strip()
                    file_path = line[3:].strip()
                    files.append({"status": status, "file": file_path})

            return {"is_git": True, "files": files, "raw": res.stdout.strip()}
        except Exception as e:
            return {"is_git": False, "files": [], "error": str(e)}

    @staticmethod
    def get_recent_diff(repo_path: Optional[str] = None) -> str:
        """Fetch current git diff (staged or unstaged)."""
        cwd = repo_path or os.getcwd()
        try:
            res = subprocess.run(
                "git diff --stat && git diff -U2",
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=5
            )
            return res.stdout.strip()
        except Exception:
            return ""

    @classmethod
    def generate_session_summary(cls, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate a concise breakdown of what was worked on recently."""
        status = cls.get_git_status(repo_path)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        if not status["is_git"]:
            return {
                "timestamp": timestamp,
                "summary": "No active Git repository detected in the current directory.",
                "files_count": 0,
                "commit_suggestion": None
            }

        files = status["files"]
        if not files:
            return {
                "timestamp": timestamp,
                "summary": "Working tree clean. All changes have been committed.",
                "files_count": 0,
                "commit_suggestion": None
            }

        # Categorize changes
        modified = [f["file"] for f in files if "M" in f["status"]]
        added = [f["file"] for f in files if "A" in f["status"] or "?" in f["status"]]
        deleted = [f["file"] for f in files if "D" in f["status"]]

        summary_lines = [f"🕒 **Session Snapshot ({timestamp})**\n"]
        if modified:
            summary_lines.append(f"• **Modified:** {', '.join(modified[:5])}")
        if added:
            summary_lines.append(f"• **New Files:** {', '.join(added[:5])}")
        if deleted:
            summary_lines.append(f"• **Deleted:** {', '.join(deleted[:5])}")

        # Smart commit message suggestion
        commit_type = "feat" if added else ("fix" if any("fix" in f.lower() or "bug" in f.lower() for f in modified) else "refactor")
        scope = modified[0].split("/")[0] if modified and "/" in modified[0] else "core"
        commit_suggestion = f"{commit_type}({scope}): update {len(files)} files and polish implementation"

        return {
            "timestamp": timestamp,
            "summary": "\n".join(summary_lines),
            "files_count": len(files),
            "files": files,
            "commit_suggestion": commit_suggestion
        }
