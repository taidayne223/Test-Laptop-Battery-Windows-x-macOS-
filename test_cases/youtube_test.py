import pyautogui
import time
import os
import platform
from utils.battery_utils import get_battery_level
from utils import clean_browser, open_in_browser, close_active_tab
from utils.config import get_config

YOUTUBE_THEATER_MODE_KEY = 't'

def run_youtube_test(duration=None):

    os_name = os.name
    platform_name = platform.system()
    config = get_config()["youtube_test"]

    print(f'Running YouTube Test on {os_name}, {platform_name}')
    get_battery_level()
    clean_browser()

    screenWidth, screenHeight = pyautogui.size() # Get the size of the primary monitor
    print(f'Screen size: {screenWidth}, {screenHeight}')

    urls = config["urls"]
    page_load_wait = config["page_load_wait_seconds"]
    focus_move_seconds = config["focus_move_seconds"]
    focus_wait = config["focus_wait_seconds"]
    reload_wait = config["reload_wait_seconds"]
    after_escape_wait = config["after_escape_wait_seconds"]
    total_seconds_per_video = config["total_seconds_per_video"]
    setup_seconds = page_load_wait + focus_move_seconds + focus_wait + reload_wait + after_escape_wait

    for url in urls:
        close_active_tab()
        clean_browser()
        get_battery_level()
        open_in_browser(url, use_extension=False)

        # Wait for the browser and YouTube page to load
        time.sleep(page_load_wait)

        # Click in the middle of the screen to focus the browser window
        pyautogui.moveTo(screenWidth / 2, screenHeight / 2, duration=focus_move_seconds)
        pyautogui.click()
        time.sleep(focus_wait)

        # Perform hard refresh to clear cache and ensure video playback starts correctly
        if platform_name == 'Darwin':
            pyautogui.hotkey('command', 'shift', 'r')
        else:
            pyautogui.hotkey('ctrl', 'shift', 'r')
        
        # Wait for reload
        time.sleep(reload_wait)

        # Press Escape to dismiss any popups (e.g., Chrome "Restore pages" popup)
        pyautogui.press('esc')
        time.sleep(after_escape_wait)

        if config["theater_mode_enabled"]:
            pyautogui.press(YOUTUBE_THEATER_MODE_KEY)
            print("Switched YouTube to Theater mode")

        # Keep the configured total per video stable even when setup waits change.
        if duration is not None:
            time.sleep(duration)
        else:
            time.sleep(max(0, total_seconds_per_video - setup_seconds))

        get_battery_level()
        close_active_tab()
        clean_browser()
