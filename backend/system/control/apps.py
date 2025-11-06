"""
App Control Module
Handles opening, closing, and monitoring applications
"""
import os
import psutil
import subprocess
import time
import winreg
from typing import Dict, List, Any

# Optional window focusing backends
try:
    import pygetwindow as gw  # type: ignore
except Exception:
    gw = None
try:
    import win32gui  # type: ignore
    import win32con  # type: ignore
    import win32process  # type: ignore
except Exception:
    win32gui = None
    win32con = None
    win32process = None
import ctypes
from ctypes import wintypes
import ctypes
from ctypes import wintypes

# Constants for ShowWindow
SW_RESTORE = 9


def open_app(name: str) -> Dict[str, Any]:
    """Dynamically open an application"""
    try:
        # Clean the app name
        app_name = name.strip().lower()
        
        # Method 1: Try Windows start command (proper way)
        try:
            # Use proper start command syntax for PowerShell/CMD
            cmd = f'start "" "{app_name}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            time.sleep(1.5)
            
            # Verify if app started
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name in proc_name or proc_name.replace('.exe', '') == app_name:
                        return {
                            'success': True,
                            'message': f'Successfully opened {name}',
                            'app': name
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except subprocess.TimeoutExpired:
            # App might be starting, continue to verification
            pass
        except Exception as e:
            # If start command fails, try other methods
            pass
        
        # Method 2: Search Windows Registry
        try:
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            ]
            
            for hkey, subkey_path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey_path) as key:
                        with winreg.OpenKey(key, f"{app_name}.exe") as app_key:
                            app_path = winreg.QueryValue(app_key, None)
                            subprocess.Popen(app_path, shell=True,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
                            time.sleep(1.5)
                            return {
                                'success': True,
                                'message': f'Successfully opened {name} from registry',
                                'app': name
                            }
                except:
                    continue
        except:
            pass
        
        # Method 3: Common installation directories
        common_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\Windows\System32",
            os.path.expanduser(r"~\AppData\Local\Programs"),
        ]
        
        for base_path in common_paths:
            try:
                # Search for executable
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.lower() == f"{app_name}.exe" or app_name in file.lower():
                            full_path = os.path.join(root, file)
                            subprocess.Popen(full_path, shell=True,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
                            time.sleep(1.5)
                            return {
                                'success': True,
                                'message': f'Successfully opened {name} from {full_path}',
                                'app': name
                            }
                    # Limit search depth
                    if root.count(os.sep) - base_path.count(os.sep) > 2:
                        break
            except:
                continue
        
        # If none of the methods worked
        return {
            'success': False,
            'message': f'Could not find or open {name}. App may not be installed or accessible.',
            'app': name
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to open {name}: {str(e)}',
            'app': name
        }


def focus_app(name: str, proc: Any = None) -> Dict[str, Any]:
    """Best-effort: bring an app window matching the name to foreground.
    Attempts with pygetwindow first, then win32gui enumeration.
    """
    target = (name or "").strip().lower()
    # Try pygetwindow by title
    if gw:
        try:
            wins = gw.getAllWindows()
            for w in wins:
                try:
                    title = (w.title or "").lower()
                    if target and (target in title):
                        try:
                            w.activate()
                            return {"success": True, "message": f"focused '{w.title}' via pygetwindow"}
                        except Exception:
                            pass
                except Exception:
                    continue
        except Exception:
            pass

    # Try win32gui by title and/or process id
    if win32gui:
        found = {"hwnd": None}

        def _enum(hwnd, _):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                title = (win32gui.GetWindowText(hwnd) or "").lower()
                if target and (target in title):
                    found["hwnd"] = hwnd
                    return False
                # If we know proc, try pid match
                if proc is not None and win32process is not None:
                    try:
                        _, wnd_pid = win32process.GetWindowThreadProcessId(hwnd)
                        if hasattr(proc, 'pid') and wnd_pid == getattr(proc, 'pid', None):
                            found["hwnd"] = hwnd
                            return False
                    except Exception:
                        pass
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(_enum, None)
            hwnd = found.get("hwnd")
            if hwnd:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE if win32con else 9)
                except Exception:
                    pass
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    pass
                return {"success": True, "message": "focused via win32gui"}
        except Exception:
            pass

    # Fallback minimal sleep
    time.sleep(0.25)
    return {"success": True, "message": "focus best-effort (fallback)"}


def close_app(name: str) -> Dict[str, Any]:
    """Close an application by name"""
    try:
        # Normalize requested name
        req = name.strip().lower()

        # Collect running processes names and pids
        procs = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'] or ''
                procs.append((proc.info['pid'], pname))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        closed_count = 0

        # First try simple substring match
        for pid, pname in procs:
            if req in pname.lower():
                try:
                    p = psutil.Process(pid)
                    p.kill()
                    closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        # If none closed, try fuzzy matching on process base names
        if closed_count == 0:
            try:
                from difflib import get_close_matches
                base_map = {}
                names = []
                for pid, pname in procs:
                    base = pname.lower().replace('.exe', '')
                    if base not in base_map:
                        base_map[base] = []
                        names.append(base)
                    base_map[base].append(pid)

                # Try to find close match to requested name
                matches = get_close_matches(req, names, n=1, cutoff=0.6)
                if matches:
                    best = matches[0]
                    for pid in base_map.get(best, []):
                        try:
                            p = psutil.Process(pid)
                            p.kill()
                            closed_count += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
            except Exception:
                pass
        
        if closed_count > 0:
            return {
                'success': True,
                'message': f'Closed {closed_count} instance(s) of {name}',
                'app': name,
                'count': closed_count
            }
        else:
            return {
                'success': False,
                'message': f'{name} is not running',
                'app': name,
                'count': 0
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to close {name}: {str(e)}',
            'app': name
        }


def get_app_info(name: str) -> Dict[str, Any]:
    """Get information about a running application"""
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if name.lower() in proc.info['name'].lower():
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
        'name': name,
        'running': False
    }


def list_running_processes() -> List[Dict[str, Any]]:
    """List all running processes"""
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


def focus_app(name: str, proc: Any = None) -> bool:
    """Best-effort: bring a window whose title or process matches `name` to the foreground.
    Returns True if a window was focused, False otherwise.
    Uses Win32 API via ctypes so no extra deps are required.
    """
    try:
        if not name:
            return False

        user32 = ctypes.windll.user32

        SW_SHOW = 5

        titles = []

        # Helper to collect candidate HWNDs
        def enum_windows_callback(hwnd, lParam):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            # get process id for this window
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            titles.append((hwnd, title, pid.value))
            return True

        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        EnumWindows(EnumWindowsProc(enum_windows_callback), 0)

        target_lower = name.lower()

        # Try exact title or substring match first
        for hwnd, title, pid in titles:
            try:
                if target_lower in title.lower():
                    # bring to foreground
                    try:
                        user32.ShowWindow(hwnd, SW_SHOW)
                        user32.SetForegroundWindow(hwnd)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        # If proc (pid or name) provided, try to match by pid
        if proc:
            proc_pid = None
            try:
                if isinstance(proc, int):
                    proc_pid = proc
                elif hasattr(proc, 'pid'):
                    proc_pid = int(proc.pid)
                elif isinstance(proc, str) and proc.isdigit():
                    proc_pid = int(proc)
            except Exception:
                proc_pid = None

            if proc_pid:
                for hwnd, title, pid in titles:
                    if pid == proc_pid:
                        try:
                            user32.ShowWindow(hwnd, SW_SHOW)
                            user32.SetForegroundWindow(hwnd)
                            return True
                        except Exception:
                            continue

        # Lastly, try fuzzy title match (substring of process base name)
        for hwnd, title, pid in titles:
            try:
                # check process name
                try:
                    p = psutil.Process(pid)
                    pname = (p.name() or '').lower()
                except Exception:
                    pname = ''
                if target_lower in pname or target_lower in title.lower():
                    try:
                        user32.ShowWindow(hwnd, SW_SHOW)
                        user32.SetForegroundWindow(hwnd)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        return False
    except Exception:
        return False


def focus_app(name: str, proc: int = None) -> Dict[str, Any]:
    """Bring the main window of the named application to the foreground.

    Attempts to find a window whose process id matches the named app or the given pid
    and calls SetForegroundWindow / ShowWindow to restore and focus it.
    """
    try:
        # Collect candidate pids
        candidates = []
        if proc:
            candidates.append(int(proc))
        else:
            req = name.strip().lower()
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    pname = (p.info['name'] or '').lower()
                    if req in pname:
                        candidates.append(p.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        if not candidates:
            return {'success': False, 'message': f'No running process matching {name}'}

        # Helper to enumerate windows and find ones matching candidate pids
        hwnds = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def _enum_windows(hwnd, lParam):
            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            try:
                if pid.value in candidates and ctypes.windll.user32.IsWindowVisible(hwnd):
                    hwnds.append(hwnd)
            except Exception:
                pass
            return True

        ctypes.windll.user32.EnumWindows(_enum_windows, 0)

        if not hwnds:
            return {'success': False, 'message': f'No window found for {name}'}

        # Bring first matched window to foreground
        target = hwnds[0]
        try:
            # If minimized, restore
            if ctypes.windll.user32.IsIconic(target):
                ctypes.windll.user32.ShowWindow(target, SW_RESTORE)
            ctypes.windll.user32.SetForegroundWindow(target)
            return {'success': True, 'message': f'Focused {name}'}
        except Exception as e:
            return {'success': False, 'message': f'Could not focus window: {e}'}
    except Exception as e:
        return {'success': False, 'message': f'focus_app error: {e}'}
