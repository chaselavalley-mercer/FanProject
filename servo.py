import RPi.GPIO as GPIO
import config

_initialized = False
_pwm = None
_current_deg = config.SERVO_HOME_DEG

def _deg_to_duty(deg):
    # Map 0..180 deg -> 2.5..12.5% duty (approx 0.5..2.5 ms at 50 Hz)
    if deg < config.SERVO_MIN_DEG: deg = config.SERVO_MIN_DEG
    if deg > config.SERVO_MAX_DEG: deg = config.SERVO_MAX_DEG
    duty = 2.5 + (deg / 180.0) * 10.0
    return duty, deg

def init():
    global _initialized, _pwm, _current_deg
    if _initialized:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.SERVO_PWM, GPIO.OUT)
    _pwm = GPIO.PWM(config.SERVO_PWM, config.SERVO_FREQ_HZ)
    _pwm.start(0)
    set_deg(config.SERVO_HOME_DEG)
    _initialized = True

def set_deg(deg):
    global _current_deg
    duty, clamped = _deg_to_duty(deg)
    _pwm.ChangeDutyCycle(duty)
    _current_deg = clamped

def nudge_left(step=config.SERVO_STEP_DEG):
    set_deg(_current_deg - step)

def nudge_right(step=config.SERVO_STEP_DEG):
    set_deg(_current_deg + step)

def get_deg():
    return _current_deg

def stop():
    try:
        _pwm.ChangeDutyCycle(0)
        _pwm.stop()
    except:
        pass
    GPIO.cleanup(config.SERVO_PWM)
