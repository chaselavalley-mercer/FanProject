import src.servo as servo
print("Servo: 'a' left 20°, 'd' right 20°, 'q' quit")
servo.init()
try:
    while True:
        c = input("> ").strip().lower()
        if c == 'a':
            servo.nudge_left()
        elif c == 'd':
            servo.nudge_right()
        elif c == 'q':
            break
finally:
    servo.stop()
