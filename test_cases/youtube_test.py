import pyautogui
import time
import webbrowser
import os
import platform
from utils.battery_utils import get_battery_level
from utils import clean_browser, open_in_browser, close_active_tab

def run_youtube_test(duration=None):

    os_name = os.name
    platform_name = platform.system()

    print(f'Running YouTube Test on {os_name}, {platform_name}')
    get_battery_level()
    clean_browser()

    screenWidth, screenHeight = pyautogui.size() # Get the size of the primary monitor
    print(f'Screen size: {screenWidth}, {screenHeight}')

    # Browsing test
    urls = [
        'https://www.youtube.com/watch?v=MbXLt7OwEXI',
        'https://www.youtube.com/watch?v=w1ucZCmvO5c',
    ]

    for url in urls:
        close_active_tab()
        clean_browser()
        get_battery_level()
        open_in_browser(url, use_extension=False)

        # Wait for the browser and YouTube page to load
        time.sleep(8)

        # Press Escape to dismiss any popups (e.g., Chrome "Restore pages" popup)
        pyautogui.press('esc')

        # YouTube playback duration: 7 minutes per video (30% speedup from 10 minutes)
        # Subtract the 9 seconds we already waited
        if duration is not None:
            time.sleep(duration)
        else:
            time.sleep(7 * 60 - 9)

        get_battery_level()
        close_active_tab()
        clean_browser()