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

# Disable fail safe mechanism of Pyautogui
import pyautogui
pyautogui.FAILSAFE = False

def start_test():
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
            # Run YouTube test case: duration=10 means each of the 2 videos runs for 10 seconds
            run_youtube_test(duration=10)
            
            print(f"\n--- Cycle {cycle} Completed. Restarting in 3 seconds... ---")
            time.sleep(3)
            cycle += 1
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        sys.exit(0)

def calculate_elapsed_time(start_time):
    elapsed_time = datetime.now() - start_time
    print(f'Elapsed time: {elapsed_time}')

def information_process():
    start_time = datetime.now()
    while True:
        get_battery_level()
        calculate_elapsed_time(start_time=start_time)
        time.sleep(3)

if __name__ == "__main__":
    # Start the battery info logging in a background daemon thread
    t2 = threading.Thread(target=information_process, daemon=True)
    t2.start()

    # Run the main test loop on the main thread to ensure proper GUI library compatibility
    start_test()
