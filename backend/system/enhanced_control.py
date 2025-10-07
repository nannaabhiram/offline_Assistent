"""
Enhanced System Control Module for Comprehensive Laptop/OS Management
Provides advanced system control capabilities for your offline assistant.
"""

import os
import time
import subprocess
from typing import List, Tuple, Dict, Any
import json
from pathlib import Path

import psutil
import sys
import platform
try:
    import ctypes  # for Windows admin check
    from ctypes import wintypes
    import winreg
except Exception:
    ctypes = None
    wintypes = None
    winreg = None

try:
    import requests
except ImportError:
    requests = None

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    wmi = None


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information."""
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }
    
    # Memory information
    memory = psutil.virtual_memory()
    info["memory"] = {
        "total": f"{memory.total // (1024**3)} GB",
        "available": f"{memory.available // (1024**3)} GB",
        "used": f"{memory.used // (1024**3)} GB",
        "percentage": f"{memory.percent}%"
    }
    
    # Disk information
    disk = psutil.disk_usage('C:' if platform.system() == 'Windows' else '/')
    info["disk"] = {
        "total": f"{disk.total // (1024**3)} GB",
        "free": f"{disk.free // (1024**3)} GB",
        "used": f"{disk.used // (1024**3)} GB",
        "percentage": f"{(disk.used/disk.total)*100:.1f}%"
    }
    
    # CPU information
    info["cpu"] = {
        "cores_physical": psutil.cpu_count(logical=False),
        "cores_logical": psutil.cpu_count(logical=True),
        "usage_percent": f"{psutil.cpu_percent(interval=1)}%"
    }
    
    # Network interfaces
    info["network"] = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == 2:  # IPv4
                info["network"].append({
                    "interface": interface,
                    "ip": addr.address
                })
                break
    
    return info


def control_volume(action: str, level: int = None) -> str:
    """Control system volume."""
    try:
        if platform.system() == "Windows":
            if action == "mute":
                subprocess.run(["powershell", "-Command", "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], 
                             check=True, capture_output=True)
                return "System muted"
            elif action == "unmute":
                subprocess.run(["powershell", "-Command", "(New-Object -comObject WScript.Shell).SendKeys([char]173)"], 
                             check=True, capture_output=True)
                return "System unmuted"
            elif action == "up":
                subprocess.run(["powershell", "-Command", "(New-Object -comObject WScript.Shell).SendKeys([char]175)"], 
                             check=True, capture_output=True)
                return "Volume increased"
            elif action == "down":
                subprocess.run(["powershell", "-Command", "(New-Object -comObject WScript.Shell).SendKeys([char]174)"], 
                             check=True, capture_output=True)
                return "Volume decreased"
            elif action == "set" and level is not None:
                # Set volume to specific level (0-100)
                level = max(0, min(100, level))
                # First mute, then set volume
                cmd = f'$wshShell = New-Object -ComObject WScript.Shell; $wshShell.SendKeys([char]173); Start-Sleep -Milliseconds 200; for($i=0; $i -lt {level}; $i++){{$wshShell.SendKeys([char]175); Start-Sleep -Milliseconds 10}}'
                subprocess.run(["powershell", "-Command", cmd], check=True, capture_output=True)
                return f"Volume set to approximately {level}%"
        else:
            # Linux/Mac volume control
            if action == "up":
                subprocess.run(["amixer", "sset", "Master", "5%+"], check=True, capture_output=True)
                return "Volume increased"
            elif action == "down":
                subprocess.run(["amixer", "sset", "Master", "5%-"], check=True, capture_output=True)
                return "Volume decreased"
            elif action == "mute":
                subprocess.run(["amixer", "sset", "Master", "mute"], check=True, capture_output=True)
                return "System muted"
            elif action == "unmute":
                subprocess.run(["amixer", "sset", "Master", "unmute"], check=True, capture_output=True)
                return "System unmuted"
    except Exception as e:
        return f"Error controlling volume: {e}"


def control_brightness(action: str, level: int = None) -> str:
    """Control screen brightness."""
    try:
        if platform.system() == "Windows":
            if action == "up":
                # Use WMI to increase brightness
                cmd = 'Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness | ForEach-Object { $current = $_.CurrentBrightness; $new = [Math]::Min(100, $current + 10) }; Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods | ForEach-Object { $_.WmiSetBrightness(1, $new) }'
                subprocess.run(["powershell", "-Command", cmd], check=True, capture_output=True)
                return "Brightness increased"
            elif action == "down":
                cmd = 'Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness | ForEach-Object { $current = $_.CurrentBrightness; $new = [Math]::Max(10, $current - 10) }; Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods | ForEach-Object { $_.WmiSetBrightness(1, $new) }'
                subprocess.run(["powershell", "-Command", cmd], check=True, capture_output=True)
                return "Brightness decreased"
            elif action == "set" and level is not None:
                level = max(10, min(100, level))
                cmd = f'Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods | ForEach-Object {{$_.WmiSetBrightness(1,{level})}}'
                subprocess.run(["powershell", "-Command", cmd], check=True, capture_output=True)
                return f"Brightness set to {level}%"
        else:
            # Linux brightness control
            if action == "up":
                subprocess.run(["xbacklight", "-inc", "10"], check=True, capture_output=True)
                return "Brightness increased"
            elif action == "down":
                subprocess.run(["xbacklight", "-dec", "10"], check=True, capture_output=True)
                return "Brightness decreased"
            elif action == "set" and level is not None:
                level = max(10, min(100, level))
                subprocess.run(["xbacklight", "-set", str(level)], check=True, capture_output=True)
                return f"Brightness set to {level}%"
    except Exception as e:
        return f"Error controlling brightness: {e}"


def power_management(action: str, delay: int = 0) -> str:
    """Control power management functions."""
    try:
        if platform.system() == "Windows":
            if action == "sleep":
                if delay > 0:
                    subprocess.run(["powershell", "-Command", f"Start-Sleep -Seconds {delay}; Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"], 
                                 check=True)
                    return f"System will sleep in {delay} seconds"
                else:
                    subprocess.run(["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"], 
                                 check=True)
                    return "System going to sleep"
            elif action == "hibernate":
                if delay > 0:
                    subprocess.run(["shutdown", "/h", f"/t", str(delay)], check=True)
                    return f"System will hibernate in {delay} seconds"
                else:
                    subprocess.run(["shutdown", "/h"], check=True)
                    return "System hibernating"
            elif action == "shutdown":
                delay_arg = str(delay) if delay > 0 else "0"
                subprocess.run(["shutdown", "/s", "/t", delay_arg], check=True)
                return f"System will shutdown in {delay} seconds" if delay > 0 else "System shutting down"
            elif action == "restart":
                delay_arg = str(delay) if delay > 0 else "0"
                subprocess.run(["shutdown", "/r", "/t", delay_arg], check=True)
                return f"System will restart in {delay} seconds" if delay > 0 else "System restarting"
            elif action == "lock":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
                return "System locked"
            elif action == "logoff":
                subprocess.run(["shutdown", "/l"], check=True)
                return "User logged off"
        else:
            # Linux/Mac commands
            if action == "sleep":
                subprocess.run(["systemctl", "suspend"], check=True)
                return "System going to sleep"
            elif action == "shutdown":
                delay_arg = f"+{delay}" if delay > 0 else "now"
                subprocess.run(["shutdown", "-h", delay_arg], check=True)
                return f"System will shutdown in {delay} minutes" if delay > 0 else "System shutting down"
            elif action == "restart":
                delay_arg = f"+{delay}" if delay > 0 else "now"
                subprocess.run(["shutdown", "-r", delay_arg], check=True)
                return f"System will restart in {delay} minutes" if delay > 0 else "System restarting"
        
        return f"Action '{action}' not supported"
    except Exception as e:
        return f"Error with power management: {e}"


def network_management(action: str, target: str = None) -> str:
    """Control network settings."""
    try:
        if platform.system() == "Windows":
            if action == "wifi_on":
                subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enable"], 
                             check=True, capture_output=True)
                return "Wi-Fi enabled"
            elif action == "wifi_off":
                subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disable"], 
                             check=True, capture_output=True)
                return "Wi-Fi disabled"
            elif action == "list_networks":
                result = subprocess.run(["netsh", "wlan", "show", "profile"], 
                                      check=True, capture_output=True, text=True)
                return f"Available networks:\n{result.stdout}"
            elif action == "current_network":
                result = subprocess.run(["netsh", "wlan", "show", "interface"], 
                                      check=True, capture_output=True, text=True)
                return f"Current network connection:\n{result.stdout}"
            elif action == "connect" and target:
                subprocess.run(["netsh", "wlan", "connect", f"name={target}"], 
                             check=True, capture_output=True)
                return f"Connecting to {target}"
            elif action == "disconnect":
                subprocess.run(["netsh", "wlan", "disconnect"], 
                             check=True, capture_output=True)
                return "Disconnected from Wi-Fi"
            elif action == "ip_config":
                result = subprocess.run(["ipconfig", "/all"], 
                                      check=True, capture_output=True, text=True)
                return f"IP Configuration:\n{result.stdout[:1500]}"  # Limit output
        
        return f"Network action '{action}' not supported or missing target"
    except Exception as e:
        return f"Error with network management: {e}"


def file_operations(action: str, path: str, target: str = None) -> str:
    """Perform file system operations."""
    try:
        path_obj = Path(path)
        
        if action == "create_folder":
            path_obj.mkdir(parents=True, exist_ok=True)
            return f"Folder created: {path}"
        elif action == "create_file":
            path_obj.touch()
            return f"File created: {path}"
        elif action == "delete":
            if path_obj.is_file():
                path_obj.unlink()
                return f"File deleted: {path}"
            elif path_obj.is_dir():
                import shutil
                shutil.rmtree(path)
                return f"Folder deleted: {path}"
        elif action == "copy" and target:
            import shutil
            if path_obj.is_file():
                shutil.copy2(path, target)
                return f"File copied: {path} -> {target}"
            elif path_obj.is_dir():
                shutil.copytree(path, target, dirs_exist_ok=True)
                return f"Folder copied: {path} -> {target}"
        elif action == "move" and target:
            import shutil
            shutil.move(path, target)
            return f"Moved: {path} -> {target}"
        elif action == "list":
            if path_obj.is_dir():
                items = list(path_obj.iterdir())
                files = [item for item in items if item.is_file()]
                folders = [item for item in items if item.is_dir()]
                result = f"Contents of {path}:\nFolders ({len(folders)}):\n"
                result += "\n".join([f"📁 {folder.name}" for folder in folders[:10]])
                if len(folders) > 10:
                    result += f"\n... and {len(folders) - 10} more folders"
                result += f"\n\nFiles ({len(files)}):\n"
                result += "\n".join([f"📄 {file.name}" for file in files[:10]])
                if len(files) > 10:
                    result += f"\n... and {len(files) - 10} more files"
                return result
        elif action == "info":
            if path_obj.exists():
                stat = path_obj.stat()
                return f"Path: {path}\nType: {'Directory' if path_obj.is_dir() else 'File'}\nSize: {stat.st_size} bytes\nModified: {time.ctime(stat.st_mtime)}\nCreated: {time.ctime(stat.st_ctime)}"
        elif action == "search" and target:
            # Search for files containing target string
            matches = []
            if path_obj.is_dir():
                for item in path_obj.rglob("*"):
                    if target.lower() in item.name.lower():
                        matches.append(str(item))
                        if len(matches) >= 20:  # Limit results
                            break
            return f"Search results for '{target}' in {path}:\n" + "\n".join(matches)
        
        return f"File operation '{action}' not supported or invalid path"
    except Exception as e:
        return f"Error with file operation: {e}"


def process_management(action: str, process_name: str = None, pid: int = None) -> str:
    """Advanced process management."""
    try:
        if action == "list":
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    info = proc.info
                    cpu_val = info.get('cpu_percent', 0)
                    mem_val = info.get('memory_percent', 0)
                    processes.append(f"PID: {info['pid']:>6} | {info['name'][:20]:20} | CPU: {cpu_val:>5.1f}% | MEM: {mem_val:>5.1f}%")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage and return top 20
            processes = sorted(processes, key=lambda x: float(x.split("MEM: ")[1].split("%")[0]) if "MEM: " in x else 0, reverse=True)[:20]
            return "Top processes by memory usage:\n" + "\n".join(processes)
        
        elif action == "kill":
            killed = []
            if pid:
                proc = psutil.Process(pid)
                proc.terminate()
                killed.append(f"PID {pid}")
            elif process_name:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if process_name.lower() in proc.info['name'].lower():
                            proc.terminate()
                            killed.append(f"{proc.info['name']} (PID {proc.info['pid']})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            if killed:
                return f"Terminated processes: {', '.join(killed)}"
            else:
                return "No matching processes found to terminate"
        
        elif action == "info":
            if pid:
                proc = psutil.Process(pid)
                info = {
                    "name": proc.name(),
                    "pid": proc.pid,
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_percent": proc.memory_percent(),
                    "create_time": time.ctime(proc.create_time()),
                    "num_threads": proc.num_threads(),
                }
                return f"Process info:\n" + "\n".join([f"{k}: {v}" for k, v in info.items()])
        
        return f"Process action '{action}' not supported or missing parameters"
    except Exception as e:
        return f"Error with process management: {e}"


def system_services(action: str, service_name: str = None) -> str:
    """Control Windows services."""
    if platform.system() != "Windows":
        return "Service management only available on Windows"
    
    try:
        if action == "list":
            result = subprocess.run(["sc", "query"], 
                                  check=True, capture_output=True, text=True)
            # Parse and format the output
            lines = result.stdout.split('\n')
            services = []
            current_service = {}
            for line in lines:
                line = line.strip()
                if line.startswith("SERVICE_NAME:"):
                    if current_service:
                        services.append(current_service)
                    current_service = {"name": line.split(": ", 1)[1]}
                elif line.startswith("STATE") and current_service:
                    current_service["state"] = line.split(": ", 1)[1]
            
            if current_service:
                services.append(current_service)
            
            # Format output
            result_text = "System services (first 20):\n"
            for service in services[:20]:
                result_text += f"Service: {service.get('name', 'Unknown')} | State: {service.get('state', 'Unknown')}\n"
            return result_text
        
        elif action == "start" and service_name:
            subprocess.run(["sc", "start", service_name], 
                         check=True, capture_output=True)
            return f"Service '{service_name}' started"
        
        elif action == "stop" and service_name:
            subprocess.run(["sc", "stop", service_name], 
                         check=True, capture_output=True)
            return f"Service '{service_name}' stopped"
        
        elif action == "status" and service_name:
            result = subprocess.run(["sc", "query", service_name], 
                                  check=True, capture_output=True, text=True)
            return f"Service '{service_name}' status:\n{result.stdout}"
        
        return f"Service action '{action}' not supported or missing service name"
    except Exception as e:
        return f"Error with service management: {e}"


def security_operations(action: str, target: str = None) -> str:
    """Security-related operations."""
    try:
        if action == "firewall_status":
            if platform.system() == "Windows":
                result = subprocess.run(["netsh", "advfirewall", "show", "allprofiles"], 
                                      check=True, capture_output=True, text=True)
                return f"Firewall status:\n{result.stdout[:1000]}"  # Limit output
        
        elif action == "running_connections":
            connections = []
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    connections.append(f"{local} -> {remote}")
            
            return f"Active network connections ({len(connections)}):\n" + "\n".join(connections[:20])
        
        elif action == "logged_users":
            users = []
            for user in psutil.users():
                users.append(f"User: {user.name}, Terminal: {user.terminal or 'N/A'}, Started: {time.ctime(user.started)}")
            
            return f"Logged in users:\n" + "\n".join(users)
        
        elif action == "open_ports":
            ports = []
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN':
                    port_info = f"Port {conn.laddr.port} ({conn.laddr.ip}) - {conn.type.name}"
                    if port_info not in ports:
                        ports.append(port_info)
            
            return f"Open listening ports:\n" + "\n".join(sorted(ports)[:20])
        
        return f"Security action '{action}' not supported"
    except Exception as e:
        return f"Error with security operation: {e}"


def application_control(action: str, app_name: str = None, app_path: str = None) -> str:
    """Control applications."""
    try:
        if action == "launch" and (app_name or app_path):
            target = app_path if app_path else app_name
            if platform.system() == "Windows":
                # Try common application paths
                common_apps = {
                    "notepad": "notepad.exe",
                    "calculator": "calc.exe",
                    "paint": "mspaint.exe",
                    "cmd": "cmd.exe",
                    "powershell": "powershell.exe",
                    "explorer": "explorer.exe",
                    "taskmgr": "taskmgr.exe",
                    "control": "control.exe",
                }
                if target.lower() in common_apps:
                    target = common_apps[target.lower()]
                
                subprocess.Popen(target, shell=True)
            else:
                subprocess.Popen([target])
            return f"Launched application: {target}"
        
        elif action == "installed_programs":
            if platform.system() == "Windows":
                programs = []
                common_dirs = [
                    r"C:\Program Files",
                    r"C:\Program Files (x86)",
                ]
                
                for dir_path in common_dirs:
                    if os.path.exists(dir_path):
                        for item in os.listdir(dir_path)[:15]:  # Limit results
                            programs.append(f"📦 {item}")
                
                return f"Installed programs (sample):\n" + "\n".join(programs)
        
        elif action == "running_apps":
            # Get user applications (exclude system processes)
            apps = set()
            exclude = {'system', 'registry', 'smss.exe', 'csrss.exe', 'wininit.exe', 'services.exe', 'lsass.exe', 'svchost.exe'}
            
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name and name.lower() not in exclude:
                        apps.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return f"Currently running applications:\n" + "\n".join(sorted(list(apps))[:25])
        
        return f"Application action '{action}' not supported or missing parameters"
    except Exception as e:
        return f"Error with application control: {e}"


def monitor_system_performance() -> Dict[str, Any]:
    """Get real-time system performance metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
        "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
        "boot_time": time.ctime(psutil.boot_time()),
        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else "Not available",
        "temperature": "Not implemented",  # Would require additional libraries
    }


def advanced_system_command(command_type: str, **kwargs) -> str:
    """Execute advanced system commands based on type."""
    command_map = {
        "system_info": lambda: format_dict_output(get_system_info()),
        "volume": lambda: control_volume(kwargs.get('action', 'mute'), kwargs.get('level')),
        "brightness": lambda: control_brightness(kwargs.get('action', 'up'), kwargs.get('level')),
        "power": lambda: power_management(kwargs.get('action', 'lock'), kwargs.get('delay', 0)),
        "network": lambda: network_management(kwargs.get('action', 'wifi_on'), kwargs.get('target')),
        "file": lambda: file_operations(kwargs.get('action', 'list'), kwargs.get('path', '.'), kwargs.get('target')),
        "process": lambda: process_management(kwargs.get('action', 'list'), kwargs.get('process_name'), kwargs.get('pid')),
        "service": lambda: system_services(kwargs.get('action', 'list'), kwargs.get('service_name')),
        "security": lambda: security_operations(kwargs.get('action', 'firewall_status'), kwargs.get('target')),
        "app": lambda: application_control(kwargs.get('action', 'running_apps'), kwargs.get('app_name'), kwargs.get('app_path')),
        "performance": lambda: format_dict_output(monitor_system_performance()),
    }
    
    if command_type in command_map:
        try:
            return command_map[command_type]()
        except Exception as e:
            return f"Error executing {command_type}: {e}"
    else:
        available = ", ".join(command_map.keys())
        return f"Unknown command type '{command_type}'. Available: {available}"


def format_dict_output(data: Dict[str, Any], indent: int = 0) -> str:
    """Format dictionary data for readable output."""
    result = []
    for key, value in data.items():
        prefix = "  " * indent
        if isinstance(value, dict):
            result.append(f"{prefix}{key}:")
            result.append(format_dict_output(value, indent + 1))
        elif isinstance(value, list):
            result.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    result.append(format_dict_output(item, indent + 1))
                else:
                    result.append(f"{prefix}  - {item}")
        else:
            result.append(f"{prefix}{key}: {value}")
    return "\n".join(result)


# Quick command shortcuts
def quick_system_info():
    """Get essential system info quickly."""
    return advanced_system_command("system_info")

def quick_performance():
    """Get performance metrics quickly."""
    return advanced_system_command("performance")

def mute_system():
    """Quick mute."""
    return control_volume("mute")

def lock_system():
    """Quick lock."""
    return power_management("lock")

def wifi_toggle(state: bool):
    """Toggle WiFi on/off."""
    return network_management("wifi_on" if state else "wifi_off")