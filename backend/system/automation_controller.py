"""
Automation Controller
Dynamic command execution using modular control system
"""
import sys
import os
import re
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.parser import parse_command, get_command_help
from system.control import apps, input_control, files, system_info
import subprocess
from typing import Dict, Any

# Execution context to remember last app between sub-commands
_execution_context = {
    "last_app_name": None,
    "last_app_proc": None,
}

def _split_compound(cmd_str):
    # split on ' and ' but keep quoted "and" inside text (simple approach)
    return re.split(r'\s+and\s+', cmd_str.strip(), flags=re.IGNORECASE)

def _handle_single(cmd, ctx):
    cmd = cmd.strip()
    low = cmd.lower()
    # Open app
    if low.startswith("open "):
        app_name = cmd[5:].strip()
        res = apps.open_app(app_name)
        if res.get("success"):
            # store context
            # apps.open_app returns 'app' key; normalize
            ctx["last_app_name"] = res.get("app") or res.get("app_name") or app_name
            ctx["last_app_proc"] = res.get("proc") if "proc" in res else None
            # best-effort focus: some control modules may provide focus; otherwise wait briefly
            try:
                if hasattr(apps, 'focus_app'):
                    # Try a couple of times in case window hasn't appeared yet
                    for _ in range(2):
                        apps.focus_app(ctx["last_app_name"], proc=ctx.get("last_app_proc"))
                        time.sleep(0.2)
                else:
                    time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        return res

    # Close app
    if low.startswith("close "):
        app_name = cmd[6:].strip()
        res = apps.close_app(app_name)
        # clear context if closing the same app
        if res.get("success") and ctx.get("last_app_name") and app_name.lower() in ctx["last_app_name"].lower():
            ctx["last_app_name"] = None
            ctx["last_app_proc"] = None
        return res

    # Type text into last app or specified app: "type hello" or "type 'hello world'"
    m = re.search(r'\btype\b\s*(.+)', cmd, flags=re.IGNORECASE)
    if m:
        text = m.group(1).strip().strip('"').strip("'")
        target = ctx.get("last_app_name")
        proc = ctx.get("last_app_proc")
        if not target:
            return {"success": False, "is_automation": True, "message": "No app focused to type into. Open an app first."}
        try:
            # Try to focus target if available, otherwise give a short delay
            if hasattr(apps, 'focus_app'):
                try:
                    # Small retry focus to improve reliability
                    for _ in range(2):
                        apps.focus_app(target, proc=proc)
                        time.sleep(0.2)
                except Exception:
                    time.sleep(0.3)
            else:
                time.sleep(0.3)
            res = input_control.type_text(text)
            return res
        except Exception as e:
            return {"success": False, "is_automation": True, "message": f"Typing failed: {e}"}

    # Fallback to generic system command: run via subprocess and capture output
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        out = (proc.stdout or '').strip()
        err = (proc.stderr or '').strip()
        success = proc.returncode == 0
        message = out if out else (err if err else f"Command exited with {proc.returncode}")
        return {"success": success, "is_automation": True, "message": message}
    except Exception as e:
        return {"success": False, "is_automation": True, "message": f"Unhandled command error: {e}"}

    return {"success": False, "is_automation": True, "message": "Unknown command"}

def execute_command(command_str):
    """
    Enhanced execute_command: handles compound commands joined by 'and'
    and maintains context (last opened app) so subsequent actions like 'type'
    apply to the opened app.
    """
    parts = _split_compound(command_str)
    messages = []
    overall_success = True
    is_automation = True

    for part in parts:
        res = _handle_single(part, _execution_context)
        # Normalize keys for caller compatibility
        is_automation = res.get("is_automation", True) and is_automation
        success = res.get("success", False)
        overall_success = overall_success and success
        msg = res.get("message") or res.get("output") or str(res)
        messages.append(msg)

        if not success:
            # stop on first failure or continue? Stop to mirror user expectation
            break

    return {
        "is_automation": is_automation,
        "success": overall_success,
        "message": " | ".join(messages)
    }


def is_automation_command(command: str) -> bool:
    """Check if command is an automation command"""
    action, _ = parse_command(command)
    return action is not None


if __name__ == "__main__":
    # Interactive test mode
    print("=" * 70)
    print("  DYNAMIC AUTOMATION CONTROLLER - TEST MODE")
    print("=" * 70)
    print("\nType 'help' for commands, 'quit' to exit\n")
    
    while True:
        try:
            command = input("You: ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if command.lower() in ['help', 'commands']:
                print(get_command_help())
                continue
            
            # Execute command
            result = execute_command(command)
            action, _ = parse_command(command)
            
            # Display result
            if result['success']:
                print(f"✅ {result['message']}")
                
                # Show additional info if available
                if action == "list_running_processes" and 'processes' in result:
                    # Show top processes
                    procs = sorted(result['processes'], key=lambda x: x['cpu'] or 0, reverse=True)[:10]
                    print("\n   Top Processes:")
                    for p in procs:
                        print(f"   - {p['name']} (CPU: {p['cpu']}%)")
                
                elif action == "list_files" and 'files' in result:
                    # Show files
                    print(f"\n   Files in {result['folder']}:")
                    for f in result['files'][:20]:
                        print(f"   - {f}")
                    if result['count'] > 20:
                        print(f"   ... and {result['count'] - 20} more")
                
                elif action == "get_full_system_status":
                    # Show full system status
                    print("\n   System Overview:")
                    print(f"   CPU: {result['cpu']['cpu_percent']}%")
                    print(f"   Memory: {result['memory']['percent']}%")
                    print(f"   Disk: {result['disk']['percent']}%")
                    if result['battery']['has_battery']:
                        print(f"   Battery: {result['battery']['percent']}%")
            else:
                print(f"❌ {result['message']}")
                if 'help' in result:
                    print(f"   💡 {result['help']}")
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
