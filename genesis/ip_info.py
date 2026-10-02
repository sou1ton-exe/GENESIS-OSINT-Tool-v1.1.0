import socket
import ipaddress
from urllib.parse import urlparse

from termcolor import colored

try: from twoip import TwoIP
except ImportError: TwoIP = None


def _is_valid_ip(value: str) -> bool:
    try: ipaddress.ip_address(value); return True
    except ValueError: return False


def _resolve_domain(domain: str) -> str | None:
    """Превращает домен в IP. Возвращает None при ошибке."""
    try: return socket.gethostbyname(domain)
    except socket.gaierror: return None


def _normalize_target(raw: str) -> tuple[str | None, str | None]:
    """
    Принимает то, что ввёл пользователь: IP, домен, URL.
    Возвращает (ip, domain) — что удалось определить.
    """
    raw = raw.strip().strip('"').strip("'")
    if not raw: return None, None

    if "://" in raw: raw = urlparse(raw).hostname or raw

    raw = raw.split("/")[0]

    if _is_valid_ip(raw): return raw, None

    ip = _resolve_domain(raw)
    return ip, raw


def _print_rows(rows: list) -> None:
    if not rows: return
    width = max(len(str(label)) for label, _ in rows) + 2
    for label, value in rows: print(f"{colored(str(label).ljust(width), 'cyan')}: {value}")


def information_about_ip():
    """Интерактивный запрос цели у пользователя."""
    raw = input("IP / domain / URL (e.g. 8.8.8.8 or github.com): ").strip()
    if not raw: print(colored("[!] Empty input.\n", "red")); return
    show_ip_info(raw)


def show_ip_info(raw_target: str):
    """Основная логика: получает данные и печатает их."""
    if TwoIP is None: print(colored("[!] Install 2ip: pip install 2ip", "red")); return

    ip, domain = _normalize_target(raw_target)
    if not ip: print(colored(f"[!] Could not resolve: {raw_target}\n", "red")); return

    print(colored(f"\n=== IP / Domain info ===", "magenta"))
    print(colored(f"Target: {raw_target}", "white"))

    header_rows = [("IP Address", ip)]
    if domain: header_rows.append(("Domain", domain))
    _print_rows(header_rows)
    print()

    try:
        twoip = TwoIP(key=None)

        print(colored("--- [ Geolocation ] ---", "magenta"))
        try:
            geo = twoip.geo(ip=ip) or {}
            if isinstance(geo, dict) and geo: _print_rows([(k, v) for k, v in geo.items() if v not in ("", None)])
            else: print(colored("(no data)", "yellow"))
        except Exception as e: print(colored(f"[!] geo error: {e}", "red"))

        print()

        print(colored("--- [ Provider ] ---", "magenta"))
        try:
            provider = twoip.provider(ip=ip) or {}
            if isinstance(provider, dict) and provider: _print_rows([(k, v) for k, v in provider.items() if v not in ("", None)])
            else: print(colored("(no data)", "yellow"))
        except Exception as e: print(colored(f"[!] provider error: {e}", "red"))

        print()

    except Exception as e: print(colored(f"[!] 2ip error: {e}\n", "red"))