#!/usr/bin/env python3
"""
System Apps Verification - Test that app launching and killing works
"""

import subprocess
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from system.optimized_control import quick_app_launch, quick_process_kill

def check_process_running(process_name):
    """Check if a process is running"""
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        return process_name.lower() in result.stdout.lower()
    except:
        return False

def test_app_lifecycle(app_name, process_name=None):
    """Test launching and killing an app"""
    if not process_name:
        process_name = app_name
    
    print(f"\n🧪 Testing {app_name.upper()}...")
    print("-" * 30)
    
    # Step 1: Launch the app
    print("1️⃣ Launching app...")
    start_time = time.time()
    launch_result = quick_app_launch(app_name)
    launch_time = (time.time() - start_time) * 1000
    print(f"   Launch result: {launch_result}")
    print(f"   Launch time: {launch_time:.1f}ms")
    
    # Step 2: Wait and check if running
    time.sleep(1)
    is_running = check_process_running(process_name)
    print(f"   Process running: {'✅ YES' if is_running else '❌ NO'}")
    
    if is_running:
        # Step 3: Kill the app
        print("2️⃣ Terminating app...")
        start_time = time.time()
        kill_result = quick_process_kill(process_name)
        kill_time = (time.time() - start_time) * 1000
        print(f"   Kill result: {kill_result}")
        print(f"   Kill time: {kill_time:.1f}ms")
        
        # Step 4: Check if killed
        time.sleep(1)
        still_running = check_process_running(process_name)
        print(f"   Process terminated: {'✅ YES' if not still_running else '❌ NO'}")
        
        return is_running and not still_running
    else:
        return False

def main():
    print("🖥️ SYSTEM APPS VERIFICATION TEST")
    print("=" * 50)
    print("Testing app launching and termination...")
    
    # Test apps with their process names
    test_apps = [
        ("notepad", "notepad"),
        ("calculator", "calc"),
        ("paint", "mspaint"),
    ]
    
    results = []
    
    for app_name, process_name in test_apps:
        success = test_app_lifecycle(app_name, process_name)
        results.append((app_name, success))
    
    print(f"\n{'=' * 50}")
    print("📊 TEST RESULTS SUMMARY:")
    print("-" * 30)
    
    all_passed = True
    for app_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{app_name.ljust(15)}: {status}")
        if not success:
            all_passed = False
    
    print(f"\n🎯 OVERALL RESULT:")
    if all_passed:
        print("🎉 ALL SYSTEM APPS WORKING PERFECTLY!")
        print("✅ App launching: FUNCTIONAL")  
        print("✅ Process killing: FUNCTIONAL")
        print("✅ Your assistant has full app control!")
    else:
        print("⚠️ SOME ISSUES DETECTED")
        print("💡 Check individual app results above")
    
    print(f"\n💡 You can now use commands like:")
    print("   python single_test.py 'open notepad'")
    print("   python single_test.py 'kill notepad'")
    print("   python single_test.py 'open calculator'")

if __name__ == "__main__":
    main()