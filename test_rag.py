"""
Test RAG (Retrieval-Augmented Generation) functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ai.rag import get_rag_status, should_use_rag, search_serp, extract_context_from_serp, enhance_with_rag

print("=" * 70)
print("🧪 RAG SYSTEM TEST")
print("=" * 70)

# Test 1: Check RAG Status
print("\n1️⃣ Testing RAG Status...")
rag_status = get_rag_status()
print(f"   Enabled: {rag_status['enabled']}")
print(f"   API Configured: {rag_status['api_configured']}")
print(f"   Status: {rag_status['status']}")

# Test 2: Check if queries should use RAG
print("\n2️⃣ Testing Query Detection...")
test_queries = [
    ("What is Python?", False),  # General knowledge - no RAG needed
    ("What's the weather today?", True),  # Real-time - needs RAG
    ("Latest news about AI", True),  # Current events - needs RAG
    ("How to cook pasta", False),  # General knowledge - no RAG needed
]

for query, expected in test_queries:
    result = should_use_rag(query)
    status_check = "✓" if result == expected else "✗"
    print(f"   {status_check} '{query}' → RAG: {result}")

# Test 3: Test SerpAPI Search (if API is configured)
if rag_status['api_configured']:
    print("\n3️⃣ Testing SerpAPI Search...")
    print("   Searching: 'What is the capital of France?'")
    
    try:
        results = search_serp("What is the capital of France?", num_results=2)
        if results:
            print("   ✓ Search successful!")
            
            # Extract context
            context = extract_context_from_serp(results)
            if context:
                print(f"\n   📄 Extracted Context:")
                print(f"   {context[:200]}...")
            else:
                print("   ⚠️ No context extracted")
        else:
            print("   ✗ Search failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Test RAG Enhancement
    print("\n4️⃣ Testing RAG Enhancement...")
    test_prompt = "What's the weather today?"
    print(f"   Original: '{test_prompt}'")
    
    try:
        enhanced, rag_used = enhance_with_rag(test_prompt)
        print(f"   RAG Used: {rag_used}")
        if rag_used:
            print(f"   ✓ Prompt enhanced with real-time data")
            print(f"   Enhanced prompt length: {len(enhanced)} characters")
        else:
            print(f"   ⚠️ RAG not applied (might need better query)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
else:
    print("\n3️⃣ ⏭️  Skipping SerpAPI tests (API not configured)")
    print("\n4️⃣ ⏭️  Skipping RAG enhancement test (API not configured)")

print("\n" + "=" * 70)
print("✅ RAG TEST COMPLETED")
print("=" * 70)

print("\n💡 How RAG Works:")
print("   1. Detects queries needing real-time info (weather, news, etc.)")
print("   2. Searches internet using SerpAPI")
print("   3. Extracts relevant context from results")
print("   4. Enhances AI prompt with real-time data")
print("   5. AI generates response based on current information")

print("\n🎯 Try asking:")
print("   - 'What's the weather today?'")
print("   - 'Latest news about technology'")
print("   - 'Current price of Bitcoin'")
print("   - And your assistant will use real-time internet data!")
