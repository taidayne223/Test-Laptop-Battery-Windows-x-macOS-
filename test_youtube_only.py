import time
import sys
from test_cases.youtube_test import run_youtube_test
from utils.system_setup import optimize_system
from utils.config import get_config
from utils.low_battery_popup import start_low_battery_popup_monitor

if __name__ == "__main__":
    config = get_config()
    restart_wait = config["cycle"]["youtube_only_restart_wait_seconds"]

    print("====================================================")
    print("   YouTube Keep-Alive Battery Test (YouTube Only)   ")
    print("====================================================")
    print("Press Ctrl+C at any time to stop the test.")
    print("")

    # Optimize system (volume 0%, screen brightness, etc.)
    optimize_system()
    start_low_battery_popup_monitor()

    try:
        while True:
            print("\n--- Starting YouTube playback cycle ---")
            run_youtube_test()
            print(f"\nCycle completed. Restarting YouTube test in {restart_wait} seconds...")
            time.sleep(restart_wait)
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        sys.exit(0)
