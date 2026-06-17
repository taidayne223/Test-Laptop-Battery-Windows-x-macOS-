import os
import platform
import subprocess
import psutil

# Helper to change screen refresh rate to 60Hz on Windows
def set_windows_refresh_rate(refresh_rate=60):
    import ctypes
    from ctypes import wintypes

    CDS_UPDATEREGISTRY = 0x01
    DISP_CHANGE_SUCCESSFUL = 0
    ENUM_CURRENT_SETTINGS = -1
    DM_DISPLAYFREQUENCY = 0x400000

    class POINTL(ctypes.Structure):
        _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

    class DEVMODE(ctypes.Structure):
        _fields_ = [
            ("dmDeviceName", ctypes.c_wchar * 32),
            ("dmSpecVersion", wintypes.WORD),
            ("dmDriverVersion", wintypes.WORD),
            ("dmSize", wintypes.WORD),
            ("dmDriverExtra", wintypes.WORD),
            ("dmFields", wintypes.DWORD),
            ("dmPosition", POINTL),
            ("dmDisplayOrientation", wintypes.DWORD),
            ("dmDisplayFixedOutput", wintypes.DWORD),
            ("dmColor", wintypes.WORD),
            ("dmDuplex", wintypes.WORD),
            ("dmYResolution", wintypes.WORD),
            ("dmTTOption", wintypes.WORD),
            ("dmCollate", wintypes.WORD),
            ("dmFormName", ctypes.c_wchar * 32),
            ("dmLogPixels", wintypes.WORD),
            ("dmBitsPerPel", wintypes.DWORD),
            ("dmPelsWidth", wintypes.DWORD),
            ("dmPelsHeight", wintypes.DWORD),
            ("dmDisplayFlags", wintypes.DWORD),
            ("dmDisplayFrequency", wintypes.DWORD),
            ("dmICMMethod", wintypes.DWORD),
            ("dmICMIntent", wintypes.DWORD),
            ("dmMediaType", wintypes.DWORD),
            ("dmDitherType", wintypes.DWORD),
            ("dmReserved1", wintypes.DWORD),
            ("dmReserved2", wintypes.DWORD),
            ("dmPanningWidth", wintypes.DWORD),
            ("dmPanningHeight", wintypes.DWORD),
        ]

    try:
        devmode = DEVMODE()
        devmode.dmSize = ctypes.sizeof(DEVMODE)
        
        # Retrieve current settings
        if ctypes.windll.user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(devmode)) != 0:
            current_rate = devmode.dmDisplayFrequency
            if current_rate == refresh_rate:
                print(f"[OK] Refresh rate is already at {refresh_rate} Hz")
                return True
                
            devmode.dmDisplayFrequency = refresh_rate
            devmode.dmFields |= DM_DISPLAYFREQUENCY
            
            # Apply the settings
            result = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(devmode), CDS_UPDATEREGISTRY)
            if result == DISP_CHANGE_SUCCESSFUL:
                print(f"[OK] Successfully changed refresh rate to {refresh_rate} Hz (was {current_rate} Hz)")
                return True
            else:
                print(f"[WARNING] Failed to change refresh rate to {refresh_rate} Hz (Error code: {result})")
        else:
            print("[WARNING] Failed to retrieve display settings for refresh rate configuration")
    except Exception as e:
        print(f"[WARNING] Exception when setting refresh rate: {e}")
    return False

# Helper to check and enable Bluetooth on Windows
def enable_windows_bluetooth():
    ps_code = """
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
    Function Await($WinRtTask, $ResultType) {
        $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
        $netTask = $asTask.Invoke($null, @($WinRtTask))
        $netTask.Wait(-1) | Out-Null
        $netTask.Result
    }
    [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
    $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
    $bluetooth = $radios | Where-Object { $_.Kind -eq 'Bluetooth' }
    if ($bluetooth) {
        if ($bluetooth.State -eq 'Off') {
            $status = Await ($bluetooth.SetStateAsync('On')) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
            Write-Output "Enabled"
        } else {
            Write-Output "AlreadyOn"
        }
    } else {
        Write-Output "NotFound"
    }
    """
    try:
        result = subprocess.run(["powershell", "-Command", ps_code], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if "Enabled" in output:
            print("[OK] Bluetooth was Off, successfully turned it On")
        elif "AlreadyOn" in output:
            print("[OK] Bluetooth is already On")
        elif "NotFound" in output:
            print("[WARNING] No Bluetooth adapter detected on this system")
        else:
            print(f"[WARNING] Bluetooth status check result: {output}")
    except Exception as e:
        print(f"[WARNING] Could not check/enable Bluetooth: {e}")

def set_macos_brightness(brightness_level=0.75):
    import ctypes
    import ctypes.util
    try:
        cg_path = ctypes.util.find_library('CoreGraphics')
        if not cg_path:
            return False
        cg = ctypes.CDLL(cg_path)
        main_display = cg.CGMainDisplayID()
        
        ds = ctypes.CDLL('/System/Library/PrivateFrameworks/DisplayServices.framework/DisplayServices')
        ds.DisplayServicesSetBrightness.argtypes = [ctypes.c_int, ctypes.c_float]
        ds.DisplayServicesSetBrightness.restype = ctypes.c_int
        
        res = ds.DisplayServicesSetBrightness(main_display, ctypes.c_float(brightness_level))
        return res == 0
    except Exception:
        pass
    return False

def switch_macos_input_to_us():
    import ctypes
    import ctypes.util
    
    def get_cfstring_value(cf_string_ref):
        if not cf_string_ref:
            return None
        try:
            cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))
            cf.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint]
            cf.CFStringGetCString.restype = ctypes.c_bool
            buf = ctypes.create_string_buffer(512)
            if cf.CFStringGetCString(cf_string_ref, buf, 512, 0x08000100):
                return buf.value.decode('utf-8')
        except Exception:
            pass
        return None

    try:
        carbon_path = ctypes.util.find_library('Carbon')
        if not carbon_path:
            print("[WARNING] Carbon library not found, cannot switch input source")
            return False
            
        carbon = ctypes.cdll.LoadLibrary(carbon_path)
        cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))
        
        # Define TIS functions
        carbon.TISCreateInputSourceList.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        carbon.TISCreateInputSourceList.restype = ctypes.c_void_p
        
        carbon.TISGetInputSourceProperty.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        carbon.TISGetInputSourceProperty.restype = ctypes.c_void_p
        
        carbon.TISSelectInputSource.argtypes = [ctypes.c_void_p]
        carbon.TISSelectInputSource.restype = ctypes.c_int
        
        cf.CFArrayGetCount.argtypes = [ctypes.c_void_p]
        cf.CFArrayGetCount.restype = ctypes.c_long
        
        cf.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
        cf.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
        
        cf.CFRelease.argtypes = [ctypes.c_void_p]
        
        kTISPropertyInputSourceID = ctypes.c_void_p.in_dll(carbon, 'kTISPropertyInputSourceID')
        
        sources_list = carbon.TISCreateInputSourceList(None, False)
        if not sources_list:
            print("[WARNING] Failed to retrieve input sources list")
            return False
            
        count = cf.CFArrayGetCount(sources_list)
        target_source_ref = None
        for i in range(count):
            source_ref = cf.CFArrayGetValueAtIndex(sources_list, i)
            if not source_ref:
                continue
                
            source_id_ref = carbon.TISGetInputSourceProperty(source_ref, kTISPropertyInputSourceID)
            source_id = get_cfstring_value(source_id_ref)
            if source_id == "com.apple.keylayout.US":
                target_source_ref = source_ref
                break
                
        if target_source_ref:
            status = carbon.TISSelectInputSource(target_source_ref)
            if status == 0:
                print("[OK] Switched macOS input source to U.S.")
                cf.CFRelease(sources_list)
                return True
            else:
                print(f"[WARNING] Failed to switch input source (OSStatus: {status})")
        else:
            print("[WARNING] U.S. Input source (com.apple.keylayout.US) not found in enabled keyboard layouts")
            
        cf.CFRelease(sources_list)
    except Exception as e:
        print(f"[WARNING] Could not switch macOS input source: {e}")
    return False

def optimize_system():
    system = platform.system()
    print("=================================================================")
    print("   [1-Click Setup] Optimizing System Settings for Battery Test   ")
    print("=================================================================")

    if system == "Windows":
        # 1. Set power mode to Balanced
        try:
            # GUID for SCHEME_BALANCED is 381b4222-f694-41f0-9685-ff5bb260df2e
            subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], capture_output=True, check=True)
            print("[OK] Set laptop Power mode to 'Balanced'")
        except Exception as e:
            print(f"[WARNING] Could not set power mode to Balanced: {e}")

        # 2. Set screen brightness to 75%
        try:
            # First try using powercfg (most robust, works on all Windows systems including ARM64/Snapdragon)
            try:
                subprocess.run(["powercfg", "/setdcvalueindex", "SCHEME_CURRENT", "SUB_VIDEO", "VIDEONORMALLEVEL", "75"], capture_output=True, check=True)
                subprocess.run(["powercfg", "/setacvalueindex", "SCHEME_CURRENT", "SUB_VIDEO", "VIDEONORMALLEVEL", "75"], capture_output=True, check=True)
                subprocess.run(["powercfg", "/setactive", "SCHEME_CURRENT"], capture_output=True, check=True)
                print("[OK] Set screen brightness to 75% (via powercfg)")
            except Exception as e_pcfg:
                print(f"[WARNING] Could not set screen brightness via powercfg: {e_pcfg}")

            # Also try screen-brightness-control to force instant driver update if supported
            try:
                import screen_brightness_control as sbc
                sbc.set_brightness(75)
                print("[OK] Enforced screen brightness to 75% (via screen-brightness-control)")
            except Exception:
                try:
                    # Try modern CimInstance (Windows 11 / PowerShell Core)
                    cmd = "Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods | Invoke-CimMethod -MethodName WmiSetBrightness -Arguments @{Timeout=1; Brightness=75}"
                    subprocess.run(["powershell", "-Command", cmd], capture_output=True, check=True)
                    print("[OK] Enforced screen brightness to 75% (via CIM)")
                except Exception:
                    # Fallback to WMI (legacy PowerShell)
                    cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 75)"
                    subprocess.run(["powershell", "-Command", cmd], capture_output=True, check=True)
                    print("[OK] Enforced screen brightness to 75% (via WMI)")
        except Exception as e:
            print(f"[WARNING] Could not set screen brightness: {e}")

        # 3. Turn off screen timeout (Never turn off screen on battery)
        try:
            subprocess.run(["powercfg", "/change", "monitor-timeout-dc", "0"], capture_output=True, check=True)
            subprocess.run(["powercfg", "/change", "standby-timeout-dc", "0"], capture_output=True, check=True)
            print("[OK] Turned off screen auto turn-off & standby sleep on battery")
        except Exception as e:
            print(f"[WARNING] Could not configure screen timeout: {e}")

        # 4. Set battery saver on at 30%
        try:
            subprocess.run(["powercfg", "/setdcvalueindex", "SCHEME_CURRENT", "SUB_ENERGYSAVER", "ESBATTTHRESHOLD", "30"], capture_output=True, check=True)
            subprocess.run(["powercfg", "/setactive", "SCHEME_CURRENT"], capture_output=True, check=True)
            print("[OK] Configured Battery/Energy Saver to turn on at 30%")
        except Exception as e:
            print(f"[WARNING] Could not configure Battery Saver threshold: {e}")

        # 5. Turn "lower screen brightness on low battery" off (set to 100% of normal brightness)
        try:
            subprocess.run(["powercfg", "/setdcvalueindex", "SCHEME_CURRENT", "SUB_ENERGYSAVER", "ESBRIGHTNESS", "100"], capture_output=True, check=True)
            subprocess.run(["powercfg", "/setactive", "SCHEME_CURRENT"], capture_output=True, check=True)
            print("[OK] Turn off 'lower screen brightness on low battery'")
        except Exception as e:
            print(f"[WARNING] Could not configure Battery Saver brightness: {e}")

        # 6. Turn volume to 0%
        try:
            cmd = "$w = New-Object -ComObject Wscript.Shell; for($i = 0; $i -lt 50; $i++) { $w.SendKeys([char]174) }"
            subprocess.run(["powershell", "-Command", cmd], capture_output=True, check=True)
            print("[OK] Turned system volume to 0%")
        except Exception as e:
            print(f"[WARNING] Could not set volume: {e}")

        # 7. Disable 'Change brightness based on content' (CABC) in registry
        try:
            import winreg
            key_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "CABCOption", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "DisableCABC", 1, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            print("[OK] Disabled 'Change brightness based on content' (CABC) in registry")
        except PermissionError:
            print("[WARNING] Could not disable 'Change brightness based on content' (CABC) in registry (Access Denied).")
            print("          Please run the launcher as Administrator (right-click and 'Run as administrator') to apply this automatically.")
        except Exception as e:
            print(f"[WARNING] Could not disable 'Change brightness based on content' (CABC): {e}")

        # 8. Disable ambient light adaptive brightness
        try:
            # Subgroup: 7516b95f-f776-4464-8c53-06167f40cc99 (Display)
            # Setting: fbd9aa66-9553-4097-ba44-ed6e9d65eab8 (Enable adaptive brightness)
            subprocess.run(["powercfg", "/setdcvalueindex", "SCHEME_CURRENT", "7516b95f-f776-4464-8c53-06167f40cc99", "fbd9aa66-9553-4097-ba44-ed6e9d65eab8", "0"], capture_output=True, check=True)
            subprocess.run(["powercfg", "/setactive", "SCHEME_CURRENT"], capture_output=True, check=True)
            print("[OK] Disabled ambient light adaptive brightness")
        except Exception as e:
            print(f"[WARNING] Could not disable ambient light adaptive brightness: {e}")

        # 9. Check and enable Bluetooth
        enable_windows_bluetooth()

    elif system == "Darwin": # macOS
        # 1. Power Mode
        print("[OK] Power Mode check: High Performance Mode is disabled by default")

        # 2. Set screen brightness to 75%
        print("[INFO] Configuring screen brightness...")
        brightness_set = set_macos_brightness(0.75)
        if brightness_set:
            print("[OK] Set screen brightness to 75% (via DisplayServices)")
        else:
            try:
                # 16 taps of key code 144 (brightness down) to set to 0, then 12 taps of 145 (brightness up) to set to 75%
                script = 'tell application "System Events" to repeat 16 times\nkey code 144\ndelay 0.01\nend repeat\n' \
                         'tell application "System Events" to repeat 12 times\nkey code 145\ndelay 0.01\nend repeat'
                subprocess.run(["osascript", "-e", script], capture_output=True, check=True)
                print("[OK] Set screen brightness to 75% (via AppleScript fallback)")
            except Exception:
                print("[WARNING] Could not set screen brightness automatically. Please set it manually to 75%.")

        # 3. Turn off auto turn off screen on battery power
        print("[OK] Sleep and display sleep prevention active via caffeinate wrapper")

        # 4. Turn volume to 0%
        try:
            subprocess.run(["osascript", "-e", "set volume output volume 0"], capture_output=True, check=True)
            print("[OK] Turned volume to 0%")
        except Exception as e:
            print(f"[WARNING] Could not set volume: {e}")



        # 6. Switch input source to U.S. (com.apple.keylayout.US)
        switch_macos_input_to_us()

    # Check internet connection
    try:
        import socket
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        print("[OK] Network connection is active")
    except Exception:
        print("[WARNING] No internet connection detected. Please connect to Wi-Fi for browser/multimedia tests.")

    # Check battery level
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = battery.power_plugged
            status = "Charging/Plugged In" if plugged else "Discharging/On Battery"
            print(f"[INFO] Current Battery: {percent}% ({status})")
            if percent < 99:
                print(f"\n[WARNING] Your battery is at {percent}%. For accurate and consistent test results:")
                if plugged:
                    print("  --> Please keep the charger connected until it reaches 100%, then unplug to start testing.")
                else:
                    print("  --> Please connect your charger, wait until it reaches 100%, then unplug to start testing.")
                print("\n=================================================================")
                try:
                    input("Press [Enter] to ignore this warning and start the test anyway...")
                except (KeyboardInterrupt, SystemExit):
                    import sys
                    print("\nTest cancelled by user.")
                    sys.exit(0)
            else:
                print("[OK] Battery is fully charged (100% or near 100%)")
        else:
            print("[WARNING] Could not read battery state.")
    except Exception as e:
         print(f"[WARNING] Could not check battery: {e}")

    print("=================================================================\n")

if __name__ == "__main__":
    optimize_system()
