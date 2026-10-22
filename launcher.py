import sys
import os
from ghost.ui.app import launch_desktop_pet

if __name__ == '__main__':
    skin = 'glass'
    if '--skin' in sys.argv:
        idx = sys.argv.index('--skin')
        if idx + 1 < len(sys.argv):
            skin = sys.argv[idx + 1]
    with_tray = True
    launch_desktop_pet(skin=skin, with_tray=with_tray)
