"""
Command line parser utilities
"""

import shlex
from typing import Tuple, List

class CommandParser:
    """Parse command lines with proper handling of quotes and escapes"""
    
    def __init__(self):
        pass
    
    def parse(self, command_line: str) -> Tuple[str, List[str]]:
        """
        Parse a command line into command and arguments
        
        Args:
            command_line: The command line string to parse
            
        Returns:
            Tuple of (command, arguments_list)
            
        Raises:
            ValueError: If command line cannot be parsed
        """
        if not command_line.strip():
            return "", []
        
        try:
            # Use shlex to properly handle quotes and escapes
            parts = shlex.split(command_line.strip())
            
            if not parts:
                return "", []
            
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            return command, args
            
        except ValueError as e:
            # Handle shlex parsing errors (unclosed quotes, etc.)
            raise ValueError(f"Invalid command syntax: {str(e)}")
    
    def parse_with_pipes(self, command_line: str) -> List[Tuple[str, List[str]]]:
        """
        Parse command line with pipe support
        
        Args:
            command_line: Command line potentially containing pipes
            
        Returns:
            List of (command, arguments) tuples for each piped command
        """
        if '|' not in command_line:
            cmd, args = self.parse(command_line)
            return [(cmd, args)]
        
        # Split by pipes and parse each part
        pipe_parts = command_line.split('|')
        commands = []
        
        for part in pipe_parts:
            part = part.strip()
            if part:
                try:
                    cmd, args = self.parse(part)
                    commands.append((cmd, args))
                except ValueError:
                    # If parsing fails, treat as simple string split
                    parts = part.split()
                    if parts:
                        commands.append((parts[0], parts[1:]))
        
        return commands
    
    def expand_globs(self, args: List[str], current_dir: str = '.') -> List[str]:
        """
        Expand glob patterns in arguments
        
        Args:
            args: List of arguments that may contain glob patterns
            current_dir: Current directory for relative path expansion
            
        Returns:
            List of arguments with globs expanded
        """
        import glob
        import os
        
        expanded_args = []
        
        for arg in args:
            if '*' in arg or '?' in arg or '[' in arg:
                # Expand glob pattern
                matches = glob.glob(arg)
                if matches:
                    # Sort matches for consistent output
                    expanded_args.extend(sorted(matches))
                else:
                    # No matches, keep original
                    expanded_args.append(arg)
            else:
                expanded_args.append(arg)
        
        return expanded_args
    
    def substitute_variables(self, command_line: str, variables: dict = None) -> str:
        """
        Substitute environment variables and custom variables
        
        Args:
            command_line: Command line with potential variables
            variables: Dictionary of custom variables (optional)
            
        Returns:
            Command line with variables substituted
        """
        import os
        import re
        
        if variables is None:
            variables = {}
        
        # Substitute $VAR and ${VAR} patterns
        def replace_var(match):
            var_name = match.group(1) or match.group(2)
            
            # Check custom variables first, then environment
            if var_name in variables:
                return str(variables[var_name])
            else:
                return os.getenv(var_name, match.group(0))  # Return original if not found
        
        # Pattern for $VAR or ${VAR}
        pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
        return re.sub(pattern, replace_var, command_line)
    
    def parse_redirections(self, args: List[str]) -> Tuple[List[str], dict]:
        """
        Parse redirection operators from arguments
        
        Args:
            args: List of command arguments
            
        Returns:
            Tuple of (cleaned_args, redirections_dict)
        """
        clean_args = []
        redirections = {}
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == '>':
                # Redirect stdout
                if i + 1 < len(args):
                    redirections['stdout'] = args[i + 1]
                    i += 2
                else:
                    clean_args.append(arg)
                    i += 1
            elif arg == '>>':
                # Append stdout
                if i + 1 < len(args):
                    redirections['stdout_append'] = args[i + 1]
                    i += 2
                else:
                    clean_args.append(arg)
                    i += 1
            elif arg == '2>':
                # Redirect stderr
                if i + 1 < len(args):
                    redirections['stderr'] = args[i + 1]
                    i += 2
                else:
                    clean_args.append(arg)
                    i += 1
            elif arg == '<':
                # Redirect stdin
                if i + 1 < len(args):
                    redirections['stdin'] = args[i + 1]
                    i += 2
                else:
                    clean_args.append(arg)
                    i += 1
            elif arg.startswith('>'):
                # Handle >file format
                redirections['stdout'] = arg[1:]
                i += 1
            elif arg.startswith('>>'):
                # Handle >>file format
                redirections['stdout_append'] = arg[2:]
                i += 1
            elif arg.startswith('2>'):
                # Handle 2>file format
                redirections['stderr'] = arg[2:]
                i += 1
            elif arg.startswith('<'):
                # Handle <file format
                redirections['stdin'] = arg[1:]
                i += 1
            else:
                clean_args.append(arg)
                i += 1
        
        return clean_args, redirections
    
    def is_background_command(self, command_line: str) -> Tuple[str, bool]:
        """
        Check if command should run in background (ends with &)
        
        Args:
            command_line: Command line to check
            
        Returns:
            Tuple of (cleaned_command_line, is_background)
        """
        command_line = command_line.strip()
        
        if command_line.endswith('&'):
            return command_line[:-1].strip(), True
        
        return command_line, False
    
    def split_on_operators(self, command_line: str) -> List[Tuple[str, str]]:
        """
        Split command line on logical operators (&& and ||)
        
        Args:
            command_line: Command line with potential operators
            
        Returns:
            List of (command, operator) tuples
        """
        import re
        
        # Split on && or ||, keeping the operators
        parts = re.split(r'(\s*&&\s*|\s*\|\|\s*)', command_line)
        
        commands = []
        i = 0
        while i < len(parts):
            cmd = parts[i].strip()
            if cmd:
                operator = None
                if i + 1 < len(parts):
                    next_part = parts[i + 1].strip()
                    if next_part in ['&&', '||']:
                        operator = next_part
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
                
                commands.append((cmd, operator))
        
        return commands