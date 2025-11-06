"""
Quick test to verify 'active online mode' command works
Run this BEFORE starting the full assistant to verify all components
"""
import sys
import os

# Add paths
sys.path.append('d:/offline_assistant')
sys.path.append('d:/offline_assistant/backend')
os.chdir('d:/offline_assistant/backend')

print("=" * 70)
print("PRE-FLIGHT CHECK: Online Mode Activation")
print("=" * 70)

# Test 1: Environment check
print("\n✈️ Test 1: Environment Variables")
from dotenv import load_dotenv
load_dotenv('d:/offline_assistant/.env')
serpapi_key = os.getenv('SERPAPI_KEY')
if serpapi_key:
    print(f"✅ SERPAPI_KEY found: {serpapi_key[:20]}...")
else:
    print("❌ SERPAPI_KEY not found!")

# Test 2: RAG module import
print("\n✈️ Test 2: RAG Module Import")
try:
    from ai.rag import get_rag_status, activate_online_mode_with_wifi
    import ai.rag as rag_module
    print("✅ RAG module imported successfully")
    RAG_AVAILABLE = True
except Exception as e:
    print(f"❌ RAG import failed: {e}")
    RAG_AVAILABLE = False
    sys.exit(1)

# Test 3: WiFi connectivity
print("\n✈️ Test 3: WiFi Connectivity")
from ai.rag import check_wifi_status
wifi = check_wifi_status()
if wifi['connected']:
    print(f"✅ WiFi connected: {wifi['status']}")
else:
    print(f"⚠️ WiFi not connected: {wifi['status']}")

# Test 4: RAG status
print("\n✈️ Test 4: RAG System Status")
status = get_rag_status()
print(f"  Enabled: {status['enabled']}")
print(f"  API Configured: {status['api_configured']}")
print(f"  Status: {status['status']}")
if status['enabled'] and status['api_configured']:
    print("✅ RAG system ready")
else:
    print("❌ RAG system not ready")

# Test 5: Activate online mode
print("\n✈️ Test 5: Online Mode Activation")
result = activate_online_mode_with_wifi()
print(f"  Success: {result['success']}")
print(f"  Message: {result['message']}")
print(f"  Online: {result.get('online_mode_active', False)}")

if result['success']:
    print("✅ Online mode activated successfully!")
else:
    print(f"❌ Online mode activation failed!")

# Test 6: Check if online mode is active
print("\n✈️ Test 6: Verify Online Mode State")
if hasattr(rag_module, 'online_mode_active'):
    print(f"  online_mode_active = {rag_module.online_mode_active}")
    if rag_module.online_mode_active:
        print("✅ Online mode flag is TRUE")
    else:
        print("⚠️ Online mode flag is FALSE")
else:
    print("❌ online_mode_active variable not found in rag_module")

# Test 7: Test search
if result['success'] and rag_module.online_mode_active:
    print("\n✈️ Test 7: Test Real-Time Search")
    try:
        from ai.rag import search_realtime
        search_result = search_realtime("current time")
        if search_result:
            print(f"✅ Search works! Got {len(search_result)} results")
            print(f"  Sample: {search_result[:100]}...")
        else:
            print("⚠️ Search returned no results")
    except Exception as e:
        print(f"❌ Search failed: {e}")

print("\n" + "=" * 70)
print("✅ PRE-FLIGHT CHECK COMPLETE!")
print("=" * 70)
print("\nNow you can run the assistant:")
print("  cd d:\\offline_assistant\\backend")
print("  python main_clean.py")
print("\nThen say: 'active online mode'")
