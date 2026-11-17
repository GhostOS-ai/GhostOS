import sys
import os

# Priority module resolution: load disk Resources/ghost ahead of frozen PYZ
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    res_dir = os.path.abspath(os.path.join(exe_dir, '..', 'Resources'))
    if os.path.isdir(os.path.join(res_dir, 'ghost')):
        if res_dir not in sys.path:
            sys.path.insert(0, res_dir)
        try:
            from importlib.machinery import PathFinder
            finders = [f for f in sys.meta_path if f is PathFinder]
            for f in finders:
                sys.meta_path.remove(f)
                sys.meta_path.insert(0, f)
        except Exception:
            pass

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
