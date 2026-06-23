import pyautogui
import time
import os
import platform
from utils.battery_utils import get_battery_level
from utils import clean_browser, open_in_browser, close_active_tab
from utils.config import get_config

YOUTUBE_THEATER_MODE_KEY = 't'


def _focus_youtube_player(screen_width, screen_height):
    pyautogui.moveTo(screen_width / 2, screen_height / 2, duration=0)
    pyautogui.click()
    time.sleep(0.3)


def _hard_refresh_youtube(platform_name, reload_wait, after_escape_wait):
    if platform_name == 'Darwin':
        pyautogui.hotkey('command', 'shift', 'r')
    else:
        pyautogui.hotkey('ctrl', 'shift', 'r')

    time.sleep(reload_wait)
    pyautogui.press('esc')
    time.sleep(after_escape_wait)


def _restore_youtube_playback(config, apply_theater_mode=False):
    if apply_theater_mode and config["theater_mode_enabled"]:
        pyautogui.press(YOUTUBE_THEATER_MODE_KEY)
        print("Switched YouTube to Theater mode")

    reset_enabled = config.get("reset_to_start_enabled", True)
    if reset_enabled:
        pyautogui.press('0')
        print("Seeked YouTube video back to start (pressed '0')")


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
    auto_hard_reload_interval = config.get("auto_hard_reload_interval_seconds", 0)
    max_auto_hard_reloads = config.get("max_auto_hard_reloads", 0)

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
        _hard_refresh_youtube(platform_name, reload_wait, after_escape_wait)

        # Re-focus the player after the reload. YouTube hotkeys ('t', '0') only
        # register when the player/page has keyboard focus, which can be lost
        # during the hard refresh above.
        _focus_youtube_player(screenWidth, screenHeight)
        _restore_youtube_playback(config, apply_theater_mode=True)

        # Force the player back to the start of the video before timing begins.
        # YouTube's autoplay can land on a video that's almost finished and then
        # freeze (autoplay bug). Pressing '0' seeks to the very beginning so each
        # test starts from a clean, playing state.
        reset_enabled = config.get("reset_to_start_enabled", True)

        # Total time to keep this video on screen.
        if duration is not None:
            watch_seconds = duration
        else:
            watch_seconds = max(0, total_seconds_per_video - setup_seconds)

        # Instead of one long sleep, optionally re-seek and hard-refresh during
        # playback. Re-seek prevents autoplay from reaching the next clip, while
        # scheduled hard-refreshes recover from YouTube black/loading screens.
        reseek_interval = config.get("reseek_interval_seconds", 0)
        watch_started_at = time.monotonic()
        next_reseek_at = watch_started_at + reseek_interval if reset_enabled and reseek_interval and reseek_interval > 0 else None
        next_hard_reload_at = (
            watch_started_at + auto_hard_reload_interval
            if auto_hard_reload_interval and auto_hard_reload_interval > 0 and max_auto_hard_reloads > 0
            else None
        )
        hard_reloads_done = 0

        while True:
            now = time.monotonic()
            watch_ends_at = watch_started_at + watch_seconds
            if now >= watch_ends_at:
                break

            wake_times = [watch_ends_at]
            if next_reseek_at is not None:
                wake_times.append(next_reseek_at)
            if next_hard_reload_at is not None:
                wake_times.append(next_hard_reload_at)

            time.sleep(max(0, min(wake_times) - now))
            now = time.monotonic()

            if next_hard_reload_at is not None and now >= next_hard_reload_at:
                hard_reloads_done += 1
                print(f"Hard-refreshed YouTube during playback ({hard_reloads_done}/{max_auto_hard_reloads})")
                _hard_refresh_youtube(platform_name, reload_wait, after_escape_wait)
                _focus_youtube_player(screenWidth, screenHeight)
                _restore_youtube_playback(config)

                if hard_reloads_done >= max_auto_hard_reloads:
                    next_hard_reload_at = None
                else:
                    next_hard_reload_at += auto_hard_reload_interval

                if next_reseek_at is not None:
                    next_reseek_at = time.monotonic() + reseek_interval
                continue

            if next_reseek_at is not None and now >= next_reseek_at:
                pyautogui.press('0')  # back to start before the video can end
                next_reseek_at += reseek_interval

        get_battery_level()
        close_active_tab()
        clean_browser()
