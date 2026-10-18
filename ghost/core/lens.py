"""
GhostOS Anti-Hallucination & Terminal Sandbox Lens
Validates shell commands against OS conventions, checks binary existence,
and deeply analyzes destructive commands to protect system integrity.
"""
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

class GhostLens:
    """
    Syntax, binary verifier, and destructive command sandbox for AI-generated commands.
    """

    KNOWN_BSD_FIXES = [
        # sed -i requires empty string '' on macOS BSD
        (r'\bsed\s+-i\s+([\'\"][^\'\"]+[\'\"])', r"sed -i '' \1", "Fixed macOS BSD 'sed -i' requirement (added empty extension '')"),
        # find -printf is GNU only
        (r'\bfind\s+(.*?)\s+-printf\b', r"find \1 -print", "Replaced GNU 'find -printf' with BSD compatible syntax"),
        # grep -P (Perl regex) is GNU only on default macOS grep
        (r'\bgrep\s+-P\b', r"grep -E", "Replaced GNU 'grep -P' with BSD POSIX extended regex 'grep -E'"),
        # readlink -f is GNU only (macOS uses realpath or python)
        (r'\breadlink\s+-f\b', r"realpath", "Replaced GNU 'readlink -f' with native macOS 'realpath'"),
    ]

    DESTRUCTIVE_RULES = [
        {
            "pattern": r'\brm\s+(-[rfRF]+)?\s+([/~]|\$HOME|\*\s*$)',
            "level": "CRITICAL",
            "blocked": True,
            "reason": "Attempts to recursively delete root (/), home directory (~), or entire workspace.",
            "alternative": "Specify an exact subdirectory or file, e.g. 'rm target/test.txt'"
        },
        {
            "pattern": r'\bdd\s+if=.*?\s+of=/dev/([a-z0-9]+)',
            "level": "CRITICAL",
            "blocked": True,
            "reason": "Direct low-level raw write to raw storage device. Destroys partition tables.",
            "alternative": "Do not overwrite block storage devices directly."
        },
        {
            "pattern": r'\bmkfs(\.[a-z0-9]+)?\b',
            "level": "CRITICAL",
            "blocked": True,
            "reason": "Formats file systems and destroys existing partition data.",
            "alternative": "Inspect disk utility GUI or verify exact partition."
        },
        {
            "pattern": r':\(\)\s*\{\s*:\|:&\s*\};:',
            "level": "CRITICAL",
            "blocked": True,
            "reason": "Fork bomb that exhausts system processes and freezes the operating system.",
            "alternative": "Command blocked."
        },
        {
            "pattern": r'\bgit\s+reset\s+--hard\b',
            "level": "DANGEROUS",
            "blocked": False,
            "reason": "Permanently discards all uncommitted modifications in the working tree.",
            "alternative": "Use 'git stash' to safely save changes before resetting."
        },
        {
            "pattern": r'\bgit\s+clean\s+-[xfd]+',
            "level": "DANGEROUS",
            "blocked": False,
            "reason": "Permanently removes untracked files and ignored build artifacts.",
            "alternative": "Use 'git clean -n' for a dry-run preview first."
        },
        {
            "pattern": r'\bchmod\s+(-R\s+)?777\b',
            "level": "DANGEROUS",
            "blocked": False,
            "reason": "Grants global read, write, and execute permissions to all users/attackers.",
            "alternative": "Use 'chmod 755' or 'chmod +x' for scripts."
        },
        {
            "pattern": r'>\s*(\.env|config\.json|id_rsa)',
            "level": "DANGEROUS",
            "blocked": False,
            "reason": "Overwrites sensitive secrets, private keys, or environmental config.",
            "alternative": "Append using '>>' or backup the secrets file first."
        },
        {
            "pattern": r'\b(format\s+[A-Z]:|del\s+/s\s+/q\s+C:\\)',
            "level": "CRITICAL",
            "blocked": True,
            "reason": "Windows destructive command that formats drives or empties system drive.",
            "alternative": "Command blocked."
        }
    ]

    @classmethod
    def verify_and_patch(cls, command: str) -> Dict[str, Any]:
        """
        Check if binary exists and patch any incompatible GNU flags for macOS.
        """
        patched_cmd = command.strip()
        modifications: List[str] = []

        if sys.platform == "darwin":
            for pattern, replacement, reason in cls.KNOWN_BSD_FIXES:
                if re.search(pattern, patched_cmd):
                    patched_cmd = re.sub(pattern, replacement, patched_cmd)
                    modifications.append(reason)

        # Extract primary binary
        first_word = patched_cmd.split()[0] if patched_cmd.split() else ""
        if "=" in first_word and not first_word.startswith("-"):
            tokens = patched_cmd.split()
            first_word = tokens[1] if len(tokens) > 1 else first_word

        is_installed = True
        missing_binary = None

        shell_builtins = {"echo", "cd", "export", "alias", "source", "kill", "eval", "for", "while", "if", "test"}
        if first_word and first_word not in shell_builtins:
            if not shutil.which(first_word):
                is_installed = False
                missing_binary = first_word

        is_valid = is_installed
        warning = None
        if not is_installed:
            warning = f"Binary '{missing_binary}' was not found in your PATH."

        # Deep Sandbox Risk Analysis
        sandbox = cls.deep_sandbox_check(patched_cmd)

        return {
            "original_command": command,
            "patched_command": patched_cmd,
            "is_valid": is_valid,
            "modifications": modifications,
            "warning": warning,
            "verified_binary": first_word if is_installed else None,
            "sandbox": sandbox
        }

    @classmethod
    def deep_sandbox_check(cls, command: str) -> Dict[str, Any]:
        """
        Scan command for destructive operations and return risk assessment.
        """
        for rule in cls.DESTRUCTIVE_RULES:
            if re.search(rule["pattern"], command, re.IGNORECASE):
                return {
                    "safety_level": rule["level"],
                    "is_blocked": rule["blocked"],
                    "danger_reason": rule["reason"],
                    "safe_alternative": rule["alternative"]
                }

        return {
            "safety_level": "SAFE",
            "is_blocked": False,
            "danger_reason": None,
            "safe_alternative": None
        }
