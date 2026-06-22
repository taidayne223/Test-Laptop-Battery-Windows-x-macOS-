import psutil
import logging
import platform
import subprocess
import re

# Configure logging once at import time. basicConfig is a no-op if the root
# logger is already configured (e.g. by test.py), so this only acts as a
# fallback when get_battery_level is used standalone.
logging.basicConfig(
    filename='logfilename.log',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s | %(message)s'
)


def get_battery_level():
    battery = psutil.sensors_battery()
    if battery is None:
        log_string = 'Battery level: unavailable'
        print(log_string)
        logging.info(log_string)
        return

    percent = str(battery.percent)
    
    capacity_str = ""
    if platform.system() == "Darwin":
        try:
            res = subprocess.run(["ioreg", "-rn", "AppleSmartBattery"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout:
                m_curr = re.search(r'"AppleRawCurrentCapacity"\s*=\s*(\d+)', res.stdout)
                if not m_curr:
                    m_curr = re.search(r'"CurrentCapacity"\s*=\s*(\d+)', res.stdout)
                if m_curr:
                    capacity_str = f" | Capacity: {m_curr.group(1)} mAh"
        except Exception:
            pass

    log_string = f'Battery level: {percent}{capacity_str}'
    print(log_string)

    logging.info(log_string)
    
