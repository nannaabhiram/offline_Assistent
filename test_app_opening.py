"""
Quick test for app opening functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from system.automation_controller import execute_command

print("=" * 70)
print("  TESTING APP OPENING")
print("=" * 70)

# Test 1: Open Notepad
print("\n1. Testing: open notepad")
result = execute_command("open notepad")
print(f"   Result: {result}")

# Test 2: Try opening a complex command (should parse just the app name)
print("\n2. Testing: open notepad and type hello")
result = execute_command("open notepad and type hello")
print(f"   Result: {result}")

# Test 3: Open Calculator
print("\n3. Testing: open calc")
result = execute_command("open calc")
print(f"   Result: {result}")

# Test 4: Try non-existent app
print("\n4. Testing: open fakeyapp12345")
result = execute_command("open fakeyapp12345")
print(f"   Result: {result}")

# Test 5: Close notepad
print("\n5. Testing: close notepad")
result = execute_command("close notepad")
print(f"   Result: {result}")

print("\n" + "=" * 70)
print("  TEST COMPLETE")
print("=" * 70)
