#!/usr/bin/env python3
# HCO-Social-Check.py
# Fixed, cleaned and fully working HCO Social Check (Hybrid Mixed Style)
# By Azhar / Hackers Colony

import os
import sys
import time
import random
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------- CONFIG ----------
YOUTUBE_CHANNEL = "https://youtube.com/@hackers_colony_tech"
TIMEOUT = 8
MAX_WORKERS = 12
USE_PROXIES = True   # keep True to attempt public proxy rotation (graceful fallback)
# --------------------------

# Colors
R = "\033[1;31m"
G = "\033[1;32m"
Y = "\033[1;33m"
C = "\033[1;36m"
B = "\033[1;34m"
W = "\033[1;37m"
RESET = "\033[0m"

# User agents for rotation
UAS = [
    "Mozilla/5.0 (Linux; Android 12; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"
]

# ---------- Helpers ----------
def clear():
    os.system("clear" if os.name != "nt" else "cls")

def open_youtube():
    # try Android intent then xdg-open
    try:
        os.system(f"am start -a android.intent.action.VIEW -d '{YOUTUBE_CHANNEL}' >/dev/null 2>&1")
    except:
        try:
            os.system(f"xdg-open '{YOUTUBE_CHANNEL}' >/dev/null 2>&1")
        except:
            pass

def random_headers():
    return {
        "User-Agent": random.choice(UAS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

def fetch_proxy():
    if not USE_PROXIES:
        return None
    try:
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=2000&country=all&ssl=all&anonymity=all"
        txt = requests.get(url, timeout=5).text
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if not lines:
            return None
        p = random.choice(lines)
        return {"http": f"http://{p}", "https": f"http://{p}"}
    except:
        return None

def safe_get(url, allow_redirects=True):
    headers = random_headers()
    proxy = fetch_proxy()
    try:
        if proxy:
            r = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=allow_redirects, proxies=proxy)
        else:
            r = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=allow_redirects)
        return r
    except Exception:
        # fallback without proxy
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=allow_redirects)
            return r
        except Exception:
            return None

def spinner(text, cycles=6):
    seq = ["|", "/", "-", "\\"]
    for _ in range(cycles):
        for s in seq:
            sys.stdout.write(f"\r{C}{text} {s}{RESET}")
            sys.stdout.flush()
            time.sleep(0.06)
    sys.stdout.write("\r")

def matrix(lines=12, delay=0.02):
    chars = "01#$%*"
    for _ in range(lines):
        print(G + "".join(random.choice(chars) for _ in range(60)) + RESET)
        time.sleep(delay)

def urllib_q(s):
    try:
        return urllib.parse.quote_plus(s)
    except:
        return s

def pretty_print(site, conf, msg):
    color = Y
    if "TAKEN" in msg or "FOUND" in msg or "TAKEN" in msg:
        color = R
    elif "AVAILABLE" in msg or "NOT FOUND" in msg or "FREE" in msg:
        color = G
    print(f"{B}{site:<18}{RESET} : {color}{msg}{RESET}   [{conf}]")

# ---------- DETECTORS (best-effort) ----------
def detect_github(u):
    # reliable via API
    url = f"https://api.github.com/users/{urllib_q(u)}"
    r = safe_get(url)
    if r is None:
        return ("LOW CONF", "ERROR")
    if r.status_code == 200:
        return ("HIGH CONF", "TAKEN ✔")
    if r.status_code == 404:
        return ("HIGH CONF", "AVAILABLE ❌")
    return ("LOW CONF", f"UNKNOWN ({r.status_code})")

def detect_gitlab(u):
    url = f"https://gitlab.com/api/v4/users?username={urllib_q(u)}"
    r = safe_get(url)
    if r is None:
        return ("LOW CONF", "ERROR")
    try:
        j = r.json()
        if isinstance(j, list) and len(j) > 0:
            return ("HIGH CONF", "TAKEN ✔")
        return ("HIGH CONF", "AVAILABLE ❌")
    except Exception:
        return ("LOW CONF", f"UNKNOWN ({r.status_code})")

def detect_reddit(u):
    url = f"https://www.reddit.com/user/{urllib_q(u)}/about.json"
    r = safe_get(url)
    if r is None:
        return ("LOW CONF", "ERROR")
    if r.status_code == 200:
        return ("HIGH CONF", "TAKEN ✔")
    if r.status_code == 404:
        return ("HIGH CONF", "AVAILABLE ❌")
    if r.status_code == 429:
        return ("LOW CONF", "RATE LIMITED")
    return ("LOW CONF", f"UNKNOWN ({r.status_code})")

def detect_stackoverflow(u):
    # best-effort: StackOverflow profiles usually numeric; treat 404 as available
    url = f"https://stackoverflow.com/users/{urllib_q(u)}"
    r = safe_get(url)
    if r is None:
        return ("LOW CONF", "ERROR")
    if r.status_code == 404:
        return ("MED CONF", "AVAILABLE ❌")
    if r.status_code == 200 and "usercard" in (r.text or "").lower():
        return ("MED CONF", "TAKEN ✔")
    return ("LOW CONF", f"UNKNOWN ({r.status_code})")

def detect_generic(u, template, positives=None, negatives=None, allow_redirect=True):
    url = template.format(username=urllib_q(u))
    r = safe_get(url, allow_redirects=allow_redirect)
    if r is None:
        return ("LOW CONF", "ERROR")
    txt = (r.text or "").lower()
    code = r.status_code

    if code == 404:
        return ("HIGH CONF", "AVAILABLE ❌")
    if code in (200, 301, 302):
        if negatives:
            for p in negatives:
                if p.lower() in txt:
                    return ("HIGH CONF", "AVAILABLE ❌")
        if positives:
            for p in positives:
                if p.lower() in txt:
                    return ("HIGH CONF", "TAKEN ✔")
        # login pages or redirects often mean account exists but blocked to bots
        if ("/accounts/login" in txt) or ("log in" in txt) or ("sign in" in txt) or ("login" in r.url.lower()):
            return ("MED CONF", "TAKEN ✔")
        return ("LOW CONF", "POSSIBLY TAKEN ⚠")
    return ("LOW CONF", f"UNKNOWN ({code})")

# ---------- PLATFORMS MAPPING ----------
PLATFORMS = {
    "Instagram": lambda u: detect_generic(u, "https://www.instagram.com/{username}/", positives=["profilepage","edge_followed_by"], negatives=["sorry, this page isn't available"]),
    "Twitter/X": lambda u: detect_generic(u, "https://x.com/{username}", positives=["profile"], negatives=["this account doesn’t exist","page doesn’t exist"]),
    "YouTube": lambda u: detect_generic(u, "https://www.youtube.com/@{username}", positives=["channelid","subscribercounttext","ytinitialdata"], negatives=["this channel does not exist"]),
    "Facebook": lambda u: detect_generic(u, "https://www.facebook.com/{username}", positives=["profile_id","timeline"], negatives=["content isn't available","page isn't available"]),
    "GitHub": detect_github,
    "GitLab": detect_gitlab,
    "Reddit": detect_reddit,
    "TikTok": lambda u: detect_generic(u, "https://www.tiktok.com/@{username}", positives=["tiktok.com/@"], negatives=["page not found"]),
    "Pinterest": lambda u: detect_generic(u, "https://www.pinterest.com/{username}/", positives=["pins","profile"], negatives=["sorry, this page isn't available"]),
    "Snapchat": lambda u: detect_generic(u, "https://www.snapchat.com/add/{username}", positives=["snapcode"], negatives=[]),
    "Telegram": lambda u: detect_generic(u, "https://t.me/{username}", positives=["tgme_page","username"], negatives=["sorry, the page you are looking for"]),
    "Medium": lambda u: detect_generic(u, "https://medium.com/@{username}", positives=["profile"], negatives=["page not found"]),
    "Quora": lambda u: detect_generic(u, "https://www.quora.com/profile/{username}", positives=["answers","questions"], negatives=["page not found"]),
    "StackOverflow": detect_stackoverflow,
    "Tumblr": lambda u: detect_generic(u, "https://{username}.tumblr.com", positives=["tumblr"], negatives=["not found"]),
    "Vimeo": lambda u: detect_generic(u, "https://vimeo.com/{username}", positives=["vimeo"], negatives=["page not found"]),
    "SoundCloud": lambda u: detect_generic(u, "https://soundcloud.com/{username}", positives=["soundcloud"], negatives=["page not found"]),
    "Behance": lambda u: detect_generic(u, "https://www.behance.net/{username}", positives=["behance"], negatives=["page not found"]),
    "Dribbble": lambda u: detect_generic(u, "https://dribbble.com/{username}", positives=["dribbble"], negatives=["page not found"]),
    "DeviantArt": lambda u: detect_generic(u, "https://www.deviantart.com/{username}", positives=["deviantart"], negatives=["not found"]),
    "Replit": lambda u: detect_generic(u, "https://replit.com/@{username}", positives=["replit"], negatives=["not found"]),
    "Archive.org": lambda u: detect_generic(u, "https://archive.org/details/@{username}", positives=["archive.org"], negatives=[]),
    "Patreon": lambda u: detect_generic(u, "https://www.patreon.com/{username}", positives=["patreon"], negatives=["page not found"]),
    "BuyMeACoffee": lambda u: detect_generic(u, "https://www.buymeacoffee.com/{username}", positives=["buymeacoffee"], negatives=["not found"]),
    "Goodreads": lambda u: detect_generic(u, "https://www.goodreads.com/{username}", positives=["goodreads"], negatives=["not found"]),
    "Kaggle": lambda u: detect_generic(u, "https://www.kaggle.com/{username}", positives=["kaggle"], negatives=["not found"]),
    "Gist (GitHub)": lambda u: detect_generic(u, "https://gist.github.com/{username}", positives=["gist"], negatives=["not found"])
}

# ---------- SCAN SINGLE PLATFORM (wrapper for parallel) ----------
def scan_one(site, detector, username):
    try:
        if callable(detector):
            return site, detector(username)
        else:
            return site, ("LOW CONF", "ERROR")
    except Exception as e:
        return site, ("LOW CONF", "ERROR")

# ---------- MAIN SCAN FUNCTION ----------
def scan_username(username):
    u = username.strip()
    if not u:
        print(Y + "No username provided. Exiting." + RESET)
        return

    matrix(10, 0.01)
    print(C + f"\nScanning username: @{u}" + RESET)
    print(G + "-"*60 + RESET)

    results = {}
    taken_list = []
    avail_list = []
    unreliable_list = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(scan_one, site, detector, u): site for site, detector in PLATFORMS.items()}
        for fut in as_completed(futures):
            site = futures[fut]
            site, res = fut.result()
            conf, msg = res if isinstance(res, tuple) else ("LOW CONF", str(res))
            results[site] = (conf, msg)

            # pretty print
            if "TAKEN" in msg or "FOUND" in msg or "TAKEN" in msg or "FOUND" in msg:
                pretty_print(site, conf, msg)
                taken_list.append(site)
            elif "AVAILABLE" in msg or "NOT FOUND" in msg or "FREE" in msg:
                pretty_print(site, conf, msg)
                avail_list.append(site)
            elif "POSSIBLY" in msg or "UNRELIABLE" in msg or "LOW CONF" in conf:
                pretty_print(site, conf, msg)
                unreliable_list.append(site)
            else:
                pretty_print(site, conf, msg)

            time.sleep(0.05)  # small throttle for nicer UI

    print(G + "-"*60 + RESET)
    # Summary box
    print(R + "╔" + "═"*56 + "╗")
    print(R + "║" + RESET + f"   Scan Summary for @{u}".ljust(56) + R + "║" + RESET)
    print(R + "╠" + "═"*56 + "╣" + RESET)
    print(R + "║ " + G + f"Found (Taken): {len(taken_list)}".ljust(54) + R + "║" + RESET)
    print(R + "║ " + G + f"Available: {len(avail_list)}".ljust(54) + R + "║" + RESET)
    print(R + "║ " + Y + f"Unreliable/Unknown: {len(unreliable_list)}".ljust(54) + R + "║" + RESET)
    print(R + "╚" + "═"*56 + "╝" + RESET)
    print()
    if taken_list:
        print(R + "Taken on:" + RESET, ", ".join(taken_list))
    if avail_list:
        print(G + "Available on:" + RESET, ", ".join(avail_list))
    if unreliable_list:
        print(Y + "Check manually (unreliable):" + RESET, ", ".join(unreliable_list))
    print()
    print(C + "Scan complete — results are best-effort: APIs used where available, heuristics elsewhere." + RESET)
    print(W + "By Azhar | Hackers Colony" + RESET)
    print()

# ---------- MAIN ----------
def main():
    try:
        clear()
        # Tool lock + YT redirect
        print(R + "⚠  THIS TOOL IS NOT FREE  ⚠" + RESET)
        print(Y + "Subscribe to Hackers Colony Tech to unlock." + RESET)
        print()
        for i in range(8,0,-1):
            print(G + f"Opening YouTube in {i}s..." + RESET, end="\r")
            time.sleep(1)
        open_youtube()
        input(C + "\nAfter subscribing, press ENTER to continue..." + RESET)
        clear()
        # Banner
        print(G + "╔" + "═"*46 + "╗")
        print(G + "║" + RESET + " " * 4 + R + "HCO Social Check" + RESET + " " * 17 + G + "║" + RESET)
        print(G + "╚" + "═"*46 + "╝" + RESET)
        print()
        user = input(C + "Enter username (no @ required): " + RESET).strip()
        if not user:
            print(Y + "No username supplied. Exiting." + RESET)
            return
        user = user.lstrip("@").strip()
        clear()
        scan_username(user)

    except KeyboardInterrupt:
        print("\n" + Y + "Interrupted. Exiting." + RESET)

if __name__ == "__main__":
    main()
