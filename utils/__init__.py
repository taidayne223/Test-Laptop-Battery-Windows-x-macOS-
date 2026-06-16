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

def open_in_browser(url, use_extension=False):
    import webbrowser
    system = platform.system()
    chrome_path = find_chrome_path()
    
    browser_path = None
    if chrome_path:
        browser_path = chrome_path
    elif system == "Windows":
        browser_path = find_edge_path()

    if browser_path:
        args = [
            browser_path,
            "--disable-session-crashed-bubble",
            "--hide-crash-restore-bubble"
        ]
        args.append(url)
        print(f"Launching browser with flags: {' '.join(args)}")
        subprocess.Popen(args)
    else:
        print("Chrome/Edge not found, falling back to webbrowser.open...")
        webbrowser.open(url)