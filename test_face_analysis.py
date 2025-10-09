#!/usr/bin/env python3
"""
Test script for face analysis system
"""

import time
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from vision.face_analyzer import start_face_analysis, stop_face_analysis, get_current_analysis, detect_user_mood

def test_face_analysis():
    print("🧪 Testing Face Analysis System...")
    print("=" * 50)

    # Start face analysis
    if not start_face_analysis():
        print("❌ Failed to start camera!")
        return

    print("✅ Camera started successfully!")
    print("📹 Testing face detection for 10 seconds...")
    print("💡 Look at the camera to test face detection!")
    print()

    try:
        for i in range(10):
            print(f"Frame {i+1}: ", end="")

            analysis = get_current_analysis()

            if analysis.get('faces_detected', 0) > 0:
                face = analysis['analysis'][0]
                emotion = face.get('emotion', {}).get('emotion', 'unknown')
                confidence = face.get('emotion', {}).get('confidence', 0)

                print(f"✅ Face detected! Mood: {emotion} ({confidence:.2f})")

                if emotion != 'neutral' and confidence > 0.5:
                    print(f"   💭 I can see you're feeling {emotion}!")
            else:
                print("❌ No face detected")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
    finally:
        stop_face_analysis()
        print("\n✅ Face analysis test completed!")

if __name__ == "__main__":
    test_face_analysis()
