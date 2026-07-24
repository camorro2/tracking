#!/usr/bin/env python3
"""
محرك توليد كلمات المرور بالذكاء الاصطناعي
يحاكي تفكير الإنسان في اختيار كلمات المرور:
- تحليل الاسم، تاريخ الميلاد، المدينة
- دمج الكلمات مع أرقام ورموز
- أنماط شائعة في العالم العربي
- كلمات مرور شائعة مخصصة
"""

import json
import os
import re
import sys
import random
import itertools
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent.resolve()
RESULTS_DIR = BASE_DIR / 'results'

CYAN = '\033[0;36m'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
NC = '\033[0m'


class PasswordGenerator:
    """
    مولد كلمات المرور الذكي
    يفكر مثل الإنسان في اختيار كلمة المرور
    """

    def __init__(self, username, info):
        self.username = username.strip().lower()
        self.info = info

        # استخراج البيانات الأساسية
        self.full_name = info.get('full_name', '')
        self.biography = info.get('biography', '')
        self.real_name = info.get('real_name', info.get('extra', {}).get('real_name', ''))
        self.birthdate = info.get('birthdate', info.get('extra', {}).get('birthdate', ''))
        self.city = info.get('city', info.get('extra', {}).get('city', ''))
        self.partner = info.get('partner_name', info.get('extra', {}).get('partner_name', ''))
        self.pet = info.get('pet_name', info.get('extra', {}).get('pet_name', ''))
        self.child = info.get('child_name', info.get('extra', {}).get('child_name', ''))
        self.hobby = info.get('hobby', info.get('extra', {}).get('hobby', ''))
        self.fav_number = info.get('fav_number', info.get('extra', {}).get('fav_number', ''))
        self.fav_color = info.get('fav_color', info.get('extra', {}).get('fav_color', ''))
        self.fav_team = info.get('fav_team', info.get('extra', {}).get('fav_team', ''))
        self.fav_artist = info.get('fav_artist', info.get('extra', {}).get('fav_artist', ''))
        self.fav_food = info.get('fav_food', info.get('extra', {}).get('fav_food', ''))
        self.phone = info.get('phone_number', info.get('extra', {}).get('phone_number', ''))
        self.keyword = info.get('keyword', info.get('extra', {}).get('keyword', ''))

        # تحليل الاسم
        self.name_parts = self._parse_name()
        self.birth_parts = self._parse_birthdate()

    def _parse_name(self):
        """تحليل الاسم إلى أجزاء"""
        name = self.real_name or self.full_name
        parts = []

        if name:
            # تقسيم الاسم
            for part in name.split():
                p = part.strip().lower()
                if len(p) >= 2:
                    parts.append(p)

        # أضف اليوزرنيم
        parts.append(self.username.lower())

        return parts

    def _parse_birthdate(self):
        """تحليل تاريخ الميلاد"""
        parts = {}
        if not self.birthdate:
            return parts

        bd = self.birthdate.strip()

        # YYYY-MM-DD
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})', bd)
        if match:
            parts['year_full'] = match.group(1)
            parts['year_short'] = match.group(1)[2:]
            parts['month'] = match.group(2)
            parts['day'] = match.group(3)
            parts['month_num'] = match.group(2)
            parts['day_num'] = match.group(3)

        # DD/MM/YYYY
        match = re.match(r'(\d{2})/(\d{2})/(\d{4})', bd)
        if match:
            parts['day'] = match.group(1)
            parts['month'] = match.group(2)
            parts['year_full'] = match.group(3)
            parts['year_short'] = match.group(3)[2:]

        # فقط سنة
        match = re.match(r'(\d{4})', bd)
        if match:
            parts['year_full'] = match.group(1)
            parts['year_short'] = match.group(1)[2:]

        return parts

    def _get_keywords(self):
        """استخراج الكلمات المفتاحية من كل البيانات"""
        keywords = set()

        # من الاسم
        for part in self.name_parts:
            keywords.add(part)
            # تنويعات
            keywords.add(part.capitalize())
            keywords.add(part.upper())
            keywords.add(part.title())

        # كلمات من البايو
        if self.biography:
            bio_words = re.findall(r'\b\w{3,}\b', self.biography.lower())
            for w in bio_words[:20]:
                if w not in ('the', 'and', 'for', 'that', 'with', 'this', 'from'):
                    keywords.add(w)

        # من المدينة
        if self.city:
            c = self.city.lower().strip()
            keywords.add(c)
            keywords.add(c.capitalize())

        # من الهواية
        if self.hobby:
            h = self.hobby.lower().strip()
            keywords.add(h)
            keywords.add(h.capitalize())

        # من الفريق
        if self.fav_team:
            t = self.fav_team.lower().strip()
            keywords.add(t)
            keywords.add(t.capitalize())

        # من الفنان
        if self.fav_artist:
            a = self.fav_artist.lower().strip()
            for part in a.split():
                keywords.add(part)
                keywords.add(part.capitalize())

        # من اسم الشريك
        if self.partner:
            p = self.partner.lower().strip()
            for part in p.split():
                keywords.add(part)
                keywords.add(part.capitalize())

        # من الطفل
        if self.child:
            keywords.add(self.child.lower())
            keywords.add(self.child.capitalize())

        # من الحيوان
        if self.pet:
            keywords.add(self.pet.lower())
            keywords.add(self.pet.capitalize())

        # من اللون
        if self.fav_color:
            keywords.add(self.fav_color.lower())

        # من الأكل
        if self.fav_food:
            keywords.add(self.fav_food.lower())

        # من الكلمة المفتاحية
        if self.keyword:
            keywords.add(self.keyword.lower())
            keywords.add(self.keyword.capitalize())

        # إزالة الكلمات القصيرة جداً
        keywords = {k for k in keywords if len(k) >= 2}

        return list(keywords)

    def _suffix_patterns(self):
        """أنماط اللواحق الشائعة"""
        current_year = datetime.now().year

        suffixes = []

        # سنوات الميلاد
        if 'year_full' in self.birth_parts:
            suffixes.append(self.birth_parts['year_full'])
            suffixes.append(self.birth_parts['year_short'])
            # سنة الميلاد + أرقام
            suffixes.append(f"{self.birth_parts['year_short']}{self.birth_parts.get('day', '01')}")
            suffixes.append(f"{self.birth_parts['year_short']}{self.birth_parts.get('month', '01')}")
            # عكس
            suffixes.append(self.birth_parts['year_full'][::-1])

        # السنة الحالية
        for y in range(current_year - 3, current_year + 1):
            suffixes.append(str(y))
            suffixes.append(str(y)[2:])

        # أرقام شائعة
        common_nums = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            '10', '11', '12', '13', '14', '15', '16', '18', '19', '20',
            '21', '22', '23', '24', '25', '30', '31',
            '69', '96', '99', '100',
            '007', '101', '111', '123', '200', '222', '300',
            '333', '404', '420', '444', '500', '555', '666',
            '777', '786', '888', '911', '999',
            '000', '0000', '1111', '2222', '3333', '4444',
            '5555', '6666', '7777', '8888', '9999',
            '1234', '12345', '123456', '1234567', '12345678',
            '1122', '1212', '1313',
            '2000', '2001', '2002', '2003', '2004', '2005',
            '1990', '1991', '1992', '1993', '1994', '1995',
            '1996', '1997', '1998', '1999',
            '2010', '2011', '2012', '2013', '2014', '2015',
            '2016', '2017', '2018', '2019',
            '2020', '2021', '2022', '2023', '2024', '2025', '2026',
        ]

        # إذا كان رقم مفضل
        if self.fav_number:
            common_nums.insert(0, self.fav_number)

        # أرقام هاتف
        if self.phone:
            phone_digits = re.sub(r'\D', '', self.phone)
            if len(phone_digits) >= 4:
                for i in range(0, len(phone_digits) - 3):
                    common_nums.append(phone_digits[i:i+4])

        suffixes.extend(common_nums)

        # رموز
        symbols = ['!', '@', '#', '$', '%', '&', '*', '_', '-', '.', '?']
        suffixes.extend(symbols)
        suffixes.extend([f'{n}{s}' for n in common_nums[:20] for s in symbols[:3]])

        return list(set(suffixes))

    def generate(self, target_count=20000):
        """
        توليد كلمات المرور
        يستخدم 10 مراحل مختلفة لمحاكاة تفكير الإنسان
        """
        print(f"\n{CYAN}[*] {WHITE}بدء توليد كلمات المرور...{NC}\n")
        passwords = set()
        keywords = self._get_keywords()
        suffixes = self._suffix_patterns()

        # =============================================
        # المرحلة 1: الكلمات الأساسية مباشرة
        # =============================================
        print(f"  {CYAN}[1/10]{NC} الكلمات الأساسية...")
        for kw in keywords:
            passwords.add(kw)
            # مع أرقام بسيطة
            for num in ['1', '123', '1234', '12345', '123456']:
                passwords.add(f"{kw}{num}")
                passwords.add(f"{num}{kw}")

        # =============================================
        # المرحلة 2: دمج أجزاء الاسم
        # =============================================
        print(f"  {CYAN}[2/10]{NC} دمج أجزاء الاسم...")
        for i, part1 in enumerate(self.name_parts):
            for part2 in self.name_parts[i+1:]:
                passwords.add(f"{part1}{part2}")
                passwords.add(f"{part2}{part1}")
                passwords.add(f"{part1}_{part2}")
                passwords.add(f"{part1}.{part2}")
                # بالأحرف الأولى
                if len(part1) > 0 and len(part2) > 0:
                    passwords.add(f"{part1[0]}{part2}")
                    passwords.add(f"{part2[0]}{part1}")

        # =============================================
        # المرحلة 3: لواحق متنوعة على الكلمات
        # =============================================
        print(f"  {CYAN}[3/10]{NC} إضافة اللواحق...")
        for kw in keywords[:30]:
            for suffix in suffixes[:100]:
                passwords.add(f"{kw}{suffix}")
                passwords.add(f"{kw}_{suffix}")
                passwords.add(f"{kw}.{suffix}")

        # =============================================
        # المرحلة 4: أنماط تاريخ الميلاد
        # =============================================
        print(f"  {CYAN}[4/10]{NC} أنماط تاريخ الميلاد...")
        if self.birth_parts:
            bp = self.birth_parts
            bd_patterns = []

            if 'day' in bp and 'month' in bp and 'year_full' in bp:
                bd_patterns.extend([
                    f"{bp['day']}{bp['month']}{bp['year_full']}",
                    f"{bp['day']}{bp['month']}{bp['year_short']}",
                    f"{bp['month']}{bp['day']}{bp['year_full']}",
                    f"{bp['month']}{bp['day']}{bp['year_short']}",
                    f"{bp['year_full']}{bp['month']}{bp['day']}",
                    f"{bp['year_short']}{bp['month']}{bp['day']}",
                    f"{bp['day']}-{bp['month']}-{bp['year_full']}",
                    f"{bp['day']}/{bp['month']}/{bp['year_full']}",
                ])

            if 'year_full' in bp:
                bd_patterns.append(bp['year_full'])
                bd_patterns.append(bp['year_full'][::-1])

            for pattern in bd_patterns:
                passwords.add(pattern)
                # مع كلمات
                for kw in keywords[:5]:
                    passwords.add(f"{kw}{pattern}")
                    passwords.add(f"{pattern}{kw}")

        # =============================================
        # المرحلة 5: كلمات مرور شائعة
        # =============================================
        print(f"  {CYAN}[5/10]{NC} كلمات المرور الشائعة...")
        common_passwords = [
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'monkey', 'dragon', 'master', 'login', 'princess',
            'football', 'shadow', 'sunshine', 'trustno1', 'iloveyou',
            'batman', 'superman', 'starwars', 'pokemon', 'naruto',
            '111111', '000000', 'letmein', 'access', 'secret',
            'hello', 'charlie', 'michael', 'andrew', 'joshua',
            # عربية
            'ahmed', 'mohamed', 'ali', 'omar', 'hassan',
            'sara', 'nour', 'laila', 'fatima', 'amira',
            'love', 'life', 'baby', 'angel', 'happy',
            'soccer', 'basket', 'gaming', 'music', 'dance',
            'instagram', 'facebook', 'snapchat', 'tiktok', 'twitter',
            'password1', 'password123', 'admin', 'root', 'user',
            '123', '1234', '12345', '123456', '1234567', '123456789',
            'qwerty123', 'qwerty1', 'abc1234', 'login1',
        ]
        for pwd in common_passwords:
            passwords.add(pwd)
            passwords.add(pwd.capitalize())

        # =============================================
        # المرحلة 6: دمج الكلمات مع بعضها
        # =============================================
        print(f"  {CYAN}[6/10]{NC} دمج الكلمات...")
        combos = ['love', 'life', 'king', 'queen', 'star', 'sun', 'moon',
                   'fire', 'water', 'dream', 'hope', 'soul', 'heart',
                   'red', 'blue', 'gold', 'dark', 'light', 'black', 'white',
                   'cool', 'hot', 'fast', 'slow', 'big', 'small', 'good',
                   'bad', 'real', 'fake', 'new', 'old', 'happy', 'sad']

        for kw in keywords[:15]:
            for combo in combos[:20]:
                passwords.add(f"{kw}{combo}")
                passwords.add(f"{combo}{kw}")
                passwords.add(f"{kw}_{combo}")
                passwords.add(f"{combo}_{kw}")

        # =============================================
        # المرحلة 7: أنماط Instagram خاصة
        # =============================================
        print(f"  {CYAN}[7/10]{NC} أنماط Instagram...")
        ig_patterns = [
            f"insta{self.username}", f"{self.username}insta",
            f"ig_{self.username}", f"{self.username}_ig",
            f"gram{self.username}", f"{self.username}gram",
            f"insta", f"instagram", f"igram",
            f"follow{self.username}", f"{self.username}follow",
        ]
        for p in ig_patterns:
            passwords.add(p)
            passwords.add(f"{p}1")
            passwords.add(f"{p}123")
            passwords.add(f"{p}!")

        # =============================================
        # المرحلة 8: أنماط تكرار الأحرف
        # =============================================
        print(f"  {CYAN}[8/10]{NC} أنماط التكرار...")
        for kw in keywords[:10]:
            if len(kw) >= 3:
                # تكرار
                passwords.add(kw * 2)
                passwords.add(kw * 3)
                # عكس
                passwords.add(kw[::-1])
                # حذف حروف العلة
                no_vowels = re.sub(r'[aeiou]', '', kw, flags=re.I)
                if no_vowels and len(no_vowels) >= 2:
                    passwords.add(no_vowels)

        # =============================================
        # المرحلة 9: Leet speak
        # =============================================
        print(f"  {CYAN}[9/10]{NC} Leet speak...")
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        for kw in keywords[:15]:
            leet = ''.join(leet_map.get(c.lower(), c) for c in kw)
            if leet != kw:
                passwords.add(leet)
                passwords.add(f"{leet}!")

        # =============================================
        # المرحلة 10: إثراء نهائي
        # =============================================
        print(f"  {CYAN}[10/10]{NC} الإثراء النهائي...")
        current_set = list(passwords)

        # أضف تنويعات
        for pwd in current_set[:10000]:
            if len(pwd) < 20:
                # حرف كبير في البداية
                passwords.add(pwd.capitalize())
                # كله كبير
                passwords.add(pwd.upper())
                # كله صغير
                passwords.add(pwd.lower())
                # إضافة علامة تعجب
                passwords.add(f"{pwd}!")
                passwords.add(f"!{pwd}")
                # إضافة أرقام في النهاية
                for n in ['1', '2', '3', '7', '10', '12', '21', '99', '100', '123']:
                    passwords.add(f"{pwd}{n}")

        # === التنقية النهائية ===
        valid_passwords = set()
        for pwd in passwords:
            pwd = str(pwd).strip()
            if 4 <= len(pwd) <= 64 and not pwd.isspace():
                valid_passwords.add(pwd)

        # ترتيب عشوائي وقص إلى العدد المطلوب
        password_list = list(valid_passwords)
        random.shuffle(password_list)

        if len(password_list) > target_count:
            password_list = password_list[:target_count]
        elif len(password_list) < target_count:
            # أضف المزيد من التنويعات العشوائية
            base = password_list.copy()
            needed = target_count - len(password_list)
            for pwd in base:
                for suffix in suffixes[:50]:
                    if len(password_list) >= target_count:
                        break
                    password_list.append(f"{pwd}{suffix}")
                if len(password_list) >= target_count:
                    break

        # خلط نهائي
        random.shuffle(password_list)

        actual_count = len(password_list)
        print(f"\n{GREEN}[✓] تم توليد {actual_count:,} كلمة مرور{NC}")

        return password_list

    def save(self, passwords):
        """حفظ كلمات المرور في ملف"""
        user_dir = RESULTS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)

        filepath = user_dir / 'passwords.txt'
        with open(filepath, 'w', encoding='utf-8') as f:
            for pwd in passwords:
                f.write(f"{pwd}\n")

        print(f"{GREEN}[✓] تم الحفظ: {filepath}{NC}")
        return filepath
