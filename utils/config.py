import copy
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "benchmark_config.json"

DEFAULT_CONFIG = {
    "system": {
        "brightness_percent": 75,
        "refresh_rate_hz": 60,
        "battery_saver_threshold_percent": 30,
        "minimum_start_battery_percent": 99,
        "require_unplugged": True,
        "macos_disable_low_power_mode": True,
    },
    "browser_test": {
        "urls": [
            "https://www.engadget.com/the-7-best-white-elephant-gifts-that-are-worth-stealing-150516076.html",
            "https://www.engadget.com/transportation/evs/tesla-is-recalling-almost-700000-vehicles-over-a-tire-pressure-monitor-issue-223639361.html",
            "https://www.engadget.com/entertainment/tv-movies/james-bond-the-movie-franchise-not-the-spy-may-be-in-deep-jeopardy-211608094.html",
            "https://www.engadget.com/cybersecurity/the-us-consumer-financial-protection-bureau-sues-zelle-and-four-of-its-partner-banks-175714692.html",
            "https://www.engadget.com/apps/flipboard-just-launched-surf-which-is-sort-of-like-an-rss-feed-for-the-open-social-web-184015833.html",
        ],
        "page_load_wait_seconds": {
            "windows": 2,
            "macos": 4,
            "default": 2,
        },
        "scroll_times": 10,
        "scroll_pause_seconds": 7,
    },
    "office_test": {
        "app_load_wait_seconds": {
            "windows": 2,
            "macos": 5,
            "default": 2,
        },
        "scroll_times": 10,
        "scroll_pause_seconds": 7,
        "quick_scroll_pause_seconds": 2,
        "close_wait_seconds": 1,
    },
    "youtube_test": {
        "urls": [
            "https://www.youtube.com/watch?v=MbXLt7OwEXI",
            "https://www.youtube.com/watch?v=w1ucZCmvO5c",
        ],
        "total_seconds_per_video": 420,
        "quick_seconds_per_video": 10,
        "page_load_wait_seconds": 8,
        "focus_move_seconds": 1,
        "focus_wait_seconds": 1,
        "reload_wait_seconds": 5,
        "after_escape_wait_seconds": 0.5,
        "theater_mode_enabled": True,
        "hard_reload_after_theater_mode_enabled": True,
        "reset_to_start_enabled": True,
        "reseek_interval_seconds": 60,
        "auto_hard_reload_interval_seconds": 120,
        "max_auto_hard_reloads": 2,
    },
    "reporting": {
        "battery_log_interval_seconds": 3,
    },
    "cycle": {
        "youtube_only_restart_wait_seconds": 5,
        "quick_restart_wait_seconds": 3,
    },
}

_CONFIG_CACHE = None


def _deep_merge(base, override):
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def get_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config = copy.deepcopy(DEFAULT_CONFIG)
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            file_config = json.load(f)
        if isinstance(file_config, dict):
            _deep_merge(config, file_config)
    except FileNotFoundError:
        print(f"[WARNING] Config file not found: {CONFIG_PATH}. Using built-in defaults.")
    except json.JSONDecodeError as e:
        print(f"[WARNING] Config file is invalid JSON: {e}. Using built-in defaults.")

    _CONFIG_CACHE = config
    return _CONFIG_CACHE


def platform_seconds(values, platform_name):
    if not isinstance(values, dict):
        return values

    key = "macos" if platform_name == "Darwin" else "windows" if platform_name == "Windows" else "default"
    return values.get(key, values.get("default", 0))


def clamp_percent(value):
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return DEFAULT_CONFIG["system"]["brightness_percent"]


def positive_int(value, default):
    try:
        value = int(value)
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default
