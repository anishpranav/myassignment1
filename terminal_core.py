"""
Terminal Core - Main terminal functionality
"""

import os
import sys
import readline
import atexit
from pathlib import Path
from typing import Dict, List

from commands.file_operations import FileOperations
from commands.system_commands import SystemCommands
from commands.ai_commands import AICommands
from filesystem.virtual_fs import VirtualFileSystem
from utils.colors import Colors
from utils.command_parser import CommandParser

class Terminal:
    """Main terminal class that orchestrates all components"""
    
    def __init__(self, use_virtual=False):
        self.use_virtual = use_virtual
        self.running = True
        
        # Initialize components
        self.virtual_fs = VirtualFileSystem() if use_virtual else None
        self.command_parser = CommandParser()
        
        # Initialize command handlers
        self.file_ops = FileOperations(self.virtual_fs)
        self.system_commands = SystemCommands()
        self.ai_commands = AICommands(self)
        
        # Command history
        self.command_history = []
        self.history_file = Path.home() / '.python_terminal_history'
        
        # Setup readline for better CLI experience
        self.setup_readline()
        
        # Register all available commands
        self.commands = self._register_commands()
    
    def _register_commands(self) -> Dict:
        """Register all available commands"""
        commands = {}
        
        # File operations
        commands.update({
            'ls': self.file_ops.cmd_ls,
            'cd': self.file_ops.cmd_cd,
            'pwd': self.file_ops.cmd_pwd,
            'mkdir': self.file_ops.cmd_mkdir,
            'rm': self.file_ops.cmd_rm,
            'rmdir': self.file_ops.cmd_rmdir,
            'touch': self.file_ops.cmd_touch,
            'cat': self.file_ops.cmd_cat,
            'cp': self.file_ops.cmd_cp,
            'mv': self.file_ops.cmd_mv,
            'find': self.file_ops.cmd_find,
            'grep': self.file_ops.cmd_grep,
        })
        
        # System commands
        commands.update({
            'ps': self.system_commands.cmd_ps,
            'top': self.system_commands.cmd_top,
            'kill': self.system_commands.cmd_kill,
            'sysinfo': self.system_commands.cmd_sysinfo,
            'df': self.system_commands.cmd_df,
            'free': self.system_commands.cmd_free,
            'uptime': self.system_commands.cmd_uptime,
            'whoami': self.system_commands.cmd_whoami,
            'date': self.system_commands.cmd_date,
            'env': self.system_commands.cmd_env,
        })
        
        # AI and utility commands
        commands.update({
            'ai': self.ai_commands.cmd_ai,
            'echo': self._cmd_echo,
            'clear': self._cmd_clear,
            'cls': self._cmd_clear,  # Windows alias
            'help': self._cmd_help,
            'history': self._cmd_history,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit,  # Alias
        })
        
        return commands
    
    def setup_readline(self):
        """Setup readline for command history and auto-completion"""
        readline.set_completer(self.completer)
        readline.parse_and_bind('tab: complete')
        readline.set_history_length(1000)
        
        # Load existing history
        self.load_history()
        
        # Save history on exit
        atexit.register(self.save_history)
    
    def completer(self, text, state):
        """Auto-completion function"""
        options = []
        
        # Command completion
        if not text or ' ' not in readline.get_line_buffer().strip():
            options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        else:
            # File/directory completion for file commands
            try:
                line_buffer = readline.get_line_buffer().strip()
                parts = line_buffer.split()
                if len(parts) >= 2:
                    cmd = parts[0]
                    if cmd in ['cd', 'ls', 'cat', 'rm', 'cp', 'mv']:
                        # Get current directory listing for completion
                        current_dir = self.get_current_directory()
                        if self.use_virtual:
                            items = self.virtual_fs.list_directory(current_dir)
                        else:
                            try:
                                items = os.listdir(current_dir)
                            except:
                                items = []
                        options = [item for item in items if item.startswith(text)]
            except:
                pass
        
        if state < len(options):
            return options[state]
        return None
    
    def load_history(self):
        """Load command history from file"""
        try:
            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
        except:
            pass  # Ignore errors
    
    def save_history(self):
        """Save command history to file"""
        try:
            readline.write_history_file(str(self.history_file))
        except:
            pass  # Ignore errors
    
    def get_current_directory(self) -> str:
        """Get current working directory"""
        if self.use_virtual:
            return self.virtual_fs.current_path
        else:
            return os.getcwd()
    
    def get_prompt(self) -> str:
        """Generate the command prompt"""
        current_dir = self.get_current_directory()
        username = os.getenv('USER', os.getenv('USERNAME', 'user'))
        hostname = 'terminal'
        
        # Shorten path for display
        if len(current_dir) > 30:
            current_dir = '...' + current_dir[-27:]
        
        return f"{Colors.GREEN}{username}@{hostname}{Colors.RESET}:{Colors.BLUE}{current_dir}{Colors.RESET}$ "
    
    def execute(self, command_line: str) -> str:
        """Execute a command and return output"""
        if not command_line.strip():
            return ""
        
        # Parse command
        try:
            cmd, args = self.command_parser.parse(command_line)
        except Exception as e:
            return f"{Colors.RED}Parse error: {str(e)}{Colors.RESET}"
        
        # Add to history
        self.command_history.append(command_line)
        
        # Execute command
        if cmd in self.commands:
            try:
                result = self.commands[cmd](args)
                return result if result else ""
            except Exception as e:
                return f"{Colors.RED}Error executing {cmd}: {str(e)}{Colors.RESET}"
        else:
            # Try to execute as system command (if not in virtual mode)
            if not self.use_virtual:
                try:
                    import subprocess
                    result = subprocess.run(command_line, shell=True, capture_output=True, 
                                          text=True, timeout=10)
                    if result.returncode == 0:
                        return result.stdout.strip()
                    else:
                        return f"{Colors.RED}Command failed: {result.stderr.strip()}{Colors.RESET}"
                except subprocess.TimeoutExpired:
                    return f"{Colors.RED}Command timed out{Colors.RESET}"
                except Exception as e:
                    return f"{Colors.RED}System command error: {str(e)}{Colors.RESET}"
            
            return f"{Colors.RED}Command not found: {cmd}{Colors.RESET}"
    
    def run(self):
        """Main terminal loop"""
        while self.running:
            try:
                # Get user input
                prompt = self.get_prompt()
                command_line = input(prompt)
                
                # Execute command
                output = self.execute(command_line)
                
                # Print output if any
                if output:
                    print(output)
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Use 'exit' to quit{Colors.RESET}")
            except EOFError:
                self.running = False
    
    # Built-in commands
    def _cmd_echo(self, args: List[str]) -> str:
        """Echo command"""
        return " ".join(args)
    
    def _cmd_clear(self, args: List[str]) -> str:
        """Clear terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return ""
    
    def _cmd_help(self, args: List[str]) -> str:
        """Show help information"""
        help_text = f"""
{Colors.CYAN}Available Commands:{Colors.RESET}

{Colors.YELLOW}File Operations:{Colors.RESET}
  ls [path]           - List directory contents
  cd <dir>            - Change directory
  pwd                 - Print working directory
  mkdir <dir>         - Create directory
  rmdir <dir>         - Remove empty directory
  rm <file/dir>       - Remove file or directory
  touch <file>        - Create empty file
  cat <file>          - Display file contents
  cp <src> <dst>      - Copy file or directory
  mv <src> <dst>      - Move/rename file or directory
  find <name>         - Find files by name
  grep <pattern> <file> - Search for pattern in file

{Colors.YELLOW}System Commands:{Colors.RESET}
  ps                  - Show running processes
  top                 - Show system resource usage
  kill <pid>          - Terminate process by PID
  sysinfo             - Show system information
  df                  - Show disk space usage
  free                - Show memory usage
  uptime              - Show system uptime
  whoami              - Show current user
  date                - Show current date/time
  env                 - Show environment variables

{Colors.YELLOW}AI & Utility:{Colors.RESET}
  ai <query>          - Natural language command interpretation
  echo <text>         - Display text
  clear/cls           - Clear terminal screen
  history             - Show command history
  help                - Show this help
  exit/quit           - Exit terminal

{Colors.YELLOW}Examples:{Colors.RESET}
  {Colors.GREEN}ai create a folder called projects{Colors.RESET}
  {Colors.GREEN}ai show me what files are here{Colors.RESET}
  {Colors.GREEN}ai copy file1.txt to backup folder{Colors.RESET}
        """
        return help_text
    
    def _cmd_history(self, args: List[str]) -> str:
        """Show command history"""
        if not self.command_history:
            return "No command history"
        
        # Show last 20 commands
        start_idx = max(0, len(self.command_history) - 20)
        history_lines = []
        
        for i, cmd in enumerate(self.command_history[start_idx:], start_idx + 1):
            history_lines.append(f"{Colors.CYAN}{i:4d}{Colors.RESET}  {cmd}")
        
        return "\n".join(history_lines)
    
    def _cmd_exit(self, args: List[str]) -> str:
        """Exit terminal"""
        self.running = False
        return f"{Colors.GREEN}Goodbye!{Colors.RESET}"