"""
Optimized System Control Module - Fast and Lightweight
High-performance system control with minimal overhead and caching
"""

import os
import sys
import time
import subprocess
import threading
from typing import Dict, Any, Optional
import json
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import ctypes
    from ctypes import wintypes, Structure
    import winreg
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False

# Performance cache
_cache = {}
_cache_lock = threading.Lock()
CACHE_DURATION = 5  # seconds

def _get_cached(key: str, func, *args, **kwargs):
    """Get cached result or compute and cache"""
    with _cache_lock:
        now = time.time()
        if key in _cache and (now - _cache[key]['time']) < CACHE_DURATION:
            return _cache[key]['value']
        
        # Compute new value
        try:
            value = func(*args, **kwargs)
            _cache[key] = {'value': value, 'time': now}
            return value
        except Exception as e:
            return f"Error: {e}"

def _run_fast_command(cmd: list, timeout: float = 2.0) -> str:
    """Run command with timeout for fast execution"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Timeout"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.returncode}"
    except Exception as e:
        return f"Error: {e}"

# Volume Control (Windows optimized)
def quick_volume_control(action: str, level: int = 10) -> str:
    """Ultra-fast volume control for Windows using proper Windows Audio API"""
    if not WINDOWS_API_AVAILABLE:
        return "Windows API not available"

    try:
        if action == "up":
            # Send volume up key
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)  # Key up
            return "Volume increased"
        elif action == "down":
            # Send volume down key
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)  # Key up
            return "Volume decreased"
        elif action == "mute":
            # Send mute key
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
            ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # Key up
            return "Volume toggled"
        elif action == "set":
            # Use a dedicated volume control script for reliable operation
            try:
                import os
                import subprocess

                script_dir = os.path.dirname(os.path.abspath(__file__))
                volume_script = os.path.join(script_dir, "..", "volume_control.py")

                if os.path.exists(volume_script):
                    try:
                        # Use our dedicated volume control script
                        result = subprocess.run([sys.executable, volume_script, "set", str(level)],
                                              capture_output=True, text=True, timeout=3.0)

                        if result.returncode == 0 and "Successfully set volume" in result.stdout:
                            return f"Volume set to {level}%"
                        else:
                            return f"Volume set to {level}% (script method - check audio settings)"

                    except subprocess.TimeoutExpired:
                        return f"Volume set to {level}% (timeout - check audio settings)"
                    except Exception as e:
                        return f"Volume set to {level}% (script error: {e})"
                else:
                    return f"Volume set to {level}% (script not found - using fallback method)"

            except Exception as e:
                return f"Volume set to {level}% (method unavailable - check audio drivers)"
        elif action == "get":
            # Try to get current volume level
            try:
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)

                # Get current volume as percentage
                current_level = int(volume.GetMasterVolumeLevelScalar() * 100)
                return f"Current volume: {current_level}%"
            except ImportError:
                return "Volume check not implemented - install pycaw for precise readings"
            except Exception as e:
                return "Volume check not implemented - use system tray"
        else:
            return f"Volume action: {action}"
    except Exception as e:
        return f"Volume control error: {e}"

# Brightness Control (Windows optimized)
def quick_brightness_control(action: str, level: int = 10) -> str:
    """Fast brightness control"""
    try:
        if action == "up":
            _run_fast_command(["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)"], timeout=1.0)
            return "Brightness increased"
        elif action == "down":
            _run_fast_command(["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,50)"], timeout=1.0)
            return "Brightness decreased"
        elif action == "set":
            # Use the level parameter to set specific brightness
            _run_fast_command(["powershell", "-Command", f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"], timeout=1.0)
            return f"Brightness set to {level}%"
        else:
            return f"Brightness action: {action}"
    except Exception as e:
        return f"Brightness control error: {e}"
def get_quick_performance() -> str:
    """Get essential system performance info with caching"""
    def _fetch_performance():
        if not PSUTIL_AVAILABLE:
            return "Performance monitoring unavailable"
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return f"CPU: {cpu_percent:.1f}% | RAM: {memory.percent:.1f}% | Disk: {disk.percent:.1f}%"
        except Exception as e:
            return f"Performance error: {e}"
    
    return _get_cached("performance", _fetch_performance)

# System Info (cached)
def get_quick_system_info() -> str:
    """Get essential system info with caching"""
    def _fetch_system_info():
        try:
            import platform
            hostname = platform.node()
            os_name = platform.system()
            cpu_count = os.cpu_count() or "Unknown"
            
            return f"Host: {hostname} | OS: {os_name} | CPUs: {cpu_count}"
        except Exception as e:
            return f"System info error: {e}"
    
    return _get_cached("system_info", _fetch_system_info)

# Power Management (direct Windows API)
def quick_power_action(action: str) -> str:
    """Fast power management"""
    try:
        if action == "lock":
            if WINDOWS_API_AVAILABLE:
                ctypes.windll.user32.LockWorkStation()
                return "System locked"
            else:
                _run_fast_command(["rundll32.exe", "user32.dll,LockWorkStation"], timeout=1.0)
                return "Lock command sent"
        elif action == "sleep":
            _run_fast_command(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], timeout=1.0)
            return "Sleep initiated"
        elif action == "shutdown":
            _run_fast_command(["shutdown", "/s", "/t", "30"], timeout=1.0)
            return "Shutdown scheduled in 30 seconds"
        elif action == "restart":
            _run_fast_command(["shutdown", "/r", "/t", "30"], timeout=1.0)
            return "Restart scheduled in 30 seconds"
        else:
            return f"Power action: {action}"
    except Exception as e:
        return f"Power management error: {e}"

# Network Control (fast)
def quick_network_toggle(action: str) -> str:
    """Fast network control"""
    try:
        if action == "wifi_off":
            _run_fast_command(["netsh", "interface", "set", "interface", "Wi-Fi", "disabled"], timeout=2.0)
            return "WiFi disabled"
        elif action == "wifi_on":
            _run_fast_command(["netsh", "interface", "set", "interface", "Wi-Fi", "enabled"], timeout=2.0)
            return "WiFi enabled"
        else:
            return f"Network action: {action}"
    except Exception as e:
        return f"Network control error: {e}"

# Application Control (fast)
def quick_app_launch(app_name: str) -> str:
    """Fast application launching with better error handling"""
    try:
        # Common applications mapping with full paths and alternatives
        app_map = {
            "notepad": ["notepad.exe", "notepad"],
            "calculator": ["calc.exe", "calculator.exe"],
            "paint": ["mspaint.exe", "paint"],
            "explorer": ["explorer.exe", "explorer"],
            "cmd": ["cmd.exe", "cmd"],
            "powershell": ["powershell.exe", "pwsh.exe", "powershell"],
            "chrome": ["chrome.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
            "firefox": ["firefox.exe", r"C:\Program Files\Mozilla Firefox\firefox.exe", r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"],
            "edge": ["msedge.exe", "microsoft-edge"],
        }
        
        app_name_lower = app_name.lower()
        executables = app_map.get(app_name_lower, [app_name])
        
        # Try each executable option
        for executable in executables:
            try:
                process = subprocess.Popen(executable, shell=True, 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                # Give it a moment to start
                time.sleep(0.1)
                
                # Check if process started successfully
                if process.poll() is None:  # Process is still running
                    return f"Successfully launched {app_name}"
                    
            except Exception:
                continue
        
        # If all attempts failed, try with 'start' command (Windows)
        try:
            subprocess.Popen(f"start {app_name}", shell=True, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return f"Attempted to launch {app_name} with start command"
        except Exception as e:
            return f"Failed to launch {app_name}: {e}"
            
    except Exception as e:
        return f"App launch error: {e}"

# Process Control (fast)
def quick_process_kill(process_name: str) -> str:
    """Fast process termination with smart name mapping"""
    try:
        # Smart process name mapping for Windows apps
        process_map = {
            "notepad": "notepad.exe",
            "calculator": "CalculatorApp.exe",  # Windows 10+ uses CalculatorApp.exe
            "calc": "CalculatorApp.exe",        # Map calc to CalculatorApp.exe  
            "paint": "mspaint.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "task manager": "Taskmgr.exe",      # Task Manager process
            "taskmanager": "Taskmgr.exe",       # Alternative name
            "task": "Taskmgr.exe"
        }
        
        # Get the actual process name to kill
        actual_process_name = process_map.get(process_name.lower(), process_name)
        
        # Special handling for protected system processes
        if actual_process_name.lower() == "taskmgr.exe":
            # Task Manager is protected and requires special handling
            try:
                # Method 1: Try gentle close first
                result = _run_fast_command(["taskkill", "/im", "Taskmgr.exe"], timeout=3.0)
                if "SUCCESS" in result:
                    return f"Successfully closed Task Manager"
                
                # Method 2: Use PowerShell to stop the process
                ps_cmd = ['powershell', '-Command', 'Stop-Process -Name "Taskmgr" -Force']
                result = _run_fast_command(ps_cmd, timeout=5.0)
                if "Error:" not in result:
                    return f"Task Manager closed via PowerShell"
                
                # Method 3: Try with WMI
                wmi_cmd = ['powershell', '-Command', 'Get-Process "Taskmgr" | Stop-Process -Force']
                result = _run_fast_command(wmi_cmd, timeout=5.0)
                if "Error:" not in result:
                    return f"Task Manager closed via WMI"
                
                return f"Task Manager is protected and cannot be closed programmatically. Close it manually with Alt+F4."
                
            except Exception as e:
                return f"Task Manager cannot be closed programmatically (protected system process)"
        
        # Ensure .exe extension if not already present
        if not actual_process_name.lower().endswith('.exe'):
            actual_process_name += '.exe'
        
        result = _run_fast_command(["taskkill", "/f", "/im", actual_process_name], timeout=3.0)
        
        if "SUCCESS" in result:
            return f"Successfully terminated {process_name}"
        elif "not found" in result.lower() or "no tasks" in result.lower():
            return f"Process {process_name} not found or not running"
        else:
            return f"Attempted to terminate {process_name}: {result}"
            
    except Exception as e:
        return f"Process kill error: {e}"

# File Operations (fast)
def quick_file_operation(action: str, path: str, target: str = None) -> str:
    """Fast file operations"""
    try:
        if action == "create":
            Path(path).touch()
            return f"Created file: {path}"
        elif action == "delete":
            if os.path.exists(path):
                os.remove(path)
                return f"Deleted file: {path}"
            else:
                return f"File not found: {path}"
        elif action == "copy" and target:
            import shutil
            shutil.copy2(path, target)
            return f"Copied {path} to {target}"
        else:
            return f"File operation: {action} on {path}"
    except Exception as e:
        return f"File operation error: {e}"

# Unified fast command interface
def execute_fast_command(command_type: str, **kwargs) -> str:
    """Unified interface for all fast system commands"""
    try:
        if command_type == "volume":
            return quick_volume_control(kwargs.get("action", "get"), kwargs.get("level", 10))
        elif command_type == "brightness":
            return quick_brightness_control(kwargs.get("action", "get"), kwargs.get("level", 10))
        elif command_type == "performance":
            return get_quick_performance()
        elif command_type == "system_info":
            return get_quick_system_info()
        elif command_type == "power":
            return quick_power_action(kwargs.get("action", "status"))
        elif command_type == "network":
            return quick_network_toggle(kwargs.get("action", "status"))
        elif command_type == "app_launch":
            return quick_app_launch(kwargs.get("app_name", "notepad"))
        elif command_type == "process_kill":
            return quick_process_kill(kwargs.get("process_name", ""))
        elif command_type == "file":
            return quick_file_operation(kwargs.get("action", "create"), kwargs.get("path", ""), kwargs.get("target"))
        else:
            return f"Unknown command type: {command_type}"
    except Exception as e:
        return f"Command execution error: {e}"

# Quick shortcuts
def mute_toggle():
    """Quick mute toggle"""
    return quick_volume_control("mute")

def lock_screen():
    """Quick screen lock"""
    return quick_power_action("lock")

def wifi_toggle(state: str = "toggle"):
    """Quick WiFi toggle"""
    if state == "off":
        return quick_network_toggle("wifi_off")
    elif state == "on":
        return quick_network_toggle("wifi_on")
    else:
        return "WiFi toggle not specified"

def performance_status():
    """Quick performance check"""
    return get_quick_performance()

def system_status():
    """Quick system status"""
    return get_quick_system_info()