"""
GhostOS Casper RPG & Evolution Engine
Gamification system that awards XP for eating files, running tasks, and debugging.
Unlocks evolved titles and visual accessories (visor, magic book, crown).
"""
import json
from pathlib import Path
from typing import Dict, Any

from ghost.config import GHOST_HOME, ensure_dirs

RPG_FILE = GHOST_HOME / "rpg_stats.json"

class CasperRPG:
    """
    Manages Casper's level, experience points (XP), and skin evolutions.
    """

    RANKS = [
        {"min_xp": 0,   "level": 1, "title": "Apprentice Wisp",  "accessory": "none",   "badge": "🌱 Wisp"},
        {"min_xp": 100, "level": 2, "title": "File Nibbler",     "accessory": "none",   "badge": "🍪 Nibbler"},
        {"min_xp": 250, "level": 3, "title": "Code Specter",     "accessory": "visor",  "badge": "🕶️ Cyber Specter"},
        {"min_xp": 500, "level": 4, "title": "Terminal Phantom", "accessory": "visor",  "badge": "⚡ Phantom"},
        {"min_xp": 900, "level": 5, "title": "Grand Scribe",     "accessory": "book",   "badge": "📖 Grand Scribe"},
        {"min_xp": 1500,"level": 6, "title": "Void Sentinel",    "accessory": "crown",  "badge": "👑 Void Sentinel"},
    ]

    @classmethod
    def load_stats(cls) -> Dict[str, Any]:
        """Load user XP and evolution stats from disk."""
        ensure_dirs()
        default_stats = {
            "xp": 0,
            "files_eaten": 0,
            "questions_answered": 0,
            "commands_executed": 0,
            "screens_inspected": 0,
        }
        if RPG_FILE.exists():
            try:
                with open(RPG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_stats.update(data)
            except Exception:
                pass
        return default_stats

    @classmethod
    def save_stats(cls, stats: Dict[str, Any]) -> None:
        """Save stats to disk."""
        ensure_dirs()
        with open(RPG_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

    @classmethod
    def add_xp(cls, amount: int, action_type: str = "general") -> Dict[str, Any]:
        """Award XP to Casper and check for level-ups."""
        stats = cls.load_stats()
        old_level = cls.get_rank(stats["xp"])["level"]

        stats["xp"] += amount
        if action_type == "eat":
            stats["files_eaten"] += 1
        elif action_type == "ask":
            stats["questions_answered"] += 1
        elif action_type == "exec":
            stats["commands_executed"] += 1
        elif action_type == "screen":
            stats["screens_inspected"] += 1

        cls.save_stats(stats)
        new_rank = cls.get_rank(stats["xp"])
        leveled_up = new_rank["level"] > old_level

        return {
            "awarded_xp": amount,
            "total_xp": stats["xp"],
            "level": new_rank["level"],
            "title": new_rank["title"],
            "badge": new_rank["badge"],
            "accessory": new_rank["accessory"],
            "leveled_up": leveled_up,
            "progress_percent": cls.get_progress_percent(stats["xp"])
        }

    @classmethod
    def get_rank(cls, xp: int) -> Dict[str, Any]:
        """Get rank details for current XP."""
        current_rank = cls.RANKS[0]
        for rank in cls.RANKS:
            if xp >= rank["min_xp"]:
                current_rank = rank
            else:
                break
        return current_rank

    @classmethod
    def get_progress_percent(cls, xp: int) -> float:
        """Calculate progress percentage towards next level."""
        for i, rank in enumerate(cls.RANKS):
            if xp < rank["min_xp"]:
                prev_xp = cls.RANKS[i - 1]["min_xp"]
                next_xp = rank["min_xp"]
                return round(((xp - prev_xp) / max(1, next_xp - prev_xp)) * 100, 1)
        return 100.0

    @classmethod
    def get_full_status(cls) -> Dict[str, Any]:
        """Get summary of Casper's RPG stats for UI/CLI."""
        stats = cls.load_stats()
        rank = cls.get_rank(stats["xp"])
        return {
            "xp": stats["xp"],
            "level": rank["level"],
            "title": rank["title"],
            "badge": rank["badge"],
            "accessory": rank["accessory"],
            "progress_percent": cls.get_progress_percent(stats["xp"]),
            "files_eaten": stats["files_eaten"],
            "questions_answered": stats["questions_answered"],
            "commands_executed": stats["commands_executed"],
            "screens_inspected": stats["screens_inspected"]
        }
