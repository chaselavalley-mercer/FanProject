import cv2
import src.config as config

# >>> ADD: picamera2 import <<<
from picamera2 import Picamera2
import numpy as np

_cap = None
_cascade = None

def init():
    global _cap, _cascade
    # >>> CHANGE: use Picamera2 instead of VideoCapture <<<
    _cap = Picamera2()
    _cap.configure(_cap.create_preview_configuration(
        main={"size": (config.FRAME_W, config.FRAME_H), "format": "RGB888"}))
    _cap.start()

    # Keep your existing cascade line if you like cv2.data:
    # _cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # If you already placed the XML in your project, you can also use:
    # from pathlib import Path
    # cascade_path = Path(__file__).resolve().parent / "assets" / "haarcascades" / "haarcascade_frontalface_default.xml"
    # _cascade = cv2.CascadeClassifier(str(cascade_path))

    _cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def step():
    """
    Returns (dx, frame, face_box)
    dx = -1 (face left => move left), 0 (within zone or no face), +1 (face right)
    """
    # >>> CHANGE: grab a frame from Picamera2 (RGB), convert to BGR for OpenCV <<<
    rgb = _cap.capture_array()          # shape (H, W, 3), RGB888
    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = _cascade.detectMultiScale(gray, 1.2, 5, minSize=(60,60))

    dx = 0
    box = None
    if len(faces) > 0:
        x,y,w,h = max(faces, key=lambda b: b[2]*b[3])  # largest face
        cx = x + w//2
        center = config.FRAME_W // 2
        box = (x,y,w,h)
        offset = cx - center
        if abs(offset) > config.FACE_ZONE_PX:
            dx = -1 if offset < 0 else +1
    return dx, frame, box

def close():
    try:
        # >>> CHANGE: stop Picamera2 instead of cap.release <<<
        if _cap is not None:
            _cap.stop()
    except:
        pass
    cv2.destroyAllWindows()


