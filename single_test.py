#!/usr/bin/env python3
"""
Single Command Tester - Test assistant commands without interactive mode
"""

import os
import sys
import time

# Add the backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_single_command(command):
    """Test a single command using the enhanced handler"""
    print(f"🤖 Testing: '{command}'")
    print("-" * 40)
    
    try:
        # Import the optimized functions
        from system.optimized_control import (
            quick_volume_control, system_status, performance_status, 
            quick_brightness_control, quick_power_action, wifi_toggle,
            quick_app_launch, quick_process_kill, execute_fast_command
        )
        
        # Import AI function
        from ai.brain import ask_ai
        
        # Parse command like the main app does
        text = command.lower().strip()
        result = None
        start_time = time.time()
        
        # System control commands
        if any(keyword in text for keyword in ["system info", "computer info", "pc info", "hardware"]):
            result = f"System: {system_status()}"
        
        elif any(keyword in text for keyword in ["performance", "cpu", "memory", "disk"]):
            result = f"Performance: {performance_status()}"
        
        elif any(keyword in text for keyword in ["volume", "sound", "audio"]):
            if "up" in text:
                result = f"Volume: {quick_volume_control('up')}"
            elif "down" in text:
                result = f"Volume: {quick_volume_control('down')}" 
            elif "mute" in text:
                result = f"Volume: {quick_volume_control('mute')}"
            else:
                result = f"Volume: {quick_volume_control('get')}"
        
        elif any(keyword in text for keyword in ["brightness", "screen"]):
            if "up" in text:
                result = f"Brightness: {quick_brightness_control('up')}"
            elif "down" in text:
                result = f"Brightness: {quick_brightness_control('down')}"
            else:
                result = f"Brightness: {quick_brightness_control('get')}"
        
        elif any(keyword in text for keyword in ["lock", "sleep", "shutdown", "restart"]):
            if "lock" in text:
                result = f"Power: {quick_power_action('lock')}"
            elif "sleep" in text:
                result = f"Power: {quick_power_action('sleep')}"
            elif "shutdown" in text:
                result = "Power: Shutdown command recognized (not executed in test)"
            elif "restart" in text:
                result = "Power: Restart command recognized (not executed in test)"
        
        elif any(keyword in text for keyword in ["open", "launch", "start"]) and ("notepad" in text or "calculator" in text or "paint" in text):
            import re
            if "notepad" in text:
                result = f"App: {quick_app_launch('notepad')}"
            elif "calculator" in text:
                result = f"App: {quick_app_launch('calculator')}"  
            elif "paint" in text:
                result = f"App: {quick_app_launch('paint')}"
        
        elif any(keyword in text for keyword in ["kill", "close", "terminate"]):
            import re
            if "notepad" in text:
                result = f"Process: {quick_process_kill('notepad')}"
            elif "calculator" in text:
                result = f"Process: {quick_process_kill('calc')}"
            elif "paint" in text:
                result = f"Process: {quick_process_kill('mspaint')}"
        
        elif "wifi" in text or "network" in text:
            if "off" in text:
                result = f"Network: WiFi disable command (not executed in test)"
            elif "on" in text:
                result = f"Network: WiFi enable command (not executed in test)"
            else:
                result = "Network: Status check"
        
        # If no system command matched, use AI
        if not result:
            result = ask_ai(command)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        # Display results
        print(f"✅ Response ({response_time:.1f}ms):")
        print(f"   {result}")
        
        # Performance feedback
        if response_time < 50:
            print("🚀 ULTRA FAST!")
        elif response_time < 200:
            print("⚡ FAST")
        elif response_time < 1000:
            print("✅ GOOD")
        else:
            print("🐌 SLOW")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 2:
        print("🤖 Single Command Tester")
        print("========================")
        print("Usage: python single_test.py '<command>'")
        print()
        print("🔥 Example commands to try:")
        print("  python single_test.py 'system info'")
        print("  python single_test.py 'performance'") 
        print("  python single_test.py 'volume up'")
        print("  python single_test.py 'open notepad'")
        print("  python single_test.py 'kill notepad'")
        print("  python single_test.py 'lock screen'")
        print("  python single_test.py 'What is artificial intelligence?'")
        print()
        print("🚀 This bypasses the interactive input loop!")
        return
    
    command = " ".join(sys.argv[1:])
    test_single_command(command)

if __name__ == "__main__":
    main()