import sys
import os
from ghost.ui.app import launch_studio, launch_desktop_pet

if __name__ == '__main__':
    skin = 'glass'
    if '--skin' in sys.argv:
        idx = sys.argv.index('--skin')
        if idx + 1 < len(sys.argv):
            skin = sys.argv[idx + 1]

    workspace = None
    if '--workspace' in sys.argv:
        idx = sys.argv.index('--workspace')
        if idx + 1 < len(sys.argv):
            workspace = sys.argv[idx + 1]

    # If explicitly asked for floating desktop pet mode, launch mini Casper pet (240x280)
    # Otherwise, launch the full GhostOS v2.0 Studio (ChatGPT AI + GhostCode IDE)
    if '--pet' in sys.argv:
        launch_desktop_pet(skin=skin, with_tray=True)
    else:
        launch_studio(skin=skin, workspace=workspace)
