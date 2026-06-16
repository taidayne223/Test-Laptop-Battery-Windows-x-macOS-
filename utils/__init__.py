import os
import platform
import subprocess
import pyautogui

def start_file(file_path:str):
    platform_name = platform.system()

    if platform_name == "Windows":
        os.startfile(file_path)
    elif platform_name == "Darwin":
        # Force open with Microsoft Word or Excel to prevent Pages/Numbers from intercepting the files
        ext = os.path.splitext(file_path)[1].lower()
        opened = False
        if ext in ['.docx', '.doc']:
            res = subprocess.run(["open", "-a", "Microsoft Word", file_path], capture_output=True)
            if res.returncode == 0:
                opened = True
        elif ext in ['.xlsx', '.xls']:
            res = subprocess.run(["open", "-a", "Microsoft Excel", file_path], capture_output=True)
            if res.returncode == 0:
                opened = True
        
        if not opened:
            subprocess.run(["open", file_path], capture_output=True)
    else:
        subprocess.call(["xdg-open", file_path])

def detect_platform():
    platform_name = platform.system()

    is_windows = True
    is_macos = False

    if platform_name == 'Darwin':
        is_windows = False
        is_macos = True

    return is_windows, is_macos

def close_window():
    is_windows, is_macos = detect_platform()

    if is_windows:
        pyautogui.hotkey('alt', 'f4')

    if is_macos:
        pyautogui.hotkey('command', 'q')

def custom_scroll(times=1, direction="down"):
    scrolling_distance = 10
    is_windows, is_macos = detect_platform()

    if is_windows:
        scrolling_distance = 150

    if direction == 'down':
        scrolling_distance = scrolling_distance * -1

    scroll_time = 1
    while scroll_time <= times:
        pyautogui.scroll(scrolling_distance)
        scroll_time += 1

import psutil
import time

def kill_processes(process_names):
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name:
                for target_name in process_names:
                    if name.lower() == target_name.lower():
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def clean_office():
    # On macOS, gracefully quit using AppleScript first to prevent "Save changes" prompts
    if platform.system() == "Darwin":
        for app in ["Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint"]:
            subprocess.run(["osascript", "-e", f'tell application "{app}" to quit saving no'], capture_output=True)
        time.sleep(1)
        # Force kill as fallback
        for app in ["Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint"]:
            subprocess.run(["pkill", "-f", app], capture_output=True)

    office_procs = ["WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE", "Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint"]
    kill_processes(office_procs)

def clean_browser():
    system_name = platform.system()
    
    # On macOS, gracefully quit using AppleScript first
    if system_name == "Darwin":
        for app in ["Google Chrome", "Safari", "Microsoft Edge", "Firefox"]:
            subprocess.run(["osascript", "-e", f'tell application "{app}" to quit'], capture_output=True)
        time.sleep(1)
        # Force kill as fallback with SIGKILL (-9)
        for app in ["Google Chrome", "Safari", "Microsoft Edge", "Firefox"]:
            subprocess.run(["pkill", "-9", "-f", app], capture_output=True)
            
    # On Windows, force kill using taskkill
    elif system_name == "Windows":
        for proc in ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe"]:
            subprocess.run(["taskkill", "/F", "/IM", proc, "/T"], capture_output=True)

    browser_procs = [
        "msedge.exe", "chrome.exe", "firefox.exe", "opera.exe", 
        "Safari", "Microsoft Edge", "Google Chrome", "Firefox"
    ]
    kill_processes(browser_procs)

def close_active_tab():
    system = platform.system()
    try:
        if system == "Darwin":
            # Focus Google Chrome first to make sure Cmd+W goes to Chrome
            subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'], capture_output=True)
            time.sleep(0.5)
            pyautogui.hotkey('command', 'w')
        else:
            # On Windows, send Ctrl+W to close active tab
            pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)
    except Exception as e:
        print(f"Error closing active tab: {e}")

def find_chrome_path():
    system = platform.system()
    if system == "Windows":
        import winreg
        # 1. Try registry
        for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                with winreg.OpenKey(hkey, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                    path, _ = winreg.QueryValueEx(key, "")
                    if os.path.exists(path):
                        return path
            except FileNotFoundError:
                continue
        
        # 2. Try common paths
        common_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
                
    elif system == "Darwin":
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path
            
    return None

def find_edge_path():
    system = platform.system()
    if system == "Windows":
        import winreg
        # 1. Try registry
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe") as key:
                path, _ = winreg.QueryValueEx(key, "")
                if os.path.exists(path):
                    return path
        except FileNotFoundError:
            pass
            
        # 2. Try common paths
        common_paths = [
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    return None

def find_default_browser_path_windows():
    try:
        import winreg
        import shlex
        
        path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")
            
        cmd_string = None
        for root in [winreg.HKEY_CURRENT_USER, winreg.HKEY_CLASSES_ROOT]:
            if root == winreg.HKEY_CURRENT_USER:
                cmd_path = fr"Software\Classes\{prog_id}\shell\open\command"
            else:
                cmd_path = fr"{prog_id}\shell\open\command"
            try:
                with winreg.OpenKey(root, cmd_path) as key:
                    cmd_string, _ = winreg.QueryValueEx(key, "")
                    if cmd_string:
                        break
            except FileNotFoundError:
                continue
                
        if cmd_string:
            parts = shlex.split(cmd_string)
            if parts:
                exe_path = parts[0]
                if os.path.exists(exe_path):
                    return exe_path
    except Exception:
        pass
    return None

def find_default_browser_mac():
    import plistlib
    try:
        plist_path = os.path.expanduser("~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist")
        if os.path.exists(plist_path):
            with open(plist_path, "rb") as f:
                data = plistlib.load(f)
                handlers = data.get("LSHandlers", [])
                for handler in handlers:
                    if handler.get("LSHandlerURLScheme") == "https":
                        bundle_id = handler.get("LSHandlerRoleAll")
                        mapping = {
                            "com.google.chrome": "Google Chrome",
                            "com.microsoft.edgemac": "Microsoft Edge",
                            "org.mozilla.firefox": "Firefox",
                            "com.apple.safari": "Safari"
                        }
                        return mapping.get(bundle_id, "Safari")
    except Exception:
        pass
    return "Safari"

def open_in_browser(url, use_extension=False):
    import webbrowser
    system = platform.system()
    
    if system == "Windows":
        default_path = find_default_browser_path_windows()
        if default_path:
            name = os.path.basename(default_path).lower()
            if any(browser in name for browser in ["chrome", "msedge", "opera"]):
                args = [
                    default_path,
                    "--disable-session-crashed-bubble",
                    "--hide-crash-restore-bubble",
                    url
                ]
                print(f"Launching default browser ({name}) with flags: {' '.join(args)}")
                subprocess.Popen(args)
                return
            else:
                print(f"Launching default browser ({name}): {default_path}")
                subprocess.Popen([default_path, url])
                return
                
    elif system == "Darwin":
        default_app = find_default_browser_mac()
        if default_app in ["Google Chrome", "Microsoft Edge"]:
            args = [
                "open",
                "-a",
                default_app,
                "--args",
                "--disable-session-crashed-bubble",
                "--hide-crash-restore-bubble",
                url
            ]
            print(f"Launching default browser ({default_app}) with flags: {' '.join(args)}")
            subprocess.Popen(args)
            return
        else:
            print(f"Launching default browser ({default_app})")
            subprocess.Popen(["open", "-a", default_app, url])
            return

    # Fallback
    print("Falling back to webbrowser.open...")
    webbrowser.open(url)