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

    # Create frameless, transparent, floating window
    # Initial size: 220x240 for Casper Desktop Pet
    window = webview.create_window(
        title="GhostOS",
        url=index_html.as_uri(),
        js_api=api,
        width=220,
        height=240,
        x=None, # system default or bottom right
        y=None,
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
