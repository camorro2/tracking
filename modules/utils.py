#!/usr/bin/env python3

"""
Camoro - Utilities Module
"""

import os
import sys
import subprocess

WORDLIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wordlists')
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')


def check_requirements():
    """تأكد من تثبيت المكتبات المطلوبة"""
    required = {
        'httpx': 'httpx[http2]',
        'colorama': 'colorama',
    }
    
    missing = []
    for module, pip_name in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        print(f"\033[91m[!] المكتبات التالية غير مثبتة:\033[0m")
        for m in missing:
            print(f"    \033[93m→\033[0m pip install {m}")
        print()
        answer = input("\033[93m[?] هل تريد تثبيتها الآن؟ (Y/N): \033[0m")
        if answer.lower() == 'y':
            for m in missing:
                print(f"\033[94m[*] جاري تثبيت {m}...\033[0m")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', m])
            print("\033[92m[✓] تم التثبيت بنجاح!\033[0m")
        else:
            print("\033[91m[!] لا يمكن الاستمرار بدون المكتبات\033[0m")
            sys.exit(1)
    
    return True


def ensure_dirs(username):
    """تأكد من وجود مجلد النتائج"""
    user_dir = os.path.join(RESULTS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def generate_common_wordlist():
    """توليد قائمة كلمات المرور الشائعة"""
    output_path = os.path.join(WORDLIST_DIR, 'common.txt')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    common = [
        "123456", "password", "123456789", "12345678", "12345",
        "1234567890", "1234", "1234567", "123123", "qwerty",
        "abc123", "football", "monkey", "iloveyou", "111111",
        "letmein", "trustno1", "dragon", "master", "sunshine",
        "princess", "welcome", "shadow", "ashley", "654321",
        "superman", "qazwsx", "michael", "baseball", "password1",
        "123321", "123qwe", "passw0rd", "zxcvbnm", "!@#$%^&*",
        "charlie", "donald", "starwars", "batman", "samsung",
        "123654", "lovely", "qwerty123", "hello", "naruto",
    ]
    
    with open(output_path, 'w') as f:
        for pwd in common:
            f.write(pwd + '\n')
    
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Camoro Utilities')
    parser.add_argument('--generate-wordlist', action='store_true', help='Generate common passwords')
    args = parser.parse_args()
    
    if args.generate_wordlist:
        check_requirements()
        path = generate_common_wordlist()
        print(f"[✓] Wordlist generated: {path}")
