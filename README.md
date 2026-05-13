# ⚡ Pro Video Downloader — by Hoàng Đức

> Tải video chất lượng cao từ **YouTube, TikTok, Facebook, Instagram, Twitter/X** và **1000+ nền tảng khác** chỉ với 1 click!

---

## 🎬 Video Hướng Dẫn

[![Xem Video Hướng Dẫn](https://img.youtube.com/vi/Bqm_FlEB83A/maxresdefault.jpg)](https://youtu.be/Bqm_FlEB83A)

👉 **[Xem Video Hướng Dẫn trên YouTube](https://youtu.be/Bqm_FlEB83A)**

---

## 📥 Tải Về & Cài Đặt

### Cách 1: Tải file .exe (Khuyến nghị)

1. Vào trang **[Releases](../../releases/latest)**
2. Tải file **`Pro Video Downloader.exe`**
3. Chạy file — **Không cần cài đặt**, chạy trực tiếp!

> ⚠️ Windows SmartScreen có thể cảnh báo "Unknown Publisher". Click **"More info"** → **"Run anyway"** để chạy.

### Cách 2: Chạy từ Source Code (Dành cho Developer)

```bash
# Clone repo
git clone https://github.com/hoangvant77internet-sudo/pro-video-downloader.git
cd pro-video-downloader

# Cài dependencies
pip install -r requirements.txt

# Chạy app
python app.py
```

---

## ✨ Tính Năng

| Tính năng | Mô tả |
|-----------|--------|
| ▶ **Tải Video** | Dán link → chọn chất lượng → tải ngay |
| ⏬ **Tải Hàng Loạt** | Dán nhiều link cùng lúc, tải tất cả 1 lần |
| 📡 **Quét Kênh** | Quét toàn bộ video của 1 kênh YouTube/Playlist và tải hàng loạt |
| 🖼 **Tải Thumbnail** | Tải ảnh thumbnail chất lượng cao (lẻ + hàng loạt) |
| 🕓 **Lịch Sử** | Lưu lại lịch sử tải, tối đa 500 video |
| 📁 **Tùy chọn thư mục** | Chọn thư mục lưu file theo ý muốn |
| 📊 **Tracking toàn cầu** | Đếm lượt sử dụng từ tất cả users (Google Sheet API) |
| 📈 **Biểu đồ 30 ngày** | Bar chart animated hiển thị thống kê 30 ngày gần nhất |
| 🔄 **Tự động cập nhật** | Kiểm tra phiên bản mới từ GitHub Releases |
| ☕ **Mời Cafe QR** | Hover vào icon café để hiện mã QR chuyển khoản |
| ⚡ **Đa luồng Turbo** | 8 luồng tải đồng thời, retry 15 lần, chunk 10MB |
| 🎵 **Trích xuất MP3** | Tải chỉ audio dưới dạng MP3 (cần FFmpeg) |

---

## 🎯 Chất Lượng Hỗ Trợ

- 🏆 **Tốt Nhất (Best)** — Tự động chọn chất lượng cao nhất
- 📺 **4K (2160p)** — Ultra HD
- 🖥 **2K (1440p)** — Quad HD
- 💻 **1080p** — Full HD
- 📱 **720p** — HD
- 📱 **480p** — SD
- 🎵 **Chỉ Lấy Nhạc (MP3)** — Trích xuất audio

---

## 🌐 Nền Tảng Hỗ Trợ

YouTube • TikTok • Facebook • Instagram • Twitter/X • Reddit • Vimeo • Dailymotion • Bilibili • Twitch • SoundCloud và **1000+ trang web khác**

---

## 💡 Yêu Cầu Hệ Thống

- **OS:** Windows 10/11 (64-bit)
- **RAM:** 4 GB trở lên
- **Kết nối:** Internet ổn định
- **FFmpeg** (khuyến nghị): Cài FFmpeg để có chất lượng tốt nhất. [Tải FFmpeg](https://ffmpeg.org/download.html)

> 💡 **Không có FFmpeg?** App vẫn hoạt động bình thường, chỉ giới hạn ở chất lượng pre-merged.

---

## 📞 Liên Hệ & Hỗ Trợ

- 💻 **Dev:** Hoàng Đức
- 📘 **Facebook:** [facebook.com/ducserving](https://www.facebook.com/ducserving)
- ☕ **Mời Cafe:** Quét mã QR trong app để ủng hộ tác giả!

---

## 📋 Changelog

### v1.9.9 (2026-05-13)
- 🔥 **ULTIMATE TURBO Edition**
- ⚡ Tải đa luồng 8 threads + retry 15 lần + chunk 10MB
- 🖼️ Tải Thumbnail hàng loạt (bulk thumbnail download)
- 📊 Biểu đồ thống kê animated 30 ngày (bar chart)
- 🔄 Tự động kiểm tra cập nhật từ GitHub Releases
- ☕ QR popup hover — mời cafe tác giả
- 🎨 Nút "⚡ BẮT ĐẦU TẢI NGAY" cho tab Hàng Loạt
- 📐 Tối ưu layout UI — hiển thị đầy đủ trên mọi tab
- 🛡️ Xử lý lỗi chi tiết — hiện rõ link nào thất bại và lý do
- 📋 Nút paste nhanh (📋) cho ô nhập link
- 🏷️ Marquee chạy chữ cảm ơn người dùng

### v1.9.0 (2026-05-12)
- 🚀 **Professional Edition**
- ⚡ Giao diện mới với Header Logo chuyên nghiệp
- 📊 Hệ thống Tracking toàn cầu (Google Sheet API)
- 🖼️ Fix lỗi hiển thị Icon và Logo trên Windows
- 🔧 Tối ưu hóa tốc độ tải và độ ổn định

### v1.0.0 (2026-04-29)
- 🎉 Phiên bản đầu tiên
- ▶ Tải video đơn lẻ từ 1000+ nền tảng
- ⏬ Tải hàng loạt nhiều link cùng lúc
- 📡 Quét & tải toàn bộ kênh YouTube/TikTok
- 🖼 Tải thumbnail chất lượng cao
- 🕓 Lịch sử tải video
- 📁 Tùy chọn thư mục lưu

---

⭐ **Nếu thấy hữu ích, hãy Star repo này để ủng hộ!** ⭐
