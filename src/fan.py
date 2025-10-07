# src/fan.py
import time
import pigpio
import config

_pi = None
_initialized = False
_PWM_RANGE = 255  # 8-bit duty

def _percent_to_dc8(user_percent: int) -> int:
    sp = max(0, min(100, int(user_percent)))
    sink_percent = 100 - sp  # open-collector inversion
    return int(round(_PWM_RANGE * sink_percent / 100.0))

def init():
    global _pi, _initialized
    if _initialized:
        return
    _pi = pigpio.pi()
    if not _pi or not _pi.connected:
        raise RuntimeError("pigpio daemon not running. Start with: sudo systemctl start pigpiod")

    _pi.set_PWM_frequency(config.FAN_PWM, config.FAN_PWM_FREQ_HZ)
    _pi.set_PWM_range(config.FAN_PWM, _PWM_RANGE)
    _pi.set_PWM_dutycycle(config.FAN_PWM, _percent_to_dc8(0))  # start at user 0%
    _initialized = True

def set_percent(percent: int):
    if not _initialized:
        raise RuntimeError("fan.init() must be called before set_percent().")
    dc = _percent_to_dc8(percent)
    _pi.set_PWM_dutycycle(config.FAN_PWM, dc)
    if 0 < percent < 25:  # optional spin-up kick
        kick_dc = _percent_to_dc8(80)
        _pi.set_PWM_dutycycle(config.FAN_PWM, kick_dc)
        time.sleep(0.2)
        _pi.set_PWM_dutycycle(config.FAN_PWM, dc)

def stop(hold_percent: int = 0):
    global _pi, _initialized
    if _initialized and _pi:
        _pi.set_PWM_dutycycle(config.FAN_PWM, _percent_to_dc8(hold_percent))
        _pi.stop()
    _pi = None
    _initialized = False


