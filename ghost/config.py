"""
GhostOS Configuration & Path Management
"""
import os
import json
from pathlib import Path
from typing import Dict, Any

# Root data directory in user home
GHOST_HOME = Path.home() / ".ghostos"
GHOST_MODELS_DIR = GHOST_HOME / "models"
GHOST_CACHE_DIR = GHOST_HOME / "cache"
GHOST_RECORDINGS_DIR = GHOST_HOME / "recordings"
GHOST_DB_PATH = GHOST_HOME / "ghost_knowledge.db"
CONFIG_FILE = GHOST_HOME / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "engine": "auto",           # "auto", "ollama", "llamacpp", "mock"
    "model_name": "qwen2.5-3b-q4",
    "vram_limit_mb": 4096,     # Target VRAM ceiling (4GB)
    "auto_sleep_seconds": 180, # Unload inactive models after 3 minutes
    "pet_mode": "floating",    # "floating", "stealth", "docked"
    "hotkey": "Cmd+Shift+Space",
    "sound_effects": True,
    "theme": "dark_neon",
    "ollama_host": "http://localhost:11434",
    "safe_terminal_mode": True,
}

def ensure_dirs() -> None:
    """Ensure all required directories exist."""
    GHOST_HOME.mkdir(parents=True, exist_ok=True)
    GHOST_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    GHOST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    GHOST_RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)

def load_config() -> Dict[str, Any]:
    """Load configuration from disk, falling back to defaults."""
    ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(data)
                return merged
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(cfg: Dict[str, Any]) -> None:
    """Save configuration to disk."""
    GHOST_HOME.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
