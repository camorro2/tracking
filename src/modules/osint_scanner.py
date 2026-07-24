#!/usr/bin/env python3
"""
OSINT Scanner - Module for comprehensive Instagram OSINT
"""

import requests
import re
import json
import time
from fake_useragent import UserAgent

class OSINTScanner:
    def __init__(self, username):
        self.username = username
        self.data = {}
        self.ua = UserAgent()
        self.session = requests.Session()
    
    def scan(self):
        """الفحص الكامل متعدد الطبقات"""
        
        # الطبقة 1: معلومات أساسية
        info = self._basic_info()
        if not info:
            return None
        self.data.update(info)
        
        # الطبقة 2: تحليل النصوص
        self.data['emails'] = self._extract_emails()
        self.data['phones'] = self._extract_phones()
        self.data['keywords'] = self._extract_keywords()
        
        # الطبقة 3: معلومات شخصية
        self.data['personal_info'] = self._personal_info()
        
        # الطبقة 4: أنماط تاريخية
        self.data['date_patterns'] = self._date_patterns()
        
        return self.data
    
    def _basic_info(self):
        """جلب المعلومات الأساسية عبر API متعددة"""
        
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'x-ig-app-id': '936619743392459',
        }
        
        # المحاولة الأولى: API web
        try:
            url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
            resp = self.session.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                user = data.get('data', {}).get('user', {})
                
                return {
                    'username': self.username,
                    'full_name': user.get('full_name', ''),
                    'biography': user.get('biography', ''),
                    'follower_count': user.get('edge_followed_by', {}).get('count', 0),
                    'following_count': user.get('edge_follow', {}).get('count', 0),
                    'post_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'is_private': user.get('is_private', False),
                    'is_verified': user.get('is_verified', False),
                    'profile_pic': user.get('profile_pic_url', ''),
                    'external_url': user.get('external_url', ''),
                }
        except:
            pass
        
        # المحاولة الثانية: طريقة قديمة
        try:
            url2 = f"https://www.instagram.com/{self.username}/?__a=1"
            resp2 = self.session.get(url2, headers=headers, timeout=10)
            
            if resp2.status_code == 200:
                content = resp2.text
                # محاولة استخراج JSON من الصفحة
                import html
                # البحث عن window.__INITIAL_STATE__
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', content, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    user = data.get('settings', {}).get('viewer', {}) or \
                           list(data.get('users', {}).values())[0] if data.get('users') else {}
                    
                    return {
                        'username': self.username,
                        'full_name': user.get('full_name', ''),
                        'biography': user.get('biography', ''),
                        'follower_count': user.get('follower_count', 0),
                        'is_verified': user.get('is_verified', False),
                    }
        except:
            pass
        
        return None
    
    def _extract_emails(self):
        """استخراج الإيميلات من البايو"""
        bio = self.data.get('biography', '')
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', bio)
        return emails
    
    def _extract_phones(self):
        """استخراج أرقام الهواتف"""
        bio = self.data.get('biography', '')
        phones = re.findall(r'(?:\+?[\d\-\(\)\s]){7,}', bio)
        return [p.strip() for p in phones if len(p.strip()) >= 7]
    
    def _extract_keywords(self):
        """استخراج الكلمات المفتاحية"""
        keywords = set()
        bio = self.data.get('biography', '')
        
        # الهاشتاغات
        hashtags = re.findall(r'#(\w+)', bio)
        keywords.update(hashtags)
        
        # المنشنات
        mentions = re.findall(r'@(\w+)', bio)
        keywords.update(mentions)
        
        # كلمات عربية وإنجليزية من النص
        words = re.findall(r'\b[a-zA-Z]{3,}\b', bio)
        keywords.update(words)
        
        arabic_words = re.findall(r'\b[\u0600-\u06FF]{2,}\b', bio)
        keywords.update(arabic_words)
        
        return list(keywords)
    
    def _personal_info(self):
        """استخراج معلومات شخصية من الاسم"""
        info = {}
        name = self.data.get('full_name', '')
        parts = name.split()
        
        if len(parts) >= 1:
            info['first_name'] = parts[0]
        if len(parts) >= 2:
            info['last_name'] = ' '.join(parts[1:])
        
        # محاولة استخراج سنة الميلاد من البايو
        bio = self.data.get('biography', '')
        years = re.findall(r'\b(19[0-9][0-9]|20[0-1][0-9]|202[0-5])\b', bio)
        if years:
            info['birth_year'] = years[0]
        
        return info
    
    def _date_patterns(self):
        """توليد أنماط تاريخية محتملة"""
        patterns = []
        name = self.data.get('full_name', '')
        bio = self.data.get('biography', '')
        
        # سنوات محتملة
        for year in range(1950, 2010):
            patterns.append(str(year))
        
        # أشهر وأيام محتملة
        months = ['01','02','03','04','05','06','07','08','09','10','11','12']
        days = [f'{d:02d}' for d in range(1,32)]
        
        return {
            'years': patterns[:50],  # اقتصار على 50 سنة
            'months': months,
            'days': days,
      }
