"""
GhostOS Desktop Window Manager
Launches the floating Casper Pet & Spotlight HUD using macOS native WebKit.
Zero Electron overhead: runs natively via pywebview.
"""
import os
import sys
from pathlib import Path
import webview

from ghost.ui.api import GhostBridgeAPI

def launch_desktop_pet():
    """
    Launches the floating transparent Casper Ghost pet on the desktop.
    """
    assets_dir = Path(__file__).parent / "assets"
    index_html = assets_dir / "index.html"
    
    if not index_html.exists():
        raise FileNotFoundError(f"Missing UI assets at: {index_html}")

    api = GhostBridgeAPI()

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
    window = webview.create_window(
        title="GhostOS",
        url=index_html.as_uri(),
        js_api=api,
        width=240,
        height=280,
        x=start_x,
        y=start_y,
        frameless=True,
        transparent=True,
        on_top=True,
        easy_drag=True,
        shadow=False,
        text_select=True,
    )

    api.set_window(window)

    # Start the native macOS WebKit window
    webview.start(debug=False)

if __name__ == "__main__":
    launch_desktop_pet()
