# tests/test_fan.py
# Interactive fan tester: type a percentage; it sets duty and (optionally) prints RPM via tach.py.
# Run: python tests/test_fan.py
# Ensure: sudo systemctl start pigpiod

import sys
from fan import init as fan_init, set_percent, stop as fan_stop
# If tach hardware is wired, uncomment the next two lines to show RPM after each change:
from tach import init as tach_init, read_rpm, close as tach_close

def main():
    fan_init()
    try:
        # Comment out the next line if you don't have the tach wired yet
        tach_init()
    except Exception as e:
        print(f"(tach init skipped: {e})")

    print("Enter 0–100 (0=stop, 100=max). 'q' to quit.")
    try:
        while True:
            s = input("Speed %: ").strip().lower()
            if s in ("q", "quit", "exit"):
                break
            try:
                p = int(s)
            except ValueError:
                print("Enter an integer 0–100.")
                continue
            p = max(0, min(100, p))
            set_percent(p)
            # If tach is available, show a quick RPM sample
            try:
                rpm = read_rpm(0.5)
                print(f"Set fan: {p}%  |  RPM ≈ {rpm}")
            except Exception:
                print(f"Set fan: {p}%")
    except KeyboardInterrupt:
        pass
    finally:
        try:
            tach_close()
        except Exception:
            pass
        fan_stop(hold_percent=0)

if __name__ == "__main__":
    sys.exit(main())
