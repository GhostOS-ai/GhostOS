"""
GhostOS Native Voice Engine
Ultra-lightweight text-to-speech (TTS) utilizing native macOS system speech synthesizers.
0 MB RAM overhead, 0% CPU impact, no heavy neural network weights needed.
"""
import re
import subprocess
import threading
import logging
from typing import Optional, List, Dict

logger = logging.getLogger("ghost.voice")

class VoiceEngine:
    """
    Manages speech output using macOS 'say' command with automatic voice selection.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VoiceEngine, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.is_enabled = False
        self._current_proc: Optional[subprocess.Popen] = None
        self._available_voices: Dict[str, str] = self._detect_voices()
        self._initialized = True

    def _detect_voices(self) -> Dict[str, str]:
        """Detect installed macOS voices for Russian and English."""
        voices = {"ru": "Milena", "en": "Samantha"}
        try:
            res = subprocess.run("say -v '?'", shell=True, capture_output=True, text=True, timeout=2)
            out = res.stdout
            if "Milena" in out:
                voices["ru"] = "Milena"
            elif "Yuri" in out:
                voices["ru"] = "Yuri"
            elif "Aru" in out:
                voices["ru"] = "Aru"

            if "Samantha" in out:
                voices["en"] = "Samantha"
            elif "Fred" in out:
                voices["en"] = "Fred"
        except Exception:
            pass
        return voices

    def clean_text_for_speech(self, text: str) -> str:
        """Strip code blocks, URLs, and markdown punctuation for natural reading."""
        # Remove code blocks
        clean = re.sub(r'```[\s\S]*?```', ' [код пропущен] ', text)
        # Remove inline code
        clean = re.sub(r'`([^`]+)`', r'\1', clean)
        # Remove markdown bold/italics
        clean = re.sub(r'[*_#~>]', '', clean)
        # Remove URLs
        clean = re.sub(r'https?://[^\s]+', '', clean)
        # Remove excessive whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def speak(self, text: str, voice: Optional[str] = None, async_mode: bool = True) -> bool:
        """
        Speak text aloud asynchronously.
        """
        if not self.is_enabled and not voice:
            return False

        clean = self.clean_text_for_speech(text)
        if not clean or len(clean) < 2:
            return False

        # Detect language
        has_cyrillic = bool(re.search(r'[а-яА-ЯёЁ]', clean))
        chosen_voice = voice or (self._available_voices.get("ru") if has_cyrillic else self._available_voices.get("en"))

        self.stop()

        def _run():
            import sys
            try:
                if sys.platform == "darwin":
                    cmd = ["say"]
                    if chosen_voice:
                        cmd.extend(["-v", chosen_voice])
                    cmd.append(clean)
                    self._current_proc = subprocess.Popen(cmd)
                    self._current_proc.wait()
                elif sys.platform == "win32":
                    escaped_clean = clean.replace('"', '`"').replace("'", "''")
                    ps_cmd = (
                        f'Add-Type -AssemblyName System.Speech; '
                        f'$syn = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                        f'$syn.Speak("{escaped_clean}")'
                    )
                    self._current_proc = subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_cmd])
                    self._current_proc.wait()
                elif sys.platform.startswith("linux"):
                    try:
                        self._current_proc = subprocess.Popen(["spd-say", clean])
                        self._current_proc.wait()
                    except Exception:
                        self._current_proc = subprocess.Popen(["espeak", clean])
                        self._current_proc.wait()
            except Exception as e:
                logger.warning(f"Voice output failed: {e}")

        if async_mode:
            t = threading.Thread(target=_run, daemon=True)
            t.start()
            return True
        else:
            _run()
            return True

    def stop(self) -> None:
        """Stop any currently playing speech."""
        if self._current_proc and self._current_proc.poll() is None:
            try:
                self._current_proc.terminate()
            except Exception:
                pass
            self._current_proc = None

    def toggle(self, state: Optional[bool] = None) -> bool:
        """Toggle voice output on/off."""
        if state is not None:
            self.is_enabled = state
        else:
            self.is_enabled = not self.is_enabled
        if not self.is_enabled:
            self.stop()
        return self.is_enabled
