import os
import subprocess
import sys
import time

from colorama import Back, Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# ASCII Art for PodIA
PODIA_LOGO = """
.-------.     ,-----.     ______     .-./`)    ____     
\  _(`)_ \  .'  .-,  '.  |    _ `''. \ .-.') .'  __ `.  
| (_ o._)| / ,-.|  \ _ \ | _ | ) _  \/ `-' \/   '  \  \ 
|  (_,_) /;  \  '_ /  | :|( ''_'  ) | `-'`"`|___|  /  | 
|   '-.-' |  _`,/ \ _/  || . (_) `. | .---.    _.-`   | 
|   |     : (  '\_/ \   ;|(_    ._) ' |   | .'   _    | 
|   |      \ `"/  \  ) / |  (_.\.' /  |   | |  _( )_  | 
/   )       '. \_/``".'  |       .'   |   | \ (_ o _) / 
`---'         '-----'    '-----'`     '---'  '.(_,_).'  
                                                                                  
{c}✨ AI Podcast Creator ✨{w}
""".format(y=Fore.YELLOW, g=Fore.GREEN, r=Fore.RED, c=Fore.CYAN, w=Fore.WHITE)

def print_step(step, message):
    """Print a formatted step message"""
    print(f"{Fore.BLUE}[{step}] {Fore.CYAN}{message}{Style.RESET_ALL}")

def print_success(message):
    """Print a formatted success message"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print a formatted warning message"""
    print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print a formatted error message"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print a formatted info message"""
    print(f"{Fore.MAGENTA}ℹ️ {message}{Style.RESET_ALL}")

def progress_bar(duration, description="Processing"):
    """Display a simple progress bar for the given duration"""
    bar_length = 40
    for i in range(duration * 10 + 1):
        progress = i / (duration * 10)
        arrow = '=' * int(round(progress * bar_length) - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))
        percentage = round(progress * 100)
        
        sys.stdout.write(f"\r{Fore.BLUE}{description}: [{Fore.GREEN}{arrow}{spaces}{Fore.BLUE}] {percentage}%")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\n')

def main():
    try:
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display the PodIA logo
        print(PODIA_LOGO)
        
        print_step("1/4", "Starting PodIA server...")
        server_proc = subprocess.Popen(
            ["python", "./podia.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print_step("2/4", "Initializing server components")
        progress_bar(10, "Server initialization")
        
        print_step("3/4", "Opening browser...")
        if sys.platform == "win32":
            subprocess.Popen(
                ["powershell", "-Command", "Start-Process", "http://localhost:4022"]
            )
        else:
            import webbrowser
            webbrowser.open("http://localhost:4022")
        
        print_success("Browser opened at http://localhost:4022")
        
        print_step("4/4", "Server is ready!")
        print(f"\n{Fore.GREEN}{'=' * 60}")
        print(f"{Fore.WHITE}{Style.BRIGHT}🎙️  PodIA Server Running  🎙️")
        print(f"{Fore.CYAN}Access the interface at: {Fore.YELLOW}http://localhost:4022")
        print(f"{Fore.WHITE}{Style.BRIGHT}Press Ctrl+C to stop the server")
        print(f"{Fore.GREEN}{'=' * 60}\n")
        
        server_proc.wait()
        
    except KeyboardInterrupt:
        print_warning("\nShutdown requested...")
        print_step("1/2", "Stopping server processes")
        progress_bar(2, "Shutting down")
        
        server_proc.terminate()
        server_proc.wait()
        
        print_success("Server stopped successfully")
        print_info("Thank you for using PodIA! 👋")


if __name__ == "__main__":
    main()
