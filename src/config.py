# src/config.py
from pathlib import Path

# Project paths
# config.py is in FanProject/src/config.py  -> project root is two parents up from this file
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
HAAR_CASCADE_PATH = ASSETS_DIR / "haarcascades.xml"   # <-- your file

# Fan control (pigpio; open-collector)
FAN_PWM = 18
FAN_PWM_FREQ_HZ = 25000

# Tachometer
FAN_TACH = 23
PULSES_PER_REV = 2
TACH_GLITCH_FILTER_US = 50

# DHT11
DHT_GPIO = 4

# Temp → PWM mapping
TEMP_MIN = 24.0
TEMP_MAX = 34.0
PWM_FLOOR_PERCENT = 0
PWM_CEIL_PERCENT  = 100

# ---- Face tracking (detect -> track) ----
# Cascade detection cadence & thresholds
DETECT_SCALE      = 1.1      # Haar scaleFactor (smaller => slower, more sensitive)
DETECT_NEIGHB     = 5        # Haar minNeighbors (higher => fewer false positives)
DETECT_MINSIZE    = (60, 60) # Smallest face to consider (px)
DETECT_EVERY_N    = 3        # Run Haar every N frames while UNLOCKED

# Lock/unlock behavior
FACE_LOCK_FRAMES  = 3        # Require N consecutive detections to lock
FACE_LOST_FRAMES  = 8        # Tracker failures before we declare lost/unlock

# Smoothing & servo-chatter control
FACE_EMA_ALPHA        = 0.35 # 0..1; higher reacts faster, lower is smoother
FACE_HYST_MARGIN_PX   = 10   # Extra margin outside FACE_ZONE_PX before nudging
FACE_CMD_COOLDOWN_S   = 0.08 # Min seconds between non-zero dx commands

# Optional: preview overlay/diagnostics
SHOW_LOCK_STATE   = True     # If your preview drawer shows "LOCKED/SEARCH"
