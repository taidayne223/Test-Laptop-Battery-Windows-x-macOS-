import time
import sys
import os
import platform
import threading
from datetime import datetime

from test_cases.youtube_test import run_youtube_test
from test_cases.office_test import run_office_test
from utils.system_setup import optimize_system
from utils.battery_utils import get_battery_level
from utils.config import get_config

# Disable fail safe mechanism of Pyautogui
import pyautogui
pyautogui.FAILSAFE = False

def start_test():
    config = get_config()
    quick_youtube_duration = config["youtube_test"]["quick_seconds_per_video"]
    quick_restart_wait = config["cycle"]["quick_restart_wait_seconds"]

    print("====================================================")
    print("   YouTube & Word Quick Switch Loop Test Runner   ")
    print("====================================================")
    print("Press Ctrl+C to stop the test.\n")

    optimize_system()

    cycle = 1
    try:
        while True:
            print(f"\n--- Cycle {cycle} Start: Office (Word) Test ---")
            run_office_test(quick=True)
            
            print(f"\n--- Cycle {cycle} Start: YouTube Test ---")
            run_youtube_test(duration=quick_youtube_duration)
            
            print(f"\n--- Cycle {cycle} Completed. Restarting in {quick_restart_wait} seconds... ---")
            time.sleep(quick_restart_wait)
            cycle += 1
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        sys.exit(0)

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
    # Start the battery info logging in a background daemon thread
    t2 = threading.Thread(target=information_process, daemon=True)
    t2.start()

    # Run the main test loop on the main thread to ensure proper GUI library compatibility
    start_test()
