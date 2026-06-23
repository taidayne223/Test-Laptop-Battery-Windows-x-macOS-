# 📌 IMPORTANT NOTE — Tài liệu bàn giao dự án

> File này dành cho **lập trình viên hoặc AI agent tiếp nhận dự án**. Nó mô tả toàn bộ kiến trúc, luồng chạy, các quyết định kỹ thuật và những điểm cần lưu ý để tiếp tục phát triển mà không phải đọc lại từ đầu. (README.md là tài liệu cho người dùng cuối; file này là tài liệu cho người code.)

Cập nhật lần cuối: 2026-06-22

---

## 1. Mục tiêu dự án

Đo **thời lượng pin thực tế** của laptop bằng cách tự động giả lập tác vụ dùng máy hằng ngày (lướt web, văn phòng, YouTube), chạy lặp vô hạn cho tới khi máy hết pin và tắt. Sau đó parse log + báo cáo pin của hệ điều hành để dựng báo cáo so sánh.

Yêu cầu cốt lõi: **kết quả phải nhất quán và công bằng** giữa các máy và giữa Windows ↔ macOS. Vì vậy phần lớn độ phức tạp nằm ở bước "chuẩn hoá môi trường" (độ sáng, refresh rate, tắt sleep/adaptive brightness, âm lượng, input source...).

- **Ngôn ngữ:** Python 3 thuần.
- **Phụ thuộc:** `pyautogui`, `psutil`, `screen-brightness-control` (xem `requirements.txt`).
- **Nền tảng:** Windows 11 (x86/x64/ARM64) và macOS 12+ (Apple Silicon).

---

## 2. Cấu trúc thư mục

```
.
├── README.md                       # Hướng dẫn cho người dùng cuối (tiếng Việt)
├── IMPORTANT_NOTE.md               # File này — bàn giao kỹ thuật
├── requirements.txt                # pyautogui, psutil, screen-brightness-control
├── benchmark_config.json           # Cấu hình runtime (override DEFAULT_CONFIG)
│
├── test.py                         # ENTRY: bài test đầy đủ (web + office + youtube), lặp vô hạn
├── test_youtube_only.py            # ENTRY: chỉ lặp YouTube
├── test_quick_youtube_word.py      # ENTRY: lặp nhanh Word ↔ YouTube (dùng để dev/thử nhanh)
├── datetime_calculator.py          # ENTRY: phân tích log + báo cáo pin (chạy sau khi test xong)
│
├── test_cases/
│   ├── browser_test.py             # run_browser_test(): mở & cuộn các URL
│   ├── office_test.py              # run_office_test(quick=False): mở & cuộn Word/Excel
│   └── youtube_test.py             # run_youtube_test(duration=None): phát video YouTube
│
├── utils/
│   ├── __init__.py                 # Hàm tiện ích: mở app/browser, kill process, scroll, đóng tab...
│   ├── config.py                   # Load/merge config (DEFAULT_CONFIG + file JSON)
│   ├── battery_utils.py            # get_battery_level(): đọc % pin (+ mAh trên macOS), ghi log
│   └── system_setup.py             # optimize_system(): chuẩn hoá toàn bộ môi trường máy
│
├── test_files/office/              # File mẫu để test văn phòng (3 docx + 1 xlsx) — commit kèm repo
│
├── Windows bat dau.bat             # Launcher Windows: tạo venv, cài deps, chạy test.py (cần Admin)
├── start_youtube_only.bat          # Launcher Windows: chạy test_youtube_only.py
├── Windows phan tich file.bat      # Launcher Windows: chạy datetime_calculator.py
├── Macos bat dau.command           # Launcher macOS: venv + deps + caffeinate python3 test.py
└── Macos phan tich file.command    # Launcher macOS: chạy datetime_calculator.py
```

**File sinh ra lúc chạy (đã đưa vào `.gitignore`, KHÔNG commit):**
`logfilename.log` (log pin), `battery_report.txt` (báo cáo), `battery-report.html` (Windows powercfg), `battery_test_env/` (venv), `__pycache__/`.

---

## 3. Luồng chạy (data flow)

### Khi test
1. Launcher (.bat/.command) tạo venv `battery_test_env`, cài `requirements.txt`, gọi entry script.
2. Entry script gọi `optimize_system()` (system_setup.py) → chuẩn hoá máy + chờ điều kiện pin/sạc.
3. Một **thread nền daemon** (`information_process`) chạy `get_battery_level()` mỗi `reporting.battery_log_interval_seconds` giây → ghi `logfilename.log` với format `YYYY-MM-DD HH:MM:SS,ms | Battery level: NN ...`.
4. **Thread chính** chạy vòng lặp `while True` gọi lần lượt các `run_*_test()`. (GUI automation phải ở main thread.)
5. Máy hết pin → tắt. Log đã lưu sẵn trên đĩa.

### Khi phân tích (`datetime_calculator.py`)
1. Lấy thông tin pin hệ thống: Windows dùng `powercfg /batteryreport` (HTML) → parse; macOS dùng `ioreg -rn AppleSmartBattery` → regex.
2. `parse_log_file()` đọc `logfilename.log` → list event (START_TEST / LEVEL).
3. `detect_cycles()` gom event thành các **chu kỳ xả pin** (heuristic: phát hiện sạc lại, gap thời gian, mốc 100%/4%...).
4. `generate_report()` dựng báo cáo text + dòng TSV để dán Google Sheets. Lưu `battery_report.txt`.

---

## 4. Hệ thống cấu hình (quan trọng)

- `utils/config.py` chứa `DEFAULT_CONFIG` (nguồn chân lý). Lúc runtime, nó **deep-merge** đè `benchmark_config.json` lên trên (nếu file thiếu/sai JSON → fallback default + cảnh báo).
- **Quy tắc khi thêm config mới:** thêm key vào CẢ `DEFAULT_CONFIG` (config.py) VÀ `benchmark_config.json`. Khi đọc trong code nên dùng `config.get("key", default)` để an toàn nếu user xài file JSON cũ.
- `platform_seconds(values, platform_name)`: cho phép một giá trị thời gian khác nhau theo OS dạng `{"windows": x, "macos": y, "default": z}`. Hiện áp dụng cho `page_load_wait_seconds` (browser/office). Có thể mở rộng cho YouTube nếu cần.
- Helper khác: `clamp_percent()` (0–100), `positive_int()`.

---

## 5. Những điểm kỹ thuật cần lưu ý (gotchas)

- **Tự động hoá bằng toạ độ + hotkey** (`pyautogui`): nhạy cảm với focus cửa sổ và độ phân giải. Trước khi gửi hotkey, code thường click giữa màn hình để lấy focus. `pyautogui.FAILSAFE = False` được bật để chuột chạm góc không làm dừng test.
- **YouTube hotkey chỉ ăn khi player có focus.** Trong `youtube_test.py`, sau hard-refresh (`Ctrl/Cmd+Shift+R`) phải click lại player rồi mới nhấn `t` (theater) / `0` (về đầu video).
- **Chống YouTube autoplay-freeze / black loading screen:** YouTube tự phát video kế tiếp, đôi khi nhảy vào đoạn gần hết rồi treo, hoặc bị kẹt màn hình đen/loading. Giải pháp: hard-refresh lúc setup, bấm `t` vào Theater mode, hard-refresh thêm lần nữa nếu `youtube_test.hard_reload_after_theater_mode_enabled` bật, nhấn `0` để tua về đầu, **re-seek định kỳ** mỗi `youtube_test.reseek_interval_seconds` giây, và **hard-refresh định kỳ** theo `youtube_test.auto_hard_reload_interval_seconds` với giới hạn `youtube_test.max_auto_hard_reloads`. Đặt `reseek_interval_seconds: 0` hoặc `auto_hard_reload_interval_seconds: 0` để tắt từng cơ chế.
- **Đóng app sạch để tránh popup "Save changes":** trên macOS dùng AppleScript `quit saving no` trước, rồi `pkill` fallback (`utils/__init__.py`: `clean_office`, `clean_browser`).
- **Ưu tiên Chrome:** `open_in_browser()` dò Chrome theo registry/đường dẫn chuẩn, fallback Edge → trình duyệt mặc định. Truyền cờ `--disable-session-crashed-bubble`, `--hide-crash-restore-bubble` để tránh bong bóng "khôi phục trang".
- **macOS dùng `caffeinate -i -d`** (trong launcher) để chống ngủ — KHÔNG chỉnh setting hệ thống. Windows thì tắt timeout bằng `powercfg`.
- **Windows cần quyền Administrator** để chỉnh registry (CABC), refresh rate, một số powercfg. Launcher tự xin UAC elevation.
- **macOS input source về U.S.**: tránh bộ gõ Telex/VNI nuốt hotkey. Làm qua Carbon TIS API bằng ctypes (`switch_macos_input_to_us`).
- **Đơn vị dung lượng pin khác nhau:** Windows = mWh (powercfg), macOS = mAh (ioreg, kèm Voltage để quy ra Wh). `generate_report()` xử lý cả hai qua tham số `battery_unit` + `voltage_mv`.
- **KHÔNG còn phụ thuộc `wmic`** (đã deprecate, gỡ khỏi Windows 11 24H2+). `datetime_calculator.py` dùng `Get-CimInstance` (PowerShell) làm chính, `wmic` chỉ còn là fallback qua helper `query_windows_info(cim_cmd, wmic_args)`.

---

## 6. Thay đổi gần đây (phiên 2026-06-23)

1. **youtube_test.py** — thêm click lấy focus sau hard-refresh; hard-refresh thêm ngay sau khi bật Theater mode; thay `sleep` dài bằng vòng lặp re-seek `0` định kỳ chống autoplay-freeze; thêm hard-refresh định kỳ trong lúc xem để thoát YouTube black/loading screen.
2. **config.py + benchmark_config.json** — thêm `youtube_test.hard_reload_after_theater_mode_enabled`, `youtube_test.reset_to_start_enabled`, `youtube_test.reseek_interval_seconds` (mặc định 60), `youtube_test.auto_hard_reload_interval_seconds` (mặc định 120) và `youtube_test.max_auto_hard_reloads` (mặc định 2).
3. **datetime_calculator.py** — thay `wmic` → `Get-CimInstance` (RAM, model, CPU, GPU); giữ `wmic` làm fallback. Thêm helper `_powershell_first_line`, `_wmic_first_value`, `query_windows_info`.
4. **test.py** — sửa typo `enable` → `enabled`.
5. **battery_utils.py** — chuyển `logging.basicConfig` ra ngoài hàm (chạy 1 lần lúc import thay vì mỗi lần đọc pin).
6. **Dọn repo** — xoá `__pycache__`, siết `.gitignore` (output files, `~$*`, `.DS_Store`).

---

## 7. Ý tưởng phát triển tiếp (TODO gợi ý)

- Cho `total_seconds_per_video` hỗ trợ dạng `{windows, macos, default}` qua `platform_seconds` để cân theo máy.
- Xuất log song song dạng **CSV/JSON** để dễ vẽ biểu đồ đường xả pin.
- `browser_test` hiện mở dồn 5 tab (không đóng giữa các URL) — có thể đóng tab mỗi vòng cho nhất quán với `youtube_test`.
- Thêm tuỳ chọn **tắt hẳn autoplay** của YouTube (toggle UI) như giải pháp thay thế cách re-seek.
- Viết unit test cho `detect_cycles()` (phần heuristic dễ hồi quy nhất) với vài file log mẫu.
- Cân nhắc cho phép chọn trình duyệt / số lượng URL qua config thay vì hard-code.

---

## 8. Cách kiểm tra nhanh (không cần laptop thật)

```bash
# Compile toàn bộ
python3 -m py_compile test.py test_youtube_only.py test_quick_youtube_word.py \
  datetime_calculator.py test_cases/*.py utils/*.py

# Validate config JSON
python3 -c "import json; json.load(open('benchmark_config.json')); print('JSON OK')"
```

Lưu ý: `import utils.*` sẽ kéo theo `pyautogui` (cần môi trường có GUI/đã cài). Khi test logic thuần (vd config, datetime_calculator) nên import module trực tiếp qua `importlib` để né phụ thuộc GUI.

---

## 9. Quy ước

- Code và comment kỹ thuật viết bằng **tiếng Anh**; tài liệu người dùng (README) viết **tiếng Việt**.
- Mọi thông số điều chỉnh được nên đặt trong config, **không hard-code** trong test case.
- Khi tự động hoá GUI: luôn lấy focus trước khi gửi hotkey, và bọc lệnh hệ thống trong `try/except` + in `[OK]`/`[WARNING]` để không làm sập cả bài test khi một bước phụ thất bại.
