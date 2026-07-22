import os
import subprocess
import socket
import ipaddress

class ScannerModule:
    def __init__(self):
        self.results_dir = os.path.expanduser("~/camorro/scans")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run(self):
        while True:
            print("\n" + "─" * 50)
            print("  NETWORK SCANNER")
            print("─" * 50)
            print("  [1] Quick LAN Scan (ICMP/Ping)")
            print("  [2] Port Scan (Nmap)")
            print("  [3] Service Detection (Nmap -sV)")
            print("  [4] OS Detection")
            print("  [5] Get Device Info (Hostname, MAC, Open Ports)")
            print("  [6] Scan Specific IP Range")
            print("  [0] Back to Main Menu")
            print("─" * 50)
            
            choice = input("\n  Scanner > ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.quick_lan_scan()
            elif choice == "2":
                self.port_scan()
            elif choice == "3":
                self.service_detection()
            elif choice == "4":
                self.os_detection()
            elif choice == "5":
                self.device_info()
            elif choice == "6":
                self.ip_range_scan()
            else:
                print("  [!] Invalid option.")
    
    def get_network(self):
        """اكتشاف الشبكة المحلية"""
        try:
            # محاولة الحصول على الـ IP والـ subnet
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            
            # افتراض /24 subnet
            subnet = ".".join(ip.split(".")[:3]) + ".0/24"
            return ip, subnet
        except:
            return "127.0.0.1", "192.168.1.0/24"
    
    def quick_lan_scan(self):
        """مسح سريع باستخدام ping"""
        ip, subnet = self.get_network()
        print(f"\n  [*] Your IP: {ip}")
        print(f"  [*] Scanning: {subnet}")
        
        # استخدام fping أو ping
        cmd = f"fping -a -g {subnet} 2>/dev/null"
        print(f"\n  [*] Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            devices = result.stdout.strip().split("\n")
            print(f"\n  [+] Live hosts found: {len(devices)}")
            for i, device in enumerate(devices, 1):
                print(f"      {i}. {device}")
            
            # حفظ النتائج
            output_file = os.path.join(self.results_dir, "live_hosts.txt")
            with open(output_file, "w") as f:
                f.write(result.stdout)
            print(f"  [+] Results saved to: {output_file}")
        else:
            print("  [!] No live hosts found or fping not installed.")
            print("  [!] Install: pkg install fping")
    
    def port_scan(self):
        """مسح المنافذ باستخدام nmap"""
        target = input("  Target IP/Host: ").strip()
        ports = input("  Ports (default: 1-1000): ").strip() or "1-1000"
        
        cmd = f"nmap -p {ports} -T4 {target}"
        print(f"\n  [*] Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        print(result.stdout)
        
        # حفظ النتائج
        output_file = os.path.join(self.results_dir, f"portscan_{target.replace('.','_')}.txt")
        with open(output_file, "w") as f:
            f.write(result.stdout)
        print(f"  [+] Results saved to: {output_file}")
    
    def service_detection(self):
        target = input("  Target IP/Host: ").strip()
        cmd = f"nmap -sV -T4 {target}"
        print(f"\n  [*] Running service detection...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        print(result.stdout)
        
        output_file = os.path.join(self.results_dir, f"services_{target.replace('.','_')}.txt")
        with open(output_file, "w") as f:
            f.write(result.stdout)
        print(f"  [+] Results saved to: {output_file}")
    
    def os_detection(self):
        target = input("  Target IP/Host: ").strip()
        cmd = f"nmap -O -T4 {target}"
        print(f"\n  [*] Running OS detection...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        print(result.stdout)
    
    def device_info(self):
        target = input("  Target IP: ").strip()
        cmd = f"nmap -A -T4 {target}"
        print(f"\n  [*] Gathering device info...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
        print(result.stdout)
    
    def ip_range_scan(self):
        target = input("  Target IP Range (e.g., 192.168.1.0/24): ").strip()
        print(f"\n  [*] Scanning range: {target}")
        
        # مسح شامل
        cmd = f"nmap -sn {target}"
        print(f"  [*] Ping sweep: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        print(result.stdout)
