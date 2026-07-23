# ⚡ DarkForge - Advanced PDF & Image Exploitation Framework

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Termux](https://img.shields.io/badge/Termux-Compatible-green)](https://termux.com)
[![Kali](https://img.shields.io/badge/Kali-Linux-blueviolet)](https://kali.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-red)](LICENSE)

**DarkForge** هو أقوى إطار عمل اختراق متخصص في ملفات **PDF** و 

*الصور**، مصمم خصيصًا لاختبارات الاختراق المصرح بها
██████╗ █████╗ ██████╗ ██╗ ██╗███████╗ ██████╗ ██████╗ ███████╗ ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██╔════╝ ██╔══██╗██╔════╝ ██╔════╝ ██║ ██║███████║██████╔╝█████╔╝ █████╗ ██║ ███╗██████╔╝██║ ███╗█████╗
██║ ██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝ ██║ ██║██╔══██╗██║ ██║██╔══╝
██████╔╝██║ ██║██║ ██║██║ ██╗██║ ╚██████╔╝██║ ██║╚██████╔╝███████╗ ╚═════╝ ╚═╝ ╚═╝╚═╝ ╚═╝╚═╝ ╚═════╝ ╚═╝ ╚═╝ ╚═════╝ ╚══════╝


## 🚀 المميزات

### 📄 هجمات PDF (13 تقنية مختلفة)
| التقنية | الوصف |
|---------|-------|
| JS Injection | حقن JavaScript لتحميل وتنفيذ بايلودات |
| Reverse Shell | اتصال عكسي مباشر عبر PDF |
| Credential Stealing | نافذة دخول مزيفة |
| CVE Exploitation | استغلال ثغرات Adobe Reader |
| Macro PDF | PDF مع فيجوال بيسك ماكرو |
| PDF Polyglot | دمج PDF مع أنواع ملفات أخرى |
| PDF Steganography | إخفاء بايلود داخل بيانات PDF |
| Form Exploitation | استغلال حقول PDF |
| Embedded File | تضمين ملف EXE داخل PDF |
| PDF Phishing | صفحات تصيد داخل PDF |
| Metadata Exploit | استغلال البيانات الوصفية |
| PDF XSS | ثغرات XSS داخل PDF |
| PDF Serialization | استغلال السيريلايزيشن |

### 🖼️ هجمات الصور (8 تقنيات مختلفة)
| التقنية | الوصف |
|---------|-------|
| LSB Steganography | إخفاء في البتات الأقل أهمية |
| Metadata Hiding | إخفاء في EXIF/metadata |
| Polyglot GIF/PNG/JPG | ملفات متعددة الصيغ |
| QR Code Exploit | أكواد QR خبيثة |
| Image Shell | Web shell داخل صورة |
| Pixel Encoding | تشفير في قيم البيكسلات |
| Palette Manipulation | التلاعب بلوحة الألوان |
| Image IDAT Exploit | استغلال IDAT chunks |

## 📦 التثبيت

### Termux (Android)
```bash
pkg update && pkg upgrade -y
pkg install python git wget curl -y
git clone https://github.com/yourusername/DarkForge.git
cd DarkForge
chmod +x setup.sh
./setup.sh
python run.py
