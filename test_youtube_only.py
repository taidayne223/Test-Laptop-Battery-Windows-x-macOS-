import time
import sys
from test_cases.youtube_test import run_youtube_test
from utils.system_setup import optimize_system

if __name__ == "__main__":
    print("====================================================")
    print("   YouTube Keep-Alive Battery Test (YouTube Only)   ")
    print("====================================================")
    print("Press Ctrl+C at any time to stop the test.")
    print("")

    # Optimize system (volume 0%, screen brightness, etc.)
    optimize_system()

    try:
        while True:
            print("\n--- Starting YouTube playback cycle ---")
            run_youtube_test()
            print("\nCycle completed. Restarting YouTube test in 5 seconds...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        sys.exit(0)
