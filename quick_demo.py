#!/usr/bin/env python3
"""
Quick Assistant Demo - 30 Second Test
"""

import os
import sys
import time

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def quick_test():
    print("🚀 30-Second Assistant Demo Starting...")
    print("=" * 50)
    
    # Import optimized functions directly for speed
    try:
        from system.optimized_control import (
            system_status, performance_status, quick_volume_control, 
            quick_app_launch, quick_process_kill
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Test sequence with timing
    tests = [
        ("System Info", lambda: system_status()),
        ("Performance", lambda: performance_status()),  
        ("Volume Control", lambda: quick_volume_control("get")),
        ("Launch App", lambda: quick_app_launch("notepad")),
        ("Kill App", lambda: quick_process_kill("notepad"))
    ]
    
    total_start = time.time()
    
    for i, (name, func) in enumerate(tests, 1):
        print(f"\n{i}. Testing {name}...")
        
        start = time.time()
        try:
            result = func()
            end = time.time()
            
            response_time = (end - start) * 1000
            print(f"   ✅ {response_time:6.1f}ms - {result}")
            
            if response_time < 50:
                print(f"   🚀 ULTRA FAST!")
            elif response_time < 200:
                print(f"   ⚡ FAST")
            else:
                print(f"   🐌 SLOW")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.2)  # Brief pause
    
    total_end = time.time()
    total_time = (total_end - total_start) * 1000
    
    print(f"\n{'=' * 50}")
    print(f"🏁 Demo Complete! Total time: {total_time:.0f}ms")
    
    if total_time < 1000:
        print("🎉 EXCELLENT - Your assistant is lightning fast!")
    elif total_time < 2000:
        print("✅ GOOD - Fast response times")
    else:
        print("⚠️ SLOW - May need optimization")
    
    print(f"\n💡 Next steps:")
    print(f"   • Run: python backend/main.py")
    print(f"   • Try commands like: 'system info', 'volume up', 'open notepad'")
    print(f"   • Check TESTING_GUIDE.md for full test suite")

if __name__ == "__main__":
    quick_test()