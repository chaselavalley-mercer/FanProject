# BCM pin numbers
FAN_PWM = 18
FAN_TACH = 23
SERVO_PWM = 12
DHT11_PIN = 4

# Fan behavior
FAN_PWM_FREQ_HZ = 25000      # PC fans want ~25 kHz
PULSES_PER_REV = 2           # most 3/4-wire fans

# Temperature control (°C)
TEMP_MIN = 24.0              # fan off at/below this
TEMP_MAX = 30.0              # fan 100% at/above this
PWM_FLOOR_PERCENT = 0
PWM_CEIL_PERCENT  = 100

# Servo behavior
SERVO_FREQ_HZ = 50           # standard hobby servo
SERVO_MIN_DEG = 20           # clamp to your mount’s safe range
SERVO_MAX_DEG = 160
SERVO_HOME_DEG = 90
SERVO_STEP_DEG = 20          # move in 20° steps on each nudge

# Camera
FRAME_W = 640
FRAME_H = 480
FACE_ZONE_PX = 60            # +/- band around center; outside => nudge
SHOW_PREVIEW = True          # press 'q' to quit preview in tests
