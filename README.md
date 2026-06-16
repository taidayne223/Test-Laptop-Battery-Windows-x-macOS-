# Laptop Battery Test

Automated tool to simulate real-world office tasks (web browsing, document scrolling, YouTube playback, and Facebook feed reading) to measure actual laptop battery life.

* **Original Creator:** Duy Luan De Thuong
* **Developer:** Tai Xai Tech

---

## 💻 Requirements
* **OS**: Windows 11 (x86/x64/ARM64) or macOS 12+ (Apple Silicon)
* **Software**: 
  * [Python 3](https://www.python.org/downloads/)
  * Default Browser (Safari on Mac, Edge on Windows recommended)
  * Microsoft Office (Word, Excel)

---

## ⚡ Simulated Tasks (Infinite Loop)
1. **Web Browsing**: Opens and scrolls through 5 websites.
2. **Office Simulation**: Opens and scrolls through 3 Word documents and 1 Excel sheet.
3. **YouTube Watching**: Plays 2 videos (7 minutes each).
4. **Facebook Feed**: Scrolls through Facebook Newsfeed (14 minutes).

---

## 🛠️ Automated 1-Click Setup
When launched, the tool automatically optimizes system settings for consistency:
* Sets screen brightness to **75%** and volume to **0%**.
* Switches macOS input source to **U.S. (English)** to prevent Telex/VNI hotkey issues.
* Prevents the screen and system from going to sleep during the test.
* Sets Windows power mode to **Balanced** and Battery Saver threshold to **30%**.
* Verifies Wi-Fi connectivity and checks if the battery is charged to at least 99%.

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
3. Double-click **`start_test.command`** in Finder to run.

### 🔌 Windows:
* Double-click **`start_test.bat`** to automatically configure, install dependencies, and start the test.

> [!TIP]
> **Disable YouTube & Facebook tests**: To run only web and office tests, execute `python test.py 1` in your terminal.
> 
> **Windows ARM Note**: If dependency installation fails, download [Visual Studio](https://visualstudio.microsoft.com/downloads/) and install the **Desktop Development with C++** workload.

---

## 📊 Result Analysis (Logs)
Once the laptop shuts down due to battery depletion, plug in the charger, boot it back up, and analyze the logs:

* **Windows**: Double-click **`analyze_battery.bat`**
* **macOS**: Double-click **`analyze_battery.command`**

This generates a detailed battery life report printed to the screen and saved to **`battery_report.txt`**.
