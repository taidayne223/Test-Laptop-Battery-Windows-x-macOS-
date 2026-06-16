# Laptop Battery Test

* **Source by:** Duy Luan De Thuong
* **Further developed by:** Tai Xai Tech

This test aims to simulate a series of office-related tasks, such as web browsing, opening and scrolling MS Office files... in order to test how long a laptop's battery may last.

The result is constantly written to a log file so you do not have to worry about losing your test. The test file will only be saved on the disk, with the accuracy of +- 1-2 minutes, not a lot (and it can be improved in the future).

# Supported OS

- Windows 11 x86 / x64
- Windows 11 ARM 64-bit
- macOS 12 ARM 64-bit

The author has tested this program on several laptops running a wide variety of CPUs, including Intel Core Ultra, Snapdragon X Elite, Apple M-Series

# Required third party software

- Python: to run the script
- A default browser: Edge, Safari, or any default browser of your choice. Edge and Safari are recommended since they are default browser for most Windows and Mac machine
- Microsoft Office: Word, Excel, PowerPoint

# Tasks to perform

The program will run an infinite loop of the following tasks:
1. **Web Browsing**: Open 5 websites using the default browser and scroll through them.
2. **Office simulation**: Open 3 Word files and 1 Excel file and scroll.
3. **YouTube Watching**: Play YouTube videos (reduced to 10 minutes per video, 2 videos total).
4. **Facebook Newsfeed Scrolling**: Open Facebook (expects pre-logged in status) and scroll through the feed simulating real reading behavior (20 minutes total).

There will be scrolling and mouse moving when running the test.

In the future, text input will be added to better resemble how a normal user would use an Office app.

# Before you run any test (Automated 1-Click Setup)

When you run `start_test.bat` (Windows) or `start_test.command` (macOS), the test launcher will now **automatically configure these settings** for you:
* **Power Mode:** Set to **Balanced** (Windows).
* **Screen Brightness:** Set to **75%** (Windows/macOS).
* **Sleep Timeout:** Screen and system sleep are disabled during the test (using power settings on Windows, and the `caffeinate` tool wrapper on macOS).
* **Battery Saver:** Configured to turn on at **30%** (Windows).
* **Battery Saver Brightness:** Configured to stay at **75%** instead of dimming on low battery (Windows).
* **Volume:** Set to **0%** (Windows/macOS).
* **Battery Health Check:** Checks if battery is fully charged (warns and prompts if below 99%).
* **Internet Check:** Verifies active internet connection (Wi-Fi).

You only need to check:
- [ ] Connect your laptop to Wi-Fi.
- [ ] Charge your laptop to 100% battery, then unplug the charger to begin the test.

# How to run

## Installation

1. Install Python https://www.python.org/downloads/
2. Download this code by click on the Code (green button) > Download ZIP, or you can use `git clone` this repo to your machine.
3. Unzip the ZIP file you have just download
4. Open Command Prompt (cmd) and navigate to your extracted folder (e.g: `cd C:\Users\Duyluan\Downloads\laptop_battery_test`)

## Run the program

**Always navigate to project folder first**

### macOS:

You can run the scripts on macOS in two ways:

#### Option 1: Double-click to run (Requires one-time permission setup)
1. Open **Terminal** and navigate to the project folder:
   * Type `cd ` (with a space)
   * Drag the project folder from Finder into the Terminal window and press **Enter**.
2. Run the following command to allow the scripts to run:
   ```sh
   chmod +x *.command
   ```
3. Now you can simply **double-click** `start_test.command` or `analyze_battery.command` in Finder to run them!

#### Option 2: Run via Terminal using `bash` (No permissions setup needed)
1. Open **Terminal** and navigate to the project folder:
   * Type `cd ` (with a space)
   * Drag the project folder from Finder into the Terminal window and press **Enter**.
2. Run the launcher script to start the test:
   ```sh
   bash start_test.command
   ```
   Or run the battery analyzer:
   ```sh
   bash analyze_battery.command
   ```


### Windows:

You can double-click **`start_test.bat`** to automatically setup and start the test!

Alternatively, you can run manually in Command Prompt (CMD):
1. First time setup & run:
```cmd
python -m venv battery_test_env
battery_test_env\Scripts\activate.bat
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
python test.py
```
2. Next runs:
```cmd
battery_test_env\Scripts\activate.bat
python test.py
```

> [!NOTE]
**Note for Windows ARM**: You may need to install C++ Builds Tools (especially on Windows ARM devices) if the error show when building wheels. Check the error message to see if you need to do so. Download [Visual Studio](https://visualstudio.microsoft.com/downloads/) and install **Desktop Development with C++**, then run the installation commands again.

# Disable YouTube & Facebook tests

By default, the script will run with YouTube playback and Facebook scrolling tests included. If you want to disable these multimedia/social tests, run:

```sh
python test.py 1
```

# How to calculate time difference (Log Analysis)

After the laptop shuts down due to low battery, plug in the charger and turn it on. Go to the project folder. The script automatically records all logs in `logfilename.log`.

To analyze the logs and get the exact testing duration for all cycles:

### Using the Automated Analyzer (Recommended):

- **Windows**: Simply **double-click `analyze_battery.bat`** in File Explorer!
- **macOS**: Simply **double-click `analyze_battery.command`** in Finder! (Make sure you have run `chmod +x *.command` once first as described in the run section).

It will parse the logs, automatically group them into battery discharging cycles, calculate the duration of each cycle (in hours/minutes), output it on the console, and save the report to **`battery_report.txt`**.

### Manual Calculation (Backward Compatible):

If you want to manually calculate the difference between two specific timestamps:

- **macOS**:
```sh
python3 datetime_calculator.py "YYYY-MM-DD HH:MM:SS" "YYYY-MM-DD HH:MM:SS"
```
- **Windows**:
```cmd
python datetime_calculator.py "YYYY-MM-DD HH:MM:SS" "YYYY-MM-DD HH:MM:SS"
```

# Next steps:
- Build a system to store the log file and allow users to search for laptop's battery test result

# How to develop:

Pull the repo, then follow the instruction above. You should start checking the `test.py` file, it is the entry file for the whole script.
I'm thinking changing it to a __main__ script

# Trouble shooting, Q&A:

**Q: Cannot run Python in command prompt?**
A: If you open the command prompt before you install Python, the `python` command has not been registered to PATH. Simply close command prompt or open a new tab will solve the issue.

