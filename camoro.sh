#!/bin/bash
# Camoro v5.0 Launcher

cd "$(dirname "$0")"

# تفعيل Tor إذا وجد
if command -v tor &> /dev/null; then
    tor &>/dev/null &
    privoxy &>/dev/null 2>&1 &
fi

# تشغيل الأداة
python3 camoro.py "$@"
