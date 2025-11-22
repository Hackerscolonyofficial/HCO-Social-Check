#!/usr/bin/env python3
# HCO-Social-Check.py - Ultimate OSINT Username Checker
# By Azhar / Hackers Colony

import os, sys, time, random, requests

YOUTUBE = "https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya"

# Colors
R = "\033[1;31m"
G = "\033[1;32m"
Y = "\033[1;33m"
C = "\033[1;36m"
W = "\033[1;37m"
RESET = "\033[0m"

def clear():
    os.system("clear")

def open_youtube():
    os.system(f"xdg-open '{YOUTUBE}'")

def matrix_effect(lines=20, delay=0.02):
    chars = "01$#@"
    for _ in range(lines):
        print(G + "".join(random.choice(chars) for _ in range(60)) + RESET)
        time.sleep(delay)

def progress_bar(task, total=30):
    for i in range(total):
        sys.stdout.write(f"\r{C}{task}: [{G}{'=' * i}{' ' * (total - i)}{C}] {int((i/total)*100)}%{RESET}")
        sys.stdout.flush()
        time.sleep(0.04)
    print()

def hacker_spinner(text):
    spinner = ["|","/","-","\\"]
    for _ in range(8):
        for s in spinner:
            sys.stdout.write(f"\r{C}{text} {s}{RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
    sys.stdout.write("\r")

def banner():
    print(G + "╔" + "═"*45 + "╗")
    print(f"║   {R}HCO SOCIAL CHECK{RESET}{G}{' ' * 20}║")
    print("╠" + "═"*45 + "╣")
    print("║" + " " * 17 + Y + "By Azhar" + G + " " * 16 + "║")
    print("╚" + "═"*45 + "╝" + RESET)
    print()

def tool_lock():
    clear()
    print(R + "⚠ THIS TOOL IS NOT FREE ⚠" + RESET)
    print(Y + "Subscribe to Hackers Colony Tech to unlock." + RESET)
    print()

    for i in range(10, 0, -1):
        print(f"{G}Redirecting in {i} sec...{RESET}", end="\r")
        time.sleep(1)

    open_youtube()
    input(C + "\nAfter subscribing, press ENTER to continue..." + RESET)
    clear()

def real_check(url):
    try:
        r = requests.get(url, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            return "TAKEN"
        elif r.status_code == 404:
            return "FREE"
        else:
            return "UNKNOWN"
    except:
        return "ERROR"

def social_check(username):

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
        "Discord": f"https://discord.com/users/{username}",
        "Behance": f"https://www.behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "Tumblr": f"https://{username}.tumblr.com",
        "WordPress": f"https://{username}.wordpress.com",
        "Vimeo": f"https://vimeo.com/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "GitLab": f"https://gitlab.com/{username}",
        "Kaggle": f"https://www.kaggle.com/{username}",
        "Goodreads": f"https://www.goodreads.com/{username}",
        "Patreon": f"https://www.patreon.com/{username}",
        "Replit": f"https://replit.com/@{username}",
        "DeviantArt": f"https://www.deviantart.com/{username}",
        "Archive.org": f"https://archive.org/details/@{username}",
        "BuyMeACoffee": f"https://www.buymeacoffee.com/{username}",
    }

    # MATRIX hacker intro
    matrix_effect(14)

    print(C + f"\nScanning username: {username}" + RESET)
    print(G + "-" * 45 + RESET)

    for site, url in platforms.items():
        hacker_spinner(f"Scanning {site}...")
        status = real_check(url)

        if status == "TAKEN":
            print(f"{site:<18}: {R}TAKEN ✔{RESET}")
        elif status == "FREE":
            print(f"{site:<18}: {G}AVAILABLE ❌{RESET}")
        elif status == "UNKNOWN":
            print(f"{site:<18}: {Y}UNKNOWN ⚠{RESET}")
        else:
            print(f"{site:<18}: {Y}ERROR ❗{RESET}")

        time.sleep(random.uniform(0.1, 0.4))

    print(G + "-" * 45 + RESET)
    print(C + "REAL Scan Completed!" + RESET)

def main():
    tool_lock()
    banner()
    username = input(C + "Enter a username to scan: " + RESET).strip()
    clear()
    progress_bar("Initializing Scanner")
    social_check(username)

if __name__ == "__main__":
    main()
