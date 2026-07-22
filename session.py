import os
import subprocess
import json
import time

class SessionModule:
    def __init__(self):
        self.sessions_dir = os.path.expanduser("~/camorro/sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.sessions_file = os.path.join(self.sessions_dir, "active_sessions.json")
    
    def run(self):
        while True:
            print("\n" + "─" * 50)
            print("  SESSION MANAGER")
            print("─" * 50)
            print("  [1] List Active Sessions")
            print("  [2] Start MSF Listener (Background)")
            print("  [3] Check Connected Devices")
            print("  [4] Manage Payloads")
            print("  [0] Back to Main Menu")
            print("─" * 50)
            
            choice = input("\n  Session > ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_sessions()
            elif choice == "2":
                self.start_background_listener()
            elif choice == "3":
                self.check_connected_devices()
            elif choice == "4":
                self.manage_payloads()
            else:
                print("  [!] Invalid option.")
    
    def list_sessions(self):
        print("\n  [*] Checking for active sessions...")
        
        # فحص جلسات Metasploit
        msf_cmd = "msfconsole -q -x 'sessions -l; exit' 2>/dev/null"
        result = subprocess.run(msf_cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout)
        else:
            print("  [!] No active Metasploit sessions.")
        
        # فحص Netcat sessions
        nc_cmd = "ps aux | grep -E 'nc -lvnp|ncat -lv' | grep -v grep"
        result = subprocess.run(nc_cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print("  [*] Active listeners:")
            print(result.stdout)
    
    def start_background_listener(self):
        lport = input("  Port to listen on: ").strip()
        protocol = input("  Protocol (tcp/udp, default: tcp): ").strip() or "tcp"
        
        print(f"\n  [*] Starting listener on port {lport}/{protocol}...")
        log_file = os.path.join(self.sessions_dir, f"listener_{lport}.log")
        
        if protocol == "tcp":
            os.system(f"ncat -lvnp {lport} > {log_file} 2>&1 &")
        else:
            os.system(f"ncat -lvnp {lport} -u > {log_file} 2>&1 &")
        
        print(f"  [+] Listener started in background (PID: check with 'ps aux | grep ncat')")
        print(f"  [+] Log file: {log_file}")
    
    def check_connected_devices(self):
        print("\n  [*] Checking connected devices...")
        
        # ADB devices
        print("\n  ─── ADB Devices ───")
        os.system("adb devices 2>/dev/null")
        
        # Network interfaces
        print("\n  ─── Network Interfaces ───")
        os.system("ip addr show | grep -E 'inet ' | grep -v 127.0.0.1")
        
        # Connected peers
        print("\n  ─── ARP Table ───")
        os.system("arp -a 2>/dev/null")
    
    def manage_payloads(self):
        payloads_dir = os.path.expanduser("~/camorro/payloads")
        
        print(f"\n  [*] Payloads directory: {payloads_dir}")
        
        if not os.path.exists(payloads_dir):
            print("  [!] No payloads directory found.")
            return
        
        files = os.listdir(payloads_dir)
        if files:
            print(f"\n  [*] Generated payloads ({len(files)}):")
            for i, f in enumerate(files, 1):
                filepath = os.path.join(payloads_dir, f)
                size = os.path.getsize(filepath)
                print(f"      {i}. {f} ({size/1024:.1f} KB)")
        else:
            print("  [!] No payloads generated yet.")
