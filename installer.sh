#!/bin/bash
# WiFi Pentest Toolkit - Installer
# Authorized security testing only

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║   WiFi Pentest Toolkit - Installer       ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# Detect environment
if command -v pkg >/dev/null 2>&1; then
    ENV="termux"
    SUDO=""
    PKG="pkg"
elif command -v apt >/dev/null 2>&1; then
    ENV="linux"
    if [ "$(id -u)" -ne 0 ]; then
        SUDO="sudo"
    else
        SUDO=""
    fi
    PKG="apt"
else
    echo -e "${RED}[!] Unsupported environment${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Detected: ${ENV}${NC}"

# Create directories
mkdir -p portals modules capture logs

if [ "$ENV" = "termux" ]; then
    echo -e "${YELLOW}[*] Updating Termux packages...${NC}"
    pkg update -y
    pkg upgrade -y

    echo -e "${YELLOW}[*] Enabling repos...${NC}"
    pkg install -y root-repo x11-repo 2>/dev/null || true

    echo -e "${YELLOW}[*] Installing packages...${NC}"
    pkg install -y \
        tsu \
        python \
        python-pip \
        git \
        wget \
        curl \
        nmap \
        php \
        openssl-tool \
        termux-api \
        2>/dev/null || true

    # Optional wireless tools (need root + compatible chipset)
    pkg install -y aircrack-ng hostapd dnsmasq iw iproute2 2>/dev/null || \
        echo -e "${YELLOW}[!] Some wireless packages unavailable in Termux without root environment${NC}"

    pip install --upgrade pip 2>/dev/null || true
    pip install flask 2>/dev/null || pip3 install flask

else
    echo -e "${YELLOW}[*] Updating apt...${NC}"
    $SUDO apt update -y

    echo -e "${YELLOW}[*] Installing packages...${NC}"
    $SUDO apt install -y \
        aircrack-ng \
        hostapd \
        dnsmasq \
        python3 \
        python3-pip \
        python3-flask \
        php \
        nmap \
        git \
        macchanger \
        iw \
        wireless-tools \
        net-tools \
        iproute2 \
        xterm \
        gnome-terminal \
        openssl \
        reaver \
        bully \
        hcxdumptool \
        hcxtools \
        hashcat \
        john \
        2>/dev/null || true

    # Flask fallback
    python3 -m pip install flask 2>/dev/null || $SUDO pip3 install flask 2>/dev/null || true
fi

# Permissions
chmod +x installer.sh wifitool.sh 2>/dev/null || true
chmod +x modules/*.sh 2>/dev/null || true
chmod +x modules/*.py 2>/dev/null || true

# Placeholder files
touch capture/.gitkeep logs/.gitkeep
touch logs/captured_passwords.log
touch logs/session.log

echo ""
echo -e "${GREEN}[✓] Installation complete${NC}"
echo -e "${BLUE}Run:${NC}"
if [ "$ENV" = "termux" ]; then
    echo -e "  ${YELLOW}tsu${NC}"
    echo -e "  ${YELLOW}bash wifitool.sh${NC}"
    echo -e "${RED}Note: Monitor mode on Android usually needs a rooted device + external USB WiFi adapter (OTG).${NC}"
else
    echo -e "  ${YELLOW}sudo bash wifitool.sh${NC}"
fi
