#!/usr/bin/env python3
"""
Interactive Assistant Tester
Quick and easy way to test your offline assistant capabilities
"""

import os
import sys
import time
from datetime import datetime

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def print_header():
    print("=" * 60)
    print("🤖 OFFLINE ASSISTANT TESTER")
    print("=" * 60)
    print("Test your assistant's capabilities quickly!")
    print()

def run_test_category(category_name, commands, description):
    print(f"🧪 {category_name.upper()} TESTS")
    print("-" * 40)
    print(f"📝 {description}")
    print()
    
    for i, cmd in enumerate(commands, 1):
        print(f"{i}. {cmd}")
    
    print()
    choice = input("Enter command number to test (or 'all' for all, 'skip' to skip): ").strip().lower()
    
    if choice == 'skip':
        return
    elif choice == 'all':
        test_commands = commands
    elif choice.isdigit() and 1 <= int(choice) <= len(commands):
        test_commands = [commands[int(choice) - 1]]
    else:
        print("❌ Invalid choice, skipping...")
        return
    
    print(f"\n🚀 Testing {len(test_commands)} command(s)...")
    
    # Import the main handler
    try:
        from main import handle_enhanced_commands
    except ImportError:
        print("❌ Could not import main handler. Run from backend directory or check imports.")
        return
    
    for cmd in test_commands:
        print(f"\n➤ Testing: '{cmd}'")
        start_time = time.time()
        
        try:
            result = handle_enhanced_commands(cmd)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            if result:
                print(f"✅ Result ({response_time:.1f}ms): {result}")
                
                if response_time < 50:
                    print("🚀 ULTRA FAST!")
                elif response_time < 200:
                    print("⚡ FAST")
                else:
                    print("🐌 Slower than expected")
            else:
                print("❌ No result returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.5)  # Brief pause between tests

def main():
    print_header()
    
    # Test categories
    test_categories = {
        "System Info": {
            "description": "Test system information and performance monitoring",
            "commands": [
                "system info",
                "performance", 
                "computer info",
                "hardware info"
            ]
        },
        
        "Volume Control": {
            "description": "Test audio/volume control (Windows API)",
            "commands": [
                "volume up",
                "volume down", 
                "mute",
                "volume max"
            ]
        },
        
        "Application Control": {
            "description": "Test application launching and management",
            "commands": [
                "open notepad",
                "launch calculator",
                "kill notepad",
                "close calculator"
            ]
        },
        
        "Power Management": {
            "description": "Test power controls (⚠️ WILL ACTUALLY EXECUTE)",
            "commands": [
                "lock screen",
                # "sleep",  # Commented out for safety
                # "shutdown"  # Commented out for safety
            ]
        },
        
        "Network Control": {
            "description": "Test network and WiFi controls",
            "commands": [
                "wifi status",
                # "wifi off",  # Commented out for safety
                # "wifi on"
            ]
        },
        
        "File Operations": {
            "description": "Test file system operations",
            "commands": [
                "create file test_file.txt",
                "delete file test_file.txt"
            ]
        }
    }
    
    print("Available test categories:")
    categories = list(test_categories.keys())
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    
    print(f"{len(categories) + 1}. Run ALL tests")
    print(f"{len(categories) + 2}. Quick demo")
    
    choice = input(f"\nChoose category (1-{len(categories) + 2}): ").strip()
    
    if choice == str(len(categories) + 1):
        # Run all tests
        for cat_name, cat_data in test_categories.items():
            print(f"\n{'=' * 60}")
            run_test_category(cat_name, cat_data["commands"], cat_data["description"])
            
    elif choice == str(len(categories) + 2):
        # Quick demo
        demo_commands = [
            "system info",
            "performance", 
            "open notepad",
            "kill notepad",
            "volume up"
        ]
        run_test_category("Quick Demo", demo_commands, "Fast demonstration of key features")
        
    elif choice.isdigit() and 1 <= int(choice) <= len(categories):
        # Run specific category
        cat_name = categories[int(choice) - 1]
        cat_data = test_categories[cat_name]
        run_test_category(cat_name, cat_data["commands"], cat_data["description"])
        
    else:
        print("❌ Invalid choice")
        return
    
    print(f"\n{'=' * 60}")
    print("🎉 Testing complete!")
    print("📋 Check TESTING_GUIDE.md for more comprehensive tests")
    print("💡 Try running the main assistant: python backend/main.py")

if __name__ == "__main__":
    main()