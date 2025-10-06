# tests/test_cam_servo_combo.py
# Run from repo root:  python3 tests/test_cam_servo_combo.py

import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import cv2
import config
import servo
import camera_track

# --- init ---
servo.init()
camera_track.init()

print("Camera+Servo test running. Center your face; move left/right to nudge the servo.")
print("Press 'q' in the preview window to exit.")

try:
    while True:
        dx, frame, box = camera_track.step()   # -1, 0, +1
        if dx == -1:
            servo.nudge_left()
        elif dx == +1:
            servo.nudge_right()

        if frame is not None and config.SHOW_PREVIEW:
            if box:
                x,y,w,h = box
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.imshow("Cam+Servo Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    try: camera_track.close()
    except: pass
    try: servo.stop()
    except: pass
    cv2.destroyAllWindows()
