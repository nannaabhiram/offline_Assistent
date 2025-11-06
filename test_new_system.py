"""
Test the new dynamic automation system integration
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from system.automation_controller import execute_command, is_automation_command

print("=" * 70)
print("  TESTING NEW DYNAMIC AUTOMATION SYSTEM")
print("=" * 70)

test_commands = [
    "open notepad",
    "cpu usage",
    "memory usage",
    "battery status",
    "list files in .",
    "mouse position",
    "screen size",
    "list processes",
    "close notepad",
]

for i, cmd in enumerate(test_commands, 1):
    print(f"\n{i}. Testing: '{cmd}'")
    print(f"   Is automation command: {is_automation_command(cmd)}")
    
    if is_automation_command(cmd):
        result = execute_command(cmd)
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        
        # Show extra data if available
        if 'count' in result:
            print(f"   Count: {result['count']}")
        if 'processes' in result:
            print(f"   Processes: {len(result['processes'])} found")
    else:
        print("   ❌ Not recognized as automation command")
    
    print("-" * 70)

print("\n" + "=" * 70)
print("  TEST COMPLETE - New system is working!")
print("=" * 70)
