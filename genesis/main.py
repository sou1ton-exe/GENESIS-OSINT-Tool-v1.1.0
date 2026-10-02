"    @Telegram Channel: https://t.me/s_lowcode_w                                                          "
"    @Author's support: https://dalink.to/sou1toon                                                        "
"    |----------------------------------------- by sou1toon -----------------------------------------|    "
"    |                                                                                               |    "
"    |                                                                                               |    "
"    |                     ░██████╗░███████╗███╗░░██╗███████╗░██████╗██╗░██████╗                     |    "
"    |                     ██╔════╝░██╔════╝████╗░██║██╔════╝██╔════╝██║██╔════╝                     |    "
"    |                     ██║░░██╗░█████╗░░██╔██╗██║█████╗░░╚█████╗░██║╚█████╗░                     |    "
"    |                     ██║░░╚██╗██╔══╝░░██║╚████║██╔══╝░░░╚═══██╗██║░╚═══██╗                     |    "
"    |                     ╚██████╔╝███████╗██║░╚███║███████╗██████╔╝██║██████╔╝                     |    "
"    |                     ░╚═════╝░╚══════╝╚═╝░░╚══╝╚══════╝╚═════╝░╚═╝╚═════╝░                     |    "
"    |                                                                                               |    "
"    |------------------------------------------- v.1.1.0 -------------------------------------------|    "
"    GENESIS is a set of basic tools for searching for information in open sources.                       "
"                                                                                                         "
"                                                                                                         "
"    Open source code to explore                                                                          "





import sys
from termcolor import colored
from prints import logo, user_option_panel, PROMPT
import metadata
import ip_info
import email_info
import nickname_info
import phone_info


def print_banner():
    B = "\033[1m"
    R = "\033[0m"
    print(logo, " " * 21,
          f"{B}═══ OSINT Tool{R}",
          colored(f"{B}v1.1.0{R}", "magenta"),
          f"{B}═══{R}")
    print(" " * 35, f"{B}═{R}",
          colored(f"{B}by{B}", "magenta"),
          f"{B}sou1toon{B}", f"{B}═\n{R}\n")


def main():
    print_banner()
    while True:
        print(user_option_panel)
        user_option = input(PROMPT).strip()

        if user_option == "1": metadata.view_photo_metadata()
        elif user_option == "2": metadata.view_pdf_metadata()
        elif user_option == "3": metadata.view_office_metadata()
        elif user_option == "4": metadata.auto_detect_and_view()
        elif user_option == "5": ip_info.information_about_ip()
        elif user_option == "6": pass #email_info.information_about_email()
        elif user_option == "7": nickname_info.information_about_nickname()
        elif user_option == "8": pass #phone_info.information_about_phone()
        elif user_option == "0": print(colored("Exiting...", "magenta")); sys.exit(0)
        else: print(colored("[!] Invalid menu option.\n", "red"))


if __name__ == "__main__": main()
