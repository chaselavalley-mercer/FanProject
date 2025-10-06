import cv2
from pathlib import Path
import config

_cap = None
_cascade = None

def _cascade_path():
    """
    Prefer a project-local cascade:
      assets/haarcascades/haarcascade_frontalface_default.xml
    Fallback to cv2.data.haarcascades if available.
    """
    local = (
        Path(__file__).resolve().parent
        / "assets"
        / "haarcascades"
        / "haarcascade_frontalface_default.xml"
    )
    if local.exists():
        return str(local)

    # Fallback: use cv2.data if this OpenCV build exposes it
    haar_base = getattr(getattr(cv2, "data", None), "haarcascades", None)
    if haar_base:
        return str(Path(haar_base) / "haarcascade_frontalface_default.xml")

    # If we get here, we couldn't find the file
    raise RuntimeError(
        "Haar cascade not found.\n"
        "Put it at: assets/haarcascades/haarcascade_frontalface_default.xml"
    )

def init():
    global _cap, _cascade
    _cap = cv2.VideoCapture(0)
    _cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_W)
    _cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_H)

    cascade_path = _cascade_path()
    _cascade = cv2.CascadeClassifier(cascade_path)
    if _cascade.empty():
        raise RuntimeError(f"Failed to load Haar cascade from: {cascade_path}")

def step():
    """
    Returns (dx, frame, face_box)
    dx = -1 (face left => move left), 0 (within zone or no face), +1 (face right)
    """
    if _cap is None or _cascade is None:
        # Not initialized
        return 0, None, None

    ok, frame = _cap.read()
    if not ok or frame is None:
        return 0, None, None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = _cascade.detectMultiScale(gray, 1.2, 5, minSize=(60,60))

    dx = 0
    box = None
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda b: b[2]*b[3])  # largest face
        cx = x + w // 2
        center = config.FRAME_W // 2
        box = (x, y, w, h)
        offset = cx - center
        if abs(offset) > config.FACE_ZONE_PX:
            dx = -1 if offset < 0 else +1
    return dx, frame, box

def close():
    try:
        if _cap is not None:
            _cap.release()
    finally:
        cv2.destroyAllWindows()

