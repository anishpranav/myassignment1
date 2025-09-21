"""
Virtual File System - Safe sandbox for file operations
"""

import os
from typing import Dict, List, Optional
from pathlib import Path
import json

class VirtualFileSystem:
    """Simulates a file system for safe operations"""
    
    def __init__(self):
        self.virtual_fs = {
            '/': {
                'type': 'directory',
                'created': '2024-01-01 00:00:00',
                'modified': '2024-01-01 00:00:00',
                'permissions': 'drwxr-xr-x',
                'children': {
                    'home': {
                        'type': 'directory',
                        'created': '2024-01-01 00:00:00',
                        'modified': '2024-01-01 00:00:00',
                        'permissions': 'drwxr-xr-x',
                        'children': {
                            'user': {
                                'type': 'directory',
                                'created': '2024-01-01 00:00:00',
                                'modified': '2024-01-01 00:00:00',
                                'permissions': 'drwxr-xr-x',
                                'children': {
                                    'documents': {
                                        'type': 'directory',
                                        'created': '2024-01-01 00:00:00',
                                        'modified': '2024-01-01 00:00:00',
                                        'permissions': 'drwxr-xr-x',
                                        'children': {
                                            'readme.txt': {
                                                'type': 'file',
                                                'content': 'Welcome to the virtual file system!\nThis is a safe environment for testing commands.',
                                                'created': '2024-01-01 00:00:00',
                                                'modified': '2024-01-01 00:00:00',
                                                'permissions': '-rw-r--r--',
                                                'size': 89
                                            }
                                        }
                                    },
                                    'downloads': {
                                        'type': 'directory',
                                        'created': '2024-01-01 00:00:00',
                                        'modified': '2024-01-01 00:00:00',
                                        'permissions': 'drwxr-xr-x',
                                        'children': {}
                                    },
                                    'projects': {
                                        'type': 'directory',
                                        'created': '2024-01-01 00:00:00',
                                        'modified': '2024-01-01 00:00:00',
                                        'permissions': 'drwxr-xr-x',
                                        'children': {
                                            'script.py': {
                                                'type': 'file',
                                                'content': '#!/usr/bin/env python3\nprint("Hello, Virtual World!")\n',
                                                'created': '2024-01-01 00:00:00',
                                                'modified': '2024-01-01 00:00:00',
                                                'permissions': '-rwxr-xr-x',
                                                'size': 46
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'tmp': {
                        'type': 'directory',
                        'created': '2024-01-01 00:00:00',
                        'modified': '2024-01-01 00:00:00',
                        'permissions': 'drwxrwxrwx',
                        'children': {}
                    },
                    'etc': {
                        'type': 'directory',
                        'created': '2024-01-01 00:00:00',
                        'modified': '2024-01-01 00:00:00',
                        'permissions': 'drwxr-xr-x',
                        'children': {
                            'hosts': {
                                'type': 'file',
                                'content': '127.0.0.1 localhost\n::1 localhost\n',
                                'created': '2024-01-01 00:00:00',
                                'modified': '2024-01-01 00:00:00',
                                'permissions': '-rw-r--r--',
                                'size': 26
                            }
                        }
                    }
                }
            }
        }
        self.current_path = '/home/user'
    
    def normalize_path(self, path: str) -> str:
        """Normalize a path by resolving . and .. components"""
        if not path.startswith('/'):
            # Relative path
            path = os.path.join(self.current_path, path)
        
        # Normalize path
        parts = []
        for part in path.split('/'):
            if part == '' or part == '.':
                continue
            elif part == '..':
                if parts and parts[-1] != '..':
                    parts.pop()
            else:
                parts.append(part)
        
        result = '/' + '/'.join(parts)
        return result if result != '/' or len(parts) == 0 else result.rstrip('/')
    
    def get_node(self, path: str) -> Optional[Dict]:
        """Get node at given path"""
        path = self.normalize_path(path)
        
        if path == '/':
            return self.virtual_fs['/']
        
        parts = path.strip('/').split('/')
        current = self.virtual_fs['/']
        
        for part in parts:
            if (current and current.get('type') == 'directory' and 
                part in current.get('children', {})):
                current = current['children'][part]
            else:
                return None
        
        return current
    
    def get_parent_node(self, path: str) -> tuple[Optional[Dict], str]:
        """Get parent node and item name"""
        path = self.normalize_path(path)
        parent_path = os.path.dirname(path)
        item_name = os.path.basename(path)
        
        parent = self.get_node(parent_path)
        return parent, item_name
    
    def exists(self, path: str) -> bool:
        """Check if path exists"""
        return self.get_node(path) is not None
    
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory"""
        node = self.get_node(path)
        return node is not None and node.get('type') == 'directory'
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        node = self.get_node(path)
        return node is not None and node.get('type') == 'file'
    
    def create_directory(self, path: str) -> bool:
        """Create a new directory"""
        path = self.normalize_path(path)
        parent, dir_name = self.get_parent_node(path)
        
        if parent and parent.get('type') == 'directory':
            if dir_name not in parent.get('children', {}):
                import datetime
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                parent.setdefault('children', {})[dir_name] = {
                    'type': 'directory',
                    'created': now,
                    'modified': now,
                    'permissions': 'drwxr-xr-x',
                    'children': {}
                }
                return True
        return False
    
    def create_file(self, path: str, content: str = '') -> bool:
        """Create a new file"""
        path = self.normalize_path(path)
        parent, file_name = self.get_parent_node(path)
        
        if parent and parent.get('type') == 'directory':
            import datetime
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            parent.setdefault('children', {})[file_name] = {
                'type': 'file',
                'content': content,
                'created': now,
                'modified': now,
                'permissions': '-rw-r--r--',
                'size': len(content)
            }
            return True
        return False
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to existing or new file"""
        node = self.get_node(path)
        if node and node.get('type') == 'file':
            import datetime
            node['content'] = content
            node['modified'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            node['size'] = len(content)
            return True
        else:
            return self.create_file(path, content)
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        node = self.get_node(path)
        if node and node.get('type') == 'file':
            return node.get('content', '')
        return None
    
    def remove_item(self, path: str) -> bool:
        """Remove file or directory"""
        path = self.normalize_path(path)
        parent, item_name = self.get_parent_node(path)
        
        if parent and parent.get('type') == 'directory':
            if item_name in parent.get('children', {}):
                del parent['children'][item_name]
                return True
        return False
    
    def move_item(self, src_path: str, dst_path: str) -> bool:
        """Move/rename item"""
        src_path = self.normalize_path(src_path)
        dst_path = self.normalize_path(dst_path)
        
        src_parent, src_name = self.get_parent_node(src_path)
        dst_parent, dst_name = self.get_parent_node(dst_path)
        
        if (src_parent and src_parent.get('type') == 'directory' and
            dst_parent and dst_parent.get('type') == 'directory' and
            src_name in src_parent.get('children', {})):
            
            # Move the item
            item = src_parent['children'][src_name]
            dst_parent.setdefault('children', {})[dst_name] = item
            del src_parent['children'][src_name]
            
            # Update modified time
            import datetime
            item['modified'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return True
        
        return False
    
    def copy_item(self, src_path: str, dst_path: str) -> bool:
        """Copy item"""
        import copy
        
        src_path = self.normalize_path(src_path)
        dst_path = self.normalize_path(dst_path)
        
        src_node = self.get_node(src_path)
        dst_parent, dst_name = self.get_parent_node(dst_path)
        
        if (src_node and dst_parent and dst_parent.get('type') == 'directory'):
            # Deep copy the source item
            item_copy = copy.deepcopy(src_node)
            
            # Update timestamps
            import datetime
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item_copy['created'] = now
            item_copy['modified'] = now
            
            dst_parent.setdefault('children', {})[dst_name] = item_copy
            return True
        
        return False
    
    def list_directory(self, path: str) -> List[str]:
        """List directory contents"""
        node = self.get_node(path)
        if node and node.get('type') == 'directory':
            items = []
            for name, item in node.get('children', {}).items():
                if item.get('type') == 'directory':
                    items.append(f"{name}/")
                else:
                    items.append(name)
            return sorted(items, key=lambda x: (x.endswith('/'), x.lower()))
        return []
    
    def get_detailed_listing(self, path: str) -> List[Dict]:
        """Get detailed directory listing with file info"""
        node = self.get_node(path)
        if node and node.get('type') == 'directory':
            items = []
            for name, item in node.get('children', {}).items():
                items.append({
                    'name': name,
                    'type': item.get('type'),
                    'permissions': item.get('permissions', '----------'),
                    'size': item.get('size', 0) if item.get('type') == 'file' else 0,
                    'modified': item.get('modified', 'unknown'),
                    'is_directory': item.get('type') == 'directory'
                })
            return sorted(items, key=lambda x: (not x['is_directory'], x['name'].lower()))
        return []
    
    def find_files(self, pattern: str, search_path: str = None) -> List[str]:
        """Find files matching pattern"""
        import fnmatch
        
        if search_path is None:
            search_path = self.current_path
        
        matches = []
        
        def search_recursive(node_path: str, node: Dict):
            if node.get('type') == 'directory':
                for child_name, child_node in node.get('children', {}).items():
                    child_path = f"{node_path}/{child_name}".replace('//', '/')
                    
                    # Check if filename matches pattern
                    if fnmatch.fnmatch(child_name.lower(), pattern.lower()):
                        matches.append(child_path)
                    
                    # Recurse into subdirectories
                    if child_node.get('type') == 'directory':
                        search_recursive(child_path, child_node)
        
        start_node = self.get_node(search_path)
        if start_node:
            search_recursive(search_path, start_node)
        
        return matches
    
    def change_directory(self, path: str) -> bool:
        """Change current directory"""
        if path == '~':
            path = '/home/user'
        
        target_path = self.normalize_path(path)
        
        if self.is_directory(target_path):
            self.current_path = target_path
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get filesystem statistics"""
        def count_items(node: Dict) -> tuple[int, int, int]:
            """Count files, directories, and total size"""
            files = 0
            dirs = 0
            size = 0
            
            if node.get('type') == 'file':
                files = 1
                size = node.get('size', 0)
            elif node.get('type') == 'directory':
                dirs = 1
                for child in node.get('children', {}).values():
                    child_files, child_dirs, child_size = count_items(child)
                    files += child_files
                    dirs += child_dirs
                    size += child_size