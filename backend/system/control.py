import os
import time
from typing import List, Tuple

import psutil
import sys
import platform
try:
    import ctypes  # for Windows admin check
except Exception:
    ctypes = None

def run_system_command(command):
    try:
        os.system(command)
        return f"Executed: {command}"
    except Exception as e:
        return f"Error: {e}"


def list_running_apps() -> List[str]:
    """Return a sorted list of unique process names for user apps (best-effort)."""
    exclude = {
        '', 'system', 'system idle process', 'idle', 'registry', 'smss.exe', 'csrss.exe',
        'wininit.exe', 'services.exe', 'lsass.exe', 'svchost.exe', 'registry', 'memcompression',
        'fontdrvhost.exe', 'dwm.exe'
    }
    names = set()
    for p in psutil.process_iter(['name']):
        try:
            name = (p.info.get('name') or '').strip()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        low = name.lower()
        if not name or low in exclude:
            continue
        names.add(name)
    return sorted(names)


def _find_processes_by_name_part(name_part: str) -> List[psutil.Process]:
    """Find processes by name. Prefer exact (case-insensitive) match, fallback to substring contains."""
    part = (name_part or '').strip().lower()
    exact: List[psutil.Process] = []
    partial: List[psutil.Process] = []
    for p in psutil.process_iter(['name']):
        try:
            name = (p.info.get('name') or '')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        low = name.lower()
        if not part:
            continue
        if low == part:
            exact.append(p)
        elif part in low:
            partial.append(p)
    return exact if exact else partial


def _is_admin() -> bool:
    if platform.system().lower() != 'windows':
        return True  # non-Windows typically doesn't need elevation for suspend
    if ctypes is None:
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def block_app_by_name(app_name: str, seconds: int, tick_callback=None, label: str = None) -> str:
    """Suspend all processes that match app_name for N seconds, then resume.

    - Prefers exact process name match (case-insensitive), otherwise substring match.
    - Reports how many were suspended and which failed due to permissions.
    - On Windows, suggests running as Administrator if nothing could be suspended due to AccessDenied.
    """
    seconds = max(0, int(seconds))
    procs = _find_processes_by_name_part(app_name)
    if not procs:
        return f"No running processes matched '{app_name}'."

    suspended: List[Tuple[int, str]] = []  # (pid, name)
    denied: List[Tuple[int, str]] = []
    other_fail: List[Tuple[int, str]] = []

    for p in procs:
        try:
            name = p.info.get('name') or p.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        try:
            p.suspend()
            suspended.append((p.pid, name))
        except psutil.AccessDenied:
            denied.append((p.pid, name))
        except psutil.NoSuchProcess:
            continue
        except Exception:
            other_fail.append((p.pid, name))

    if not suspended:
        if denied and platform.system().lower() == 'windows' and not _is_admin():
            details = ", ".join(f"{n}({pid})" for pid, n in denied[:5])
            more = " ..." if len(denied) > 5 else ""
            return (
                f"Found processes for '{app_name}' but could not suspend any due to permissions (e.g., {details}{more}). "
                f"Please run the terminal as Administrator and try again."
            )
        return f"Found processes for '{app_name}', but none could be suspended."

    # Keep suspended for the requested duration
    if seconds > 0:
        width = 30
        for elapsed in range(0, seconds):
            remaining = seconds - elapsed
            filled = int((elapsed / seconds) * width)
            bar = '#' * filled + '-' * (width - filled)
            print(f"Blocking '{app_name}' [{bar}] {remaining:>3}s remaining", end='\r', flush=True)
            if tick_callback and (remaining == seconds or remaining % 5 == 0 or remaining <= 3):
                try:
                    tick_callback(remaining, seconds, label or app_name)
                except Exception:
                    pass
            time.sleep(1)
        # Clear the line after countdown
        print(" " * 80, end='\r')

    # Resume those we suspended
    resumed = 0
    for pid, _ in suspended:
        try:
            psutil.Process(pid).resume()
            resumed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Build a detailed, but concise, message
    suspended_preview = ", ".join(f"{name}({pid})" for pid, name in suspended[:5])
    if len(suspended) > 5:
        suspended_preview += " ..."
    parts = [
        f"Blocked '{app_name}' for {seconds} seconds",
        f"suspended {len(suspended)} process(es)"
    ]
    if denied:
        parts.append(f"denied on {len(denied)} process(es)")
    if suspended_preview:
        parts.append(f"[{suspended_preview}]")
    return " (".join([parts[0], ", ".join(parts[1:])]) + ")"


def block_apps_by_names(app_names: List[str], seconds: int, tick_callback=None, label: str = None) -> str:
    """Suspend all processes matching any of the provided names for N seconds, then resume.

    - Accepts multiple names and prefers exact (case-insensitive) match; falls back to substring.
    - Returns a concise summary including counts and a preview of suspended processes.
    - On Windows, suggests running as Administrator if nothing could be suspended due to permissions.
    """
    seconds = max(0, int(seconds))
    # Normalize requested names
    requested = [n.strip() for n in (app_names or []) if (n or "").strip()]
    if not requested:
        return "No application names provided to block."

    # Collect candidate processes across all requested names (avoid PID duplicates)
    seen_pids = set()
    procs: List[psutil.Process] = []
    for name in requested:
        for p in _find_processes_by_name_part(name):
            if p.pid not in seen_pids:
                seen_pids.add(p.pid)
                procs.append(p)

    if not procs:
        return f"No running processes matched: {', '.join(requested)}."

    suspended: List[Tuple[int, str]] = []  # (pid, name)
    denied: List[Tuple[int, str]] = []
    other_fail: List[Tuple[int, str]] = []

    for p in procs:
        try:
            name = p.info.get('name') or p.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        try:
            p.suspend()
            suspended.append((p.pid, name))
        except psutil.AccessDenied:
            denied.append((p.pid, name))
        except psutil.NoSuchProcess:
            continue
        except Exception:
            other_fail.append((p.pid, name))

    if not suspended:
        if denied and platform.system().lower() == 'windows' and not _is_admin():
            details = ", ".join(f"{n}({pid})" for pid, n in denied[:5])
            more = " ..." if len(denied) > 5 else ""
            return (
                f"Found processes for {', '.join(requested)} but could not suspend any due to permissions (e.g., {details}{more}). "
                f"Please run the terminal as Administrator and try again."
            )
        return f"Found processes for {', '.join(requested)}, but none could be suspended."

    if seconds > 0:
        names_preview = ", ".join(requested[:3]) + (" ..." if len(requested) > 3 else "")
        width = 30
        for elapsed in range(0, seconds):
            remaining = seconds - elapsed
            filled = int((elapsed / seconds) * width)
            bar = '#' * filled + '-' * (width - filled)
            print(f"Blocking [{names_preview}] [{bar}] {remaining:>3}s remaining", end='\r', flush=True)
            if tick_callback and (remaining == seconds or remaining % 5 == 0 or remaining <= 3):
                try:
                    tick_callback(remaining, seconds, label or names_preview)
                except Exception:
                    pass
            time.sleep(1)
        # Clear the line after countdown
        print(" " * 80, end='\r')

    resumed = 0
    for pid, _ in suspended:
        try:
            psutil.Process(pid).resume()
            resumed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Build message
    suspended_preview = ", ".join(f"{name}({pid})" for pid, name in suspended[:5])
    if len(suspended) > 5:
        suspended_preview += " ..."
    parts = [
        f"Blocked {len(requested)} app name(s) for {seconds} seconds",
        f"suspended {len(suspended)} process(es)"
    ]
    if denied:
        parts.append(f"denied on {len(denied)} process(es)")
    if suspended_preview:
        parts.append(f"[{suspended_preview}]")
    return " (".join([parts[0], ", ".join(parts[1:])]) + ")"
