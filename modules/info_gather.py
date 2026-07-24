#!/usr/bin/env python3
"""Camoro - Information Gathering"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    print("[!] pip install httpx")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

G = "\033[0;32m"
R = "\033[0;31m"
C = "\033[0;36m"
Y = "\033[1;33m"
W = "\033[1;37m"
P = "\033[0;35m"
N = "\033[0m"

IG_APP_ID = "936619743392459"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]


class InfoGatherer:
    def __init__(self, username: str, proxy_manager=None) -> None:
        self.username = username.strip().lstrip("@").lower()
        self.proxy_manager = proxy_manager  # reserved; recon uses direct
        self.info: Dict[str, Any] = {
            "username": self.username,
            "exists": False,
            "blocked": False,
            "error": None,
            "full_name": "",
            "biography": "",
            "followers_count": 0,
            "following_count": 0,
            "posts_count": 0,
            "is_private": None,
            "is_verified": None,
            "is_business": None,
            "business_category": "",
            "external_url": "",
            "instagram_id": "",
            "profile_pic": "",
            "source": "",
            "collected_at": "",
        }

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "X-IG-App-ID": IG_APP_ID,
            "X-ASBD-ID": "129477",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
            "Origin": "https://www.instagram.com",
        }

    def _client(self) -> httpx.Client:
        # Recon = DIRECT (no Tor) — more reliable
        return httpx.Client(
            headers=self._headers(),
            timeout=httpx.Timeout(12.0, connect=6.0),
            follow_redirects=True,
            verify=False,
        )

    def _map_user(self, user: dict, source: str) -> Dict[str, Any]:
        followers = 0
        following = 0
        posts = 0
        efb = user.get("edge_followed_by") or {}
        efl = user.get("edge_follow") or {}
        eot = user.get("edge_owner_to_timeline_media") or {}
        if isinstance(efb, dict):
            followers = int(efb.get("count") or 0)
        if isinstance(efl, dict):
            following = int(efl.get("count") or 0)
        if isinstance(eot, dict):
            posts = int(eot.get("count") or 0)
        followers = followers or int(user.get("follower_count") or 0)
        following = following or int(user.get("following_count") or 0)
        posts = posts or int(user.get("media_count") or 0)
        return {
            "exists": True,
            "blocked": False,
            "error": None,
            "full_name": user.get("full_name") or "",
            "biography": user.get("biography") or "",
            "followers_count": followers,
            "following_count": following,
            "posts_count": posts,
            "is_private": bool(user.get("is_private", False)),
            "is_verified": bool(user.get("is_verified", False)),
            "is_business": bool(
                user.get("is_business_account", False) or user.get("is_business", False)
            ),
            "business_category": user.get("business_category_name")
            or user.get("category_name")
            or "",
            "external_url": user.get("external_url") or "",
            "instagram_id": str(user.get("id") or user.get("pk") or ""),
            "profile_pic": user.get("profile_pic_url_hd")
            or user.get("profile_pic_url")
            or "",
            "source": source,
        }

    def _try_ios_api(self) -> Optional[Dict[str, Any]]:
        url = (
            "https://i.instagram.com/api/v1/users/web_profile_info/"
            f"?username={self.username}"
        )
        try:
            with self._client() as c:
                try:
                    c.get("https://www.instagram.com/")
                except Exception:
                    pass
                r = c.get(url)
                if r.status_code == 404:
                    return {"exists": False, "blocked": False, "error": "not_found"}
                if r.status_code in (401, 403):
                    return {"exists": None, "blocked": True, "error": f"blocked_{r.status_code}"}
                if r.status_code == 429:
                    return {"exists": None, "blocked": True, "error": "rate_limit"}
                if r.status_code != 200:
                    return {"exists": None, "blocked": True, "error": f"http_{r.status_code}"}
                user = (r.json().get("data") or {}).get("user")
                if not user:
                    return {"exists": None, "blocked": True, "error": "empty"}
                return self._map_user(user, "i.instagram.com")
        except httpx.TimeoutException:
            return {"exists": None, "blocked": True, "error": "timeout"}
        except Exception as e:
            return {"exists": None, "blocked": True, "error": type(e).__name__}

    def _try_web_api(self) -> Optional[Dict[str, Any]]:
        url = (
            "https://www.instagram.com/api/v1/users/web_profile_info/"
            f"?username={self.username}"
        )
        try:
            with self._client() as c:
                try:
                    c.get("https://www.instagram.com/")
                except Exception:
                    pass
                r = c.get(url)
                if r.status_code == 404:
                    return {"exists": False, "blocked": False, "error": "not_found"}
                if r.status_code != 200:
                    return {"exists": None, "blocked": True, "error": f"http_{r.status_code}"}
                user = (r.json().get("data") or {}).get("user")
                if not user:
                    return None
                return self._map_user(user, "www.web_profile_info")
        except Exception:
            return None

    def _try_html(self) -> Optional[Dict[str, Any]]:
        url = f"https://www.instagram.com/{self.username}/"
        try:
            with self._client() as c:
                r = c.get(url, headers={**self._headers(), "Accept": "text/html"})
                html = r.text
                if r.status_code == 404 or "Sorry, this page isn't available" in html:
                    return {"exists": False, "blocked": False, "error": "not_found"}
                if r.status_code != 200:
                    return {"exists": None, "blocked": True, "error": f"http_{r.status_code}"}

                info: Dict[str, Any] = {
                    "exists": True,
                    "blocked": False,
                    "error": None,
                    "source": "html",
                }

                def grab(pat: str):
                    m = re.search(pat, html)
                    return m.group(1) if m else None

                title = grab(r'property="og:title" content="([^"]+)"')
                if title:
                    name = re.sub(r"\s*\(@[^)]+\).*", "", title)
                    name = re.sub(r"\s*[•·].*", "", name).strip()
                    if name and "instagram" not in name.lower():
                        info["full_name"] = name

                desc = grab(r'property="og:description" content="([^"]+)"') or grab(
                    r'name="description" content="([^"]+)"'
                )
                if desc:
                    m = re.search(
                        r"([\d,\.]+)\s*Followers?,\s*([\d,\.]+)\s*Following,\s*([\d,\.]+)\s*Posts?",
                        desc,
                        re.I,
                    )
                    if m:
                        def ph(s):
                            s = s.replace(",", "").lower()
                            if s.endswith("k"):
                                return int(float(s[:-1]) * 1000)
                            if s.endswith("m"):
                                return int(float(s[:-1]) * 1_000_000)
                            return int(float(s))

                        info["followers_count"] = ph(m.group(1))
                        info["following_count"] = ph(m.group(2))
                        info["posts_count"] = ph(m.group(3))
                        bio = re.sub(
                            r"^[\d,\.]+\s*Followers?,\s*[\d,\.]+\s*Following,\s*[\d,\.]+\s*Posts?\s*[-–—]?\s*",
                            "",
                            desc,
                            flags=re.I,
                        ).strip()
                        if bio:
                            info["biography"] = bio

                fn = grab(r'"full_name":"([^"]*)"')
                if fn and not info.get("full_name"):
                    info["full_name"] = fn.encode().decode("unicode_escape", errors="ignore")
                bio = grab(r'"biography":"([^"]*)"')
                if bio and not info.get("biography"):
                    info["biography"] = bio.encode().decode("unicode_escape", errors="ignore")
                for key, pat in [
                    ("followers_count", r'"edge_followed_by":\{"count":(\d+)\}'),
                    ("following_count", r'"edge_follow":\{"count":(\d+)\}'),
                    ("posts_count", r'"edge_owner_to_timeline_media":\{"count":(\d+)\}'),
                ]:
                    m = re.search(pat, html)
                    if m:
                        info[key] = int(m.group(1))
                info["is_private"] = '"is_private":true' in html
                info["is_verified"] = '"is_verified":true' in html
                pic = grab(r'"profile_pic_url_hd":"([^"]+)"') or grab(
                    r'"profile_pic_url":"([^"]+)"'
                )
                if pic:
                    info["profile_pic"] = pic.replace("\\u0026", "&")
                i_id = grab(r'"profilePage_(\d+)"') or grab(r'"id":"(\d+)"')
                if i_id:
                    info["instagram_id"] = i_id

                if info.get("full_name") or info.get("followers_count") or info.get("instagram_id"):
                    return info
                return None
        except Exception:
            return None

    def gather(self) -> Dict[str, Any]:
        print(f"\n{C}[*]{N} جمع معلومات: @{self.username}\n")
        methods = [
            ("iOS API", self._try_ios_api),
            ("Web API", self._try_web_api),
            ("HTML", self._try_html),
        ]
        last_block = None
        for name, fn in methods:
            print(f"  {C}[→]{N} {name} ... ", end="", flush=True)
            try:
                data = fn()
                if not data:
                    print(f"{Y}no data{N}")
                    continue
                if data.get("exists") is True:
                    print(f"{G}OK{N}")
                    self.info.update(data)
                    self.info["exists"] = True
                    self.info["collected_at"] = datetime.now().isoformat()
                    return self.info
                if data.get("exists") is False:
                    print(f"{R}not found{N}")
                    self.info["exists"] = False
                    self.info["error"] = "not_found"
                    self.info["collected_at"] = datetime.now().isoformat()
                    return self.info
                # blocked / technical
                err = data.get("error") or "blocked"
                last_block = err
                print(f"{Y}{err}{N}")
            except Exception as e:
                print(f"{R}fail ({e}){N}")
            time.sleep(0.5)

        if last_block:
            print(f"\n{Y}[!]{N} Instagram حاجب/فشل الشبكة: {last_block}")
            print(f"    الحساب قد يكون موجود — عطّل Tor وبدّل WiFi/VPN")
            self.info["exists"] = False
            self.info["blocked"] = True
            self.info["error"] = last_block
        else:
            self.info["exists"] = False
            self.info["error"] = "failed"
        self.info["collected_at"] = datetime.now().isoformat()
        return self.info

    def save(self) -> Path:
        user_dir = RESULTS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / "info.json"
        path.write_text(
            json.dumps(self.info, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"{G}[✓]{N} حفظ: {path}")
        return path

    def display(self) -> None:
        print(f"\n{P}════ معلومات الحساب ════{N}")
        if self.info.get("blocked"):
            print(f"{Y}[!] فشل تقني / حظر: {self.info.get('error')}{N}")
            print(f"    ليس بالضرورة أن الحساب غير موجود.")
            return
        if not self.info.get("exists"):
            print(f"{R}[!] الحساب غير موجود{N}")
            return
        rows = [
            ("username", "المستخدم"),
            ("full_name", "الاسم"),
            ("biography", "البايو"),
            ("followers_count", "متابعون"),
            ("following_count", "يتابع"),
            ("posts_count", "منشورات"),
            ("is_private", "خاص"),
            ("is_verified", "موثق"),
            ("is_business", "تجاري"),
            ("business_category", "التصنيف"),
            ("external_url", "رابط"),
            ("instagram_id", "ID"),
            ("source", "المصدر"),
        ]
        for key, label in rows:
            val = self.info.get(key)
            if val in (None, "", False, 0, []):
                if key in ("followers_count", "following_count", "posts_count") and val == 0:
                    pass
                else:
                    if val in (None, "", []):
                        continue
            if isinstance(val, bool):
                val = "نعم" if val else "لا"
            elif isinstance(val, int):
                val = f"{val:,}"
            print(f"  {Y}{label}:{N} {W}{val}{N}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Camoro Info Gatherer")
    parser.add_argument("-u", "--username", required=True)
    args = parser.parse_args()
    g = InfoGatherer(args.username, proxy_manager=None)
    data = g.gather()
    g.save()
    g.display()
    sys.exit(0 if data.get("exists") else 1)


if __name__ == "__main__":
    main()
