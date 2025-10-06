import RPi.GPIO as GPIO
from time import sleep, time
import config

# Simple pulse counter using interrupt callback
_pulse_count = 0
_initialized = False

def _on_falling(channel):
    global _pulse_count
    _pulse_count += 1

def init():
    global _initialized
    if _initialized:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.FAN_TACH, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 3.3V pull-up
    GPIO.add_event_detect(config.FAN_TACH, GPIO.FALLING, callback=_on_falling, bouncetime=1)
    _initialized = True

def read_rpm(sample_time=0.5):
    """Count pulses for sample_time seconds and convert to RPM."""
    global _pulse_count
    _pulse_count = 0
    start = time()
    sleep(sample_time)
    pulses = _pulse_count
    freq = pulses / sample_time                 # pulses/sec
    rps = freq / config.PULSES_PER_REV
    rpm = rps * 60.0
    return int(rpm)

def close():
    try:
        GPIO.remove_event_detect(config.FAN_TACH)
    except:
        pass
    GPIO.cleanup(config.FAN_TACH)
