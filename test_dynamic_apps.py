"""
Test dynamic app opening
"""
import sys
sys.path.append('d:/offline_assistant/backend')

from system import automation
import time

print("=" * 70)
print("TESTING DYNAMIC APP OPENING")
print("=" * 70)

apps_to_test = [
    "notepad",
    "calc", 
    "mspaint",
    "explorer"
]

for app in apps_to_test:
    print(f"\n📱 Testing: {app}")
    print("-" * 70)
    
    result = automation.open_app(app)
    
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    if 'method' in result:
        print(f"   Method: {result['method']}")
    if 'path' in result:
        print(f"   Path: {result['path']}")
    
    if result['success']:
        print(f"   ✅ {app} should now be open!")
        time.sleep(2)
        
        # Try to close it
        close_result = automation.close_app(app)
        print(f"   Closing: {close_result['message']}")
    else:
        print(f"   ❌ Failed to open {app}")
    
    time.sleep(1)

print("\n" + "=" * 70)
print("✅ DYNAMIC APP OPENING TEST COMPLETE!")
print("=" * 70)
