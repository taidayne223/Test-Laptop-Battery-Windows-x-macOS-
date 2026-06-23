# 🔋 Công Cụ Test Pin Laptop (Windows & macOS)

Công cụ tự động **giả lập các tác vụ dùng máy hằng ngày** — lướt web, đọc tài liệu Word/Excel và xem YouTube — để đo **thời lượng pin thực tế** của laptop. Máy cứ tự chạy cho đến khi hết pin và tắt, sau đó bạn mở file phân tích để xem kết quả.

Mục tiêu: cho ra con số pin **giống nhau, công bằng** giữa các máy và giữa Windows với macOS, để so sánh chính xác.

* **Người sáng lập ý tưởng:** Duy Luân Dể Thương
* **Người phát triển:** Tài Xài Tech

---

## 💻 Cần chuẩn bị gì?

* **Hệ điều hành:** Windows 11 (x86/x64/ARM64) hoặc macOS 12 trở lên (Apple Silicon)
* **Phần mềm:**
  * [Python 3](https://www.python.org/downloads/) — nền tảng để chạy công cụ
  * Google Chrome — trình duyệt dùng để test web và YouTube
  * Microsoft Office (Word, Excel) — để test tác vụ văn phòng

> 💡 Lần đầu cài Python trên Windows, nhớ **tick vào ô "Add Python to PATH"** ở màn hình cài đặt.

---

## 🚀 Cách chạy (rất đơn giản)

### 🪟 Trên Windows
Chỉ cần **bấm đúp vào file `Windows bat dau.bat`**.

Công cụ sẽ tự làm hết phần còn lại: xin quyền Administrator, cài các thư viện cần thiết, tối ưu máy rồi bắt đầu test. Bạn không cần gõ lệnh gì cả.

### 🍏 Trên macOS
1. Mở **Terminal**, lần đầu tiên cấp quyền chạy cho các file (chỉ làm **một lần duy nhất**):
   ```sh
   cd đường/dẫn/tới/thư-mục-này
   chmod +x *.command
   ```
2. Sau đó **bấm đúp vào `Macos bat dau.command`** trong Finder để chạy.

> 🛑 Muốn **dừng test** bất cứ lúc nào: bấm `Ctrl + C` trong cửa sổ đang chạy.

---

## ⚙️ Công cụ làm gì khi chạy?

### 1. Tự động tối ưu máy (1-Click Setup)
Để kết quả công bằng, công cụ tự chỉnh máy về một trạng thái chuẩn:
- Đặt **độ sáng màn hình** theo cấu hình và **âm lượng về 0%**.
- Chỉnh **tần số quét** (refresh rate) về mức cấu hình trên Windows nếu hỗ trợ.
- **Tắt tự động ngủ / tắt màn hình / ngủ đông** khi đang chạy bằng pin.
- Tắt các tính năng tự đổi độ sáng (adaptive brightness, CABC) để độ sáng luôn cố định.
- Trên macOS: chuyển bàn phím về **U.S. (English)** để tránh lỗi gõ tắt Telex/VNI, và thử tắt **Low Power Mode**.
- Kiểm tra **kết nối Wi-Fi**, kiểm tra **mức pin tối thiểu**, và có thể yêu cầu **rút sạc** trước khi bắt đầu.

### 2. Lặp lại liên tục 3 nhóm tác vụ (cho tới khi hết pin)
1. **Lướt web** — mở và cuộn qua 5 trang web.
2. **Văn phòng** — mở và cuộn 3 file Word + 1 file Excel.
3. **Xem YouTube** — phát video YouTube và tự hard-refresh để giữ playback ổn định.

Mọi đường link, thời lượng, độ sáng... đều chỉnh được trong file **`benchmark_config.json`** (xem mục bên dưới).

---

## 🎬 Chỉ muốn test YouTube hoặc bỏ qua YouTube?

* **Chỉ test YouTube:** bấm đúp `start_youtube_only.bat` (Windows), hoặc chạy `python test_youtube_only.py`.
* **Bỏ qua YouTube** (chỉ web + văn phòng): chạy `python test.py 1` trong Terminal.

> 🧯 **Về lỗi YouTube hay bị "đơ" / đen màn hình:** YouTube có cơ chế tự phát video tiếp theo, đôi khi nhảy vào đoạn gần hết video rồi treo hoặc kẹt ở màn hình loading. Công cụ đã xử lý bằng cách **hard-refresh trang**, **tự tua video về đầu** (nhấn phím `0`) và **hard-refresh định kỳ** trong lúc xem.

---

## 📊 Xem kết quả sau khi máy hết pin

Khi laptop tự tắt vì cạn pin: **cắm sạc, bật máy lên lại**, rồi mở file phân tích:

* **Windows:** bấm đúp `Windows phan tich file.bat`
* **macOS:** bấm đúp `Macos phan tich file.command`

Công cụ sẽ in ra **báo cáo thời lượng pin chi tiết** (mỗi lần xả pin kéo dài bao lâu, tụt bao nhiêu %, tốc độ xả mỗi giờ, độ chai pin...) và lưu vào file **`battery_report.txt`**. Cuối báo cáo còn có sẵn một dòng để **copy-paste thẳng vào Google Sheets**.

---

## 🛠️ Tùy chỉnh bài test (`benchmark_config.json`)

Bạn có thể đổi cách test mà **không cần đụng vào code** — chỉ sửa file `benchmark_config.json`. Vài thông số hay dùng:

| Thông số | Ý nghĩa |
|---|---|
| `system.brightness_percent` | Độ sáng màn hình khi test (%) |
| `system.refresh_rate_hz` | Tần số quét màn hình mục tiêu (Windows) |
| `system.minimum_start_battery_percent` | Mức pin tối thiểu nên có trước khi test |
| `system.require_unplugged` | Bắt buộc rút sạc mới cho chạy |
| `browser_test.urls` | Danh sách trang web để test lướt web |
| `youtube_test.urls` | Danh sách video YouTube để test |
| `youtube_test.total_seconds_per_video` | Thời gian xem mỗi video (giây) |
| `youtube_test.reseek_interval_seconds` | Cứ sau bao nhiêu giây thì tua video về đầu (chống lỗi treo). Để `0` nếu muốn tắt |
| `youtube_test.auto_hard_reload_interval_seconds` | Cứ sau bao nhiêu giây thì hard-refresh lại trang YouTube trong lúc xem. Để `0` nếu muốn tắt |
| `youtube_test.max_auto_hard_reloads` | Số lần hard-refresh thêm tối đa trong một video, không tính lần hard-refresh lúc bắt đầu |

> ⚠️ File này là dạng JSON: nhớ giữ đúng dấu phẩy, ngoặc và dấu nháy. Nếu lỡ sửa sai, công cụ vẫn chạy được bằng cấu hình mặc định và sẽ báo cảnh báo.

---

## ❓ Câu hỏi thường gặp

**Đang test có dùng máy được không?**
Không nên. Công cụ tự điều khiển chuột và bàn phím, bạn cứ để máy chạy yên một mình cho tới khi hết pin.

**Mất bao lâu?**
Tùy pin từng máy — thường vài tiếng, chạy cho đến khi máy tự tắt.

**Có hại pin không?**
Không. Đây chỉ là một chu kỳ xả pin bình thường như khi bạn dùng máy hằng ngày.

**Windows ARM cài thư viện bị lỗi?**
Tải [Visual Studio](https://visualstudio.microsoft.com/downloads/) và cài gói **Desktop Development with C++**, rồi chạy lại.

---

Chúc bạn test pin vui vẻ! Nếu thấy hữu ích, đừng quên ⭐ cho dự án nhé.
