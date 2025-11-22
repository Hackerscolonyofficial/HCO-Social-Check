#!/usr/bin/env python3
# HCO-Social-Check.py
# By Azhar — Hackers Colony
# GitHub ready Termux tool (colourful UI + tool-lock + YouTube redirect)

import os
import time
import webbrowser
import requests

YOUTUBE_LINK = "https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya"

# Terminal colours
R = "\033[1;31m"   # Red Bold
G = "\033[1;32m"   # Green
Y = "\033[1;33m"   # Yellow
C = "\033[1;36m"   # Cyan
W = "\033[1;37m"   # White
RESET = "\033[0m"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    print(G + "╔" + "═" * 38 + "╗" + RESET)
    # HCO Social Check in red, inside green box
    print(G + "║" + RESET + " " * 2 + R + "HCO Social Check" + RESET + " " * 13 + G + "║" + RESET)
    print(G + "╠" + "═" * 38 + "╣" + RESET)
    print(" " * 4 + Y + "By Azhar" + RESET)
    print(G + "╚" + "═" * 38 + "╝" + RESET)
    print()

def tool_lock(countdown=10):
    clear()
    print(R + "⚠  THIS TOOL IS NOT FREE  ⚠" + RESET)
    print(Y + "You must subscribe to Hackers Colony Tech to use this tool." + RESET)
    print()
    print(C + f"Redirecting to YouTube in {countdown} seconds..." + RESET)
    for i in range(countdown, 0, -1):
        print(f"{G}Redirecting in {i} seconds...{RESET}", end="\r")
        time.sleep(1)

    try:
        webbrowser.open(YOUTUBE_LINK)
    except:
        pass

    print()
    input(C + "After subscribing, press ENTER to continue..." + RESET)
    clear()

def check_url_head(url, timeout=6):
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        return r.status_code
    except requests.RequestException:
        # fallback to GET if HEAD fails for some sites
        try:
            r = requests.get(url, allow_redirects=True, timeout=timeout)
            return r.status_code
        except requests.RequestException:
            return None

def social_check(username):
    print()
    print(C + f"Checking username: {username}" + RESET)
    print(G + "-" * 40 + RESET)

    platforms = {
        "Instagram": f"https://www.instagram.com/{username}",
        "Twitter (X)": f"https://x.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "Snapchat": f"https://www.snapchat.com/add/{username}",
        "Telegram": f"https://t.me/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Quora": f"https://www.quora.com/profile/{username}",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "StackOverflow": f"https://stackoverflow.com/users/{username}",
        "Facebook": f"https://www.facebook.com/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "Behance": f"https://www.behance.net/{username}",
        "Discord (invite)": f"https://discord.com/users/{username}",
    }

    for site, url in platforms.items():
        status = check_url_head(url)
        if status is None:
            print(f"{Y}{site:<18} : ERROR ❗{RESET}")
        else:
            # treat 200 as taken, 301/302 as taken, 404 as available
            if status == 200 or str(status).startswith(("3", "4")) is False:
                # If status is 200 or 3xx treat as taken; else if 404 treat as available.
                if status == 404:
                    print(f"{G}{site:<18} : AVAILABLE ❌{RESET}")
                else:
                    print(f"{R}{site:<18} : TAKEN ✔{RESET}")
            else:
                # common cases: 301/302/200 -> taken; 404 -> available
                if status in (301, 302, 200):
                    print(f"{R}{site:<18} : TAKEN ✔{RESET}")
                elif status == 404:
                    print(f"{G}{site:<18} : AVAILABLE ❌{RESET}")
                else:
                    print(f"{Y}{site:<18} : UNKNOWN ({status}){RESET}")

    print()
    print(G + "-" * 40 + RESET)
    print(Y + "Scan Complete!" + RESET)
    print()

def main():
    try:
        tool_lock(countdown=10)
        banner()
        username = input(C + "Enter a username to check: " + RESET).strip()
        if not username:
            print(Y + "No username provided. Exiting." + RESET)
            return
        social_check(username)
    except KeyboardInterrupt:
        print("\n" + Y + "Interrupted by user. Exiting." + RESET)

if __name__ == "__main__":
    main()
