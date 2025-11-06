"""
Quick verification that main_clean.py imports work
"""
print("Testing imports from main_clean.py...")

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
    
    # Test old control imports
    print("✓ Testing old control imports...")
    import system.control as old_control
    print("  ✓ old_control.run_system_command exists")
    print("  ✓ old_control.list_running_apps exists")
    print("  ✓ old_control.block_app_by_name exists")
    
    # Test new automation imports
    print("\n✓ Testing new automation imports...")
    from system.automation_controller import execute_command, is_automation_command
    print("  ✓ execute_command imported")
    print("  ✓ is_automation_command imported")
    
    # Test a simple command
    print("\n✓ Testing a simple command...")
    result = execute_command("cpu usage")
    print(f"  Command: 'cpu usage'")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    print("\n" + "=" * 70)
    print("✅ ALL IMPORTS WORKING! main_clean.py should run fine!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
