import src.camera_track as camera_track
import src.config as config
import cv2

camera_track.init()
print("Camera preview. Press 'q' in the window to quit.")
try:
    while True:
        dx, frame, box = camera_track.step()
        if frame is None:
            continue
        if box:
            x,y,w,h = box
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow("Preview", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    camera_track.close()
