#!/usr/bin/env python3
"""
Direct Main Assistant Test

Test the main.py directly with CLI input
"""

import sys
import os
sys.path.append('backend')

print("🤖 Starting Direct Main Assistant Test...")
print("📁 Current directory:", os.getcwd())
print("🔧 Activating virtual environment...")

# Activate virtual environment if available
import subprocess
venv_script = r"D:\offline_assistant\venv\Scripts\Activate.ps1"
if os.path.exists(venv_script):
    print("✅ Virtual environment found")
else:
    print("⚠️ Virtual environment not found, continuing anyway...")

# Import and run main
try:
    from main import main
    print("✅ Successfully imported main")
    print("🚀 Starting main assistant...")
    main()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()