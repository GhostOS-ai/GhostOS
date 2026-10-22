#!/usr/bin/env bash
# ==============================================================================
#  👻 GhostOS — One-Line Instant Installer for macOS & Linux
#  Repository: https://github.com/GhostOS-ai/GhostOS
#  Author: KIB.best (GhostOS@kib.best)
# ==============================================================================

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${PURPLE}"
cat << "EOF"
      .---.
     /     \
    | () () |   G H O S T O S
     \  -  /    The Invisible, Featherweight, Offline Desktop AI Copilot
    /`---'\
   /       \    [ 100% Private • <35MB RAM • Dynamic VRAM Juggler • Zero-DB RAG ]
  (_/^\_/\_/^)
EOF
echo -e "${NC}"

echo -e "${CYAN}🚀 Installing GhostOS Copilot...${NC}"

# 1. Detect Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 is not installed.${NC}"
    echo -e "Please install Python 3.9+ from https://www.python.org or run: brew install python"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ Found Python ${PY_VER}${NC}"

# 2. Install / Upgrade ghostos-ai via pip
echo -e "${CYAN}📦 Installing latest ghostos-ai package...${NC}"
python3 -m pip install --upgrade --quiet ghostos-ai 2>/dev/null || \
python3 -m pip install --upgrade --user ghostos-ai 2>/dev/null || \
pip install --upgrade ghostos-ai

# 3. macOS Native Application Bundle Creation (/Applications/GhostOS.app)
if [ "$(uname)" == "Darwin" ]; then
    APP_DIR="/Applications/GhostOS.app"
    echo -e "${CYAN}🍎 Setting up macOS Application in /Applications/GhostOS.app...${NC}"
    
    mkdir -p "$APP_DIR/Contents/MacOS"
    mkdir -p "$APP_DIR/Contents/Resources"
    
    # Launcher script
    cat << 'LAUNCHER' > "$APP_DIR/Contents/MacOS/GhostOS"
#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/Library/Python/3.11/bin:$HOME/Library/Python/3.9/bin:$PATH"
if command -v ghost &> /dev/null; then
    exec ghost pet --tray
else
    exec python3 -m ghost pet --tray
fi
LAUNCHER
    chmod +x "$APP_DIR/Contents/MacOS/GhostOS"
    
    # Info.plist
    cat << 'PLIST' > "$APP_DIR/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>GhostOS</string>
    <key>CFBundleIconFile</key>
    <string>GhostOS.icns</string>
    <key>CFBundleIdentifier</key>
    <string>best.kib.ghostos</string>
    <key>CFBundleName</key>
    <string>GhostOS</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.2.1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

    # Download or copy Casper icon
    ICON_DEST="$APP_DIR/Contents/Resources/GhostOS.icns"
    if [ ! -f "$ICON_DEST" ]; then
        curl -fsSL -o "$ICON_DEST" "https://raw.githubusercontent.com/GhostOS-ai/GhostOS/main/ghost/ui/assets/GhostOS.icns" 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ Created /Applications/GhostOS.app with Casper icon!${NC}"
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}🎉 GhostOS successfully installed!${NC}"
echo -e "${GREEN}======================================================${NC}\n"

echo -e "You can launch GhostOS in two ways:"
echo -e "  1. ${YELLOW}ghost pet${NC}           (Run from any terminal)"
echo -e "  2. ${YELLOW}Launch from Spotlight / Applications${NC} (Open 'GhostOS.app')"
echo -e ""
echo -e "Try these commands:"
echo -e "  • ${CYAN}ghost spot${NC}                 (Instant Spotlight HUD query bar)"
echo -e "  • ${CYAN}ghost pet --skin cyberpunk${NC} (Launch with Neon theme)"
echo -e "  • ${CYAN}ghost models${NC}               (Inspect local AI hardware acceleration)"
echo -e ""
