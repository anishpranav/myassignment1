"""
AI Commands - Natural language command interpretation
"""

import re
from typing import List, Tuple, Dict, Any
from utils.colors import Colors

class AICommandInterpreter:
    """Interprets natural language commands into terminal commands"""
    
    def __init__(self):
        self.command_patterns = {
            'create_dir': [
                r'(?:create|make).*?(?:folder|directory).*?(?:called|named)?\s+(["\']?)(\w+)\1',
                r'mkdir\s+(["\']?)(\w+)\1',
                r'new\s+(?:folder|directory)\s+(["\']?)(\w+)\1',
            ],
            'create_file': [
                r'(?:create|make).*?file.*?(?:called|named)?\s+(["\']?)([^"\'\s]+)\1',
                r'touch\s+(["\']?)([^"\'\s]+)\1',
                r'new\s+file\s+(["\']?)([^"\'\s]+)\1',
            ],
            'list': [
                r'(?:list|show).*?(?:files|directories|contents|what\'?s here)',
                r'what.*?(?:here|directory|folder)',
                r'ls',
                r'dir',
                r'show\s+me.*?(?:files|contents)'
            ],
            'list_detailed': [
                r'(?:list|show).*?(?:detailed|details|long)',
                r'ls.*?-l',
                r'detailed.*?(?:list|listing)'
            ],
            'change_dir': [
                r'(?:go|navigate|change).*?(?:to|into)\s+(["\']?)([^"\'\s]+)\1',
                r'cd\s+(["\']?)([^"\'\s]+)\1',
                r'enter\s+(?:folder|directory)\s+(["\']?)([^"\'\s]+)\1',
            ],
            'go_home': [
                r'go\s+home',
                r'cd\s+~',
                r'home\s+directory'
            ],
            'go_back': [
                r'go\s+back',
                r'cd\s+\.\.',
                r'parent\s+directory',
                r'up\s+(?:one\s+)?(?:level|directory)'
            ],
            'current_dir': [
                r'where.*?am.*?i',
                r'current.*?(?:directory|folder|location|path)',
                r'pwd',
                r'print.*?working.*?directory'
            ],
            'remove_file': [
                r'(?:delete|remove).*?file\s+(["\']?)([^"\'\s]+)\1',
                r'rm\s+(["\']?)([^"\'\s]+)\1',
            ],
            'remove_dir': [
                r'(?:delete|remove).*?(?:folder|directory)\s+(["\']?)([^"\'\s]+)\1',
                r'rmdir\s+(["\']?)([^"\'\s]+)\1',
                r'rm\s+-r\s+(["\']?)([^"\'\s]+)\1',
            ],
            'copy': [
                r'copy\s+(["\']?)([^"\'\s]+)\1.*?(?:to|into)\s+(["\']?)([^"\'\s]+)\3',
                r'cp\s+(["\']?)([^"\'\s]+)\1\s+(["\']?)([^"\'\s]+)\3',
            ],
            'move': [
                r'move\s+(["\']?)([^"\'\s]+)\1.*?(?:to|into)\s+(["\']?)([^"\'\s]+)\3',
                r'mv\s+(["\']?)([^"\'\s]+)\1\s+(["\']?)([^"\'\s]+)\3',
                r'rename\s+(["\']?)([^"\'\s]+)\1.*?(?:to)\s+(["\']?)([^"\'\s]+)\3',
            ],
            'show_file': [
                r'(?:show|display|cat|read).*?file\s+(["\']?)([^"\'\s]+)\1',
                r'cat\s+(["\']?)([^"\'\s]+)\1',
                r'what\'?s\s+in\s+(["\']?)([^"\'\s]+)\1',
            ],
            'find_file': [
                r'find.*?file.*?(?:called|named)\s+(["\']?)([^"\'\s]+)\1',
                r'search.*?for.*?(["\']?)([^"\'\s]+)\1',
                r'locate.*?(["\']?)([^"\'\s]+)\1',
            ],
            'system_info': [
                r'(?:show|display).*?system.*?(?:info|information)',
                r'sysinfo',
                r'system\s+details',
                r'computer\s+info'
            ],
            'processes': [
                r'(?:show|list).*?(?:processes|running\s+programs)',
                r'ps',
                r'what.*?running',
                r'active\s+processes'
            ],
            'memory': [
                r'(?:show|check).*?memory.*?usage',
                r'free\s+memory',
                r'ram\s+usage',
                r'memory\s+info'
            ],
            'disk_space': [
                r'(?:show|check).*?disk.*?(?:space|usage)',
                r'df',
                r'storage\s+info',
                r'free\s+space'
            ],
            'clear_screen': [
                r'clear.*?(?:screen|terminal)',
                r'cls',
                r'clean.*?screen'
            ],
            'help': [
                r'help',
                r'what.*?can.*?do',
                r'available.*?commands',
                r'show.*?commands'
            ]
        }
        
        # Common file/directory shortcuts
        self.shortcuts = {
            'desktop': 'Desktop',
            'documents': 'Documents', 
            'downloads': 'Downloads',
            'home': '~',
            'root': '/',
            'temp': '/tmp',
            'temporary': '/tmp'
        }
    
    def normalize_path(self, path: str) -> str:
        """Normalize path using shortcuts"""
        path_lower = path.lower()
        if path_lower in self.shortcuts:
            return self.shortcuts[path_lower]
        return path
    
    def interpret(self, query: str) -> List[Tuple[str, List[str]]]:
        """Interpret natural language query into commands"""
        query = query.strip()
        if not query:
            return []
        
        commands = []
        
        # Check each command pattern
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    cmd, args = self._process_match(command_type, match, query)
                    if cmd:
                        commands.append((cmd, args))
                        return commands  # Return first match
        
        # If no patterns matched, try to extract basic commands
        words = query.lower().split()
        if 'create' in words or 'make' in words:
            if 'folder' in words or 'directory' in words:
                # Try to extract folder name
                for word in words:
                    if word not in ['create', 'make', 'a', 'folder', 'directory', 'called', 'named']:
                        commands.append(('mkdir', [word]))
                        break
            elif 'file' in words:
                # Try to extract file name
                for word in words:
                    if word not in ['create', 'make', 'a', 'file', 'called', 'named']:
                        commands.append(('touch', [word]))
                        break
        
        return commands
    
    def _process_match(self, command_type: str, match: re.Match, query: str) -> Tuple[str, List[str]]:
        """Process regex match and return command and arguments"""
        
        if command_type == 'create_dir':
            # Extract directory name (handle both quoted and unquoted)
            groups = match.groups()
            if len(groups) >= 2:
                dir_name = groups[1] or groups[0]  # Take non-empty group
            else:
                dir_name = groups[0] if groups else 'newfolder'
            return 'mkdir', [self.normalize_path(dir_name)]
            
        elif command_type == 'create_file':
            groups = match.groups()
            if len(groups) >= 2:
                file_name = groups[1] or groups[0]
            else:
                file_name = groups[0] if groups else 'newfile.txt'
            return 'touch', [file_name]
            
        elif command_type == 'list':
            return 'ls', []
            
        elif command_type == 'list_detailed':
            return 'ls', ['-l']
            
        elif command_type == 'change_dir':
            groups = match.groups()
            if len(groups) >= 2:
                dir_name = groups[1] or groups[0]
            else:
                dir_name = groups[0] if groups else '.'
            return 'cd', [self.normalize_path(dir_name)]
            
        elif command_type == 'go_home':
            return 'cd', ['~']
            
        elif command_type == 'go_back':
            return 'cd', ['..']
            
        elif command_type == 'current_dir':
            return 'pwd', []
            
        elif command_type == 'remove_file':
            groups = match.groups()
            if len(groups) >= 2:
                file_name = groups[1] or groups[0]
            else:
                file_name = groups[0] if groups else ''
            return 'rm', [file_name] if file_name else ('rm', [])
            
        elif command_type == 'remove_dir':
            groups = match.groups()
            if len(groups) >= 2:
                dir_name = groups[1] or groups[0]
            else:
                dir_name = groups[0] if groups else ''
            return 'rm', ['-r', dir_name] if dir_name else ('rm', ['-r'])
            
        elif command_type == 'copy':
            groups = match.groups()
            if len(groups) >= 4:
                source = groups[1] or groups[0]
                dest = groups[3] or groups[2]
                return 'cp', [source, dest]
            return None, []
            
        elif command_type == 'move':
            groups = match.groups()
            if len(groups) >= 4:
                source = groups[1] or groups[0]
                dest = groups[3] or groups[2]
                return 'mv', [source, dest]
            return None, []
            
        elif command_type == 'show_file':
            groups = match.groups()
            if len(groups) >= 2:
                file_name = groups[1] or groups[0]
            else:
                file_name = groups[0] if groups else ''
            return 'cat', [file_name] if file_name else ('cat', [])
            
        elif command_type == 'find_file':
            groups = match.groups()
            if len(groups) >= 2:
                pattern = groups[1] or groups[0]
            else:
                pattern = groups[0] if groups else '*'
            return 'find', [pattern]
            
        elif command_type == 'system_info':
            return 'sysinfo', []
            
        elif command_type == 'processes':
            return 'ps', []
            
        elif command_type == 'memory':
            return 'free', []
            
        elif command_type == 'disk_space':
            return 'df', []
            
        elif command_type == 'clear_screen':
            return 'clear', []
            
        elif command_type == 'help':
            return 'help', []
        
        return None, []
    
    def get_suggestions(self, query: str) -> List[str]:
        """Get command suggestions based on partial query"""
        suggestions = []
        query_lower = query.lower()
        
        suggestion_map = {
            'create': ['create folder myproject', 'create file readme.txt'],
            'make': ['make directory docs', 'make file script.py'],
            'list': ['list files', 'show directory contents'],
            'show': ['show files', 'show system info', 'show processes'],
            'copy': ['copy file1.txt to backup/', 'copy folder1 to archive/'],
            'move': ['move file.txt to documents/', 'rename old.txt to new.txt'],
            'delete': ['delete file unwanted.txt', 'remove folder oldstuff'],
            'find': ['find file *.py', 'search for readme'],
            'go': ['go to documents', 'go home', 'go back'],
        }
        
        for keyword, examples in suggestion_map.items():
            if keyword in query_lower:
                suggestions.extend(examples)
        
        return suggestions[:5]  # Return top 5 suggestions


class AICommands:
    """AI command handler"""
    
    def __init__(self, terminal):
        self.terminal = terminal
        self.interpreter = AICommandInterpreter()
    
    def cmd_ai(self, args: List[str]) -> str:
        """Process AI natural language commands"""
        if not args:
            return f"""{Colors.CYAN}AI Assistant - Natural Language Commands{Colors.RESET}

{Colors.YELLOW}Examples:{Colors.RESET}
  ai create folder called projects
  ai show me what files are here  
  ai copy readme.txt to backup folder
  ai go to documents directory
  ai find files with .py extension
  ai show system information
  ai delete file olddata.txt

{Colors.YELLOW}Supported operations:{Colors.RESET}
  • File/folder creation, deletion, copying, moving
  • Directory navigation and listing
  • File searching and content viewing
  • System information and process monitoring
  • Memory and disk usage checking

{Colors.GREEN}Try: ai <your command in plain English>{Colors.RESET}
            """
        
        query = " ".join(args)
        commands = self.interpreter.interpret(query)
        
        if commands:
            outputs = []
            outputs.append(f"{Colors.CYAN}AI:{Colors.RESET} Interpreting: {Colors.YELLOW}'{query}'{Colors.RESET}")
            
            for cmd, cmd_args in commands:
                cmd_str = f"{cmd} {' '.join(cmd_args)}" if cmd_args else cmd
                outputs.append(f"{Colors.GREEN}➤{Colors.RESET} Executing: {Colors.BOLD}{cmd_str}{Colors.RESET}")
                
                # Execute the command
                result = self.terminal.execute(cmd_str)
                if result:
                    # Indent the output for better readability
                    indented_result = '\n'.join(f"  {line}" for line in result.split('\n'))
                    outputs.append(indented_result)
            
            return '\n'.join(outputs)
        else:
            # Provide suggestions
            suggestions = self.interpreter.get_suggestions(query)
            output = f"{Colors.YELLOW}AI:{Colors.RESET} I couldn't understand that command.\n"
            
            if suggestions:
                output += f"\n{Colors.CYAN}Did you mean:{Colors.RESET}\n"
                for suggestion in suggestions:
                    output += f"  • ai {suggestion}\n"
            else:
                output += f"\n{Colors.CYAN}Try something like:{Colors.RESET}\n"
                output += f"  • ai create folder myproject\n"
                output += f"  • ai show files in current directory\n"
                output += f"  • ai copy file.txt to backup\n"
                output += f"  • ai find files named *.py\n"
            
            return output.rstrip()