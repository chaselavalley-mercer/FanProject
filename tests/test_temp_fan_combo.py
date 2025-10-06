# tests/test_temp_fan_combo.py
# Run from repo root:  python3 tests/test_temp_fan_combo.py

import sys, pathlib, time
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import config
import fan
import dht11_read
import tach

def temp_to_percent(t):
    if t <= config.TEMP_MIN:
        return 0
    if t >= config.TEMP_MAX:
        return config.PWM_CEIL_PERCENT
    frac = (t - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)
    return int(config.PWM_FLOOR_PERCENT + frac * (config.PWM_CEIL_PERCENT - config.PWM_FLOOR_PERCENT))

# --- init ---
fan.init()
tach.init()

print("Temp+Fan test running. Reads DHT11 and sets fan PWM accordingly. Ctrl+C to exit.")
print(f"Mapping: {config.TEMP_MIN:.1f}°C → 0%   {config.TEMP_MAX:.1f}°C → 100%")

try:
    while True:
        try:
            t_c = dht11_read.read_temp_c()
            pct = temp_to_percent(t_c)
            fan.set_percent(pct)
            rpm = tach.read_rpm(0.3)
            print(f"T={t_c:.1f}°C  →  Fan={pct:3d}%   ~{rpm} RPM")
        except Exception as e:
            print("DHT11 read failed; keeping last fan setting.", e)
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
finally:
    try: fan.stop()
    except: pass
    try: tach.close()
    except: pass
