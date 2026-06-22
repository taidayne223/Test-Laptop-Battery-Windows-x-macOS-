import psutil
import logging
import platform
import subprocess
import re


def get_battery_level():
    logging.basicConfig(
        filename=f'logfilename.log',
        encoding='utf-8',
        level=logging.INFO,
        format='%(asctime)s | %(message)s'
    )

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
    
