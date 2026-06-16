import pyautogui
import time
import webbrowser
import os
import platform
import random
from utils.battery_utils import get_battery_level
from utils import clean_browser, custom_scroll, open_in_browser

def run_facebook_test():
    os_name = os.name
    platform_name = platform.system()

    print(f'Running Facebook Newsfeed Test on {os_name}, {platform_name}')
    get_battery_level()
    clean_browser()

    screenWidth, screenHeight = pyautogui.size()
    print(f'Screen size: {screenWidth}, {screenHeight}')

    # Open Facebook
    open_in_browser('https://www.facebook.com', use_extension=False)
    time.sleep(5)  # Wait for page load

    # Click in the middle of the screen to focus the browser window
    pyautogui.moveTo(screenWidth / 2, screenHeight / 2, duration=1)
    pyautogui.click()
    time.sleep(1)

    # Reload page to bypass Facebook's anti-spam logo screen
    print("Reloading page to bypass Facebook anti-spam logo...")
    if platform_name == 'Darwin':
        pyautogui.hotkey('command', 'r')
    else:
        pyautogui.press('f5')
    time.sleep(5)  # Wait for page load after reload

    # Click in the middle of the screen again to focus the window
    pyautogui.click()
    time.sleep(1)

    # Run the test for 14 minutes (30% speedup from 20 minutes)
    total_duration = 14 * 60  
    start_time = time.time()
    last_log_time = start_time

    print("Simulating Facebook Newsfeed scrolling for 14 minutes...")
    while time.time() - start_time < total_duration:
        # Dismiss any accidentally opened Reels/Stories modal or overlay to return focus to newsfeed
        pyautogui.press('esc')
        time.sleep(0.5)

        # Scroll down to simulate reading feed (increased to 8 times)
        custom_scroll(times=8, direction="down")
        
        # Sleep to mimic real reading behavior (reduced to 6 seconds for realistic fast scrolling)
        time.sleep(6)
        
        # Occasionally scroll up a tiny bit to simulate reviewing a post (15% chance)
        if random.random() < 0.15:
            pyautogui.press('esc')
            time.sleep(0.5)
            custom_scroll(times=4, direction="up")
            time.sleep(3)

        # Log battery level approximately every 5 minutes (300 seconds)
        current_time = time.time()
        if current_time - last_log_time >= 300:
            get_battery_level()
            last_log_time = current_time

    get_battery_level()
    clean_browser()
