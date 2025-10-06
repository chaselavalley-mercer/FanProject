"""
DHT11 + PWM Fan Integration Test
---------------------------------
Reads temperature (°C) from DHT11 and maps it linearly to fan PWM:
    TEMP_MIN → 0%   ...   TEMP_MAX → 100%

Usage:
    python3 tests/test_temp_fan_combo.py

Notes:
    - DHT11 data pin on GPIO4 (per config).
    - Fan PWM on GPIO18 via NPN open-collector with 5 V pull-up on the fan side.
    - Tach input on GPIO23 with 3.3 V pull-up only.
"""

import sys
import pathlib
import time
import signal

# Allow "import config, fan, dht11_read, tach" from project root
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import config
import fan
import dht11_read
import tach

RUN = True

def _handle_sigint(sig, frame):
    """Allow Ctrl+C to exit cleanly."""
    global RUN
    RUN = False

def temp_to_percent(t_c: float) -> int:
    """Linear map from temperature (°C) to PWM percent using config thresholds."""
    if t_c <= config.TEMP_MIN:
        return 0
    if t_c >= config.TEMP_MAX:
        return config.PWM_CEIL_PERCENT
    frac = (t_c - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)
    return int(config.PWM_FLOOR_PERCENT + frac * (config.PWM_CEIL_PERCENT - config.PWM_FLOOR_PERCENT))

def main():
    signal.signal(signal.SIGINT, _handle_sigint)

    fan.init()
    tach.init()

    print(f"Temp+Fan test: {config.TEMP_MIN:.1f}°C → 0%   {config.TEMP_MAX:.1f}°C → 100%. Ctrl+C to exit.")

    try:
        while RUN:
            try:
                t_c = dht11_read.read_temp_c()
                pct = temp_to_percent(t_c)
                fan.set_percent(pct)
                rpm = tach.read_rpm(0.3)  # short sample window for responsiveness
                print(f"T = {t_c:4.1f} °C | Fan = {pct:3d}% | ≈ {rpm:4d} RPM")
            except Exception as e:
                # Keep previous PWM if sensor glitches
                print("DHT11 read failed; keeping last fan setting.", e)
            time.sleep(1.0)
    finally:
        try:
            fan.stop()
        finally:
            tach.close()

if __name__ == "__main__":
    main()
