"""
Simple test to verify automation works without main_clean.py complexity
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from system.automation_controller import execute_command, is_automation_command

print("=" * 70)
print("  QUICK AUTOMATION TEST")
print("=" * 70)

# Test if command detection works
cmd = "open notepad"
print(f"\n1. Testing: '{cmd}'")
print(f"   Is automation command: {is_automation_command(cmd)}")

# Execute the command
print(f"   Executing...")
result = execute_command(cmd)

print(f"\n   Result:")
print(f"   - Success: {result.get('success')}")
print(f"   - Message: {result.get('message')}")

print("\n" + "=" * 70)
print("  If notepad opened, the system is working!")
print("=" * 70)
