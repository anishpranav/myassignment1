#!/usr/bin/env python3
"""
AI-Powered Terminal - Main Entry Point
A fully functional terminal with Python backend
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from terminal_core import Terminal
from utils.colors import Colors

def print_banner():
    """Print the terminal banner"""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║          AI-POWERED PYTHON TERMINAL v2.0                ║
║                                                          ║
║  {Colors.GREEN}Type 'help' for available commands{Colors.CYAN}                     ║
║  {Colors.GREEN}Type 'ai <query>' for natural language commands{Colors.CYAN}        ║
║  {Colors.GREEN}Type 'exit' to quit{Colors.CYAN}                                    ║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(banner)

def install_requirements():
    """Install required packages if not present"""
    required_packages = ['psutil']
    
    try:
        import psutil
    except ImportError:
        print(f"{Colors.YELLOW}Installing required packages...{Colors.RESET}")
        import subprocess
        for package in required_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"{Colors.RED}Failed to install {package}. Some features may not work.{Colors.RESET}")
        print(f"{Colors.GREEN}Installation complete!{Colors.RESET}")

def main():
    """Main entry point"""
    # Install requirements
    install_requirements()
    
    # Parse command line arguments
    use_virtual = False
    if len(sys.argv) > 1:
        if '--virtual' in sys.argv:
            use_virtual = True
        elif '--help' in sys.argv or '-h' in sys.argv:
            print(f"""
{Colors.CYAN}Python Terminal Usage:{Colors.RESET}

{Colors.GREEN}python main.py{Colors.RESET}          - Run terminal with real filesystem
{Colors.GREEN}python main.py --virtual{Colors.RESET} - Run terminal with virtual filesystem (safe mode)
{Colors.GREEN}python main.py --help{Colors.RESET}    - Show this help message

{Colors.YELLOW}Features:{Colors.RESET}
- Full file system operations (ls, cd, mkdir, rm, etc.)
- System monitoring (ps, top, sysinfo)
- AI natural language command interpretation
- Command history and auto-completion
- Process management
- Real-time system information
            """)
            return
    
    print_banner()
    
    # Initialize terminal
    if use_virtual:
        print(f"{Colors.YELLOW}Running in VIRTUAL filesystem mode (safe){Colors.RESET}")
    else:
        print(f"{Colors.GREEN}Running with REAL filesystem{Colors.RESET}")
    
    terminal = Terminal(use_virtual=use_virtual)
    
    # Main terminal loop
    try:
        terminal.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Terminal interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
    finally:
        print(f"{Colors.CYAN}Goodbye!{Colors.RESET}")

if __name__ == "__main__":
    main()