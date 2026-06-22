# Laptop Battery Test

Automated tool to simulate real-world office tasks (web browsing, document scrolling, and YouTube playback) to measure actual laptop battery life.

* **Original Creator:** Duy Luan De Thuong
* **Developer:** Tai Xai Tech

---

## 💻 Requirements
* **OS**: Windows 11 (x86/x64/ARM64) or macOS 12+ (Apple Silicon)
* **Software**: 
  * [Python 3](https://www.python.org/downloads/)
  * Google Chrome (used by default for browser and YouTube tests)
  * Microsoft Office (Word, Excel)

---

## ⚡ Simulated Tasks (Infinite Loop)
1. **Web Browsing**: Opens and scrolls through 5 websites.
2. **Office Simulation**: Opens and scrolls through 3 Word documents and 1 Excel sheet.
3. **YouTube Watching**: Plays configured videos in Theater mode.

Benchmark URLs, durations, and brightness are configured in **`benchmark_config.json`**.

---

## 🛠️ Automated 1-Click Setup
When launched, the tool automatically optimizes system settings for consistency:
* Sets screen brightness from **`system.brightness_percent`** and volume to **0%**.
* Sets Windows refresh rate from **`system.refresh_rate_hz`** when supported.
* Disables Windows display/sleep/hibernate/disk timeouts on battery during the test.
* Switches macOS input source to **U.S. (English)** to prevent Telex/VNI hotkey issues.
* Attempts to disable macOS Low Power Mode when supported.
* Prevents the screen and system from going to sleep during the test.
* Sets Windows power mode to **Balanced** and Battery Saver threshold from **`system.battery_saver_threshold_percent`**.
* Verifies Wi-Fi connectivity, checks the configured minimum battery level, and can require unplugging before the test starts.

---

## 🚀 How to Run

### 🍏 macOS:
1. Open Terminal and navigate to the project directory:
   ```sh
   cd /path/to/project
   ```
2. Grant execution permissions (only required **once**):
   ```sh
   chmod +x *.command
   ```
3. Double-click **`Macos bat dau.command`** in Finder to run.

### 🔌 Windows:
* Double-click **`Windows bat dau.bat`** to automatically configure, install dependencies, and start the test.

> [!TIP]
> **Disable YouTube test**: To run only web and office tests, execute `python test.py 1` in your terminal.
> 
> **Windows ARM Note**: If dependency installation fails, download [Visual Studio](https://visualstudio.microsoft.com/downloads/) and install the **Desktop Development with C++** workload.

---

## ⚙️ Benchmark Config
Edit **`benchmark_config.json`** to change the benchmark without touching code:
* **`system.brightness_percent`**: screen brightness used during setup.
* **`system.refresh_rate_hz`**: Windows display refresh-rate target when supported.
* **`system.battery_saver_threshold_percent`**: Windows Battery/Energy Saver threshold.
* **`system.minimum_start_battery_percent`**: battery level warning threshold before running.
* **`system.require_unplugged`**: require the charger to be unplugged before the benchmark starts.
* **`system.macos_disable_low_power_mode`**: attempt to disable macOS Low Power Mode.
* **`browser_test.urls`**: websites opened during the browser test.
* **`youtube_test.urls`**: YouTube videos used during the playback test.
* **`youtube_test.total_seconds_per_video`**: target total time per YouTube video.
* **`youtube_test.quick_seconds_per_video`**: short YouTube duration used by `test_quick_youtube_word.py`.
* **`browser_test`**, **`office_test`**, **`reporting`**, and **`cycle`** wait values: timing knobs for page load, scrolling, logging, and cycle restart.

---

## 📊 Result Analysis (Logs)
Once the laptop shuts down due to battery depletion, plug in the charger, boot it back up, and analyze the logs:

* **Windows**: Double-click **`Windows phan tich file.bat`**
* **macOS**: Double-click **`Macos phan tich file.command`**

This generates a detailed battery life report printed to the screen and saved to **`battery_report.txt`**.
