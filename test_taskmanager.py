#!/usr/bin/env python3
import sys
import os
sys.path.append('backend')

from system.optimized_control import quick_process_kill

def test_task_manager():
    print("Testing Task Manager termination...")
    
    # Test different variations
    test_names = [
        "task manager",
        "taskmanager", 
        "task",
        "Taskmgr.exe"
    ]
    
    for name in test_names:
        print(f"\nTesting: {name}")
        result = quick_process_kill(name)
        print(f"Result: {result}")
        
if __name__ == "__main__":
    test_task_manager()