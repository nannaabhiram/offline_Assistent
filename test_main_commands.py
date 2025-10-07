#!/usr/bin/env python3
"""
Test the main.py command handling with Task Manager
"""

import sys
import os
sys.path.append('backend')

from main import handle_enhanced_commands

def test_main_commands():
    print("Testing main.py command handling...")
    
    test_cases = [
        "close task manager app",
        "kill task manager",
        "terminate taskmanager",
        "close task",
        "open calculator app",
        "close calculator app"
    ]
    
    for command in test_cases:
        print(f"\nTesting: '{command}'")
        result = handle_enhanced_commands(command)
        print(f"Result: {result}")
        
if __name__ == "__main__":
    test_main_commands()