#!/usr/bin/env python3
"""Camoro - Information Gathering / OSINT"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError as e:
    raise SystemExit("[!] pip install httpx httpx[socks]") from e

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

R = "\033[0;31m"
G = "\033[0;32m"
Y = "\033[1;33m"
C = "\033[0;36m"
W = "\033[1;37m"
N = "\033[0m"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]


class InfoGatherer:
    def __init__(self, username: str, proxy_manager: Any = None) -> None:
        self.username = username.strip().lstrip("@").lower()
        self.proxy_manager = proxy_manager
        self.info: Dict[str, Any] = {
            "username": self.username,
            "exists": False,
            "user_id": None,
            "full_name": "",
            "biography": "",
            "external_url": "",
            "is_private": None,
            "is_verified": None,
            "is_business": None,
            "followers": 0,
            "following": 0,
            "posts": 0,
            "profile_pic_url": "",
            "category": "",
            "public_email": "",
            "public_phone": "",
            "business_address": "",
            "keywords": [],
            "possible_names": [],
            "years_found": [],
            "gathered_at": "",
            "source": "",
        }
        self.user_dir = RESULTS_DIR / self.username
        self.user_dir.mkdir(parents=True, exist_ok=True)

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
            "X-IG-App-ID": "936619743392459",
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "Referer": "https://www.instagram.com/",
        }

    def _client(self) -> httpx.Client:
        kwargs: Dict[str, Any] = {
            "headers": self._headers(),
            "timeout": 25.0,
            "follow_redirects": True,
            "verify": False,
        }
        if self.proxy_manager is not None:
            try:
                proxy = self.proxy_manager.get_proxy()
                if proxy:
                    kwargs["proxy"] = proxy
            except Exception:
                pass
        try:
            return httpx.Client(http2=True, **kwargs)
        except Exception:
            return httpx.Client(**kwargs)

    def _safe_int(self, val: Any, default: int = 0) -> int:
        try:
            if val is None:
                return default
            if isinstance(val, dict):
                val = val.get("count", default)
            return int(val)
        except Exception:
            return default

    def _extract_keywords(self) -> None:
        text_parts: List[str] = []
        for key in ("full_name", "biography", "username", "category", "external_url"):
            v = self.info.get(key) or ""
            if v:
                text_parts.append(str(v))

        blob = " ".join(text_parts)

        # words / names
        words = re.findall(r"[A-Za-z\u0600-\u06FF]{3,}", blob)
        seen = set()
        keywords: List[str] = []
        for w in words:
            wl = w.lower()
            if wl not in seen and wl != self.username.lower():
                seen.add(wl)
                keywords.append(w)
        self.info["keywords"] = keywords[:40]

        # possible person names from full_name
        names: List[str] = []
        full = (self.info.get("full_name") or "").strip()
        if full:
            names.append(full)
            for part in re.split(r"[\s_\-\.]+", full):
                if len(part) >= 2:
                    names.append(part)
        # username chunks
        for part in re.split(r"[._\-]+", self.username):
            if len(part) >= 2 and part.lower() not in ("official", "real", "the", "ig"):
                names.append(part)
        self.info["possible_names"] = list(dict.fromkeys(names))[:25]

        # years 1980-2030
        years = re.findall(r"\b(19[8-9]\d|20[0-2]\d)\b", blob)
        self.info["years_found"] = list(dict.fromkeys(years))

    # ── Method 1: Web profile HTML ─────────────────────────────
    def _from_web_html(self, client: httpx.Client) -> bool:
        url = f"https://www.instagram.com/{self.username}/"
        try:
            r = client.get(url)
            if r.status_code == 404:
                return False
            if r.status_code != 200:
                return False

            html = r.text

            # blocked / login wall indicators without data
            if "Sorry, this page isn't available" in html:
                self.info["exists"] = False
                return False

            # JSON-LD
            for m in re.finditer(
                r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                html,
                re.DOTALL,
            ):
                try:
                    data = json.loads(m.group(1))
                    if isinstance(data, dict):
                        if data.get("name"):
                            self.info["full_name"] = str(data["name"])
                        if data.get("description"):
                            self.info["biography"] = str(data["description"])
                        if data.get("url"):
                            self.info["external_url"] = str(data.get("mainEntityofPage") or data.get("url") or "")
                        img = data.get("image")
                        if isinstance(img, str):
                            self.info["profile_pic_url"] = img
                        elif isinstance(img, list) and img:
                            self.info["profile_pic_url"] = str(img[0])
                        self.info["exists"] = True
                        self.info["source"] = "web_html_jsonld"
                except Exception:
                    pass

            # meta tags
            meta_map = {
                "og:title": "full_name",
                "og:description": "biography",
                "og:image": "profile_pic_url",
                "description": "biography",
            }
            for prop, field in meta_map.items():
                m = re.search(
                    rf'<meta[^>]+(?:property|name)="{re.escape(prop)}"[^>]+content="([^"]*)"',
                    html,
                    re.I,
                )
                if not m:
                    m = re.search(
                        rf'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="{re.escape(prop)}"',
                        html,
                        re.I,
                    )
                if m and m.group(1) and not self.info.get(field):
                    val = m.group(1).replace("&#064;", "@").replace("&amp;", "&")
                    # og:title often "Name (@user) • Instagram photos..."
                    if field == "full_name":
                        val = re.sub(r"\s*\(@[^)]+\).*", "", val).strip()
                        val = val.replace("• Instagram", "").strip()
                    if field == "biography":
                        # strip "X Followers, Y Following..." noise if present
                        pass
                    self.info[field] = val
                    self.info["exists"] = True
                    if not self.info["source"]:
                        self.info["source"] = "web_html_meta"

            # window._sharedData or additional data
            shared = re.search(
                r"window\._sharedData\s*=\s*(\{.+?\});</script>",
                html,
                re.DOTALL,
            )
            if shared:
                try:
                    data = json.loads(shared.group(1))
                    user = (
                        data.get("entry_data", {})
                        .get("ProfilePage", [{}])[0]
                        .get("graphql", {})
                        .get("user")
                    )
                    if user:
                        self._apply_user_obj(user, source="web_sharedData")
                        return True
                except Exception:
                    pass

            # Require some success marker
            if self.info.get("exists") or self.info.get("full_name") or self.info.get("biography"):
                self.info["exists"] = True
                if not self.info["source"]:
                    self.info["source"] = "web_html"
                # try counts from description: "1,234 Followers, 56 Following, 7 Posts"
                desc = self.info.get("biography") or ""
                m = re.search(
                    r"([\d,\.]+)\s*Followers?,\s*([\d,\.]+)\s*Following,\s*([\d,\.]+)\s*Posts?",
                    desc,
                    re.I,
                )
                if m:
                    self.info["followers"] = self._parse_count(m.group(1))
                    self.info["following"] = self._parse_count(m.group(2))
                    self.info["posts"] = self._parse_count(m.group(3))
                    # biography after counts often in og:description
                    bio2 = re.sub(
                        r"^[\d,\.]+\s*Followers?,\s*[\d,\.]+\s*Following,\s*[\d,\.]+\s*Posts?\s*[-–—]?\s*",
                        "",
                        desc,
                        flags=re.I,
                    ).strip()
                    if bio2 and bio2 != desc:
                        self.info["biography"] = bio2
                return True
            return False
        except Exception as e:
            print(f"{Y}[!] web_html: {e}{N}")
            return False

    def _parse_count(self, s: str) -> int:
        s = (s or "").strip().lower().replace(",", "")
        try:
            if s.endswith("k"):
                return int(float(s[:-1]) * 1000)
            if s.endswith("m"):
                return int(float(s[:-1]) * 1_000_000)
            return int(float(s))
        except Exception:
            return 0

    def _apply_user_obj(self, user: dict, source: str = "") -> None:
        if not user:
            return
        self.info["exists"] = True
        self.info["user_id"] = str(user.get("id") or user.get("pk") or self.info.get("user_id") or "")
        self.info["full_name"] = user.get("full_name") or self.info.get("full_name") or ""
        self.info["biography"] = user.get("biography") or self.info.get("biography") or ""
        self.info["external_url"] = (
            user.get("external_url") or user.get("external_lynx_url") or self.info.get("external_url") or ""
        )
        self.info["is_private"] = user.get("is_private")
        self.info["is_verified"] = user.get("is_verified")
        self.info["is_business"] = user.get("is_business_account") or user.get("is_business")
        self.info["followers"] = self._safe_int(
            user.get("edge_followed_by") or user.get("follower_count") or user.get("followers")
        )
        self.info["following"] = self._safe_int(
            user.get("edge_follow") or user.get("following_count") or user.get("following")
        )
        self.info["posts"] = self._safe_int(
            user.get("edge_owner_to_timeline_media")
            or user.get("media_count")
            or user.get("posts")
        )
        pic = (
            user.get("profile_pic_url_hd")
            or user.get("profile_pic_url")
            or user.get("hd_profile_pic_url_info", {}).get("url")
            if isinstance(user.get("hd_profile_pic_url_info"), dict)
            else None
        )
        if pic:
            self.info["profile_pic_url"] = str(pic)
        self.info["category"] = (
            user.get("category_name") or user.get("business_category_name") or self.info.get("category") or ""
        )
        self.info["public_email"] = user.get("public_email") or user.get("business_email") or ""
        self.info["public_phone"] = (
            user.get("public_phone_number")
            or user.get("contact_phone_number")
            or self.info.get("public_phone")
            or ""
        )
        addr = user.get("business_address_json") or user.get("address_street") or ""
        if isinstance(addr, str) and addr.startswith("{"):
            try:
                aj = json.loads(addr)
                parts = [aj.get("city_name"), aj.get("region_name"), aj.get("street_address")]
                self.info["business_address"] = ", ".join(p for p in parts if p)
            except Exception:
                self.info["business_address"] = addr
        elif addr:
            self.info["business_address"] = str(addr)
        if source:
            self.info["source"] = source

    # ── Method 2: Web Profile Info API ─────────────────────────
    def _from_web_api(self, client: httpx.Client) -> bool:
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
        headers = {
            **self._headers(),
            "X-Requested-With": "XMLHttpRequest",
            "X-IG-App-ID": "936619743392459",
            "Accept": "*/*",
            "Referer": f"https://www.instagram.com/{self.username}/",
        }
        try:
            r = client.get(url, headers=headers)
            if r.status_code != 200:
                return False
            data = r.json()
            user = data.get("data", {}).get("user")
            if not user:
                return False
            self._apply_user_obj(user, source="web_profile_info")
            return True
        except Exception as e:
            print(f"{Y}[!] web_api: {e}{N}")
            return False

    # ── Method 3: Embed page ───────────────────────────────────
    def _from_embed(self, client: httpx.Client) -> bool:
        url = f"https://www.instagram.com/{self.username}/embed/"
        try:
            r = client.get(url)
            if r.status_code != 200:
                return False
            html = r.text
            # username appears?
            if self.username.lower() not in html.lower() and "Page Not Found" in html:
                return False

            m = re.search(r'"username"\s*:\s*"([^"]+)"', html)
            if m:
                self.info["exists"] = True
            m = re.search(r'"full_name"\s*:\s*"([^"]*)"', html)
            if m and m.group(1):
                self.info["full_name"] = m.group(1).encode().decode("unicode_escape", errors="ignore")
                self.info["exists"] = True
            m = re.search(r'"biography"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
            if m:
                try:
                    self.info["biography"] = json.loads(f'"{m.group(1)}"')
                except Exception:
                    self.info["biography"] = m.group(1)
                self.info["exists"] = True
            m = re.search(r'"id"\s*:\s*"(\d+)"', html)
            if m:
                self.info["user_id"] = m.group(1)
            m = re.search(r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
            if m:
                self.info["followers"] = int(m.group(1))
            m = re.search(r'"edge_follow"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
            if m:
                self.info["following"] = int(m.group(1))
            m = re.search(r'"is_private"\s*:\s*(true|false)', html)
            if m:
                self.info["is_private"] = m.group(1) == "true"
            m = re.search(r'"is_verified"\s*:\s*(true|false)', html)
            if m:
                self.info["is_verified"] = m.group(1) == "true"
            m = re.search(r'"profile_pic_url"\s*:\s*"([^"]+)"', html)
            if m:
                self.info["profile_pic_url"] = m.group(1).replace("\\u0026", "&")

            if self.info.get("exists"):
                self.info["source"] = self.info.get("source") or "embed"
                return True
            return False
        except Exception as e:
            print(f"{Y}[!] embed: {e}{N}")
            return False

    # ── Method 4: Topsearch ────────────────────────────────────
    def _from_topsearch(self, client: httpx.Client) -> bool:
        url = "https://www.instagram.com/web/search/topsearch/"
        try:
            r = client.get(url, params={"query": self.username, "context": "blended"})
            if r.status_code != 200:
                return False
            data = r.json()
            for item in data.get("users", []):
                u = item.get("user") or item
                uname = (u.get("username") or "").lower()
                if uname == self.username:
                    self.info["exists"] = True
                    self.info["user_id"] = str(u.get("pk") or u.get("id") or "")
                    self.info["full_name"] = u.get("full_name") or self.info.get("full_name") or ""
                    self.info["is_private"] = u.get("is_private")
                    self.info["is_verified"] = u.get("is_verified")
                    self.info["profile_pic_url"] = (
                        u.get("profile_pic_url") or self.info.get("profile_pic_url") or ""
                    )
                    if not self.info.get("source"):
                        self.info["source"] = "topsearch"
                    return True
            return False
        except Exception as e:
            print(f"{Y}[!] topsearch: {e}{N}")
            return False

    # ── Method 5: oEmbed ───────────────────────────────────────
    def _from_oembed(self, client: httpx.Client) -> bool:
        url = "https://api.instagram.com/oembed"
        try:
            r = client.get(
                url,
                params={"url": f"https://www.instagram.com/{self.username}/"},
            )
            if r.status_code != 200:
                return False
            data = r.json()
            if data.get("author_name"):
                self.info["exists"] = True
                # author_name can be username
            if data.get("title") and not self.info.get("full_name"):
                # title sometimes has caption not name
                pass
            if data.get("thumbnail_url") and not self.info.get("profile_pic_url"):
                self.info["profile_pic_url"] = data["thumbnail_url"]
            if data.get("author_name"):
                self.info["exists"] = True
                if not self.info["source"]:
                    self.info["source"] = "oembed"
                return True
            return bool(self.info.get("exists"))
        except Exception:
            return False

    def gather(self) -> Dict[str, Any]:
        print(f"\n{C}[*]{N} جمع معلومات @{self.username} ...")
        client = self._client()
        methods = [
            ("Web API", self._from_web_api),
            ("Web HTML", self._from_web_html),
            ("Embed", self._from_embed),
            ("TopSearch", self._from_topsearch),
            ("oEmbed", self._from_oembed),
        ]
        success = False
        try:
            for name, fn in methods:
                print(f"  {C}→{N} {name}...", end=" ", flush=True)
                try:
                    ok = fn(client)
                    if ok and self.info.get("exists"):
                        print(f"{G}OK{N}")
                        success = True
                        # keep going if we still lack core fields
                        if self.info.get("user_id") and (
                            self.info.get("followers") or self.info.get("full_name")
                        ):
                            break
                    else:
                        print(f"{Y}skip{N}")
                except Exception as e:
                    print(f"{R}fail ({e}){N}")
                time.sleep(random.uniform(0.4, 1.2))
        finally:
            try:
                client.close()
            except Exception:
                pass

        if success or self.info.get("exists"):
            self.info["exists"] = True
            self._extract_keywords()
            self.info["gathered_at"] = datetime.now().isoformat()
            print(f"{G}[✓]{N} تم جمع المعلومات (source={self.info.get('source')})")
        else:
            # minimal fallback so pipeline continues
            self.info["exists"] = False
            self.info["gathered_at"] = datetime.now().isoformat()
            print(f"{R}[!]{N} فشل الجمع — الحساب غير موجود أو محجوب")

        return self.info

    def save(self, path: Optional[Path] = None) -> Path:
        out = path or (self.user_dir / "info.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(self.info, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        # human readable
        txt = self.user_dir / "info.txt"
        lines = [
            f"Username : @{self.info.get('username')}",
            f"Exists   : {self.info.get('exists')}",
            f"User ID  : {self.info.get('user_id')}",
            f"Name     : {self.info.get('full_name')}",
            f"Bio      : {self.info.get('biography')}",
            f"Private  : {self.info.get('is_private')}",
            f"Verified : {self.info.get('is_verified')}",
            f"Business : {self.info.get('is_business')}",
            f"Followers: {self.info.get('followers')}",
            f"Following: {self.info.get('following')}",
            f"Posts    : {self.info.get('posts')}",
            f"URL      : {self.info.get('external_url')}",
            f"Email    : {self.info.get('public_email')}",
            f"Phone    : {self.info.get('public_phone')}",
            f"Address  : {self.info.get('business_address')}",
            f"Category : {self.info.get('category')}",
            f"Keywords : {', '.join(self.info.get('keywords') or [])}",
            f"Names    : {', '.join(self.info.get('possible_names') or [])}",
            f"Years    : {', '.join(self.info.get('years_found') or [])}",
            f"Source   : {self.info.get('source')}",
            f"Time     : {self.info.get('gathered_at')}",
        ]
        txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{G}[✓]{N} حفظ: {out}")
        return out

    def display(self) -> None:
        i = self.info
        print(f"\n{C}════════════ معلومات الحساب ════════════{N}")
        print(f"  {W}Username {N}: @{i.get('username')}")
        print(f"  {W}Exists   {N}: {i.get('exists')}")
        print(f"  {W}User ID  {N}: {i.get('user_id') or '-'}")
        print(f"  {W}Name     {N}: {i.get('full_name') or '-'}")
        print(f"  {W}Bio      {N}: {(i.get('biography') or '-')[:120]}")
        print(f"  {W}Private  {N}: {i.get('is_private')}")
        print(f"  {W}Verified {N}: {i.get('is_verified')}")
        print(f"  {W}Business {N}: {i.get('is_business')}")
        print(f"  {W}Followers{N}: {i.get('followers')}")
        print(f"  {W}Following{N}: {i.get('following')}")
        print(f"  {W}Posts    {N}: {i.get('posts')}")
        print(f"  {W}Website  {N}: {i.get('external_url') or '-'}")
        print(f"  {W}Email    {N}: {i.get('public_email') or '-'}")
        print(f"  {W}Phone    {N}: {i.get('public_phone') or '-'}")
        print(f"  {W}Address  {N}: {i.get('business_address') or '-'}")
        print(f"  {W}Category {N}: {i.get('category') or '-'}")
        kws = i.get("keywords") or []
        if kws:
            print(f"  {W}Keywords {N}: {', '.join(kws[:12])}")
        names = i.get("possible_names") or []
        if names:
            print(f"  {W}Names    {N}: {', '.join(names[:10])}")
        years = i.get("years_found") or []
        if years:
            print(f"  {W}Years    {N}: {', '.join(years)}")
        print(f"  {W}Source   {N}: {i.get('source') or '-'}")
        print(f"{C}════════════════════════════════════════{N}\n")

    @staticmethod
    def load(username: str) -> Optional[Dict[str, Any]]:
        path = RESULTS_DIR / username.strip().lstrip("@").lower() / "info.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Camoro Info Gatherer")
    parser.add_argument("-u", "--username", required=True, help="Instagram username")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy/Tor")
    args = parser.parse_args()

    proxy = None
    if not args.no_proxy:
        try:
            from modules.proxy_manager import ProxyManager

            proxy = ProxyManager()
        except Exception:
            try:
                # when run as script directly
                sys.path.insert(0, str(BASE_DIR))
                from modules.proxy_manager import ProxyManager

                proxy = ProxyManager()
            except Exception:
                proxy = None

    g = InfoGatherer(args.username, proxy_manager=proxy)
    info = g.gather()
    g.save()
    g.display()
    sys.exit(0 if info.get("exists") else 1)


if __name__ == "__main__":
    main()
