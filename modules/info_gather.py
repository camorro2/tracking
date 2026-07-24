#!/usr/bin/env python3

"""
Camoro - Information Gathering Module (v2)
Uses Instagram public API properly
"""

import requests
import json
import os
import sys
import time
import re
import random
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
NC = '\033[0m'

# Real mobile user agents
USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; OnePlus 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36',
]

class InstagramInfoGatherer:
    """Professional Instagram info gatherer using real API endpoints."""
    
    def __init__(self, username):
        self.username = username
        self.session = requests.Session()
        self.csrf_token = None
        self.user_id = None
        
    def init_session(self):
        """Initialize a real browser-like session."""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5,ar;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        
        try:
            # Step 1: Visit homepage to get cookies
            resp = self.session.get('https://www.instagram.com/', headers=headers, timeout=15)
            time.sleep(random.uniform(1, 2))
            
            # Extract CSRF token
            for cookie in self.session.cookies:
                if cookie.name == 'csrftoken':
                    self.csrf_token = cookie.value
                    break
            
            if not self.csrf_token:
                # Extract from HTML
                match = re.search(r'csrf_token["\']:\s*["\']([^"\']+)', resp.text)
                if match:
                    self.csrf_token = match.group(1)
            
            if self.csrf_token:
                print(f"{GREEN}[✓] Session initialized | CSRF: {self.csrf_token[:8]}...{NC}")
                return True
            
            # Fallback: get from login page
            resp2 = self.session.get('https://www.instagram.com/accounts/login/', 
                                     headers={'User-Agent': random.choice(USER_AGENTS)}, 
                                     timeout=15)
            for cookie in self.session.cookies:
                if cookie.name == 'csrftoken':
                    self.csrf_token = cookie.value
                    return True
            
            return False
            
        except Exception as e:
            print(f"{RED}[!] Session init failed: {e}{NC}")
            return False
    
    def get_user_info_api(self):
        """Try the Instagram API directly - most reliable method."""
        
        api_url = f'https://i.instagram.com/api/v1/users/web_profile_info/?username={self.username}'
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-CSRFToken': self.csrf_token or '',
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://www.instagram.com/{self.username}/',
            'Connection': 'keep-alive',
        }
        
        try:
            resp = self.session.get(api_url, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                user = data.get('data', {}).get('user', {})
                
                if user:
                    info = {
                        'username': user.get('username', self.username),
                        'full_name': user.get('full_name', ''),
                        'biography': user.get('biography', ''),
                        'followers_count': user.get('edge_followed_by', {}).get('count', 0),
                        'following_count': user.get('edge_follow', {}).get('count', 0),
                        'posts_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'is_private': user.get('is_private', False),
                        'is_verified': user.get('is_verified', False),
                        'is_business': user.get('is_business_account', False),
                        'profile_pic': user.get('profile_pic_url_hd', ''),
                        'external_url': user.get('external_url', ''),
                        'business_category': user.get('business_category_name', ''),
                        'extracted_at': datetime.now().isoformat(),
                        'source': 'api_v1_web_profile_info'
                    }
                    
                    # Extract bio links
                    bio_links = user.get('bio_links', [])
                    if bio_links:
                        info['biography_links'] = [link.get('url', '') for link in bio_links if link.get('url')]
                    
                    return info
            
            return None
            
        except Exception as e:
            print(f"{YELLOW}[!] API method failed: {e}{NC}")
            return None
    
    def get_user_info_graphql(self):
        """Alternative: Instagram GraphQL API."""
        
        # This is the query Instagram uses internally
        query_hash = '56a7068fea504063273cc2120ffd54f3'  # This changes periodically
        
        variables = json.dumps({
            'username': self.username,
            'first': 12
        })
        
        url = f'https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={variables}'
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-CSRFToken': self.csrf_token or '',
            'X-Instagram-AJAX': '1',
            'Referer': f'https://www.instagram.com/{self.username}/',
        }
        
        try:
            resp = self.session.get(url, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                user = data.get('data', {}).get('user', {})
                
                if user:
                    info = {
                        'username': user.get('username', self.username),
                        'full_name': user.get('full_name', ''),
                        'biography': user.get('biography', ''),
                        'followers_count': user.get('edge_followed_by', {}).get('count', 0),
                        'following_count': user.get('edge_follow', {}).get('count', 0),
                        'posts_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'is_private': user.get('is_private', False),
                        'is_verified': user.get('is_verified', False),
                        'is_business': user.get('is_business_account', False),
                        'profile_pic': user.get('profile_pic_url_hd', ''),
                        'extracted_at': datetime.now().isoformat(),
                        'source': 'graphql_query'
                    }
                    return info
            
            return None
            
        except Exception as e:
            print(f"{YELLOW}[!] GraphQL method failed: {e}{NC}")
            return None
    
    def get_user_info_fallback(self):
        """Last resort: try to extract what we can from the HTML."""
        url = f'https://www.instagram.com/{self.username}/'
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.instagram.com/',
        }
        
        try:
            resp = self.session.get(url, headers=headers, timeout=15)
            
            if resp.status_code == 404:
                print(f"{RED}[!] User '{self.username}' not found!{NC}")
                return None
            
            info = {'username': self.username, 'source': 'html_fallback'}
            
            # Try to get meta description
            match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', resp.text)
            if match:
                desc = match.group(1)
                info['meta_description'] = desc
                
                # Try to parse followers/following from description
                followers_match = re.search(r'([\d,]+)\s*Followers?', desc)
                following_match = re.search(r'([\d,]+)\s*Following?', desc)
                posts_match = re.search(r'([\d,]+)\s*Posts?', desc)
                
                if followers_match:
                    info['followers_count'] = followers_match.group(1).replace(',', '')
                if following_match:
                    info['following_count'] = following_match.group(1).replace(',', '')
                if posts_match:
                    info['posts_count'] = posts_match.group(1).replace(',', '')
            
            # Try to get og:title for full name
            match = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', resp.text)
            if match:
                title = match.group(1)
                # Usually format: "Full Name (@username)"
                name_match = re.search(r'^([^(]+)', title)
                if name_match:
                    info['full_name'] = name_match.group(1).strip()
            
            # Try to get profile pic
            match = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', resp.text)
            if match:
                info['profile_pic'] = match.group(1)
            
            info['extracted_at'] = datetime.now().isoformat()
            
            return info
            
        except Exception as e:
            print(f"{RED}[!] Fallback method failed: {e}{NC}")
            return None
    
    def gather(self):
        """Try all methods in order of reliability."""
        
        info = None
        
        # Method 1: Official API (most reliable)
        print(f"{CYAN}[*] {WHITE}Method 1: Instagram API...{NC}")
        info = self.get_user_info_api()
        
        if info:
            print(f"{GREEN}[✓] API method succeeded!{NC}")
            return info
        
        # Method 2: Re-init session and try GraphQL
        print(f"{YELLOW}[!] API failed. Trying GraphQL...{NC}")
        time.sleep(2)
        
        # Fresh session
        self.session = requests.Session()
        self.init_session()
        time.sleep(1)
        
        info = self.get_user_info_graphql()
        
        if info:
            print(f"{GREEN}[✓] GraphQL method succeeded!{NC}")
            return info
        
        # Method 3: HTML fallback
        print(f"{YELLOW}[!] GraphQL failed. Trying HTML extraction...{NC}")
        time.sleep(2)
        
        info = self.get_user_info_fallback()
        
        if info and len(info) > 2:  # Got something useful
            print(f"{GREEN}[✓] HTML fallback extracted some data{NC}")
            return info
        
        # Method 4: Try with Instagram basic display API (no auth needed)
        print(f"{YELLOW}[!] Trying Instagram basic display API...{NC}")
        time.sleep(1)
        
        try:
            basic_url = f'https://www.instagram.com/{self.username}/?__a=1&__d=1'
            resp = self.session.get(basic_url, 
                                    headers={'User-Agent': random.choice(USER_AGENTS)},
                                    timeout=15)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if 'graphql' in data:
                        user = data['graphql']['user']
                        info = {
                            'username': user.get('username'),
                            'full_name': user.get('full_name'),
                            'biography': user.get('biography'),
                            'followers_count': user.get('edge_followed_by', {}).get('count'),
                            'following_count': user.get('edge_follow', {}).get('count'),
                            'posts_count': user.get('edge_owner_to_timeline_media', {}).get('count'),
                            'is_private': user.get('is_private'),
                            'is_verified': user.get('is_verified'),
                            'is_business': user.get('is_business_account'),
                            'profile_pic': user.get('profile_pic_url_hd'),
                            'extracted_at': datetime.now().isoformat(),
                            'source': 'basic_display_api'
                        }
                        print(f"{GREEN}[✓] Basic display API succeeded!{NC}")
                        return info
                except:
                    pass
        except:
            pass
        
        return None
    
    def save_info(self, info):
        """Save gathered information."""
        user_dir = os.path.join(RESULTS_DIR, self.username)
        os.makedirs(user_dir, exist_ok=True)
        
        filepath = os.path.join(user_dir, 'info.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"{GREEN}[✓] Saved to: {filepath}{NC}")
        return filepath
    
    def display_info(self, info):
        """Display gathered info beautifully."""
        print(f"\n{CYAN}╔{'═'*50}╗{NC}")
        print(f"{CYAN}║{' ' * 17}📊 INSTAGRAM PROFILE{' ' * 17}║{NC}")
        print(f"{CYAN}╚{'═'*50}╝{NC}")
        
        fields = [
            ('Username', 'username'),
            ('Full Name', 'full_name'),
            ('Bio', 'biography'),
            ('Posts', 'posts_count'),
            ('Followers', 'followers_count'),
            ('Following', 'following_count'),
            ('Private', 'is_private'),
            ('Verified', 'is_verified'),
            ('Business', 'is_business'),
            ('Category', 'business_category'),
            ('External URL', 'external_url'),
            ('Source', 'source'),
        ]
        
        for label, key in fields:
            value = info.get(key)
            if value is not None and value != '':
                if isinstance(value, bool):
                    value = '✅ Yes' if value else '❌ No'
                print(f"  {YELLOW}{label}:{NC} {WHITE}{value}{NC}")
        
        print(f"\n{YELLOW}[*] Bio links:{NC}")
        for link in info.get('biography_links', []):
            print(f"  {CYAN}→{NC} {link}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Camoro - Info Gatherer v2')
    parser.add_argument('--username', '-u', required=True, help='Target username')
    args = parser.parse_args()
    
    print(f"\n{CYAN}╔{'═'*50}╗{NC}")
    print(f"{CYAN}║{' ' * 12}🔍 CAMORO INFO GATHERER v2{' ' * 14}║{NC}")
    print(f"{CYAN}╚{'═'*50}╝{NC}\n")
    
    gatherer = InstagramInfoGatherer(args.username)
    
    print(f"{YELLOW}[*] Target: {WHITE}{args.username}{NC}")
    print(f"{YELLOW}[*] Initializing session...{NC}")
    
    if not gatherer.init_session():
        print(f"{RED}[!] Session init failed. Trying anyway...{NC}")
    
    print()
    info = gatherer.gather()
    
    if info:
        gatherer.save_info(info)
        gatherer.display_info(info)
        print(f"\n{GREEN}[✓] Information gathered successfully!{NC}")
        sys.exit(0)
    else:
        print(f"\n{RED}╔{'═'*50}╗{NC}")
        print(f"{RED}║{' ' * 10}❌ FAILED TO GATHER INFORMATION{' ' * 10}║{NC}")
        print(f"{RED}╚{'═'*50}╝{NC}")
        print(f"\n{YELLOW}[!] Possible reasons:{NC}")
        print(f"  {RED}→{NC} The account does not exist")
        print(f"  {RED}→{NC} Instagram is blocking automated requests")
        print(f"  {RED}→{NC} Network/VPN issues")
        print(f"  {RED}→{NC} Account might have been suspended")
        print(f"\n{YELLOW}[*] Suggestions:{NC}")
        print(f"  {CYAN}1.{NC} Make sure the username is correct")
        print(f"  {CYAN}2.{NC} Try using a VPN or different network")
        print(f"  {CYAN}3.{NC} If account is private, info will be limited")
        print(f"  {CYAN}4.{NC} Try again after 15-30 minutes")
        sys.exit(1)
