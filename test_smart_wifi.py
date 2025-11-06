"""
Test Smart WiFi Connection and Online Mode Activation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ai.rag import check_wifi_status, smart_wifi_connect, activate_online_mode_with_wifi

print("=" * 70)
print("🌐 SMART WIFI & ONLINE MODE TEST")
print("=" * 70)

# Test 1: Check WiFi Status
print("\n1️⃣ Checking WiFi Status...")
wifi_status = check_wifi_status()
print(f"   Connected: {wifi_status['connected']}")
print(f"   Status: {wifi_status['status']}")

# Test 2: Smart WiFi Connect
print("\n2️⃣ Testing Smart WiFi Connection...")
connect_result = smart_wifi_connect()
print(f"   Success: {connect_result['success']}")
print(f"   Message: {connect_result['message']}")
if 'actions_taken' in connect_result:
    print(f"   Actions: {len(connect_result['actions_taken'])} steps taken")

# Test 3: Activate Online Mode with WiFi
print("\n3️⃣ Testing Online Mode Activation...")
activation_result = activate_online_mode_with_wifi()
print(f"   Success: {activation_result['success']}")
print(f"   Message: {activation_result['message']}")
print(f"   Online Mode Active: {activation_result['online_mode_active']}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETED")
print("=" * 70)

print("\n💡 How it works:")
print("   When you say 'active online mode':")
print("   1. ✓ Checks WiFi status")
print("   2. ✓ Enables WiFi if disconnected")
print("   3. ✓ Waits for connection")
print("   4. ✓ Shows reason if can't connect")
print("   5. ✓ Activates online mode if connected")
print("   6. ✓ Gives you a clear status message")
