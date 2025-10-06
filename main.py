import time
import signal
import sys

import config
import fan
import tach
import servo
import dht11_read
import camera_track

_run = True
def _sigint(sig, frame):
    global _run
    _run = False

def temp_to_percent(t):
    if t <= config.TEMP_MIN:
        return 0
    if t >= config.TEMP_MAX:
        return config.PWM_CEIL_PERCENT
    # linear map between min and max
    frac = (t - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)
    return int(config.PWM_FLOOR_PERCENT + frac * (config.PWM_CEIL_PERCENT - config.PWM_FLOOR_PERCENT))

def main():
    signal.signal(signal.SIGINT, _sigint)

    # Init subsystems
    fan.init()
    tach.init()
    servo.init()
    camera_track.init()

    last_temp_t = 0
    last_tach_t = 0

    try:
        while _run:
            # 1) Camera step -> servo nudge if needed
            dx, frame, box = camera_track.step()
            if dx == -1:          # face is left of center
                servo.nudge_left()
            elif dx == +1:        # face is right of center
                servo.nudge_right()
            # else within zone or no face -> do nothing

            # Optional live preview for debugging
            if config.SHOW_PREVIEW and frame is not None:
                import cv2
                if box:
                    x,y,w,h = box
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                cv2.imshow("Smart Fan", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            now = time.time()

            # 2) Temp -> Fan PWM (about once per second)
            if now - last_temp_t > 1.0:
                try:
                    temp_c = dht11_read.read_temp_c()
                    pct = temp_to_percent(temp_c)
                    fan.set_percent(pct)
                    # print(f"T={temp_c:.1f}C -> {pct}%")
                except Exception as e:
                    # keep previous fan setting on read failure
                    # print("DHT error:", e)
                    pass
                last_temp_t = now

            # 3) Optional: read tach for logging (every ~2s)
            if now - last_tach_t > 2.0:
                rpm = tach.read_rpm(0.3)
                # print("RPM ~", rpm)
                last_tach_t = now

        # graceful exit
    finally:
        try: camera_track.close()
        except: pass
        try: servo.stop()
        except: pass
        try: fan.stop()
        except: pass
        try: tach.close()
        except: pass
        sys.exit(0)

if __name__ == "__main__":
    main()
