#!/bin/bash
# MemoryForge - Setup Script
# Supports: Linux & Termux (Android)

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║        MemoryForge - Setup Script        ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# Detect platform
if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
    PLATFORM="termux"
    echo -e "${YELLOW}[i] Detected: Termux (Android)${NC}"
else
    PLATFORM="linux"
    echo -e "${YELLOW}[i] Detected: Linux${NC}"
fi

# Check Python
echo -ne "[*] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
    echo -e " ${GREEN}found${NC}"
elif command -v python &> /dev/null; then
    PYTHON=python
    echo -e " ${GREEN}found${NC}"
else
    echo -e " ${RED}not found${NC}"
    echo "[!] Installing Python..."
    if [ "$PLATFORM" = "termux" ]; then
        pkg install python -y
    else
        apt update && apt install python3 python3-pip -y
    fi
    PYTHON=python3
fi

# Install dependencies
echo -e "\n[*] Installing Python dependencies..."
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r requirements.txt 2>/dev/null || true

# Make main script executable
chmod +x memory_forge.py

# Create symlink (optional)
if [ "$PLATFORM" = "linux" ]; then
    if [ -d "/usr/local/bin" ]; then
        ln -sf "$(pwd)/memory_forge.py" /usr/local/bin/memoryforge 2>/dev/null || true
        echo -e "${GREEN}[✓] Installed to /usr/local/bin/memoryforge${NC}"
    fi
fi

echo -e "\n${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Installation Complete! 🚀            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo "  Run with:"
echo "    sudo $PYTHON memory_forge.py              # Interactive mode"
echo "    sudo $PYTHON memory_forge.py --list       # List processes"
echo "    sudo $PYTHON memory_forge.py -n firefox   # Target by name"
echo "    sudo $PYTHON memory_forge.py -p 1234      # Target by PID"
echo ""
echo "  NOTE: Root access required for memory operations!"
