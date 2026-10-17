"""
GhostOS VRAM Juggler - Smart Memory & Model Dispatcher

Solves the critical low-memory constraint by ensuring only ONE heavy model
(LLM, Vision, or Whisper) is active in VRAM/RAM at any given moment.
Unloads idle models automatically, keeping total footprint <= 3.5GB.
"""
import time
import threading
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("ghost.juggler")

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class MemoryJuggler:
    """
    Orchestrates hot-swapping between LLM, Vision, and Whisper models.
    Prevents Out-Of-Memory (OOM) crashes on 4GB-8GB laptops.
    """
    
    MODEL_LLM = "llm"
    MODEL_VISION = "vision"
    MODEL_WHISPER = "whisper"

    # Estimated VRAM/RAM requirements per model type in MB
    ESTIMATED_SIZES = {
        MODEL_LLM: 2200,      # Qwen 2.5 1.5B/3B Q4
        MODEL_VISION: 1800,   # Moondream2 / MiniCPM
        MODEL_WHISPER: 600,   # Whisper base/small.en
    }

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryJuggler, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, auto_sleep_seconds: int = 180):
        if self._initialized:
            return
        self.auto_sleep_seconds = auto_sleep_seconds
        self.active_model: Optional[str] = None
        self.last_active_time = time.time()
        self.swap_lock = threading.Lock()
        
        # Registry of loaders and unloaders: name -> (load_cb, unload_cb)
        self._handlers: Dict[str, tuple[Callable, Callable]] = {}
        
        # Total simulated savings (in MB) achieved across swaps
        self.total_swaps = 0

        # Background watchdog for auto-sleep
        self._running = True
        self._watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog_thread.start()
        self._initialized = True

    def register_handler(self, model_type: str, load_cb: Callable, unload_cb: Callable) -> None:
        """Register lifecycle hooks for a specific model backend."""
        self._handlers[model_type] = (load_cb, unload_cb)

    def request_model(self, model_type: str) -> None:
        """
        Request a model to be active. If another model is active, unload it first
        to free VRAM, then load the requested one.
        """
        with self.swap_lock:
            self.last_active_time = time.time()
            if self.active_model == model_type:
                return

            if self.active_model is not None:
                logger.info(f"[VRAM Juggler] Swapping out '{self.active_model}' to free memory...")
                self._unload_current()
                self.total_swaps += 1

            logger.info(f"[VRAM Juggler] Loading '{model_type}' into active memory...")
            if model_type in self._handlers:
                load_cb, _ = self._handlers[model_type]
                try:
                    load_cb()
                except Exception as e:
                    logger.error(f"[VRAM Juggler] Failed to load {model_type}: {e}")
                    raise
            self.active_model = model_type

    def _unload_current(self) -> None:
        """Unload whichever model is currently active."""
        if self.active_model and self.active_model in self._handlers:
            _, unload_cb = self._handlers[self.active_model]
            try:
                unload_cb()
            except Exception as e:
                logger.error(f"[VRAM Juggler] Error unloading {self.active_model}: {e}")
        self.active_model = None

    def sleep_all(self) -> None:
        """Release all models from memory (deep sleep)."""
        with self.swap_lock:
            if self.active_model:
                logger.info("[VRAM Juggler] Idle timeout reached. Putting all models to sleep (0% VRAM).")
                self._unload_current()

    def touch(self) -> None:
        """Record user activity to reset auto-sleep timer."""
        self.last_active_time = time.time()

    def get_memory_status(self) -> Dict[str, Any]:
        """Return real-time memory and VRAM stats."""
        total_ram_mb = 8192
        used_ram_mb = 4096
        free_ram_mb = 4096
        percent_used = 50.0

        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            total_ram_mb = int(mem.total / (1024 * 1024))
            used_ram_mb = int(mem.used / (1024 * 1024))
            free_ram_mb = int(mem.available / (1024 * 1024))
            percent_used = mem.percent

        # VRAM saved is the sum of models not currently loaded in memory
        all_models_size = sum(self.ESTIMATED_SIZES.values())
        active_size = self.ESTIMATED_SIZES.get(self.active_model, 0) if self.active_model else 0
        vram_saved_mb = all_models_size - active_size

        return {
            "active_model": self.active_model or "idle (sleeping)",
            "status": "active" if self.active_model else "idle",
            "active_vram_mb": active_size,
            "vram_saved_mb": vram_saved_mb,
            "system_ram_total_mb": total_ram_mb,
            "system_ram_used_mb": used_ram_mb,
            "system_ram_free_mb": free_ram_mb,
            "system_ram_percent": percent_used,
            "total_swaps": self.total_swaps,
            "idle_seconds": int(time.time() - self.last_active_time)
        }

    def _watchdog_loop(self) -> None:
        """Periodic background monitor checking for inactivity."""
        while self._running:
            time.sleep(10)
            if self.active_model and (time.time() - self.last_active_time > self.auto_sleep_seconds):
                self.sleep_all()

    def shutdown(self) -> None:
        self._running = False
        self.sleep_all()
