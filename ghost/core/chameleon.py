"""
GhostOS Memory Chameleon
Adaptive power and memory profile manager that dynamically tunes model
context window, CPU threads, and auto-sleep timeouts based on battery & RAM pressure.
"""
import subprocess
import logging
from typing import Dict, Any

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger("ghost.chameleon")

class MemoryChameleon:
    """
    Monitors hardware vitals and optimizes GhostOS runtime parameters
    so modest hardware runs without lag, fan noise, or battery drain.
    """

    MODE_ECO = "eco"
    MODE_BALANCED = "balanced"
    MODE_PERFORMANCE = "performance"

    PROFILE_CONFIGS = {
        MODE_ECO: {
            "name": "🍃 Eco Mode (Battery & Low RAM)",
            "context_window": 1024,
            "cpu_threads": 2,
            "auto_sleep_seconds": 60,
            "pet_fps": 30,
            "preferred_model": "qwen2.5-1.5b-q4",
            "vram_cap_mb": 2048,
        },
        MODE_BALANCED: {
            "name": "⚖️ Balanced Mode",
            "context_window": 2048,
            "cpu_threads": 4,
            "auto_sleep_seconds": 180,
            "pet_fps": 60,
            "preferred_model": "qwen2.5-3b-q4",
            "vram_cap_mb": 3584,
        },
        MODE_PERFORMANCE: {
            "name": "⚡ Performance Beast",
            "context_window": 4096,
            "cpu_threads": 8,
            "auto_sleep_seconds": 300,
            "pet_fps": 60,
            "preferred_model": "qwen2.5-7b-q4",
            "vram_cap_mb": 6144,
        }
    }

    _override_mode = None

    @classmethod
    def set_override(cls, mode: str) -> None:
        if mode in cls.PROFILE_CONFIGS or mode is None:
            cls._override_mode = mode

    @classmethod
    def is_on_battery(cls) -> bool:
        """Check if macOS is running on battery."""
        try:
            res = subprocess.run("pmset -g batt", shell=True, capture_output=True, text=True, timeout=2)
            out = res.stdout.lower()
            return "battery power" in out or ("discharging" in out and "ac power" not in out)
        except Exception:
            return False

    @classmethod
    def get_ram_pressure_percent(cls) -> float:
        """Get current system RAM usage percentage."""
        if HAS_PSUTIL:
            try:
                return float(psutil.virtual_memory().percent)
            except Exception:
                pass
        return 50.0

    @classmethod
    def get_active_mode(cls) -> str:
        """Determine optimal runtime mode dynamically."""
        if cls._override_mode:
            return cls._override_mode

        on_battery = cls.is_on_battery()
        ram_percent = cls.get_ram_pressure_percent()

        # If on battery or RAM pressure is critically high (>82%), switch to ECO
        if on_battery or ram_percent > 82.0:
            return cls.MODE_ECO

        # If plugged in and plenty of RAM (>55% free), go PERFORMANCE
        if not on_battery and ram_percent < 45.0:
            return cls.MODE_PERFORMANCE

        return cls.MODE_BALANCED

    @classmethod
    def get_profile(cls) -> Dict[str, Any]:
        """Return the complete profile dict for the current active mode."""
        mode = cls.get_active_mode()
        profile = dict(cls.PROFILE_CONFIGS[mode])
        profile["active_mode"] = mode
        profile["is_battery"] = cls.is_on_battery()
        profile["ram_pressure_percent"] = cls.get_ram_pressure_percent()
        profile["is_overridden"] = cls._override_mode is not None
        return profile
