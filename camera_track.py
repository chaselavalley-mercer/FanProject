import cv2
import config

_cap = None
_cascade = None

def init():
    global _cap, _cascade
    _cap = cv2.VideoCapture(0)
    _cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_W)
    _cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_H)
    _cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def step():
    """
    Returns (dx, frame, face_box)
    dx = -1 (face left => move left), 0 (within zone or no face), +1 (face right)
    """
    ok, frame = _cap.read()
    if not ok:
        return 0, None, None

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
        _cap.release()
    except:
        pass
    cv2.destroyAllWindows()
