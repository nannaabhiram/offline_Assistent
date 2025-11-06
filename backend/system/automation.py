"""
Advanced Automation Module
Provides app control, mouse/keyboard automation, file system operations, and system info
"""
import os
import shutil
import platform
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any

# Try to import pyautogui (optional dependency)
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui not available. Install with: pip install pyautogui")


# ============================================================================
# 🧩 1. APP CONTROL
# ============================================================================

def open_app(app_name: str) -> Dict[str, Any]:
    """Open an application by name - dynamically finds and launches apps"""
    try:
        import subprocess
        import winreg
        import time
        
        # Try method 1: Direct start command (works for built-in Windows apps)
        try:
            result = subprocess.Popen(['start', '', app_name], shell=True, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            time.sleep(1.5)  # Give app time to start
            
            # Verify if app started by checking running processes
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name.lower() in proc_name or proc_name.replace('.exe', '') == app_name.lower():
                        return {
                            'success': True,
                            'message': f'Successfully opened {app_name}',
                            'app': app_name,
                            'method': 'start_command'
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        
        # Method 2: Search Windows Registry for installed apps
        try:
            # Common registry paths for installed applications
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            ]
            
            for hkey, subkey_path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey_path) as key:
                        # Try exact name match
                        try:
                            with winreg.OpenKey(key, f"{app_name}.exe") as app_key:
                                app_path = winreg.QueryValue(app_key, None)
                                subprocess.Popen(app_path, shell=True)
                                time.sleep(1.5)
                                return {
                                    'success': True,
                                    'message': f'Successfully opened {app_name}',
                                    'app': app_name,
                                    'method': 'registry',
                                    'path': app_path
                                }
                        except:
                            pass
                except:
                    continue
        except:
            pass
        
        # Method 3: Search common installation directories
        common_dirs = [
            os.path.expandvars(r'%ProgramFiles%'),
            os.path.expandvars(r'%ProgramFiles(x86)%'),
            os.path.expandvars(r'%LocalAppData%\Programs'),
            os.path.expandvars(r'%AppData%'),
        ]
        
        for base_dir in common_dirs:
            if os.path.exists(base_dir):
                for root, dirs, files in os.walk(base_dir):
                    for file in files:
                        if file.lower() == f"{app_name.lower()}.exe" or app_name.lower() in file.lower():
                            app_path = os.path.join(root, file)
                            try:
                                subprocess.Popen(app_path, shell=True)
                                time.sleep(1.5)
                                return {
                                    'success': True,
                                    'message': f'Successfully opened {app_name}',
                                    'app': app_name,
                                    'method': 'file_search',
                                    'path': app_path
                                }
                            except:
                                continue
                    # Limit search depth to avoid taking too long
                    if root.count(os.sep) - base_dir.count(os.sep) > 2:
                        break
        
        # Method 4: Try as Windows Store app (ms-windows-store: protocol)
        try:
            subprocess.Popen(['start', f'shell:AppsFolder\\{app_name}'], shell=True)
            time.sleep(1.5)
            return {
                'success': True,
                'message': f'Attempted to open {app_name} as Windows Store app',
                'app': app_name,
                'method': 'store_app'
            }
        except:
            pass
        
        # If we get here, app wasn't found
        return {
            'success': False,
            'message': f'Could not find or open {app_name}. Try using the exact executable name (e.g., "notepad", "calc", "chrome")',
            'app': app_name
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to open {app_name}: {str(e)}',
            'app': app_name
        }


def close_app(app_name: str) -> Dict[str, Any]:
    """Close an application by name"""
    try:
        closed_count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if app_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if closed_count > 0:
            return {
                'success': True,
                'message': f'Closed {closed_count} instance(s) of {app_name}',
                'app': app_name,
                'count': closed_count
            }
        else:
            return {
                'success': False,
                'message': f'{app_name} is not running',
                'app': app_name,
                'count': 0
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to close {app_name}: {str(e)}',
            'app': app_name
        }


def list_running_processes() -> List[Dict[str, Any]]:
    """List all running processes with details"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu': proc.info['cpu_percent'],
                'memory': proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def get_app_info(app_name: str) -> Dict[str, Any]:
    """Get information about a running application"""
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            if app_name.lower() in proc.info['name'].lower():
                return {
                    'found': True,
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent'],
                    'running': True
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return {
        'found': False,
        'name': app_name,
        'running': False
    }


# ============================================================================
# 🖱️ 2. MOUSE & KEYBOARD CONTROL
# ============================================================================

def move_mouse(x: int, y: int) -> Dict[str, Any]:
    """Move mouse to specified coordinates"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed. Install with: pip install pyautogui'
        }
    
    try:
        pyautogui.moveTo(x, y)
        return {
            'success': True,
            'message': f'Moved mouse to ({x}, {y})',
            'x': x,
            'y': y
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to move mouse: {str(e)}'
        }


def click_mouse(button: str = 'left') -> Dict[str, Any]:
    """Click mouse button"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        pyautogui.click(button=button)
        return {
            'success': True,
            'message': f'{button} mouse button clicked',
            'button': button
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to click: {str(e)}'
        }


def type_text(text: str, interval: float = 0.1) -> Dict[str, Any]:
    """Type text using keyboard automation"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        pyautogui.write(text, interval=interval)
        return {
            'success': True,
            'message': f'Typed: {text[:50]}...' if len(text) > 50 else f'Typed: {text}',
            'length': len(text)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to type: {str(e)}'
        }


def press_key(key: str) -> Dict[str, Any]:
    """Press a keyboard key"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        pyautogui.press(key)
        return {
            'success': True,
            'message': f'Pressed key: {key}',
            'key': key
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to press key: {str(e)}'
        }


def get_mouse_position() -> Dict[str, Any]:
    """Get current mouse position"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        x, y = pyautogui.position()
        return {
            'success': True,
            'x': x,
            'y': y,
            'position': f'({x}, {y})'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get position: {str(e)}'
        }


def get_screen_size() -> Dict[str, Any]:
    """Get screen dimensions"""
    if not PYAUTOGUI_AVAILABLE:
        return {
            'success': False,
            'message': 'pyautogui not installed'
        }
    
    try:
        width, height = pyautogui.size()
        return {
            'success': True,
            'width': width,
            'height': height,
            'resolution': f'{width}x{height}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get screen size: {str(e)}'
        }


# ============================================================================
# 📁 3. FILE SYSTEM CONTROL
# ============================================================================

def list_files(folder: str) -> Dict[str, Any]:
    """List files in a folder"""
    try:
        files = os.listdir(folder)
        return {
            'success': True,
            'folder': folder,
            'files': files,
            'count': len(files)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to list files: {str(e)}',
            'folder': folder
        }


def copy_file(src: str, dst: str) -> Dict[str, Any]:
    """Copy a file from source to destination"""
    try:
        # Create destination folder if it doesn't exist
        dst_folder = os.path.dirname(dst)
        if dst_folder:
            Path(dst_folder).mkdir(parents=True, exist_ok=True)
        
        shutil.copy(src, dst)
        return {
            'success': True,
            'message': f'Copied {src} to {dst}',
            'source': src,
            'destination': dst
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to copy file: {str(e)}',
            'source': src,
            'destination': dst
        }


def move_file(src: str, dst: str) -> Dict[str, Any]:
    """Move a file from source to destination"""
    try:
        # Create destination folder if it doesn't exist
        dst_folder = os.path.dirname(dst)
        if dst_folder:
            Path(dst_folder).mkdir(parents=True, exist_ok=True)
        
        shutil.move(src, dst)
        return {
            'success': True,
            'message': f'Moved {src} to {dst}',
            'source': src,
            'destination': dst
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to move file: {str(e)}',
            'source': src,
            'destination': dst
        }


def delete_file(path: str) -> Dict[str, Any]:
    """Delete a file"""
    try:
        if os.path.isfile(path):
            os.remove(path)
            return {
                'success': True,
                'message': f'Deleted file: {path}',
                'path': path
            }
        else:
            return {
                'success': False,
                'message': f'File not found: {path}',
                'path': path
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to delete file: {str(e)}',
            'path': path
        }


def create_folder(path: str) -> Dict[str, Any]:
    """Create a folder (with parent directories)"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {
            'success': True,
            'message': f'Created folder: {path}',
            'path': path
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to create folder: {str(e)}',
            'path': path
        }


def delete_folder(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete a folder"""
    try:
        if recursive:
            shutil.rmtree(path)
            return {
                'success': True,
                'message': f'Deleted folder recursively: {path}',
                'path': path
            }
        else:
            os.rmdir(path)
            return {
                'success': True,
                'message': f'Deleted empty folder: {path}',
                'path': path
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to delete folder: {str(e)}',
            'path': path
        }


def get_file_info(path: str) -> Dict[str, Any]:
    """Get file information"""
    try:
        if not os.path.exists(path):
            return {
                'success': False,
                'message': f'File not found: {path}',
                'path': path
            }
        
        stats = os.stat(path)
        return {
            'success': True,
            'path': path,
            'size': stats.st_size,
            'size_mb': round(stats.st_size / (1024 * 1024), 2),
            'created': stats.st_ctime,
            'modified': stats.st_mtime,
            'is_file': os.path.isfile(path),
            'is_dir': os.path.isdir(path)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get file info: {str(e)}',
            'path': path
        }


# ============================================================================
# 🖥️ 4. SYSTEM INFO
# ============================================================================

def get_cpu_usage() -> Dict[str, Any]:
    """Get CPU usage percentage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        return {
            'success': True,
            'cpu_percent': cpu_percent,
            'cpu_count': cpu_count,
            'message': f'CPU usage: {cpu_percent}% ({cpu_count} cores)'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get CPU usage: {str(e)}'
        }


def get_memory_info() -> Dict[str, Any]:
    """Get memory information"""
    try:
        mem = psutil.virtual_memory()
        return {
            'success': True,
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'message': f'Memory: {mem.percent}% used ({round(mem.used / (1024**3), 2)} GB / {round(mem.total / (1024**3), 2)} GB)'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get memory info: {str(e)}'
        }


def get_disk_info(path: str = 'C:\\') -> Dict[str, Any]:
    """Get disk usage information"""
    try:
        disk = psutil.disk_usage(path)
        return {
            'success': True,
            'path': path,
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'message': f'Disk {path}: {disk.percent}% used ({round(disk.free / (1024**3), 2)} GB free)'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get disk info: {str(e)}',
            'path': path
        }


def get_battery_status() -> Dict[str, Any]:
    """Get battery status"""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return {
                'success': False,
                'message': 'No battery detected (desktop PC)',
                'has_battery': False
            }
        
        return {
            'success': True,
            'has_battery': True,
            'percent': battery.percent,
            'plugged_in': battery.power_plugged,
            'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
            'message': f'Battery: {battery.percent}% {"(charging)" if battery.power_plugged else "(on battery)"}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get battery status: {str(e)}'
        }


def get_os_info() -> Dict[str, Any]:
    """Get operating system information"""
    try:
        return {
            'success': True,
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'platform': platform.platform(),
            'message': f'OS: {platform.platform()}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get OS info: {str(e)}'
        }


def get_network_info() -> Dict[str, Any]:
    """Get network information"""
    try:
        net_io = psutil.net_io_counters()
        return {
            'success': True,
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'message': f'Network: {round(net_io.bytes_recv / (1024**2), 2)} MB received, {round(net_io.bytes_sent / (1024**2), 2)} MB sent'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get network info: {str(e)}'
        }


def get_full_system_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    try:
        return {
            'success': True,
            'cpu': get_cpu_usage(),
            'memory': get_memory_info(),
            'disk': get_disk_info(),
            'battery': get_battery_status(),
            'os': get_os_info(),
            'network': get_network_info(),
            'timestamp': platform.platform()
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get system status: {str(e)}'
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_pyautogui_available() -> bool:
    """Check if pyautogui is available"""
    return PYAUTOGUI_AVAILABLE


if __name__ == "__main__":
    # Test functions
    print("Testing Automation Module...")
    print("\n=== System Info ===")
    print(get_cpu_usage())
    print(get_memory_info())
    print(get_battery_status())
    print(get_os_info())
    
    print("\n=== App Info ===")
    print(get_app_info("explorer"))
    
    print("\n=== PyAutoGUI Status ===")
    print(f"PyAutoGUI Available: {is_pyautogui_available()}")
