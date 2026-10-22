"""
GhostOS Native Menu Bar & System Tray Controller
Provides a featherweight menu bar status icon (NSStatusBar on macOS) with 0 Electron overhead.
"""
import sys
import threading
import subprocess
from typing import Optional, Callable

from ghost.core.engine import GhostEngine
from ghost.core.memory_juggler import MemoryJuggler

class GhostTrayController:
    """
    Lightweight, native Menu Bar / System Tray item.
    """

    def __init__(self, on_toggle_pet: Optional[Callable] = None, on_open_hud: Optional[Callable] = None):
        self.engine = GhostEngine()
        self.juggler = MemoryJuggler()
        self.on_toggle_pet = on_toggle_pet
        self.on_open_hud = on_open_hud
        self.status_item = None
        self._running = False

    def is_supported(self) -> bool:
        """Returns True if native platform tray is supported."""
        return sys.platform == "darwin"

    def run(self, blocking: bool = True):
        """Runs the menu bar tray item."""
        if sys.platform != "darwin":
            self._run_fallback()
            return

        try:
            from AppKit import (
                NSApplication,
                NSStatusBar,
                NSVariableStatusItemLength,
                NSMenu,
                NSMenuItem,
                NSObject
            )
            import objc
        except ImportError:
            self._run_fallback()
            return

        self._running = True
        app = NSApplication.sharedApplication()
        status_bar = NSStatusBar.systemStatusBar()
        self.status_item = status_bar.statusItemWithLength_(NSVariableStatusItemLength)

        # Set tray icon text
        if self.status_item.button():
            self.status_item.button().setTitle_("👻")
            self.status_item.button().setToolTip_("GhostOS: Offline AI Copilot (<35MB RAM)")

        # Build native menu
        menu = NSMenu.alloc().init()

        # 1. Header
        header = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("👻 GhostOS v1.2.0 (<35MB RAM)", None, "")
        header.setEnabled_(False)
        menu.addItem_(header)
        menu.addItem_(NSMenuItem.separatorItem())

        # 2. Launch / Toggle Pet
        class MenuActionHandler(NSObject):
            def init(self):
                self = objc.super(MenuActionHandler, self).init()
                return self

            def launchPet_(self, sender):
                subprocess.Popen([sys.executable, "-m", "ghost", "pet"])

            def launchSpotlight_(self, sender):
                subprocess.Popen([sys.executable, "-m", "ghost", "spot"])

            def flushMemory_(self, sender):
                MemoryJuggler().flush_memory()

            def setSkinGlass_(self, sender):
                subprocess.Popen([sys.executable, "-m", "ghost", "pet", "--skin", "glass"])

            def setSkinCyberpunk_(self, sender):
                subprocess.Popen([sys.executable, "-m", "ghost", "pet", "--skin", "cyberpunk"])

            def setSkinGold_(self, sender):
                subprocess.Popen([sys.executable, "-m", "ghost", "pet", "--skin", "gold"])

            def setSkinMatrix_(self, sender):
                subprocess.Popen([sys.executable, "-m", "ghost", "pet", "--skin", "matrix"])

            def quitApp_(self, sender):
                NSApplication.sharedApplication().terminate_(None)

        handler = MenuActionHandler.alloc().init()
        self._handler = handler  # retain reference

        pet_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("👁️ Launch Casper Desktop Pet", "launchPet:", "p")
        pet_item.setTarget_(handler)
        menu.addItem_(pet_item)

        spot_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("🔍 Open Spotlight HUD", "launchSpotlight:", "g")
        spot_item.setTarget_(handler)
        menu.addItem_(spot_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # 3. Casper Skins Submenu
        skins_menu = NSMenu.alloc().init()
        skins = [
            ("💎 Ethereal Glass (Default)", "setSkinGlass:"),
            ("⚡ Cyberpunk Neon", "setSkinCyberpunk:"),
            ("👑 Royal Gold", "setSkinGold:"),
            ("🟢 Matrix Hacker", "setSkinMatrix:")
        ]
        for title, action in skins:
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, "")
            item.setTarget_(handler)
            skins_menu.addItem_(item)

        skins_parent = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("🎨 Casper Wardrobe Skins", None, "")
        skins_parent.setSubmenu_(skins_menu)
        menu.addItem_(skins_parent)

        # 4. Hardware & Memory
        menu.addItem_(NSMenuItem.separatorItem())
        flush_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("🧹 Flush VRAM (Sleep Juggler)", "flushMemory:", "")
        flush_item.setTarget_(handler)
        menu.addItem_(flush_item)

        # 5. Quit
        menu.addItem_(NSMenuItem.separatorItem())
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("🚪 Quit GhostOS", "quitApp:", "q")
        quit_item.setTarget_(handler)
        menu.addItem_(quit_item)

        self.status_item.setMenu_(menu)

        if blocking:
            app.run()

    def _run_fallback(self):
        """CLI fallback for platforms without native AppKit."""
        print("GhostOS Tray: Native AppKit menu bar is active on macOS.")

def launch_tray():
    """Entry point for CLI 'ghost bar' / 'ghost tray'."""
    tray = GhostTrayController()
    tray.run(blocking=True)

if __name__ == "__main__":
    launch_tray()
