#!/usr/bin/env python3

"""
Camoro - Information Gathering Module
Collects public Instagram profile information
"""

import requests
import re
import json
import os
import sys
import time
from datetime import datetime

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
NC = '\033[0m'

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5,ar;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'TE': 'trailers',
}


def extract_json_from_html(html_text):
    """Extract JSON data from Instagram's HTML page."""
    patterns = [
        r'window\._sharedData\s*=\s*({.*?});',
        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        r'<script type="application/json" data-content-len="\d+" data-sjs>({.*?})</script>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON-LD
    pattern = r'<script type="application/ld\+json">({.*?})</script>'
    match = re.search(pattern, html_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None


def scrape_public_profile(username):
    """Scrape public Instagram profile information."""
    url = f"https://www.instagram.com/{username}/"
    
    print(f"{CYAN}[*] {WHITE}Fetching profile: {YELLOW}{url}{NC}")
    
    session = requests.Session()
    
    try:
        # First request to get cookies
        response = session.get('https://www.instagram.com/', headers=HEADERS, timeout=15)
        time.sleep(1)
        
        # Second request for the profile
        response = session.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 404:
            print(f"{RED}[!] Profile not found: {username}{NC}")
            return None
        elif response.status_code == 429:
            print(f"{RED}[!] Rate limited. Waiting 60 seconds...{NC}")
            time.sleep(60)
            return scrape_public_profile(username)
        elif response.status_code != 200:
            print(f"{RED}[!] HTTP {response.status_code} error{NC}")
            return None
        
        # Extract data
        data = extract_json_from_html(response.text)
        
        if data is None:
            print(f"{YELLOW}[!] Trying alternative extraction method...{NC}")
            # Try to extract from meta tags
            name_match = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', response.text)
            desc_match = re.search(r'<meta[^>]*property="og:description"[^>]*content="([^"]+)"', response.text)
            img_match = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', response.text)
            
            if name_match and desc_match:
                info = {
                    'username': username,
                    'full_name': name_match.group(1).replace(' (@' + username + ')', '') if username in name_match.group(1) else name_match.group(1),
                    'description': desc_match.group(1),
                    'profile_pic': img_match.group(1) if img_match else None,
                    'extracted_at': datetime.now().isoformat(),
                    'note': 'Limited data - extracted from meta tags'
                }
                return info
            else:
                print(f"{RED}[!] Could not extract data from page{NC}")
                return None
        
        # Parse based on structure
        info = {}
        
        # Try graphql route
        if 'entry_data' in data:
            try:
                user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
                info = {
                    'username': user_data.get('username'),
                    'full_name': user_data.get('full_name'),
                    'biography': user_data.get('biography'),
                    'followers_count': user_data.get('edge_followed_by', {}).get('count'),
                    'following_count': user_data.get('edge_follow', {}).get('count'),
                    'posts_count': user_data.get('edge_owner_to_timeline_media', {}).get('count'),
                    'is_private': user_data.get('is_private'),
                    'is_verified': user_data.get('is_verified'),
                    'is_business': user_data.get('is_business_account'),
                    'external_url': user_data.get('external_url'),
                    'profile_pic': user_data.get('profile_pic_url_hd'),
                    'business_category': user_data.get('business_category_name'),
                    'biography_links': [link.get('url') for link in user_data.get('bio_links', [])],
                    'extracted_at': datetime.now().isoformat(),
                }
            except (KeyError, IndexError, TypeError) as e:
                print(f"{YELLOW}[!] GraphQL extraction failed: {e}{NC}")
                info = {'username': username, 'raw_data': str(data)[:500]}
        
        elif '__INITIAL_STATE__' in data or 'initial_state' in str(data).lower():
            # Try to extract what we can
            info = {
                'username': username,
                'raw_data': str(data)[:1000],
                'extracted_at': datetime.now().isoformat(),
                'note': 'Used INITIAL_STATE extraction'
            }
        
        return info
        
    except requests.exceptions.Timeout:
        print(f"{RED}[!] Connection timeout{NC}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"{RED}[!] Connection error - check internet{NC}")
        return None
    except Exception as e:
        print(f"{RED}[!] Unexpected error: {e}{NC}")
        return None


def save_info(username, info):
    """Save gathered information to file."""
    user_dir = os.path.join(RESULTS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    
    filepath = os.path.join(user_dir, 'info.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"{GREEN}[✓] Information saved to: {filepath}{NC}")
    return filepath


def display_info(info):
    """Display gathered information in a formatted way."""
    print(f"\n{CYAN}╔{'═'*50}╗{NC}")
    print(f"{CYAN}║{' ' * 18}📊 PROFILE INFO{' ' * 18}║{NC}")
    print(f"{CYAN}╚{'═'*50}╝{NC}")
    
    fields = {
        'username': 'Username',
        'full_name': 'Full Name',
        'biography': 'Bio',
        'followers_count': 'Followers',
        'following_count': 'Following',
        'posts_count': 'Posts',
        'is_private': 'Private',
        'is_verified': 'Verified',
        'is_business': 'Business',
        'external_url': 'External URL',
        'business_category': 'Category',
    }
    
    for key, label in fields.items():
        value = info.get(key)
        if value is not None and value != '':
            if isinstance(value, bool):
                value = '✅ Yes' if value else '❌ No'
            print(f"  {YELLOW}{label}:{NC} {WHITE}{value}{NC}")
    
    if 'biography_links' in info and info['biography_links']:
        print(f"  {YELLOW}Bio Links:{NC}")
        for link in info['biography_links']:
            print(f"    {CYAN}→{NC} {link}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Camoro - Instagram Info Gatherer')
    parser.add_argument('--username', '-u', required=True, help='Instagram username to target')
    args = parser.parse_args()
    
    print(f"\n{CYAN}╔{'═'*50}╗{NC}")
    print(f"{CYAN}║{' ' * 12}🔍 CAMORO INFORMATION GATHERING{' ' * 12}║{NC}")
    print(f"{CYAN}╚{'═'*50}╝{NC}\n")
    
    info = scrape_public_profile(args.username)
    
    if info:
        save_info(args.username, info)
        display_info(info)
        sys.exit(0)
    else:
        print(f"{RED}[!] Failed to gather information for: {args.username}{NC}")
        sys.exit(1)
