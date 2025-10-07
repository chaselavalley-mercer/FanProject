import cv2
import config

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

def _clip_box(b, w, h):
    x, y, ww, hh = [int(v) for v in b]
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))
    ww = max(1, min(ww, w - x))
    hh = max(1, min(hh, h - y))
    return (x, y, ww, hh)

def step():
    """
    Returns (dx, frame, face_box)
    dx = -1 (face left => move left), 0 (within zone or no face/rate-limit), +1 (face right)
    face_box = (x,y,w,h) or None
    """
    global _frame_idx, _tracker, _locked, _lock_count, _lost_count, _last_cx_ema, _last_cmd_ts

    # 1) Grab frame (RGB from Picamera2) -> BGR
    rgb = _cap.capture_array()
    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    h, w = frame.shape[:2]

    box = None
    have_box = False

    # 2) If locked, update tracker; otherwise (occasionally) detect to (re)lock
    if _locked and _tracker is not None:
        ok, bb = _tracker.update(frame)
        if ok:
            box = _clip_box(bb, w, h)
            _lost_count = 0
            have_box = True
        else:
            _lost_count += 1
            if _lost_count >= LOST_FRAMES:
                _locked = False
                _tracker = None
                _lock_count = 0
                _last_cx_ema = None

    if not _locked and (_frame_idx % DETECT_EVERY_N == 0):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = _cascade.detectMultiScale(gray, DETECT_SCALE, DETECT_NEIGHB, minSize=DETECT_MINSIZE)
        if len(faces) > 0:
            # largest face
            x, y, ww, hh = max(faces, key=lambda b: b[2] * b[3])
            box = _clip_box((x, y, ww, hh), w, h)
            _lock_count += 1
            if _lock_count >= LOCK_FRAMES:
                # MOSSE is light and stable on Pi Zero 2 W
                try:
                    _tracker = cv2.legacy.TrackerMOSSE_create()
                except AttributeError:
                    _tracker = cv2.TrackerMOSSE_create()
                _tracker.init(frame, tuple(box))
                _locked = True
                _lost_count = 0
                have_box = True
                _last_cx_ema = None
        else:
            _lock_count = 0

    _frame_idx += 1

    # 3) Convert box to dx with smoothing, hysteresis, and cooldown
    dx = 0
    if have_box and box is not None:
        x, y, ww, hh = box
        cx = x + 0.5 * ww
        center = 0.5 * w

        # EMA smoothing to reduce jitter
        if _last_cx_ema is None:
            _last_cx_ema = cx
        else:
            _last_cx_ema = (1.0 - EMA_ALPHA) * _last_cx_ema + EMA_ALPHA * cx

        offset = _last_cx_ema - center

        # Deadzone + hysteresis to avoid chattering near center
        if offset < -(DEADZONE_PX + HYST_MARGIN_PX):
            want = -1
        elif offset > (DEADZONE_PX + HYST_MARGIN_PX):
            want = +1
        else:
            want = 0

        # Command cooldown so servo doesn’t “buzz”
        now = time.time()
        if want != 0 and (now - _last_cmd_ts) >= CMD_COOLDOWN_S:
            dx = want
            _last_cmd_ts = now

    return dx, frame, box


def close():
    try:
        # >>> CHANGE: stop Picamera2 instead of cap.release <<<
        if _cap is not None:
            _cap.stop()
    except:
        pass
    cv2.destroyAllWindows()


