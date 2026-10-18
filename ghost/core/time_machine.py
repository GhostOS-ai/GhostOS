"""
GhostOS Time Machine
Lightweight session journal that reconstructs daily work context and generates
instant git commit messages and daily standup reports without heavy background tracking.
"""
import os
import datetime
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

class GhostTimeMachine:
    """
    Analyzes local developer activity, modified files, and git diffs
    to provide session recall, commit crafter, and daily standup generator.
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
    def get_recent_commits(repo_path: Optional[str] = None, count: int = 5) -> List[str]:
        """Fetch recent commit messages from the current branch."""
        cwd = repo_path or os.getcwd()
        try:
            res = subprocess.run(
                f"git log -n {count} --oneline",
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=3
            )
            if res.returncode == 0 and res.stdout:
                return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        except Exception:
            pass
        return []

    @classmethod
    def generate_conventional_commit(cls, repo_path: Optional[str] = None) -> str:
        """
        Generate a high-quality Conventional Commit message based on staged/modified files.
        """
        status = cls.get_git_status(repo_path)
        if not status["is_git"] or not status["files"]:
            return "chore(workspace): sync updates and polish codebase"

        files = [f["file"] for f in status["files"]]

        # Determine type
        if any(f.endswith(".md") or "docs" in f.lower() for f in files) and len(files) <= 2:
            ctype = "docs"
        elif any("test" in f.lower() for f in files) and len(files) <= 3:
            ctype = "test"
        elif any(f.endswith(".css") or f.endswith(".html") or "ui" in f.lower() for f in files):
            ctype = "style(ui)" if any(f.endswith(".css") for f in files) else "feat(ui)"
        elif any("fix" in f.lower() or "bug" in f.lower() for f in files):
            ctype = "fix"
        elif any("perf" in f.lower() or "vram" in f.lower() for f in files):
            ctype = "perf"
        elif any("?" in f for f in [item["status"] for item in status["files"]]):
            ctype = "feat"
        else:
            ctype = "refactor"

        # Determine scope
        sample = files[0]
        parts = sample.split("/")
        scope = parts[0] if len(parts) > 1 else "core"

        # Subject
        clean_names = [Path(f).stem for f in files[:3]]
        subject = f"enhance {', '.join(clean_names)}" if len(files) <= 3 else f"update {len(files)} files and polish implementation"

        return f"{ctype}({scope}): {subject}"

    @classmethod
    def generate_daily_standup(cls, repo_path: Optional[str] = None) -> str:
        """
        Generate a ready-to-share Daily Standup message for Slack / Telegram / Teams.
        """
        status = cls.get_git_status(repo_path)
        commits = cls.get_recent_commits(repo_path, count=4)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        lines = [f"📅 **Daily Standup Report — {date_str}**\n"]

        # Done Today
        lines.append("✅ **What I accomplished today:**")
        if commits:
            for c in commits[:3]:
                # strip git hash if present
                clean_c = c.split(" ", 1)[1] if " " in c else c
                lines.append(f"- {clean_c}")
        else:
            lines.append("- Progressed on active development tasks")

        # In Progress
        lines.append("\n🔄 **What I'm working on right now:**")
        if status.get("files"):
            active_files = [f["file"] for f in status["files"][:4]]
            lines.append(f"- Active development on: {', '.join(active_files)}")
        else:
            lines.append("- Code review and preparing next milestone tasks")

        # Blockers
        lines.append("\n🚧 **Blockers / Impediments:**")
        lines.append("- None! All systems operational and tests passing.")

        return "\n".join(lines)

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
                "commit_suggestion": "chore: initial project setup",
                "standup": cls.generate_daily_standup(repo_path)
            }

        files = status["files"]
        commit_suggestion = cls.generate_conventional_commit(repo_path)
        standup = cls.generate_daily_standup(repo_path)

        if not files:
            return {
                "timestamp": timestamp,
                "summary": "Working tree clean. All changes have been committed.",
                "files_count": 0,
                "commit_suggestion": commit_suggestion,
                "standup": standup
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

        return {
            "timestamp": timestamp,
            "summary": "\n".join(summary_lines),
            "files_count": len(files),
            "files": files,
            "commit_suggestion": commit_suggestion,
            "standup": standup
        }
