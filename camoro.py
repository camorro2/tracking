#!/data/data/com.termux/files/usr/bin/bash
# Camoro launcher
set -e
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 camoro.py "$@"
else
  python camoro.py "$@"
fi
