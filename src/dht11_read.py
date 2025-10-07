import Adafruit_DHT as dht
import time
import src.config as config

_sensor = dht.DHT11

def read_temp_c(max_tries=5):
    """Return temperature C (float). Raises if it keeps failing."""
    for _ in range(max_tries):
        humidity, temperature = dht.read_retry(_sensor, config.DHT11_PIN)
        if temperature is not None:
            return float(temperature)
        time.sleep(0.2)
    raise RuntimeError("DHT11 read failed")
