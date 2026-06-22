import pyautogui
import time
import os
import platform
from utils.battery_utils import get_battery_level
from utils import custom_scroll, clean_browser, open_in_browser
from utils.config import get_config, platform_seconds

def run_browser_test():

    os_name = os.name
    platform_name = platform.system()
    config = get_config()["browser_test"]

    print(f'Running Browser Test on {os_name}, {platform_name}')
    get_battery_level()
    clean_browser()

    screenWidth, screenHeight = pyautogui.size() # Get the size of the primary monitor
    print(f'Screen size: {screenWidth}, {screenHeight}')

    urls = config["urls"]
    page_load_wait = platform_seconds(config["page_load_wait_seconds"], platform_name)
    scroll_times = config["scroll_times"]
    scroll_pause = config["scroll_pause_seconds"]

    for url in urls:
        open_in_browser(url, use_extension=False)

        # Sleep to allow the browser/tab to fully load
        time.sleep(page_load_wait)

        pyautogui.moveTo(screenWidth/2, screenHeight/2, duration=1)
        pyautogui.click(clicks=1)

        custom_scroll(times=scroll_times, direction="down")
        time.sleep(scroll_pause)
        custom_scroll(times=scroll_times, direction="up")
        time.sleep(scroll_pause)
        custom_scroll(times=scroll_times, direction="down")

    # Close the browser:
    clean_browser()
