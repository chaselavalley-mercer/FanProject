# ============================================
# src/camera_track.py — simple detect + compare
# ============================================

import time
import cv2
from picamera2 import Picamera2
import config

# Camera & detector handles
_cap = None
_cascade = None

# --- minimal helper: clamp box into frame
def _clip_box(b, w, h):
    x, y, ww, hh = [int(v) for v in b]
    x  = max(0, min(x,  w - 1))
    y  = max(0, min(y,  h - 1))
    ww = max(1, min(ww, w - x))
    hh = max(1, min(hh, h - y))
    return (x, y, ww, hh)

# --- prefer larger & more centered face
def _score_face(b, w):
    x, y, ww, hh = b
    cx = x + 0.5 * ww
    size = ww * hh
    center = 0.5 * w
    lam = 1.5  # center weight
    return size - lam * abs(cx - center)

# --- optional contrast equalization for Haar
def _maybe_clahe(gray):
    if not getattr(config, "USE_CLAHE", True):
        return gray
    clip = getattr(config, "CLAHE_CLIP", 2.0)
    tile = getattr(config, "CLAHE_TILE", (8, 8))
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=tile)
    return clahe.apply(gray)

# ------------------------------------------------
# init(): camera + cascade
# ------------------------------------------------
def init():
    global _cap, _cascade
    _cap = Picamera2()
    _cap.configure(_cap.create_preview_configuration(
        main={
            "size":   (config.FRAME_W, config.FRAME_H),
            "format": getattr(config, "CAM_FORMAT", "RGB888")
        }
    ))
    _cap.start()
    time.sleep(0.2)

    # Face cascade
    path = getattr(config, "CASCADE_PATH", None)
    if path:
        _cascade = cv2.CascadeClassifier(str(path))
    else:
        _cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        )

# ------------------------------------------------
# step(): detect face -> compare to deadzone -> dx
# ------------------------------------------------
def step():
    """
    Returns:
      dx:  -1 (face left of deadzone) / 0 (inside) / +1 (right of deadzone)
      frame: BGR image with HUD drawn
      face_box: (x,y,w,h) or None
    """
    # grab frame (RGB from Picamera2) -> BGR for OpenCV
    rgb = _cap.capture_array()
    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    h, w = frame.shape[:2]

    # constants from config
    DETECT_SCALE   = config.DETECT_SCALE
    DETECT_NEIGHB  = config.DETECT_NEIGHB
    DETECT_MINSIZE = config.DETECT_MINSIZE

    DEADZONE_PX    = config.FACE_ZONE_PX
    HYST_MARGIN_PX = config.FACE_HYST_MARGIN_PX

    # 1) detect faces this frame (no skipping, no counters)
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray  = _maybe_clahe(gray)
    faces = _cascade.detectMultiScale(gray, DETECT_SCALE, DETECT_NEIGHB, minSize=DETECT_MINSIZE)

    box = None
    if len(faces) > 0:
        # pick best (big + centered)
        cand = max(faces, key=lambda b: _score_face(b, w))
        box  = _clip_box(cand, w, h)

    # 2) compute dx from horizontal offset vs deadzone
    dx = 0
    if box is not None:
        x, y, ww, hh = box
        cx_face  = x + 0.5 * ww              # face center x
        cx_frame = 0.5 * w                   # image center x
        offset   = cx_face - cx_frame        # signed px (left negative, right positive)
        threshold = DEADZONE_PX + HYST_MARGIN_PX

        # decide: outside deadzone -> move
        if offset < -threshold:
            dx = -1
        elif offset > threshold:
            dx = +1
        else:
            dx = 0

        # 3) HUD: show center, deadzone, current face x and threshold
        # center line
        cv2.line(frame, (int(cx_frame), 0), (int(cx_frame), h), (255, 255, 255), 1)
        # deadzone rectangle
        dz = int(DEADZONE_PX)
        cv2.rectangle(frame, (int(cx_frame - dz), 0), (int(cx_frame + dz), h), (80, 80, 80), 1)
        # face box
        cv2.rectangle(frame, (x, y), (x + ww, y + hh), (0, 255, 0), 2)
        # text: show current x and threshold edges
        left_edge  = cx_frame - threshold
        right_edge = cx_frame + threshold
        hud = f"cx_face={cx_face:.0f}  center={cx_frame:.0f}  thr=[{left_edge:.0f},{right_edge:.0f}]  dx={dx}"
        cv2.putText(frame, hud, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)
    else:
        # no face this frame -> dx=0, draw center/deadzone only
        cx_frame = 0.5 * w
        dz = int(DEADZONE_PX)
        cv2.line(frame, (int(cx_frame), 0), (int(cx_frame), h), (255, 255, 255), 1)
        cv2.rectangle(frame, (int(cx_frame - dz), 0), (int(cx_frame + dz), h), (80, 80, 80), 1)
        cv2.putText(frame, "no face", (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

    return dx, frame, box

# ------------------------------------------------
# close(): stop camera
# ------------------------------------------------
def close():
    global _cap
    try:
        if _cap:
            _cap.stop()
    finally:
        _cap = None


