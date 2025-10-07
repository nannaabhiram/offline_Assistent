#!/usr/bin/env python3
"""
Direct AI Performance Test - Bypass system command parsing
"""

import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ai.brain import ask_ai

def test_ai_direct(question):
    """Test AI directly without command parsing"""
    print(f"🤖 Direct AI Test: '{question}'")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        response = ask_ai(question)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        print(f"✅ Response ({response_time:.1f}ms):")
        print(f"   {response}")
        
        if response_time < 1000:
            print("🚀 ULTRA FAST!")
        elif response_time < 3000:
            print("⚡ FAST")
        elif response_time < 8000:
            print("✅ GOOD")
        else:
            print("🐌 SLOW")
        
        return response_time
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python direct_ai_test.py '<question>'")
        print()
        print("Examples:")
        print("  python direct_ai_test.py 'What is blockchain?'")
        print("  python direct_ai_test.py 'Explain neural networks'")
        print("  python direct_ai_test.py 'How does GPS work?'")
        return
    
    question = " ".join(sys.argv[1:])
    test_ai_direct(question)

if __name__ == "__main__":
    main()