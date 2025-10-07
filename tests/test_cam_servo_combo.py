"""
Camera + Servo Integration Test
--------------------------------
Tracks the largest face in the frame. If the face center moves outside a
±FACE_ZONE_PX band around the image center, the servo nudges by SERVO_STEP_DEG.

Usage:
    python3 tests/test_cam_servo_combo.py

Controls:
    Press 'q' in the preview window to quit.
Notes:
    - Requires camera connected and enabled.
    - Ensure servo is powered from an external 6 V buck (≥2.5 A) and
      shares ground with the Raspberry Pi.
"""

import sys
import pathlib
import signal

# Allow "import config, servo, camera_track" from project root
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import cv2
import src.config as config
import src.servo as servo
import src.camera_track as camera_track

RUN = True

def _handle_sigint(sig, frame):
    """Allow Ctrl+C to exit cleanly."""
    global RUN
    RUN = False

def main():
    signal.signal(signal.SIGINT, _handle_sigint)

    # Initialize hardware subsystems
    servo.init()            # sets 50 Hz PWM and moves to SERVO_HOME_DEG
    camera_track.init()     # opens the camera and loads Haar cascade

    print("Cam+Servo test: move left/right; servo will nudge to re-center. 'q' to quit.")

    try:
        while RUN:
            dx, frame, box = camera_track.step()  # dx ∈ {-1, 0, +1}
            if dx == -1:
                servo.nudge_left()
            elif dx == +1:
                servo.nudge_right()
            # dx == 0 → within zone or no face → no movement

            if config.SHOW_PREVIEW and frame is not None:
                if box:
                    x, y, w, h = box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow("Cam+Servo Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        # Always release resources even on error/interrupt
        try:
            camera_track.close()
        finally:
            servo.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
