#!/usr/bin/env python3
"""
Simple test to start the main assistant properly
"""

import os
import sys

# Ensure we're in the right directory
os.chdir(r'd:\offline_assistant')
sys.path.append(r'd:\offline_assistant\backend')

print("🤖 Starting Offline Assistant...")
print("📁 Working directory:", os.getcwd())
print("📦 Python path:", sys.path[:3])

try:
    from backend.main import main
    print("✅ Successfully imported main function")
    print("🚀 Starting assistant...")
    main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📂 Let's check the backend structure...")
    import glob
    files = glob.glob("backend/*.py") + glob.glob("backend/**/*.py", recursive=True)
    for f in files[:10]:
        print(f"  📄 {f}")
except Exception as e:
    print(f"❌ Error starting assistant: {e}")
    import traceback
    traceback.print_exc()