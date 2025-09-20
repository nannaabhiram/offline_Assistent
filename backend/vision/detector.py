import os
import time
import threading
from typing import List, Tuple, Callable

import cv2
import numpy as np
import platform
try:
    import msvcrt  # Windows console key capture
except Exception:
    msvcrt = None
from ultralytics import YOLO

# YOLOv11 model expected under project_root/models/, e.g. 'yolo11n.pt' or 'yolo11s.pt'.
# If multiple are present, the first match in the PREFERRED_WEIGHTS order is used.
PREFERRED_WEIGHTS = [
    "yolo11s.pt",  # good balance
    "yolo11n.pt",  # fastest, smallest
    "yolo11m.pt",
    "yolo11l.pt",
    "yolo11x.pt",
]


class VisionDetector:
    def __init__(self, models_dir: str, speak: Callable[[str], None] = print,
                 conf_threshold: float = 0.5, announce_interval: float = 2.0,
                 show_window: bool = True):
        self.models_dir = models_dir
        self.speak = speak
        self.conf_threshold = conf_threshold
        self.announce_interval = announce_interval
        self.show_window = show_window
        self.model: YOLO | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._running = threading.Event()
        self._last_announced: dict[str, float] = {}
        self._weights_path: str | None = None

    def available(self) -> Tuple[bool, str]:
        for fname in PREFERRED_WEIGHTS:
            path = os.path.join(self.models_dir, fname)
            if os.path.exists(path):
                self._weights_path = path
                return True, f"found {fname}"
        return False, (
            "Missing YOLOv11 weights. Please place one of "
            + ", ".join(PREFERRED_WEIGHTS)
            + f" in {self.models_dir}."
        )
        return True, "ready"

    def _load(self):
        ok, msg = self.available()
        if not ok:
            raise FileNotFoundError(msg)
        self.model = YOLO(self._weights_path)

    def is_running(self) -> bool:
        return self._running.is_set()

    def start(self, camera_index: int = 0):
        if self.is_running():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, args=(camera_index,), daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._running.clear()

    def _run(self, camera_index: int):
        try:
            self._load()
        except Exception as e:
            self.speak(f"Vision error: {e}")
            return
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            self.speak("Cannot access camera. Check permissions or camera index.")
            return
        self._running.set()
        self.speak("Vision (YOLO) started. I am watching.")
        try:
            while not self._stop.is_set():
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.05)
                    continue
                detections = self.detect(frame)
                # Draw boxes if window is enabled
                if self.show_window:
                    for label, conf, (x1, y1, x2, y2) in detections:
                        color = (0, 255, 0) if label == "person" else (255, 0, 0)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(
                            frame,
                            f"{label}: {int(conf*100)}%",
                            (x1, max(20, y1-10)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            color,
                            2,
                        )
                    cv2.imshow("Assistant Vision - press 'q' to stop", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key in (27, ord('q')):  # ESC or q
                        self._stop.set()
                        break
                # Also listen for ESC/q from console (Windows only)
                if platform.system().lower() == 'windows' and msvcrt is not None:
                    try:
                        if msvcrt.kbhit():
                            ch = msvcrt.getch()
                            if ch in (b'\x1b', b'q', b'Q'):
                                self._stop.set()
                                break
                    except Exception:
                        pass
                # Speak newly observed prominent objects (debounced by announce_interval)
                now = time.time()
                said_any = False
                for label, conf, _ in detections:
                    if conf < max(0.6, self.conf_threshold):
                        continue
                    last = self._last_announced.get(label, 0)
                    if now - last >= self.announce_interval:
                        self.speak(f"I see {label}")
                        self._last_announced[label] = now
                        said_any = True
                # Slow down speaking to avoid chatter
                if not said_any:
                    time.sleep(0.05)
        finally:
            cap.release()
            self._running.clear()
            if self.show_window:
                try:
                    cv2.destroyWindow("Assistant Vision - press 'q' to stop")
                except Exception:
                    pass
            self.speak("Vision stopped.")

    def detect(self, frame) -> List[Tuple[str, float, Tuple[int, int, int, int]]]:
        if self.model is None:
            self._load()
        h, w = frame.shape[:2]
        # Run YOLO inference
        res = self.model.predict(frame, imgsz=640, verbose=False)[0]
        results: List[Tuple[str, float, Tuple[int, int, int, int]]] = []
        names = self.model.names if hasattr(self.model, 'names') else {}
        if res and res.boxes is not None:
            for box in res.boxes:
                conf = float(box.conf[0]) if box.conf is not None else 0.0
                if conf < self.conf_threshold:
                    continue
                cls_id = int(box.cls[0]) if box.cls is not None else -1
                label = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else str(cls_id)
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                # Clamp to frame size
                x1 = max(0, min(x1, w-1)); x2 = max(0, min(x2, w-1))
                y1 = max(0, min(y1, h-1)); y2 = max(0, min(y2, h-1))
                results.append((label, conf, (x1, y1, x2, y2)))
        return results


# Singleton-style helpers for the assistant
_detector: VisionDetector | None = None

def get_detector(project_root: str, speak: Callable[[str], None]):
    global _detector
    if _detector is None:
        models_dir = os.path.join(project_root, "models")
        _detector = VisionDetector(models_dir=models_dir, speak=speak)
    return _detector


def start_vision(project_root: str, speak: Callable[[str], None], camera_index: int = 0):
    det = get_detector(project_root, speak)
    det.start(camera_index)


def stop_vision(project_root: str, speak: Callable[[str], None]):
    det = get_detector(project_root, speak)
    det.stop()


def vision_running() -> bool:
    return _detector.is_running() if _detector else False


def describe_frame(project_root: str, speak: Callable[[str], None], top_k: int = 3):
    """Capture one frame and speak the most confident detections."""
    det = get_detector(project_root, speak)
    # Lazy load
    try:
        det._load()
    except Exception as e:
        speak(f"Vision error: {e}")
        return
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Cannot access camera.")
        return
    ok, frame = cap.read()
    cap.release()
    if not ok:
        speak("Failed to capture a frame.")
        return
    detections = det.detect(frame)
    if not detections:
        speak("I don't see any known objects.")
        return
    detections.sort(key=lambda x: x[1], reverse=True)
    names = []
    for label, conf, _ in detections[:top_k]:
        names.append(f"{label}")
    speak("I can see " + ", ".join(names))
