import pyautogui
import time
import threading
import os
import platform
import logging
import argparse
from datetime import datetime

from utils.battery_utils import get_battery_level
from utils.config import get_config
from test_cases.office_test import run_office_test
from test_cases.browser_test import run_browser_test
from test_cases.youtube_test import run_youtube_test


# Disable fail safe mechanism of Pyautogui
pyautogui.FAILSAFE = False

logging.basicConfig(
    filename=f'logfilename.log',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s | %(message)s'
)

def start_test(no_youtube='0'):
    logging.info('====================== Starting new test... ====================')
    if (no_youtube == '1'):
        youtube_message = 'YouTube test is disabled'
    else:
        youtube_message = 'YouTube test is enabled'

    print(youtube_message)
    logging.info(youtube_message)

    os_name = os.name
    platform_name = platform.system()

    print(f'Running on {os_name}, {platform_name}')
    get_battery_level()

    while True:
        run_browser_test()
        run_office_test()

        if str(no_youtube) != '1':
            run_youtube_test()


def calculate_elapsed_time(start_time):
    elapsed_time = datetime.now() - start_time
    print(f'Elapsed time: {elapsed_time}')

def information_process():
    config = get_config()
    battery_log_interval = config["reporting"]["battery_log_interval_seconds"]
    start_time = datetime.now()
    while True:
        get_battery_level()
        calculate_elapsed_time(start_time=start_time)
        time.sleep(battery_log_interval)

if __name__ == "__main__":
    from utils.system_setup import optimize_system
    optimize_system()

    parser=argparse.ArgumentParser(description="Run a script and measure battery life")
    parser.add_argument("no_youtube", nargs='?', choices=['1', '0'], default='0')

    args = parser.parse_args()

    # Start the battery info logging in a background daemon thread
    t2 = threading.Thread(target=information_process, daemon=True)
    t2.start()

    # Run the main test loop on the main thread to ensure proper GUI library compatibility
    start_test(args.no_youtube)
