"""
Test GUI with CLI integration
This shows how GUI and CLI work together
"""
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from gui.assistant_gui import start_gui, update_command, update_response, update_system_stats, show_processing, show_idle
from system.automation_controller import execute_command

print("=" * 70)
print("  🤖 OFFLINE ASSISTANT - GUI + CLI MODE")
print("=" * 70)
print("\n✓ Starting GUI panel...")

# Start GUI in background thread
gui = start_gui()
time.sleep(1)  # Wait for GUI to open

print("✓ GUI panel opened!")
print("✓ CLI is still active - you can type commands")
print("\nDemonstrating commands...\n")

# Test commands
test_commands = [
    ("open notepad", "Opening application..."),
    ("cpu usage", "Checking CPU..."),
    ("memory usage", "Checking memory..."),
    ("battery status", "Checking battery..."),
    ("list files in .", "Listing files..."),
]

try:
    for cmd, description in test_commands:
        print(f"\n>>> {cmd}")
        
        # Update GUI
        update_command(cmd)
        show_processing()
        
        # Execute command
        result = execute_command(cmd)
        
        # Update GUI with result
        update_response(result.get('message', str(result)), result.get('success', False))
        show_idle()
        
        # Print to CLI
        if result.get('success'):
            print(f"✓ {result.get('message', 'Done')}")
        else:
            print(f"✗ {result.get('message', 'Failed')}")
        
        # Update system stats if available
        if 'cpu_percent' in result:
            update_system_stats(cpu=int(result['cpu_percent']))
        if 'percent' in result and 'used_gb' in result:
            update_system_stats(memory=int(result['percent']))
        if 'percent' in result and 'plugged_in' in result:
            battery_text = f"{result['percent']}% {'(charging)' if result['plugged_in'] else '(on battery)'}"
            update_system_stats(battery=battery_text)
        
        time.sleep(2)  # Pause between commands
    
    print("\n" + "=" * 70)
    print("  Demo complete! GUI will stay open.")
    print("  Press Ctrl+C to exit")
    print("=" * 70)
    
    # Keep running
    while True:
        cmd = input("\n>>> ").strip()
        
        if cmd.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
            
        if cmd:
            update_command(cmd)
            show_processing()
            
            result = execute_command(cmd)
            
            update_response(result.get('message', str(result)), result.get('success', False))
            show_idle()
            
            if result.get('success'):
                print(f"✓ {result.get('message', 'Done')}")
            else:
                print(f"✗ {result.get('message', 'Failed')}")

except KeyboardInterrupt:
    print("\n\nShutting down...")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
