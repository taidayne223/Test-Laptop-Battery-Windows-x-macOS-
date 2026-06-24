import ctypes
import logging
import os
import platform
import subprocess
import threading
import time

import psutil

from utils.config import get_config


_monitor_lock = threading.Lock()
_monitor_started = False

_POWERSHELL_SCRIPT = r"""
Add-Type -AssemblyName UIAutomationClient
Add-Type @'
using System;
using System.Runtime.InteropServices;

public static class BatteryPopupNativeMethods {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool PostMessage(
        IntPtr hWnd,
        uint Msg,
        IntPtr wParam,
        IntPtr lParam
    );
}
'@

try {
    $WindowHandle = [long]$env:BATTERY_POPUP_WINDOW_HANDLE
    $MessageText = $env:BATTERY_POPUP_MESSAGE_TEXT
    $window = [System.Windows.Automation.AutomationElement]::FromHandle(
        [IntPtr]$WindowHandle
    )
    if ($null -eq $window) {
        exit 0
    }

    $elements = $window.FindAll(
        [System.Windows.Automation.TreeScope]::Subtree,
        [System.Windows.Automation.Condition]::TrueCondition
    )

    $matched = $false
    foreach ($element in $elements) {
        if ($element.Current.Name -like "*$MessageText*") {
            $matched = $true
            break
        }
    }

    if ($matched) {
        [BatteryPopupNativeMethods]::PostMessage(
            [IntPtr]$WindowHandle, 0x0100, [IntPtr]0x0D, [IntPtr]0
        ) | Out-Null
        [BatteryPopupNativeMethods]::PostMessage(
            [IntPtr]$WindowHandle, 0x0101, [IntPtr]0x0D, [IntPtr]0
        ) | Out-Null
        Write-Output "CLOSED"
    }
} catch {
    exit 0
}
"""


def _get_foreground_window_handle():
    try:
        return int(ctypes.windll.user32.GetForegroundWindow())
    except (AttributeError, OSError):
        return 0


def _close_matching_popup(window_handle, message_text, timeout_seconds):
    if not window_handle:
        return False

    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    command_environment = os.environ.copy()
    command_environment["BATTERY_POPUP_WINDOW_HANDLE"] = str(window_handle)
    command_environment["BATTERY_POPUP_MESSAGE_TEXT"] = message_text

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-WindowStyle",
                "Hidden",
                "-Command",
                _POWERSHELL_SCRIPT,
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            creationflags=creation_flags,
            env=command_environment,
        )
    except (OSError, subprocess.SubprocessError):
        return False

    return result.returncode == 0 and "CLOSED" in result.stdout


def _config_number(config, key, default, minimum):
    try:
        return max(minimum, float(config.get(key, default)))
    except (TypeError, ValueError):
        return default


def _monitor_low_battery_popup(config):
    threshold = _config_number(config, "threshold_percent", 15, 0)
    check_interval = _config_number(
        config,
        "check_interval_seconds",
        2,
        0.5,
    )
    rescan_interval = _config_number(
        config,
        "rescan_interval_seconds",
        10,
        1,
    )
    command_timeout = _config_number(
        config,
        "command_timeout_seconds",
        5,
        1,
    )
    message_text = config.get(
        "message_text",
        "Your battery is running low",
    )

    last_window_handle = 0
    last_scan_at = 0.0

    while True:
        try:
            battery = psutil.sensors_battery()
        except Exception:
            battery = None

        if (
            battery is not None
            and not battery.power_plugged
            and battery.percent <= threshold
        ):
            now = time.monotonic()
            window_handle = _get_foreground_window_handle()
            window_changed = window_handle != last_window_handle
            rescan_due = now - last_scan_at >= rescan_interval

            if window_handle and (window_changed or rescan_due):
                last_window_handle = window_handle
                last_scan_at = now
                if _close_matching_popup(
                    window_handle,
                    message_text,
                    command_timeout,
                ):
                    message = (
                        "[OK] Closed the Windows low-battery popup "
                        "automatically (pressed Enter)"
                    )
                    print(message)
                    logging.info(message)

        time.sleep(check_interval)


def start_low_battery_popup_monitor():
    global _monitor_started

    if platform.system() != "Windows":
        return False

    config = get_config().get("low_battery_popup", {})
    if not config.get("enabled", True):
        return False

    with _monitor_lock:
        if _monitor_started:
            return True

        monitor_thread = threading.Thread(
            target=_monitor_low_battery_popup,
            args=(config,),
            daemon=True,
            name="low-battery-popup-monitor",
        )
        monitor_thread.start()
        _monitor_started = True

    print("[OK] Windows low-battery popup auto-close is active")
    return True
