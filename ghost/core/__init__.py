"""
GhostOS Core Submodules
"""
from ghost.core.engine import GhostEngine
from ghost.core.memory_juggler import MemoryJuggler
from ghost.core.rag import ZeroDbRAG
from ghost.core.vision import ScreenInspector
from ghost.core.autopilot import TerminalAutopilot
from ghost.core.audio import MeetingCopilot
from ghost.core.vacuum import ContextVacuum
from ghost.core.chameleon import MemoryChameleon
from ghost.core.clipboard import PhantomClipboard
from ghost.core.lens import GhostLens
from ghost.core.time_machine import GhostTimeMachine
from ghost.core.rpg import CasperRPG

__all__ = [
    "GhostEngine",
    "MemoryJuggler",
    "ZeroDbRAG",
    "ScreenInspector",
    "TerminalAutopilot",
    "MeetingCopilot",
    "ContextVacuum",
    "MemoryChameleon",
    "PhantomClipboard",
    "GhostLens",
    "GhostTimeMachine",
    "CasperRPG",
]
