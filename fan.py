import RPi.GPIO as GPIO
from time import sleep
import config

# IMPORTANT: Use an NPN transistor + 5V pull-up on the FAN's PWM pin.
# This code just toggles the Pi pin. The hardware must present open-collector behavior to the fan.

_initialized = False

def init():
    global _initialized, _pwm
    if _initialized:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.FAN_PWM, GPIO.OUT)
    _pwm = GPIO.PWM(config.FAN_PWM, config.FAN_PWM_FREQ_HZ)
    _pwm.start(0)  # start at 0% duty
    _initialized = True

def set_percent(percent):
    """Clamp 0..100 and set PWM duty cycle."""
    if percent < 0: percent = 0
    if percent > 100: percent = 100
    _pwm.ChangeDutyCycle(percent)

def stop():
    try:
        _pwm.ChangeDutyCycle(0)
        _pwm.stop()
    except:
        pass
    GPIO.cleanup(config.FAN_PWM)
