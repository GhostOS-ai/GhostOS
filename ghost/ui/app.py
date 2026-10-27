"""
GhostOS Desktop Window Manager
Launches the floating Casper Pet & Spotlight HUD using macOS native WebKit.
Zero Electron overhead: runs natively via pywebview.
"""
import os
import sys
from pathlib import Path
import webview

# Smooth native window dragging configuration (eliminates drag jitter and preserves button clicks)
webview.settings['DRAG_REGION_SELECTOR'] = '.pywebview-drag-region'
webview.settings['DRAG_REGION_DIRECT_TARGET_ONLY'] = True

from ghost.ui.api import GhostBridgeAPI

def set_macos_dock_icon():
    """Sets custom Casper Ghost icon in macOS Dock instead of default Python rocket."""
    if sys.platform == "darwin":
        try:
            from AppKit import NSApplication, NSImage
            app = NSApplication.sharedApplication()
            icon_file = Path(__file__).parent / "assets" / "icon.png"
            if not icon_file.exists():
                icon_file = Path(__file__).parents[2] / "avatar.jpg"
            if icon_file.exists():
                img = NSImage.alloc().initWithContentsOfFile_(str(icon_file))
                if img:
                    app.setApplicationIconImage_(img)
        except Exception:
            pass

def launch_desktop_pet(skin: str = "glass", with_tray: bool = False):
    """
    Launches the floating transparent Casper Ghost pet on the desktop.
    """
    set_macos_dock_icon()
    assets_dir = Path(__file__).parent / "assets"
    index_html = assets_dir / "index.html"
    
    if not index_html.exists():
        raise FileNotFoundError(f"Missing UI assets at: {index_html}")

    if with_tray and sys.platform == "darwin":
        try:
            import threading
            from ghost.ui.tray import GhostTrayController
            tray_thread = threading.Thread(target=lambda: GhostTrayController().run(blocking=False), daemon=True)
            tray_thread.start()
        except Exception as e:
            print(f"Warning: Could not start menu bar tray: {e}")

    api = GhostBridgeAPI()
    api.skin = skin

    # Calculate bottom-right desktop placement
    try:
        screens = webview.screens
        if screens:
            primary = screens[0]
            start_x = max(80, primary.width - 270)
            start_y = max(80, primary.height - 340)
        else:
            start_x = 1200
            start_y = 650
    except Exception:
        start_x = 1200
        start_y = 650

    # Create frameless, transparent, floating window
    # Initial size: 240x280 for Casper Desktop Pet
    window_url = f"{index_html.as_uri()}?skin={skin}&mode=pet"
    window = webview.create_window(
        title="GhostOS",
        url=window_url,
        js_api=api,
        width=240,
        height=280,
        x=start_x,
        y=start_y,
        frameless=True,
        transparent=True,
        on_top=True,
        easy_drag=False,
        shadow=False,
        text_select=True,
    )

    api.set_window(window)

    # Start the native macOS WebKit window
    webview.start(debug=False)

def launch_spotlight_hud(skin: str = "glass"):
    """
    Launches the Spotlight HUD directly centered on screen for quick offline queries.
    """
    set_macos_dock_icon()
    assets_dir = Path(__file__).parent / "assets"
    index_html = assets_dir / "index.html"
    
    if not index_html.exists():
        raise FileNotFoundError(f"Missing UI assets at: {index_html}")

    api = GhostBridgeAPI()
    api.skin = skin
    api.current_mode = "hud"

    try:
        screens = webview.screens
        if screens:
            primary = screens[0]
            start_x = max(20, (primary.width - 740) // 2)
            start_y = max(20, (primary.height - 580) // 3)
        else:
            start_x = 300
            start_y = 150
    except Exception:
        start_x = 300
        start_y = 150

    window_url = f"{index_html.as_uri()}?skin={skin}&mode=hud"
    window = webview.create_window(
        title="GhostOS Spotlight",
        url=window_url,
        js_api=api,
        width=740,
        height=580,
        x=start_x,
        y=start_y,
        frameless=True,
        transparent=True,
        on_top=True,
        easy_drag=False,
        shadow=True,
        text_select=True,
    )

    api.set_window(window)
    webview.start(debug=False)

def launch_studio(skin: str = "glass", workspace: str = None):
    """
    Launches GhostOS Studio v2.0 (The Unified ChatGPT-style AI & GhostCode IDE).
    """
    set_macos_dock_icon()
    assets_dir = Path(__file__).parent / "assets"
    index_html = assets_dir / "index.html"

    if not index_html.exists():
        raise FileNotFoundError(f"Missing UI assets at: {index_html}")

    api = GhostBridgeAPI()
    api.skin = skin
    api.current_mode = "studio"
    if workspace:
        api.get_coder().set_workspace(workspace)

    try:
        screens = webview.screens
        if screens:
            primary = screens[0]
            start_x = max(20, (primary.width - 1160) // 2)
            start_y = max(20, (primary.height - 780) // 2)
        else:
            start_x = 100
            start_y = 60
    except Exception:
        start_x = 100
        start_y = 60

    window_url = f"{index_html.as_uri()}?skin={skin}&mode=studio"
    window = webview.create_window(
        title="GhostOS Studio — AI & Code Copilot",
        url=window_url,
        js_api=api,
        width=1160,
        height=780,
        x=start_x,
        y=start_y,
        frameless=True,
        transparent=True,
        on_top=False,
        easy_drag=False,
        shadow=True,
        text_select=True,
    )

    api.set_window(window)
    webview.start(debug=False)

if __name__ == "__main__":
    launch_desktop_pet()
