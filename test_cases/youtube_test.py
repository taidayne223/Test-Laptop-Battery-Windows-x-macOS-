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

        # Re-focus the player after the reload. YouTube hotkeys ('t', '0') only
        # register when the player/page has keyboard focus, which can be lost
        # during the hard refresh above.
        pyautogui.moveTo(screenWidth / 2, screenHeight / 2, duration=0)
        pyautogui.click()
        time.sleep(0.3)

        if config["theater_mode_enabled"]:
            pyautogui.press(YOUTUBE_THEATER_MODE_KEY)
            print("Switched YouTube to Theater mode")

        # Force the player back to the start of the video before timing begins.
        # YouTube's autoplay can land on a video that's almost finished and then
        # freeze (autoplay bug). Pressing '0' seeks to the very beginning so each
        # test starts from a clean, playing state.
        reset_enabled = config.get("reset_to_start_enabled", True)
        if reset_enabled:
            pyautogui.press('0')
            print("Seeked YouTube video back to start (pressed '0')")

        # Total time to keep this video on screen.
        if duration is not None:
            watch_seconds = duration
        else:
            watch_seconds = max(0, total_seconds_per_video - setup_seconds)

        # Instead of one long sleep, optionally re-seek to the start every
        # `reseek_interval_seconds`. This stops the video from ever reaching its
        # end, which is where YouTube autoplay jumps to another (often almost
        # finished) clip and can freeze. Battery draw is unchanged because the
        # video keeps playing the whole time.
        reseek_interval = config.get("reseek_interval_seconds", 0)
        if reset_enabled and reseek_interval and reseek_interval > 0:
            remaining = watch_seconds
            while remaining > 0:
                chunk = min(reseek_interval, remaining)
                time.sleep(chunk)
                remaining -= chunk
                if remaining > 0:
                    pyautogui.press('0')  # back to start before the video can end
        else:
            time.sleep(watch_seconds)

        get_battery_level()
        close_active_tab()
        clean_browser()
