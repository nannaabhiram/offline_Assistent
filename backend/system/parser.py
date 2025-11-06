"""
Dynamic Command Parser
Interprets user commands and maps them to appropriate actions
"""
import re
from typing import Tuple, Any, Optional


def parse_command(command: str) -> Tuple[Optional[str], Any]:
    """
    Parse user command and return (action, value) tuple
    
    Returns:
        (action_name, parameters) or (None, None) if command not recognized
    """
    command = command.lower().strip()
    
    # ============================================================================
    # APP CONTROL COMMANDS
    # ============================================================================
    
    if "open" in command and "app" in command:
        # "open app notepad" or "open notepad app"
        app = command.replace("open", "").replace("app", "").strip()
        return ("open_app", app)
    
    elif command.startswith("open "):
        # "open notepad" - extract just the app name (first word after "open")
        rest = command.replace("open", "").strip()
        app = rest.split()[0] if rest else ""
        return ("open_app", app)
    
    elif "close" in command and "app" in command:
        # "close app chrome"
        app = command.replace("close", "").replace("app", "").strip()
        return ("close_app", app)
    
    elif command.startswith("close "):
        # "close chrome"
        app = command.replace("close", "").strip()
        return ("close_app", app)
    
    elif "app info" in command:
        # "app info chrome"
        app = command.replace("app", "").replace("info", "").strip()
        return ("get_app_info", app)
    
    elif command in ["list processes", "show processes", "running processes"]:
        return ("list_running_processes", None)
    
    # ============================================================================
    # MOUSE & KEYBOARD COMMANDS
    # ============================================================================
    
    elif "move mouse" in command:
        # "move mouse to 300 400" or "move mouse 300,400"
        try:
            # Extract numbers from command
            numbers = re.findall(r'\d+', command)
            if len(numbers) >= 2:
                x, y = int(numbers[0]), int(numbers[1])
                return ("move_mouse", (x, y))
        except:
            pass
    
    elif command in ["click mouse", "mouse click", "click"]:
        return ("click_mouse", None)
    
    elif command.startswith("type "):
        # "type Hello World"
        text = command.replace("type", "").strip()
        return ("type_text", text)
    
    elif command.startswith("press "):
        # "press enter"
        key = command.replace("press", "").strip()
        return ("press_key", key)
    
    elif command in ["mouse position", "get mouse position", "where is mouse"]:
        return ("get_mouse_position", None)
    
    elif command in ["screen size", "screen resolution", "display size"]:
        return ("get_screen_size", None)
    
    # ============================================================================
    # FILE SYSTEM COMMANDS
    # ============================================================================
    
    elif "list files in" in command:
        # "list files in C:\Users"
        folder = command.replace("list files in", "").strip()
        return ("list_files", folder)
    
    elif "copy file" in command and " to " in command:
        # "copy file source.txt to dest.txt"
        parts = command.replace("copy file", "").split(" to ")
        if len(parts) == 2:
            src = parts[0].strip()
            dst = parts[1].strip()
            return ("copy_file", (src, dst))
    
    elif "move file" in command and " to " in command:
        # "move file source.txt to dest.txt"
        parts = command.replace("move file", "").split(" to ")
        if len(parts) == 2:
            src = parts[0].strip()
            dst = parts[1].strip()
            return ("move_file", (src, dst))
    
    elif "create folder" in command:
        # "create folder MyFolder"
        folder = command.replace("create", "").replace("folder", "").strip()
        return ("create_folder", folder)
    
    elif "delete file" in command:
        # "delete file old.txt"
        filepath = command.replace("delete", "").replace("file", "").strip()
        return ("delete_file", filepath)
    
    elif "delete folder" in command:
        # "delete folder OldFolder"
        folder = command.replace("delete", "").replace("folder", "").strip()
        return ("delete_folder", folder)
    
    elif "file info" in command:
        # "file info document.pdf"
        filepath = command.replace("file", "").replace("info", "").strip()
        return ("get_file_info", filepath)
    
    # ============================================================================
    # SYSTEM INFO COMMANDS
    # ============================================================================
    
    elif command in ["cpu usage", "check cpu", "processor usage", "cpu"]:
        return ("get_cpu_usage", None)
    
    elif command in ["memory usage", "ram usage", "check memory", "check ram", "memory", "ram"]:
        return ("get_memory_info", None)
    
    elif command in ["battery status", "check battery", "battery level", "battery"]:
        return ("get_battery_status", None)
    
    elif command in ["disk space", "storage space", "check disk", "disk usage", "disk"]:
        return ("get_disk_info", None)
    
    elif command in ["network info", "network status", "network"]:
        return ("get_network_info", None)
    
    elif command in ["os info", "operating system", "system info"]:
        return ("get_os_info", None)
    
    elif command in ["full system status", "complete system info", "system overview", "system status"]:
        return ("get_full_system_status", None)
    
    # Command not recognized
    return (None, None)


def get_command_help() -> str:
    """Return help text showing available commands"""
    help_text = """
📋 AVAILABLE COMMANDS:

🎯 App Control:
  • open <app>               - Open an application
  • close <app>              - Close an application
  • app info <app>           - Get app information
  • list processes           - Show running processes

🖱️ Mouse & Keyboard:
  • move mouse to <x> <y>    - Move mouse to coordinates
  • click mouse              - Click mouse
  • type <text>              - Type text
  • press <key>              - Press a key
  • mouse position           - Get mouse position
  • screen size              - Get screen resolution

📁 File System:
  • list files in <folder>   - List files in directory
  • copy file <src> to <dst> - Copy a file
  • create folder <path>     - Create a folder
  • delete file <path>       - Delete a file
  • file info <path>         - Get file information

🖥️ System Info:
  • cpu usage                - Check CPU usage
  • memory usage             - Check RAM usage
  • battery status           - Check battery level
  • disk space               - Check disk space
  • full system status       - Complete system overview
"""
    return help_text
