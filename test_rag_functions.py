"""
Test the actual RAG functions
"""
import sys
sys.path.append('d:/offline_assistant')

from backend.ai.rag import (
    check_wifi_status,
    smart_wifi_connect,
    activate_online_mode_with_wifi,
    get_rag_status
)

print("=" * 60)
print("Testing RAG WiFi Functions")
print("=" * 60)

print("\n1️⃣ Testing check_wifi_status()...")
status = check_wifi_status()
print(f"Result: {status}")

print("\n2️⃣ Testing smart_wifi_connect()...")
wifi_result = smart_wifi_connect()
print(f"Result: {wifi_result}")

print("\n3️⃣ Testing activate_online_mode_with_wifi()...")
activation_result = activate_online_mode_with_wifi()
print(f"Result: {activation_result}")

print("\n4️⃣ Testing get_rag_status()...")
rag_status = get_rag_status()
print(f"Result: {rag_status}")

print("\n" + "=" * 60)
print("✅ All tests complete!")
