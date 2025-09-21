"""
System Commands - Handles system information and process management
"""

import os
import sys
import platform
from datetime import datetime
from typing import List
from utils.colors import Colors

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class SystemCommands:
    """Handles system information and process commands"""
    
    def __init__(self):
        self.psutil_available = PSUTIL_AVAILABLE
    
    def cmd_ps(self, args: List[str]) -> str:
        """Show running processes"""
        if not self.psutil_available:
            return f"{Colors.RED}psutil not available. Install with: pip install psutil{Colors.RESET}"
        
        try:
            processes = []
            header = f"{Colors.CYAN}{'PID':>7} {'NAME':20} {'CPU%':>6} {'MEM%':>6} {'STATUS':10}{Colors.RESET}"
            processes.append(header)
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    if pinfo['pid'] == 0:  # Skip system idle process
                        continue
                    
                    # Truncate long process names
                    name = pinfo['name'][:19] if pinfo['name'] else 'N/A'
                    
                    line = (f"{pinfo['pid']:7d} {name:20} "
                           f"{pinfo['cpu_percent']:5.1f}% "
                           f"{pinfo['memory_percent']:5.1f}% "
                           f"{pinfo['status'][:9]:10}")
                    
                    processes.append(line)
                    
                    # Limit output to prevent overwhelming
                    if len(processes) > 25:
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return '\n'.join(processes)
            
        except Exception as e:
            return f"{Colors.RED}Error retrieving processes: {str(e)}{Colors.RESET}"
    
    def cmd_top(self, args: List[str]) -> str:
        """Show system resource usage"""
        if not self.psutil_available:
            return f"{Colors.RED}psutil not available. Install with: pip install psutil{Colors.RESET}"
        
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Get disk usage for root/main drive
            try:
                disk = psutil.disk_usage('/' if os.name != 'nt' else 'C:')
                disk_available = True
            except:
                disk_available = False
            
            # Get boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Get load average (Unix only)
            load_avg = "N/A"
            if hasattr(os, 'getloadavg'):
                try:
                    load_avg = f"{os.getloadavg()[0]:.2f}"
                except:
                    pass
            
            # Format output
            output = f"""
{Colors.CYAN}System Resource Usage:{Colors.RESET}
{Colors.YELLOW}{'='*50}{Colors.RESET}

{Colors.GREEN}CPU Information:{Colors.RESET}
  Usage:          {cpu_percent:5.1f}%
  Physical cores: {cpu_count}
  Logical cores:  {cpu_count_logical}
  Load average:   {load_avg}

{Colors.GREEN}Memory Information:{Colors.RESET}
  Total:     {memory.total / (1024**3):8.1f} GB
  Available: {memory.available / (1024**3):8.1f} GB
  Used:      {memory.used / (1024**3):8.1f} GB ({memory.percent:5.1f}%)
  Free:      {memory.free / (1024**3):8.1f} GB

{Colors.GREEN}Swap Information:{Colors.RESET}
  Total:     {swap.total / (1024**3):8.1f} GB
  Used:      {swap.used / (1024**3):8.1f} GB ({swap.percent:5.1f}%)
  Free:      {swap.free / (1024**3):8.1f} GB"""

            if disk_available:
                output += f"""

{Colors.GREEN}Disk Information:{Colors.RESET}
  Total:     {disk.total / (1024**3):8.1f} GB
  Used:      {disk.used / (1024**3):8.1f} GB ({disk.percent:5.1f}%)
  Free:      {disk.free / (1024**3):8.1f} GB"""

            output += f"""

{Colors.GREEN}System Information:{Colors.RESET}
  Boot time:     {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
  Uptime:        {str(uptime).split('.')[0]}
  Processes:     {len(psutil.pids())}
"""
            
            return output
            
        except Exception as e:
            return f"{Colors.RED}Error retrieving system information: {str(e)}{Colors.RESET}"
    
    def cmd_kill(self, args: List[str]) -> str:
        """Terminate process by PID"""
        if not self.psutil_available:
            return f"{Colors.RED}psutil not available. Install with: pip install psutil{Colors.RESET}"
        
        if not args:
            return f"{Colors.YELLOW}Usage: kill <pid>{Colors.RESET}"
        
        try:
            pid = int(args[0])
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            # Safety check - don't kill critical system processes
            if pid in [0, 1] or proc_name.lower() in ['init', 'kernel', 'systemd']:
                return f"{Colors.RED}Cannot kill critical system process: {proc_name} (PID {pid}){Colors.RESET}"
            
            proc.terminate()
            return f"{Colors.GREEN}Terminated process: {proc_name} (PID {pid}){Colors.RESET}"
            
        except ValueError:
            return f"{Colors.RED}Invalid PID: {args[0]}{Colors.RESET}"
        except psutil.NoSuchProcess:
            return f"{Colors.RED}No such process: {args[0]}{Colors.RESET}"
        except psutil.AccessDenied:
            return f"{Colors.RED}Permission denied to kill process: {args[0]}{Colors.RESET}"
        except Exception as e:
            return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"
    
    def cmd_sysinfo(self, args: List[str]) -> str:
        """Show detailed system information"""
        try:
            # Basic system info
            system_info = f"""
{Colors.CYAN}System Information:{Colors.RESET}
{Colors.YELLOW}{'='*50}{Colors.RESET}

{Colors.GREEN}Operating System:{Colors.RESET}
  OS:           {platform.system()}
  Release:      {platform.release()}
  Version:      {platform.version()}
  Architecture: {platform.machine()}
  Processor:    {platform.processor() or 'Unknown'}
  Hostname:     {platform.node()}

{Colors.GREEN}Python Environment:{Colors.RESET}
  Version:      {sys.version.split()[0]}
  Executable:   {sys.executable}
  Platform:     {sys.platform}
"""
            
            if self.psutil_available:
                # Additional system details with psutil
                cpu_info = f"""
{Colors.GREEN}Hardware Information:{Colors.RESET}
  CPU Cores:    {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical
  CPU Freq:     {psutil.cpu_freq().current:.1f} MHz (max: {psutil.cpu_freq().max:.1f} MHz)
  Memory:       {psutil.virtual_memory().total / (1024**3):.1f} GB
"""
                system_info += cpu_info
                
                # Network interfaces
                try:
                    network_info = f"\n{Colors.GREEN}Network Interfaces:{Colors.RESET}\n"
                    for interface, addresses in psutil.net_if_addrs().items():
                        network_info += f"  {interface}:\n"
                        for addr in addresses:
                            if addr.family == 2:  # IPv4
                                network_info += f"    IPv4: {addr.address}\n"
                    system_info += network_info
                except:
                    pass
            
            return system_info
            
        except Exception as e:
            return f"{Colors.RED}Error retrieving system information: {str(e)}{Colors.RESET}"
    
    def cmd_df(self, args: List[str]) -> str:
        """Show disk space usage"""
        if not self.psutil_available:
            return f"{Colors.RED}psutil not available. Install with: pip install psutil{Colors.RESET}"
        
        try:
            partitions = psutil.disk_partitions()
            
            output = f"{Colors.CYAN}Disk Usage:{Colors.RESET}\n"
            output += f"{'Filesystem':20} {'Size':>10} {'Used':>10} {'Avail':>10} {'Use%':>5} {'Mounted on':15}\n"
            output += f"{'-'*75}\n"
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    size_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    free_gb = usage.free / (1024**3)
                    percent = (usage.used / usage.total) * 100
                    
                    filesystem = partition.device[:19] if len(partition.device) > 19 else partition.device
                    
                    output += (f"{filesystem:20} {size_gb:8.1f}G {used_gb:8.1f}G "
                              f"{free_gb:8.1f}G {percent:4.0f}% {partition.mountpoint:15}\n")
                              
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            return output
            
        except Exception as e:
            return f"{Colors.RED}Error retrieving disk usage: {str(e)}{Colors.RESET}"
    
    def cmd_free(self, args: List[str]) -> str:
        """Show memory usage"""
        if not self.psutil_available:
            return f"{Colors.RED}psutil not available. Install with: pip install psutil{Colors.RESET}"
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Convert to human readable format
            def format_bytes(bytes_val):
                for unit in ['B', 'K', 'M', 'G']:
                    if bytes_val < 1024.0:
                        return f"{bytes_val:7.1f}{unit}"
                    bytes_val /= 1024.0
                return f"{bytes_val:7.1f}T"
            
            output = f"{Colors.CYAN}Memory Usage:{Colors.RESET}\n"
            output += f"{'':14} {'Total':>8} {'Used':>8} {'Free':>8} {'Available':>10} {'Buff/Cache':>11}\n"
            output += f"{'-'*65}\n"
            
            # Calculate buffer/cache (approximation)
            buffers_cache = memory.total - memory.available - memory.free
            
            output += (f"{'Mem:':14} {format_bytes(memory.total):>8} "
                      f"{format_bytes(memory.used):>8} {format_bytes(memory.free):>8} "
                      f"{format_bytes(memory.available):>10} {format_bytes(buffers_cache):>11}\n")
            
            output += (f"{'Swap:':14} {format_bytes(swap.total):>8} "
                      f"{format_bytes(swap.used):>8} {format_bytes(swap.free):>8} "
                      f"{'':>10} {'':>11}\n")
            
            return output
            
        except Exception as e:
            return f"{Colors.RED}Error retrieving memory information: {str(e)}{Colors.RESET}"
    
    def cmd_uptime(self, args: List[str]) -> str:
        """Show system uptime"""
        if not self.psutil_available:
            # Fallback without psutil
            return f"{Colors.YELLOW}System uptime information requires psutil{Colors.RESET}"
        
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Format uptime
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            uptime_str = f"{days} days, {hours} hours, {minutes} minutes"
            
            # Get load average (Unix systems)
            load_info = ""
            if hasattr(os, 'getloadavg'):
                try:
                    load1, load5, load15 = os.getloadavg()
                    load_info = f", load average: {load1:.2f}, {load5:.2f}, {load15:.2f}"
                except:
                    pass
            
            # Get number of users (simplified)
            users = len(psutil.users()) if hasattr(psutil, 'users') else 0
            
            current_time = datetime.now().strftime('%H:%M:%S')
            
            return f"{current_time} up {uptime_str}, {users} users{load_info}"
            
        except Exception as e:
            return f"{Colors.RED}Error retrieving uptime: {str(e)}{Colors.RESET}"
    
    def cmd_whoami(self, args: List[str]) -> str:
        """Show current user"""
        return os.getenv('USER', os.getenv('USERNAME', 'unknown'))
    
    def cmd_date(self, args: List[str]) -> str:
        """Show current date and time"""
        if args and args[0] == '+%s':
            # Unix timestamp
            return str(int(datetime.now().timestamp()))
        else:
            # Human readable format
            return datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')
    
    def cmd_env(self, args: List[str]) -> str:
        """Show environment variables"""
        if args:
            # Show specific environment variable
            var_name = args[0]
            value = os.getenv(var_name)
            if value is not None:
                return f"{var_name}={value}"
            else:
                return f"{Colors.RED}Environment variable not found: {var_name}{Colors.RESET}"
        else:
            # Show all environment variables
            env_vars = []
            for key, value in sorted(os.environ.items()):
                # Truncate very long values
                if len(value) > 100:
                    value = value[:97] + "..."
                env_vars.append(f"{Colors.GREEN}{key}{Colors.RESET}={value}")
            
            return '\n'.join(env_vars)