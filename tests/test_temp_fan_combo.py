"""
DHT11 + PWM Fan Integration Test
--------------------------------
Reads temperature (°C) from DHT11 and maps it linearly to fan PWM:
    TEMP_MIN → PWM_FLOOR_PERCENT
    TEMP_MAX → PWM_CEIL_PERCENT

Usage:
    python3 tests/test_temp_fan_combo.py

Requires:
    - pigpio daemon running: sudo systemctl start pigpiod
    - pytest.ini with: [pytest] pythonpath = src
"""

import time
import signal

import config
import fan
import tach
import dht11_read  # your existing DHT11 reader module in src/

RUN = True

def _handle_sigint(sig, frame):
    """Allow Ctrl+C to exit cleanly."""
    global RUN
    RUN = False

def temp_to_percent(t_c: float) -> int:
    """Linear map from temperature (°C) to PWM percent using config thresholds."""
    # Clamp and map
    if t_c <= config.TEMP_MIN:
        return int(config.PWM_FLOOR_PERCENT)
    if t_c >= config.TEMP_MAX:
        return int(config.PWM_CEIL_PERCENT)
    span = config.TEMP_MAX - config.TEMP_MIN
    frac = (t_c - config.TEMP_MIN) / span if span > 0 else 1.0
    pct = config.PWM_FLOOR_PERCENT + frac * (config.PWM_CEIL_PERCENT - config.PWM_FLOOR_PERCENT)
    return int(round(max(0, min(100, pct))))

def main():
    signal.signal(signal.SIGINT, _handle_sigint)

    # Init subsystems (tach optional if not wired yet)
    fan.init()
    tach_inited = False
    try:
        tach.init()
        tach_inited = True
    except Exception as e:
        print(f"(tach init skipped: {e})")

    print(f"Temp→Fan test running. {config.TEMP_MIN:.1f}°C → {config.PWM_FLOOR_PERCENT}%   "
          f"{config.TEMP_MAX:.1f}°C → {config.PWM_CEIL_PERCENT}%. Ctrl+C to exit.")

    try:
        while RUN:
            try:
                t_c = dht11_read.read_temp_c()  # must raise on failure or return float('nan')
                if t_c != t_c:  # NaN check
                    raise ValueError("NaN temperature reading")
                pct = temp_to_percent(t_c)
                fan.set_percent(pct)
                if tach_inited:
                    rpm = tach.read_rpm(0.3)  # short sample window for responsiveness
                    print(f"T = {t_c:4.1f} °C | Fan = {pct:3d}% | ≈ {rpm:4d} RPM")
                else:
                    print(f"T = {t_c:4.1f} °C | Fan = {pct:3d}%")
            except Exception as e:
                # Keep previous PWM if sensor glitches
                print(f"DHT11 read failed; keeping last fan setting. ({e})")
            time.sleep(1.0)
    finally:
        try:
            if tach_inited:
                tach.close()
        finally:
            fan.stop(hold_percent=0)

if __name__ == "__main__":
    main()

