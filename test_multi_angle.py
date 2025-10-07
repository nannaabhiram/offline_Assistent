#!/usr/bin/env python3
"""
Test Multi-Angle Face Learning System

This tests the enhanced face recognition with phone-like multi-angle capture
"""

import sys
import os
sys.path.append('backend')

def test_multi_angle_face_learning():
    print("🎭 Multi-Angle Face Learning Test")
    print("=" * 50)
    print("This system now captures faces like phone face locks:")
    print("✅ Multiple angles (straight, left, right, up, down)")
    print("✅ Different expressions (neutral, smile, blink)")
    print("✅ Multiple profiles per person for better recognition")
    print("=" * 50)
    
    # Import required modules
    from vision.opencv_enhanced_detector import (
        start_opencv_enhanced_vision, stop_opencv_enhanced_vision, 
        opencv_enhanced_vision_running, learn_opencv_face_name,
        get_opencv_enhanced_detector
    )
    from vision.opencv_face_memory import initialize_opencv_face_system
    
    def speak_func(message):
        print(f"🤖 {message}")
    
    project_root = os.path.abspath('.')
    
    print("\n🚀 Commands available:")
    print("  start enhanced vision  - Start multi-angle face learning")
    print("  my name is [name]      - Learn your face with multi-angle capture")
    print("  single learn [name]    - Learn with single frame (old method)")
    print("  who do you know        - List known people")
    print("  stop vision           - Stop camera")
    print("  exit                  - Quit")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("👋 Goodbye!")
                break
                
            elif user_input.lower() in ["start enhanced vision", "start face recognition"]:
                if opencv_enhanced_vision_running():
                    speak_func("Enhanced vision is already running.")
                else:
                    # Initialize face system first
                    if initialize_opencv_face_system(speak_func):
                        start_opencv_enhanced_vision(project_root, speak_func, camera_index=0, face_recognition=True)
                        speak_func("🎭 Multi-angle learning enabled! When I see an unknown face, I'll guide you through professional face capture.")
                    else:
                        speak_func("Face recognition system failed to initialize.")
                        
            elif user_input.lower() in ["stop vision", "stop enhanced vision"]:
                if opencv_enhanced_vision_running():
                    stop_opencv_enhanced_vision(project_root, speak_func)
                else:
                    speak_func("Enhanced vision is not running.")
                    
            elif user_input.lower().startswith("my name is "):
                name = user_input[11:].strip()
                if opencv_enhanced_vision_running() and name:
                    speak_func(f"🎭 Starting ADVANCED multi-angle learning for {name}")
                    speak_func("This will be like setting up face unlock on your phone!")
                    success = learn_opencv_face_name(project_root, speak_func, name, use_multi_angle=True)
                    if not success:
                        speak_func("Please show me your face while saying your name.")
                elif not name:
                    speak_func("Please tell me your name.")
                else:
                    speak_func("Please start enhanced vision first.")
                    
            elif user_input.lower().startswith("single learn "):
                name = user_input[13:].strip()
                if opencv_enhanced_vision_running() and name:
                    speak_func(f"📸 Learning single-frame profile for {name} (old method)")
                    success = learn_opencv_face_name(project_root, speak_func, name, use_multi_angle=False)
                    if not success:
                        speak_func("Please show me your face while saying your name.")
                elif not name:
                    speak_func("Please tell me the name to learn.")
                else:
                    speak_func("Please start enhanced vision first.")
                    
            elif user_input.lower() in ["who do you know", "known people"]:
                try:
                    detector = get_opencv_enhanced_detector(project_root, speak_func)
                    people = detector.get_known_people()
                    if people:
                        speak_func(f"I know {len(people)} people: " + ", ".join(people))
                    else:
                        speak_func("I don't know anyone yet.")
                except Exception:
                    speak_func("Face system not available.")
                    
            elif user_input.lower() in ["status", "vision status"]:
                running = opencv_enhanced_vision_running()
                speak_func(f"Enhanced vision is {'running' if running else 'stopped'}.")
                
            elif user_input.lower() == "help":
                print("\n📋 Available commands:")
                print("  start enhanced vision  - Start camera with multi-angle learning")
                print("  my name is [name]      - Multi-angle face learning (RECOMMENDED)")
                print("  single learn [name]    - Single-frame learning (basic)")
                print("  who do you know        - List all known people")
                print("  status                 - Check if camera is running")
                print("  help                   - Show this help")
                print("  exit                   - Quit program")
                
            else:
                speak_func("I don't understand. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_multi_angle_face_learning()