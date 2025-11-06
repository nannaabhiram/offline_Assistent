"""
Test the complete flow: Start assistant and activate online mode
"""
import sys
sys.path.append('d:/offline_assistant')
sys.path.append('d:/offline_assistant/backend')

print("=" * 70)
print("TESTING: 'active online mode' command flow")
print("=" * 70)

# Step 1: Test RAG import
print("\n1️⃣ Testing RAG import...")
try:
    from ai.rag import get_rag_status, activate_online_mode_with_wifi
    import ai.rag as rag_module
    print("✅ RAG module imported successfully")
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"❌ RAG import failed: {e}")
    RAG_AVAILABLE = False
except Exception as e:
    print(f"❌ RAG loading error: {e}")
    RAG_AVAILABLE = False

if not RAG_AVAILABLE:
    print("\n❌ Cannot continue - RAG not available")
    sys.exit(1)

# Step 2: Check RAG status
print("\n2️⃣ Checking RAG status...")
status = get_rag_status()
print(f"Status: {status}")

# Step 3: Simulate user saying "active online mode"
print("\n3️⃣ Simulating user command: 'active online mode'")
user_input = "active online mode"

# Check if command matches
phrases = ["active online mode", "activate online mode", "enable online mode", "turn on online mode", "online mode on"]
if any(phrase in user_input.lower() for phrase in phrases):
    print("✅ Command matched!")
    
    print("\n4️⃣ Calling activate_online_mode_with_wifi()...")
    result = activate_online_mode_with_wifi()
    
    print(f"\n📊 Result:")
    print(f"  - Success: {result['success']}")
    print(f"  - Message: {result['message']}")
    print(f"  - Online mode active: {result.get('online_mode_active', False)}")
    
    if result['success']:
        print("\n🎉 SUCCESS! Online mode activated!")
        print(f"   Response to user: {result['message']}")
    else:
        print(f"\n⚠️ FAILED: {result['message']}")
        if 'wifi_status' in result:
            print(f"   WiFi details: {result['wifi_status']}")
else:
    print("❌ Command did not match!")

print("\n" + "=" * 70)
print("Test complete!")
