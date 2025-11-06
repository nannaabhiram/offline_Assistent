#!/usr/bin/env python3
"""
Advanced Face Analysis Module for Visual AI Assistant
Provides comprehensive face detection, emotion analysis, and recognition capabilities
"""

import cv2
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
import json
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize variables at module level
MEDIAPIPE_AVAILABLE = False
DLIB_AVAILABLE = False
mp = None
dlib = None

# Try to import mediapipe, but make it optional
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    mp = None
    MEDIAPIPE_AVAILABLE = False
except Exception as e:
    mp = None
    MEDIAPIPE_AVAILABLE = False

# Try to import dlib for better face detection
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    dlib = None
    DLIB_AVAILABLE = False
except Exception as e:
    dlib = None
    DLIB_AVAILABLE = False

class FaceAnalyzer:
    def __init__(self):
        """Initialize face analysis components"""
        self.cap = None
        self.is_active = False

        # Initialize available solutions
        if globals().get('MEDIAPIPE_AVAILABLE', False) and globals().get('mp') is not None:
            try:
                mp_module = globals().get('mp')
                self.mp_face_detection = mp_module.solutions.face_detection
                self.mp_face_mesh = mp_module.solutions.face_mesh

                # Initialize MediaPipe solutions
                self.face_detection = self.mp_face_detection.FaceDetection(
                    model_selection=1,  # Use full range model for better accuracy
                    min_detection_confidence=0.5
                )
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
            except Exception as e:
                print(f"Error initializing MediaPipe: {e}")
                globals()['MEDIAPIPE_AVAILABLE'] = False

        # Try to load OpenCV's built-in face detector
        self.face_cascade = None
        if hasattr(cv2, 'data'):
            try:
                # Try to use OpenCV's Haar cascades
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if os.path.exists(cascade_path):
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception:
                pass

        # Emotion detection variables
        self.emotion_model = None
        self.age_gender_model = None

    def start_camera(self, camera_id: int = 0) -> bool:
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(camera_id)
            if not self.cap.isOpened():
                return False

            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            self.is_active = True
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        """Stop camera capture"""
        if self.cap:
            self.cap.release()
        self.is_active = False
        cv2.destroyAllWindows()

    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame from camera"""
        if not self.is_active or not self.cap:
            return None

        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces in frame using available methods"""
        try:
            faces = []

            # Try MediaPipe first if available
            if globals().get('MEDIAPIPE_AVAILABLE', False) and globals().get('mp') is not None and hasattr(self, 'face_detection'):
                try:
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Process frame
                    results = self.face_detection.process(rgb_frame)

                    if results.detections:
                        for detection in results.detections:
                            # Get bounding box
                            bboxC = detection.location_data.relative_bounding_box
                            ih, iw, _ = frame.shape

                            x = int(bboxC.xmin * iw)
                            y = int(bboxC.ymin * ih)
                            w = int(bboxC.width * iw)
                            h = int(bboxC.height * ih)

                            # Ensure coordinates are within frame bounds
                            x = max(0, x)
                            y = max(0, y)
                            w = min(w, iw - x)
                            h = min(h, ih - y)

                            faces.append({
                                'bbox': (x, y, w, h),
                                'confidence': detection.score[0],
                                'frame': frame[y:y+h, x:x+w] if h > 0 and w > 0 else None
                            })
                except Exception as e:
                    print(f"MediaPipe detection error: {e}")

            # Fallback to OpenCV Haar cascades if MediaPipe failed or unavailable
            if not faces and self.face_cascade is not None:
                try:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    detected_faces = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )

                    for (x, y, w, h) in detected_faces:
                        faces.append({
                            'bbox': (x, y, w, h),
                            'confidence': 0.8,  # Default confidence for Haar cascades
                            'frame': frame[y:y+h, x:x+w] if h > 0 and w > 0 else None
                        })

                except Exception as e:
                    print(f"OpenCV detection error: {e}")

            # If no face detection methods worked, try simple motion detection
            if not faces:
                try:
                    # Simple brightness-based detection as last resort
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    brightness = np.mean(gray)

                    # If frame is reasonably bright, assume there's a face
                    if brightness > 50:
                        # Center of frame as approximate face location
                        h, w = frame.shape[:2]
                        face_w, face_h = int(w * 0.3), int(h * 0.4)
                        x, y = (w - face_w) // 2, (h - face_h) // 2

                        faces.append({
                            'bbox': (x, y, face_w, face_h),
                            'confidence': 0.3,  # Low confidence for fallback method
                            'frame': frame[y:y+face_h, x:x+face_w] if face_h > 0 and face_w > 0 else None,
                            'method': 'brightness_fallback'
                        })
                except Exception:
                    pass

            return faces

        except Exception as e:
            print(f"Error in face detection: {e}")
            return []

    def analyze_emotion(self, face_image: np.ndarray) -> Dict:
        """Analyze emotion from face image (simplified version)"""
        try:
            # This is a simplified emotion detection
            # In a real implementation, you'd use a trained model

            # Analyze image characteristics for basic emotion detection
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

            # Simple emotion detection based on facial features
            # This is a placeholder - real implementation needs ML model

            height, width = gray.shape

            # Analyze different regions
            eyes_region = gray[height//4:height//2, width//4:3*width//4]
            mouth_region = gray[height//2:3*height//4, width//3:2*width//3]

            # Simple heuristics (this would be replaced with actual ML model)
            eye_darkness = np.mean(eyes_region) if eyes_region.size > 0 else 128
            mouth_brightness = np.mean(mouth_region) if mouth_region.size > 0 else 128

            # Very basic emotion detection
            if mouth_brightness > 140:  # Bright mouth = smiling
                emotion = "happy"
                confidence = 0.8
            elif eye_darkness < 80:  # Dark eyes = possibly tired/sad
                emotion = "sad"
                confidence = 0.7
            else:
                emotion = "neutral"
                confidence = 0.9

            return {
                'emotion': emotion,
                'confidence': confidence,
                'brightness': int(mouth_brightness),
                'eye_darkness': int(eye_darkness)
            }

        except Exception as e:
            return {'emotion': 'unknown', 'confidence': 0.0, 'error': str(e)}

    def analyze_age_gender(self, face_image: np.ndarray) -> Dict:
        """Analyze age and gender (simplified version)"""
        try:
            # This is a simplified implementation
            # Real version would use a trained CNN model

            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape

            # Simple age estimation based on skin texture and face shape
            # This is very basic and would need a proper ML model

            # Analyze skin texture (wrinkles = older)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Simple heuristics
            if laplacian_var > 500:  # High texture variance = older
                age_range = "adult"
                age_confidence = 0.6
            elif laplacian_var > 200:
                age_range = "young_adult"
                age_confidence = 0.7
            else:
                age_range = "teen"
                age_confidence = 0.5

            # Very basic gender detection (face shape)
            # This is highly inaccurate and needs proper ML model
            aspect_ratio = width / height

            if aspect_ratio > 0.8:  # Wider face = possibly male
                gender = "male"
                gender_confidence = 0.6
            else:
                gender = "female"
                gender_confidence = 0.6

            return {
                'age_range': age_range,
                'age_confidence': age_confidence,
                'gender': gender,
                'gender_confidence': gender_confidence
            }

        except Exception as e:
            return {
                'age_range': 'unknown',
                'age_confidence': 0.0,
                'gender': 'unknown',
                'gender_confidence': 0.0,
                'error': str(e)
            }

    def check_liveness(self, frame: np.ndarray, face_bbox: Tuple) -> Dict:
        """Check if detected face is real (not photo/spoof)"""
        try:
            x, y, w, h = face_bbox

            # Simple liveness detection based on movement and texture
            # Real implementation would need more sophisticated methods

            if w > 0 and h > 0:
                face_roi = frame[y:y+h, x:x+w]
                gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

                # Check texture variance (photos usually have less texture)
                texture_var = cv2.Laplacian(gray, cv2.CV_64F).var()

                # Simple movement detection (would need frame comparison in real implementation)
                brightness = np.mean(gray)

                # Basic heuristics
                if texture_var > 100 and brightness > 50:  # Good texture and brightness
                    liveness = "real"
                    confidence = 0.7
                else:
                    liveness = "uncertain"
                    confidence = 0.4

                return {
                    'liveness': liveness,
                    'confidence': confidence,
                    'texture_variance': texture_var,
                    'brightness': brightness
                }

        except Exception as e:
            pass

        return {'liveness': 'unknown', 'confidence': 0.0}

    def analyze_face(self, frame: np.ndarray) -> Dict:
        """Complete face analysis"""
        try:
            faces = self.detect_faces(frame)

            if not faces:
                return {
                    'faces_detected': 0,
                    'analysis': []
                }

            analysis_results = []

            for face in faces:
                x, y, w, h = face['bbox']
                face_image = face.get('frame')

                if face_image is None or face_image.size == 0:
                    continue

                # Perform all analyses
                emotion = self.analyze_emotion(face_image)
                age_gender = self.analyze_age_gender(face_image)
                liveness = self.check_liveness(frame, (x, y, w, h))

                face_analysis = {
                    'bbox': (x, y, w, h),
                    'confidence': face['confidence'],
                    'emotion': emotion,
                    'age_gender': age_gender,
                    'liveness': liveness,
                    'timestamp': time.time()
                }

                analysis_results.append(face_analysis)

            return {
                'faces_detected': len(faces),
                'analysis': analysis_results,
                'frame_shape': frame.shape
            }

        except Exception as e:
            return {
                'faces_detected': 0,
                'analysis': [],
                'error': str(e)
            }

    def get_live_analysis(self) -> Dict:
        """Get real-time face analysis"""
        frame = self.capture_frame()
        if frame is not None:
            return self.analyze_face(frame)
        return {'faces_detected': 0, 'analysis': []}

# Global analyzer instance - initialize after imports
face_analyzer = None

# Initialize after all imports are complete
try:
    face_analyzer = FaceAnalyzer()
except Exception as e:
    print(f"Error initializing face analyzer: {e}")
    face_analyzer = None

def start_face_analysis(camera_id: int = 0) -> bool:
    """Start face analysis system"""
    if face_analyzer is None:
        return False
    return face_analyzer.start_camera(camera_id)

def stop_face_analysis():
    """Stop face analysis system"""
    if face_analyzer is not None:
        face_analyzer.stop_camera()

def get_current_analysis() -> Dict:
    """Get current face analysis"""
    if face_analyzer is None:
        return {'faces_detected': 0, 'analysis': []}
    return face_analyzer.get_live_analysis()

def detect_user_mood() -> str:
    """Detect current user mood for assistant response"""
    try:
        analysis = get_current_analysis()

        if analysis.get('faces_detected', 0) == 0:
            return "no_face"

        face = analysis['analysis'][0] if analysis['analysis'] else {}

        emotion = face.get('emotion', {}).get('emotion', 'neutral')
        confidence = face.get('emotion', {}).get('confidence', 0)

        # Only return emotion if confidence is reasonable
        if confidence > 0.4:
            return emotion

        return "neutral"

    except Exception as e:
        print(f"Error detecting mood: {e}")
        return "neutral"

if __name__ == "__main__":
    # Test the face analyzer
    print("Starting face analysis test...")

    if start_face_analysis():
        print("Camera started successfully!")

        for i in range(10):  # Test for 10 frames
            analysis = get_current_analysis()
            print(f"Frame {i}: {analysis.get('faces_detected', 0)} faces detected")
            time.sleep(1)

        stop_face_analysis()
        print("Test completed!")
    else:
        print("Failed to start camera!")
