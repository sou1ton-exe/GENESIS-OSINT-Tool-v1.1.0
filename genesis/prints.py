from termcolor import colored

logo = colored("""
    
       
       ▄██████▄     ▄████████ ███▄▄▄▄      ▄████████    ▄████████  ▄█     ▄████████ 
      ███    ███   ███    ███ ███▀▀▀██▄   ███    ███   ███    ███ ███    ███    ███ 
      ███    █▀    ███    █▀  ███   ███   ███    █▀    ███    █▀  ███▌   ███    █▀  
     ▄███         ▄███▄▄▄     ███   ███  ▄███▄▄▄       ███        ███▌   ███        
    ▀▀███ ████▄  ▀▀███▀▀▀     ███   ███ ▀▀███▀▀▀     ▀███████████ ███▌ ▀███████████ 
      ███    ███   ███    █▄  ███   ███   ███    █▄           ███ ███           ███ 
      ███    ███   ███    ███ ███   ███   ███    ███    ▄█    ███ ███     ▄█    ███ 
      ████████▀    ██████████  ▀█   █▀    ██████████  ▄████████▀  █▀    ▄████████▀  
                                                                                


        """, "magenta")

BM = "\033[1;35m"
R  = "\033[0m"

PROMPT = f"{BM}>>>{R} "

user_option_panel = (
    "    \033[1m[1]\033[0m Viewing image metadata\n"
    "    \033[1m[2]\033[0m Viewing PDF metadata\n"
    "    \033[1m[3]\033[0m Viewing office document metadata\n"
    "    \033[1m[4]\033[0m Auto-detect file type\n"
    "    \033[1m[5]\033[0m Information about an IP address or domain\n"
    f"    \033[1m[6]\033[0m Check email (120+ platforms) - {colored("not done [x]", "red")}\n"
    "    \033[1m[7]\033[0m Check nickname (3000+ sites)\n"
    f"    \033[1m[8]\033[0m Check phone number (telegram + operator) - {colored("not done [x]", "red")}\n"
    f"    {colored('[0]', 'red', attrs=['bold'])} exit\n"
)