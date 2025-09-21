"""
File Operations Commands - Handles all file system operations
"""

import os
import shutil
import fnmatch
from pathlib import Path
from typing import List, Optional
from filesystem.virtual_fs import VirtualFileSystem
from utils.colors import Colors

class FileOperations:
    """Handles file and directory operations"""
    
    def __init__(self, virtual_fs: Optional[VirtualFileSystem] = None):
        self.virtual_fs = virtual_fs
        self.use_virtual = virtual_fs is not None
    
    def cmd_ls(self, args: List[str]) -> str:
        """List directory contents"""
        path = args[0] if args else '.'
        detailed = '-l' in args or '--long' in args
        all_files = '-a' in args or '--all' in args
        
        if self.use_virtual:
            current_path = self.virtual_fs.current_path if path == '.' else path
            
            if detailed:
                items = self.virtual_fs.get_detailed_listing(current_path)
                if not items:
                    return f"{Colors.YELLOW}(empty directory){Colors.RESET}"
                
                lines = []
                for item in items:
                    size_str = str(item['size']).rjust(8) if item['type'] == 'file' else '     dir'
                    color = Colors.BLUE if item['is_directory'] else Colors.RESET
                    name = item['name'] + ('/' if item['is_directory'] else '')
                    lines.append(f"{item['permissions']} {size_str} {item['modified']} {color}{name}{Colors.RESET}")
                return '\n'.join(lines)
            else:
                items = self.virtual_fs.list_directory(current_path)
                if not items:
                    return f"{Colors.YELLOW}(empty directory){Colors.RESET}"
                
                # Color directories and files differently
                colored_items = []
                for item in items:
                    if item.endswith('/'):
                        colored_items.append(f"{Colors.BLUE}{item}{Colors.RESET}")
                    else:
                        colored_items.append(item)
                
                return "  ".join(colored_items)
        else:
            try:
                actual_path = os.path.expanduser(path)
                items = os.listdir(actual_path)
                
                if not all_files:
                    items = [item for item in items if not item.startswith('.')]
                
                if detailed:
                    lines = []
                    for item in sorted(items):
                        item_path = os.path.join(actual_path, item)
                        stat_info = os.stat(item_path)
                        
                        # Format permissions
                        perms = '-' if os.path.isfile(item_path) else 'd'
                        perms += 'rwx' if os.access(item_path, os.R_OK | os.W_OK | os.X_OK) else '---'
                        perms += 'r-x' * 2  # Simplified permissions
                        
                        # Format size
                        size = stat_info.st_size
                        
                        # Format time
                        import datetime
                        mod_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                        time_str = mod_time.strftime('%b %d %H:%M')
                        
                        # Color
                        color = Colors.BLUE if os.path.isdir(item_path) else Colors.RESET
                        name = item + ('/' if os.path.isdir(item_path) else '')
                        
                        lines.append(f"{perms} {size:8d} {time_str} {color}{name}{Colors.RESET}")
                    
                    return '\n'.join(lines)
                else:
                    # Simple listing with colors
                    colored_items = []
                    for item in sorted(items):
                        item_path = os.path.join(actual_path, item)
                        if os.path.isdir(item_path):
                            colored_items.append(f"{Colors.BLUE}{item}/{Colors.RESET}")
                        else:
                            colored_items.append(item)
                    
                    return "  ".join(colored_items)
                    
            except FileNotFoundError:
                return f"{Colors.RED}Directory not found: {path}{Colors.RESET}"
            except PermissionError:
                return f"{Colors.RED}Permission denied: {path}{Colors.RESET}"
            except Exception as e:
                return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"
    
    def cmd_cd(self, args: List[str]) -> str:
        """Change directory"""
        path = args[0] if args else '~'
        
        if self.use_virtual:
            if self.virtual_fs.change_directory(path):
                return ""
            else:
                return f"{Colors.RED}Directory not found: {path}{Colors.RESET}"
        else:
            try:
                if path == '~':
                    path = str(Path.home())
                os.chdir(os.path.expanduser(path))
                return ""
            except FileNotFoundError:
                return f"{Colors.RED}Directory not found: {path}{Colors.RESET}"
            except PermissionError:
                return f"{Colors.RED}Permission denied: {path}{Colors.RESET}"
            except Exception as e:
                return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"
    
    def cmd_pwd(self, args: List[str]) -> str:
        """Print working directory"""
        if self.use_virtual:
            return self.virtual_fs.current_path
        else:
            return os.getcwd()
    
    def cmd_mkdir(self, args: List[str]) -> str:
        """Create directory"""
        if not args:
            return f"{Colors.YELLOW}Usage: mkdir <directory_name>{Colors.RESET}"
        
        for dir_name in args:
            if dir_name.startswith('-'):
                continue  # Skip options
            
            if self.use_virtual:
                if self.virtual_fs.create_directory(dir_name):
                    return f"{Colors.GREEN}Directory created: {dir_name}{Colors.RESET}"
                else:
                    return f"{Colors.RED}Failed to create directory: {dir_name}{Colors.RESET}"
            else:
                try:
                    os.makedirs(dir_name, exist_ok=True)
                    return f"{Colors.GREEN}Directory created: {dir_name}{Colors.RESET}"
                except Exception as e:
                    return f"{Colors.RED}Error creating directory: {str(e)}{Colors.RESET}"
        
        return ""
    
    def cmd_rmdir(self, args: List[str]) -> str:
        """Remove empty directory"""
        if not args:
            return f"{Colors.YELLOW}Usage: rmdir <directory_name>{Colors.RESET}"
        
        dir_name = args[0]
        
        if self.use_virtual:
            if self.virtual_fs.is_directory(dir_name):
                items = self.virtual_fs.list_directory(dir_name)
                if items:
                    return f"{Colors.RED}Directory not empty: {dir_name}{Colors.RESET}"
                else:
                    if self.virtual_fs.remove_item(dir_name):
                        return f"{Colors.GREEN}Directory removed: {dir_name}{Colors.RESET}"
            return f"{Colors.RED}Directory not found: {dir_name}{Colors.RESET}"
        else:
            try:
                os.rmdir(dir_name)
                return f"{Colors.GREEN}Directory removed: {dir_name}{Colors.RESET}"
            except OSError as e:
                return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"
    
    def cmd_rm(self, args: List[str]) -> str:
        """Remove file or directory"""
        if not args:
            return f"{Colors.YELLOW}Usage: rm <file_or_directory>{Colors.RESET}"
        
        recursive = '-r' in args or '--recursive' in args
        force = '-f' in args or '--force' in args
        
        # Filter out options
        items_to_remove = [arg for arg in args if not arg.startswith('-')]
        
        if not items_to_remove:
            return f"{Colors.YELLOW}No items specified for removal{Colors.RESET}"
        
        results = []
        for item_name in items_to_remove:
            if self.use_virtual:
                if self.virtual_fs.exists(item_name):
                    if self.virtual_fs.is_directory(item_name) and not recursive:
                        results.append(f"{Colors.RED}Cannot remove directory '{item_name}': use -r for recursive{Colors.RESET}")
                    else:
                        if self.virtual_fs.remove_item(item_name):
                            results.append(f"{Colors.GREEN}Removed: {item_name}{Colors.RESET}")
                        else:
                            results.append(f"{Colors.RED}Failed to remove: {item_name}{Colors.RESET}")
                else:
                    if not force:
                        results.append(f"{Colors.RED}File not found: {item_name}{Colors.RESET}")
            else:
                try:
                    if os.path.isdir(item_name):
                        if recursive:
                            shutil.rmtree(item_name)
                            results.append(f"{Colors.GREEN}Removed directory: {item_name}{Colors.RESET}")
                        else:
                            results.append(f"{Colors.RED}Cannot remove directory '{item_name}': use -r for recursive{Colors.RESET}")
                    else:
                        os.remove(item_name)
                        results.append(f"{Colors.GREEN}Removed: {item_name}{Colors.RESET}")
                except FileNotFoundError:
                    if not force:
                        results.append(f"{Colors.RED}File not found: {item_name}{Colors.RESET}")
                except Exception as e:
                    results.append(f"{Colors.RED}Error removing {item_name}: {str(e)}{Colors.RESET}")
        
        return '\n'.join(results)
    
    def cmd_touch(self, args: List[str]) -> str:
        """Create empty file or update timestamp"""
        if not args:
            return f"{Colors.YELLOW}Usage: touch <filename>{Colors.RESET}"
        
        results = []
        for file_name in args:
            if self.use_virtual:
                if self.virtual_fs.exists(file_name):
                    # File exists, update timestamp (simulated)
                    node = self.virtual_fs.get_node(file_name)
                    if node and node.get('type') == 'file':
                        import datetime
                        node['modified'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        results.append(f"{Colors.GREEN}Updated timestamp: {file_name}{Colors.RESET}")
                else:
                    if self.virtual_fs.create_file(file_name):
                        results.append(f"{Colors.GREEN}File created: {file_name}{Colors.RESET}")
                    else:
                        results.append(f"{Colors.RED}Failed to create file: {file_name}{Colors.RESET}")
            else:
                try:
                    Path(file_name).touch()
                    results.append(f"{Colors.GREEN}File created/updated: {file_name}{Colors.RESET}")
                except Exception as e:
                    results.append(f"{Colors.RED}Error: {str(e)}{Colors.RESET}")
        
        return '\n'.join(results)
    
    def cmd_cat(self, args: List[str]) -> str:
        """Display file contents"""
        if not args:
            return f"{Colors.YELLOW}Usage: cat <filename>{Colors.RESET}"
        
        results = []
        for file_name in args:
            if self.use_virtual:
                content = self.virtual_fs.read_file(file_name)
                if content is not None:
                    results.append(content)
                else:
                    results.append(f"{Colors.RED}File not found or is not a file: {file_name}{Colors.RESET}")
            else:
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        results.append(f.read())
                except FileNotFoundError:
                    results.append(f"{Colors.RED}File not found: {file_name}{Colors.RESET}")
                except IsADirectoryError:
                    results.append(f"{Colors.RED}Is a directory: {file_name}{Colors.RESET}")
                except UnicodeDecodeError:
                    results.append(f"{Colors.RED}Binary file: {file_name}{Colors.RESET}")
                except Exception as e:
                    results.append(f"{Colors.RED}Error reading file: {str(e)}{Colors.RESET}")
        
        return '\n'.join(results)
    
    def cmd_cp(self, args: List[str]) -> str:
        """Copy file or directory"""
        if len(args) < 2:
            return f"{Colors.YELLOW}Usage: cp <source> <destination>{Colors.RESET}"
        
        recursive = '-r' in args or '--recursive' in args
        # Filter out options
        file_args = [arg for arg in args if not arg.startswith('-')]
        
        if len(file_args) < 2:
            return f"{Colors.YELLOW}Usage: cp <source> <destination>{Colors.RESET}"
        
        source, dest = file_args[0], file_args[1]
        
        if self.use_virtual:
            if not self.virtual_fs.exists(source):
                return f"{Colors.RED}Source not found: {source}{Colors.RESET}"
            
            if self.virtual_fs.is_directory(source) and not recursive:
                return f"{Colors.RED}Cannot copy directory '{source}': use -r for recursive{Colors.RESET}"
            
            if self.virtual_fs.copy_item(source, dest):
                return f"{Colors.GREEN}Copied {source} to {dest}{Colors.RESET}"
            else:
                return f"{Colors.RED}Failed to copy {source} to {dest}{Colors.RESET}"
        else:
            try:
                if os.path.isdir(source):
                    if recursive:
                        shutil.copytree(source, dest)
                        return f"{Colors.GREEN}Copied directory {source} to {dest}{Colors.RESET}"
                    else:
                        return f"{Colors.RED}Cannot copy directory '{source}': use -r for recursive{Colors.RESET}"
                else:
                    shutil.copy2(source, dest)
                    return f"{Colors.GREEN}Copied {source} to {dest}{Colors.RESET}"
            except Exception as e:
                return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"
    
    def cmd_mv(self, args: List[str]) -> str:
        """Move/rename file or directory"""
        if len(args) < 2:
            return f"{Colors.YELLOW}Usage: mv <source> <destination>{Colors.RESET}"
        
        source, dest = args[0], args[1]
        
        if self.use_virtual:
            if not self.virtual_fs.exists(source):
                return f"{Colors.RED}Source not found: {source}{Colors.RESET}"
            
            if self.virtual_fs.move_item(source, dest):
                return f"{Colors.GREEN}Moved {source} to {dest}{Colors.RESET}"
            else:
                return f"{Colors.RED}Failed to move {source} to {dest}{Colors.RESET}"
        else:
            try:
                shutil.move(source, dest)
                return f"{Colors.GREEN}Moved {source} to {dest}{Colors.RESET}"
            except Exception as e:
                return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"
    
    def cmd_find(self, args: List[str]) -> str:
        """Find files by name pattern"""
        if not args:
            return f"{Colors.YELLOW}Usage: find <pattern>{Colors.RESET}"
        
        pattern = args[0]
        search_path = args[1] if len(args) > 1 else None
        
        if self.use_virtual:
            matches = self.virtual_fs.find_files(pattern, search_path)
            if matches:
                return '\n'.join(matches)
            else:
                return f"{Colors.YELLOW}No files found matching pattern: {pattern}{Colors.RESET}"
        else:
            try:
                start_path = search_path or '.'
                matches = []
                
                for root, dirs, files in os.walk(start_path):
                    for file in files:
                        if fnmatch.fnmatch(file.lower(), pattern.lower()):
                            matches.append(os.path.join(root, file))
                
                if matches:
                    return '\n'.join(matches)
                else:
                    return f"{Colors.YELLOW}No files found matching pattern: {pattern}{Colors.RESET}"
            except Exception as e:
                return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"
    
    def cmd_grep(self, args: List[str]) -> str:
        """Search for pattern in files"""
        if len(args) < 2:
            return f"{Colors.YELLOW}Usage: grep <pattern> <file>{Colors.RESET}"
        
        pattern = args[0]
        file_name = args[1]
        
        if self.use_virtual:
            content = self.virtual_fs.read_file(file_name)
            if content is None:
                return f"{Colors.RED}File not found: {file_name}{Colors.RESET}"
            
            matches = []
            for line_no, line in enumerate(content.split('\n'), 1):
                if pattern.lower() in line.lower():
                    matches.append(f"{Colors.CYAN}{line_no}:{Colors.RESET} {line}")
            
            if matches:
                return '\n'.join(matches)
            else:
                return f"{Colors.YELLOW}Pattern not found: {pattern}{Colors.RESET}"
        else:
            try:
                matches = []
                with open(file_name, 'r', encoding='utf-8') as f:
                    for line_no, line in enumerate(f, 1):
                        if pattern.lower() in line.lower():
                            matches.append(f"{Colors.CYAN}{line_no}:{Colors.RESET} {line.rstrip()}")
                
                if matches:
                    return '\n'.join(matches)
                else:
                    return f"{Colors.YELLOW}Pattern not found: {pattern}{Colors.RESET}"
            except Exception as e:
                return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"