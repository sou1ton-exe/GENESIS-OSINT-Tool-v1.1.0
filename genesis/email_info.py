# import subprocess
# import json
# import urllib.request
# import urllib.error
# import re
# import sys


# try: import requests
# except ImportError:
#     print("Установка библиотеки requests...")
#     subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
#     import requests

# from termcolor import colored


# def _holehe_available() -> bool:
#     """Проверяет, установлен ли Holehe в системе."""
#     try:
#         subprocess.run(["holehe", "--help"], capture_output=True, timeout=5)
#         return True
#     except (FileNotFoundError, subprocess.TimeoutExpired): return False

# def _parse_holehe_output(output: str) -> list:
#     """
#     Парсит stdout Holehe.
#     Ищет строки, где есть [+] и URL/название платформы.
#     Игнорирует строки типа '[+] Email used'.
#     """
#     results = []
#     pattern = re.compile(r"\[\+\]\s+([^\s]+)") # Регулярное выражение для поиска строк с [+]

#     for line in output.splitlines():
#         line = line.strip()
#         if line.startswith("[+]"):
#             match = pattern.search(line)
#             if match:
#                 platform = match.group(1)
#                 if platform.lower() in ["email", "used", "rate", "limit"]: continue
                
#                 url = ""
#                 parts = line.split()
#                 if len(parts) > 2:
#                     potential_url = parts[2]
#                     if "http" in potential_url or ".com" in potential_url: url = potential_url
                
#                 results.append({"platform": platform, "url": url})
                
#     return results


# def search_email_holehe(email: str) -> list:
#     """Проверяет email на 120+ платформах через Holehe. Возвращает список находок."""
#     if not _holehe_available():
#         print(colored("[!] Holehe not installed. Run: pip install holehe", "red"))
#         return []

#     try:
#         proc = subprocess.run(
#             ["holehe", email, "--only-used"],
#             capture_output=True, text=True, timeout=120
#         )
#         output = proc.stdout + proc.stderr
#     except subprocess.TimeoutExpired:
#         print(colored("[!] Holehe timeout (120s).", "red"))
#         return []
#     except Exception as e:
#         print(colored(f"[!] Holehe error: {e}", "red"))
#         return []

#     found = _parse_holehe_output(output)

#     if not found:
#         print(colored("(no accounts found)", "yellow"))
#         return []

#     print(colored(f"Found on {len(found)} platform(s):\n", "white"))
#     for item in found:
#         platform = item["platform"].ljust(25)
#         url = item["url"] if item["url"] else ""
#         print(f"  {colored(platform, 'cyan')} {url}")

#     return found


# def search_email_breaches(email: str):
#     """Проверяет email в утечках через бесплатный API XposedOrNot."""
#     url = f"https://api.xposedornot.com/v1/check-email/{email}"
    
#     try:
#         response = requests.get(url, timeout=15)
        
#         if response.status_code == 404:
#             print(colored("(no breaches found)", "yellow"))
#             return
            
#         response.raise_for_status()
#         data = response.json()
        
#         breaches = data.get("breaches") or data.get("ExposedBreaches") or []
        
#         if isinstance(breaches, str): breaches = [breaches]

#         if not breaches:
#             print(colored("(no breaches found)", "yellow"))
#             return
        
#         print(colored(f"Found in {len(breaches)} breach(es):\n", "white"))
        
#         for breach in breaches:
#             if isinstance(breach, dict):
#                 name = breach.get("breach_id") or breach.get("breach") or breach.get("Name") or "Unknown"
#                 date = breach.get("breach_date") or breach.get("date") or breach.get("BreachDate") or "Unknown"
#                 data_classes = breach.get("data_classes") or breach.get("fields") or breach.get("DataClasses") or []
#             else:
#                 name = str(breach)
#                 date = "Unknown"
#                 data_classes = []
            
#             print(f"  {colored(name, 'cyan')}")
#             print(f"    Date: {date}")
#             if data_classes:
#                 if isinstance(data_classes, list): print(f"    Data: {', '.join(data_classes)}")
#                 else: print(f"    Data: {data_classes}")
#             print()

#     except requests.exceptions.HTTPError as e:
#         if e.response.status_code == 429: print(colored("[!] XposedOrNot rate limit. Try later.", "yellow"))
#         else: print(colored(f"[!] XposedOrNot HTTP error: {e}", "red"))
#     except requests.exceptions.RequestException as e: print(colored(f"[!] XposedOrNot request failed: {e}", "red"))
#     except json.JSONDecodeError: print(colored("[!] XposedOrNot returned invalid JSON.", "red"))


# def search_email_reputation(email: str):
#     """Проверяет репутацию email через бесплатный API emailrep.io."""
#     try:
#         req = urllib.request.Request(
#             f"https://emailrep.io/{email}",
#             headers={"User-Agent": "OSINT-Tool/1.0"}
#         )
#         with urllib.request.urlopen(req, timeout=10) as resp: data = json.loads(resp.read().decode("utf-8"))
#     except urllib.error.HTTPError as e:
#         if e.code == 429: print(colored("[!] EmailRep rate limit. Try later or add API key.", "yellow"))
#         else: print(colored(f"[!] EmailRep HTTP error: {e.code}", "red"))
#         return
#     except Exception as e:
#         print(colored(f"[!] EmailRep error: {e}", "red"))
#         return

#     print(f"  Reputation : {data.get('reputation', '?')}")
#     print(f"  Suspicious : {data.get('suspicious', '?')}")
#     print(f"  References : {data.get('references', '?')}")

#     details = data.get("details", {})
#     if isinstance(details, dict):
#         profiles = details.get("profiles", [])
#         if profiles: print(f"  Profiles   : {', '.join(profiles)}")
#         if details.get("credentials_leaked"): print(colored("  [!] Credentials leaked in breaches", "red"))
#         if details.get("data_breach"): print(colored("  [!] Present in known data breaches", "red"))
#         if details.get("disposable"): print(colored("  [!] Disposable email", "yellow"))
#         if details.get("spam"): print(colored("  [!] Marked as spam", "yellow"))


# def search_email(email: str):
#     """Расширенный поиск по email: Holehe + XposedOrNot + EmailRep."""
#     print(colored(f"\n=== Check email: {email} ===\n", "magenta"))

#     print(colored("[1] Holehe — registration check (120+ platforms)", "white"))
#     print(colored("-" * 60, "white"))
#     search_email_holehe(email)

#     print()
#     print(colored("[2] XposedOrNot — breach check (free)", "white"))
#     print(colored("-" * 60, "white"))
#     search_email_breaches(email)

#     print()
#     print(colored("[3] EmailRep.io — reputation check", "white"))
#     print(colored("-" * 60, "white"))
#     search_email_reputation(email)

#     print()


# def information_about_email():
#     """Интерактивный ввод email."""
#     email = input("Email address: ").strip()
#     if not email or "@" not in email:
#         print(colored("[!] Invalid email.\n", "red"))
#         return
    
#     search_email(email)


# if __name__ == "__main__": information_about_email()