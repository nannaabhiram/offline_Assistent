#!/usr/bin/env python3
"""
Quick performance test for the optimized control system
"""

import time
import sys
import os

# Add the backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from system.optimized_control import (
        system_status, performance_status, mute_toggle,
        quick_volume_control, execute_fast_command
    )
    print("✅ Optimized control module imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def time_function(func, name, *args, **kwargs):
    """Time a function execution"""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    duration = (end - start) * 1000  # Convert to milliseconds
    print(f"⚡ {name}: {duration:.1f}ms - {result}")
    return result, duration

def main():
    print("🚀 Testing optimized system control performance...\n")
    
    # Test various functions
    functions_to_test = [
        (system_status, "System Status", ()),
        (performance_status, "Performance Status", ()),
        (quick_volume_control, "Volume Control", ("get",)),
        (execute_fast_command, "Unified Command", ("system_info",)),
    ]
    
    total_time = 0
    
    for func, name, args in functions_to_test:
        try:
            result, duration = time_function(func, name, *args)
            total_time += duration
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
    print(f"\n📊 Total execution time: {total_time:.1f}ms")
    
    if total_time < 500:  # Less than 500ms
        print("🎉 Performance: EXCELLENT - Very fast response!")
    elif total_time < 1000:  # Less than 1 second
        print("✅ Performance: GOOD - Fast response")
    else:
        print("⚠️ Performance: SLOW - May need further optimization")

if __name__ == "__main__":
    main()