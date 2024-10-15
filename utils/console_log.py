from colorama import Fore, Style, init

init(autoreset=True)

def blue_log(text):
    print(Fore.BLUE + text)

def green_log(text):
    print(Fore.GREEN + text)

def yellow_log(text):
    print(Fore.YELLOW + text)

def red_log(text):
    print(Fore.RED + text)