# src/tach.py
# Tachometer reading via pigpio callbacks (counts falling edges).
# Hardware: fan tach (green) -> Pi GPIO with 10k pull-up to 3.3V, optional 1k series to Pi.
import time
import pigpio
import config

_pi = None
_cb = None
_initialized = False
_pulse_count = 0

def _on_edge(gpio, level, tick):
    # Count FALLING edges only (level == 0)
    global _pulse_count
    if level == 0:
        _pulse_count += 1

def init():
    """Initialize pigpio, configure tach pin as input, enable glitch filter, register callback."""
    global _pi, _cb, _initialized
    if _initialized:
        return
    _pi = pigpio.pi()
    if not _pi or not _pi.connected:
        raise RuntimeError("pigpio daemon not running. Start with: sudo systemctl start pigpiod")

    _pi.set_mode(config.FAN_TACH, pigpio.INPUT)
    # Redundant internal pull-up (still keep your external 10k to 3.3V in hardware)
    _pi.set_pull_up_down(config.FAN_TACH, pigpio.PUD_UP)
    # Filter out short spikes/noise
    if getattr(config, "TACH_GLITCH_FILTER_US", 0) > 0:
        _pi.set_glitch_filter(config.FAN_TACH, config.TACH_GLITCH_FILTER_US)

    _cb = _pi.callback(config.FAN_TACH, pigpio.FALLING_EDGE, _on_edge)
    _initialized = True

def read_rpm(sample_time: float = 0.5) -> int:
    """
    Block for sample_time seconds, count pulses, convert to RPM.
    RPM = (pulses / sample_time) / PULSES_PER_REV * 60
    """
    if not _initialized:
        raise RuntimeError("tach.init() must be called before read_rpm().")

    global _pulse_count
    _pulse_count = 0
    time.sleep(sample_time)
    pulses = _pulse_count

    freq_hz = pulses / sample_time
    rps = freq_hz / config.PULSES_PER_REV
    rpm = int(round(rps * 60.0))
    return rpm

def close():
    global _pi, _cb, _initialized
    try:
        if _cb:
            _cb.cancel()
    except Exception:
        pass
    if _pi:
        _pi.stop()
    _cb = None
    _pi = None
    _initialized = False