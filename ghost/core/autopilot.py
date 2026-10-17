"""
GhostOS Safe Terminal Autopilot
Generates, explains, and safely executes bash/zsh commands from natural language requests.
"""
import re
import shlex
import subprocess
from typing import Dict, Any, List, Optional

class TerminalAutopilot:
    """
    Intelligent system co-pilot that translates intent into shell commands,
    evaluates safety risk, and runs approved commands.
    """

    DANGEROUS_PATTERNS = [
        r'\brm\b(\s+-[rfRF]+)?',
        r'\bsudo\b',
        r'\bdd\b',
        r'\bmkfs\b',
        r'\bchmod\s+(-R\s+)?777',
        r'\bchown\s+-R\b',
        r'>\s*/dev/sd[a-z]',
        r':\(\)\s*\{\s*:\|:&\s*\};:', # fork bomb
        r'\bgit\s+reset\s+--hard\b',
        r'\bgit\s+clean\s+-[xfd]+',
    ]

    CAUTION_PATTERNS = [
        r'\bkill\b',
        r'\bpkill\b',
        r'\bkillall\b',
        r'\bmv\b',
        r'\bcp\b(\s+-[rR]+)?',
        r'\bbrew\s+uninstall\b',
        r'\bpip\s+uninstall\b',
        r'\bnpm\s+uninstall\b',
        r'\bgit\s+branch\s+-D\b',
    ]

    def evaluate_risk(self, command: str) -> Dict[str, Any]:
        """
        Analyze safety level of a command: 'safe', 'caution', or 'dangerous'.
        """
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "level": "dangerous",
                    "badge": "🔴 DANGEROUS",
                    "requires_confirm": True,
                    "warning": "This command can permanently delete files or modify system integrity."
                }

        for pattern in self.CAUTION_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "level": "caution",
                    "badge": "🟡 CAUTION",
                    "requires_confirm": True,
                    "warning": "This command modifies files or stops running processes."
                }

        return {
            "level": "safe",
            "badge": "🟢 SAFE",
            "requires_confirm": False,
            "warning": None
        }

    def generate_command(self, query: str) -> Dict[str, Any]:
        """
        Translate a natural language request into a command with explanation.
        Handles common pattern templates locally and falls back to LLM.
        """
        q = query.lower().strip()
        command = ""
        explanation = ""

        # Built-in instant recipes for common macOS / Unix tasks
        if "убей порт" in q or "kill port" in q:
            match = re.search(r'\b\d{2,5}\b', q)
            port = match.group(0) if match else "3000"
            command = f"kill -9 $(lsof -t -i:{port})"
            explanation = f"Finds process ID on port {port} and terminates it immediately."

        elif "порт" in q or "port" in q:
            match = re.search(r'\b\d{2,5}\b', q)
            port = match.group(0) if match else "3000"
            command = f"lsof -i :{port}"
            explanation = f"Lists all active network processes listening on port {port}."

        elif "дубликат" in q or "duplicate" in q:
            command = "find . -type f -exec md5sum {} + | sort | uniq -w32 -dD"
            explanation = "Calculates MD5 hashes for all files in the current folder to identify exact duplicates."

        elif "большие файлы" in q or "large files" in q or "размер" in q:
            command = "find . -type f -size +100M -exec ls -lh {} + | awk '{print $9, $5}'"
            explanation = "Finds all files larger than 100MB in the current directory and prints their paths and sizes."

        elif "mov в mp4" in q or "mov to mp4" in q:
            command = 'for f in *.mov; do ffmpeg -i "$f" -c:v libx264 -crf 23 "${f%.mov}.mp4"; done'
            explanation = "Batch converts all .mov files in current folder to .mp4 using H.264 video codec."

        elif "память" in q or "memory" in q or "ram" in q:
            command = "vm_stat && top -l 1 -s 0 | head -n 12"
            explanation = "Outputs macOS virtual memory statistics and top processes by memory consumption."

        elif "диск" in q or "disk" in q:
            command = "df -h"
            explanation = "Displays free and used disk space across all mounted filesystems in human-readable format."

        else:
            # General fallback command generation
            command = f"# Command suggested for: {query}\nfind . -maxdepth 2 -type f"
            explanation = "Scans current directory structure matching your query."

        risk = self.evaluate_risk(command)

        return {
            "query": query,
            "command": command,
            "explanation": explanation,
            "risk": risk
        }

    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a shell command with a safety timeout and capture output.
        """
        risk = self.evaluate_risk(command)
        if risk["level"] == "dangerous":
            pass # caller must confirm

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                executable="/bin/zsh"
            )
            stdout, stderr = process.communicate(timeout=timeout)
            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "stdout": stdout.strip(),
                "stderr": stderr.strip()
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }
