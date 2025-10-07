#!/usr/bin/env python3
"""
Quick test for system control commands - lightweight version
"""

import os
import sys
import time

# Add the backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from system.optimized_control import (
        quick_volume_control, quick_brightness_control, quick_power_action,
        quick_network_toggle, quick_app_launch, system_status, performance_status,
        mute_toggle, lock_screen, wifi_toggle
    )
    print("✅ System control module loaded successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def handle_fast_commands(user_input):
    """Fast command handler - optimized version"""
    text = user_input.lower().strip()
    
    # Volume commands
    if "volume" in text:
        if "up" in text:
            return quick_volume_control("up")
        elif "down" in text:
            return quick_volume_control("down")  
        elif "mute" in text:
            return mute_toggle()
        else:
            return "Volume command recognized"
    
    # System info commands
    elif "system" in text and "info" in text:
        return system_status()
    
    # Performance commands
    elif "performance" in text:
        return performance_status()
    
    # Power commands
    elif "lock" in text:
        return "Lock command recognized (not executed in test)"
    
    # App commands
    elif "open" in text and "notepad" in text:
        return quick_app_launch("notepad")
    
    else:
        return f"Command '{text}' not recognized"

def main():
    print("🚀 Fast System Control Test")
    print("Available commands: 'volume up', 'volume down', 'mute', 'system info', 'performance', 'lock', 'open notepad'")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("Command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Time the command
            start_time = time.time()
            result = handle_fast_commands(user_input)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            print(f"⚡ Result ({response_time:.1f}ms): {result}")
            
            if response_time < 100:
                print("🎉 Very fast response!")
            elif response_time < 500:
                print("✅ Fast response!")
            else:
                print("⚠️ Slow response - needs optimization")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()