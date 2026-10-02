import subprocess
from termcolor import colored


def _maigret_available() -> bool:
    """Проверяет, установлен ли Maigret"""
    try:
        subprocess.run(["maigret", "--help"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired): return False


def search_nickname(username: str):
    """Сканирует сайты через Maigret и выводит результаты в консоль"""
    print(colored(f"\n=== Check nickname: {username} ===\n", "magenta"))

    if not _maigret_available():
        print(colored("[!] Maigret not installed. Run: pip install maigret", "red"))
        return

    try:
        proc = subprocess.run(
            [
                "maigret", username,
                "-a",
                "--no-color",
                 "--dns-resolver", "threaded",
            ],
            timeout=1800
        )
    except subprocess.TimeoutExpired:
        print(colored("[!] Maigret timeout (1800s).", "red"))
        return
    except Exception as e:
        print(colored(f"[!] Maigret error: {e}", "red"))
        return

    if proc.returncode != 0: print(colored(f"[!] Maigret exited with code {proc.returncode}", "red"))
    print()


def information_about_nickname():
    username = input("Username / nickname: ").strip()
    if not username:
        print(colored("[!] Empty input.\n", "red"))
        return
    
    search_nickname(username)
    
    
    