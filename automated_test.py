#!/usr/bin/env python3
"""
Automated Main Assistant Test

This will test the main assistant with automated inputs
"""

import sys
import os
import time
import threading
from io import StringIO

sys.path.append('backend')

def test_main_with_commands():
    """Test main assistant with automated commands"""
    print("🤖 Automated Main Assistant Test")
    print("=" * 40)
    
    # List of commands to test
    test_commands = [
        "start enhanced vision",
        "my name is abhiram", 
        "who do you know",
        "stop vision",
        "exit"
    ]
    
    print(f"📋 Will test these commands: {test_commands}")
    print("🚀 Starting main assistant...")
    
    # Import main function
    try:
        from main import main
        
        # Mock input function to provide automated responses
        original_input = __builtins__['input']
        command_index = [0]  # Use list to make it mutable in closure
        mode_chosen = [False]
        
        def mock_input(prompt):
            if not mode_chosen[0]:
                mode_chosen[0] = True
                print("You: cli")
                return "cli"
            
            if command_index[0] < len(test_commands):
                cmd = test_commands[command_index[0]]
                command_index[0] += 1
                print(f"You: {cmd}")
                time.sleep(1)  # Small delay to see output
                return cmd
            else:
                # End the test
                print("You: exit")
                return "exit"
        
        # Replace input function temporarily
        __builtins__['input'] = mock_input
        
        try:
            main()
        finally:
            # Restore original input function
            __builtins__['input'] = original_input
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_with_commands()