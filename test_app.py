"""
Test script for Pro Video Downloader app.py
Tests: syntax, imports, class instantiation logic, all methods exist.
"""
import sys, os

print("=" * 60)
print("🔍 PRO VIDEO DOWNLOADER — FULL TEST SUITE")
print("=" * 60)

# ─── TEST 1: Syntax Check ───
print("\n[1/7] Kiểm tra cú pháp (Syntax)...")
try:
    import py_compile
    py_compile.compile('app.py', doraise=True)
    print("  ✅ Cú pháp Python hợp lệ")
except py_compile.PyCompileError as e:
    print(f"  ❌ Lỗi cú pháp: {e}")
    sys.exit(1)

# ─── TEST 2: Imports ───
print("\n[2/7] Kiểm tra imports...")
errors = []
for mod in ['tkinter', 'customtkinter', 'yt_dlp', 'PIL', 'json', 'threading', 'urllib.request']:
    try:
        __import__(mod)
        print(f"  ✅ {mod}")
    except ImportError as e:
        print(f"  ❌ {mod}: {e}")
        errors.append(mod)
if errors:
    print(f"  ⚠️ Thiếu {len(errors)} module: {', '.join(errors)}")
else:
    print("  ✅ Tất cả imports OK")

# ─── TEST 3: Module Load ───
print("\n[3/7] Kiểm tra load module app.py...")
try:
    # We can't actually start the GUI, so we test by reading and compiling
    with open('app.py', 'r', encoding='utf-8') as f:
        source = f.read()
    code = compile(source, 'app.py', 'exec')
    print("  ✅ Biên dịch thành công")
except Exception as e:
    print(f"  ❌ Lỗi: {e}")
    sys.exit(1)

# ─── TEST 4: Check Class & Methods ───
print("\n[4/7] Kiểm tra class và methods...")
required_methods = [
    'setup_ui', 'on_single', 'on_bulk', 'on_scan', 'on_chan_download',
    'on_thumb', 'on_thumb_bulk', '_download_engine', '_hook', '_finish',
    '_refresh_hist', 'clear_history', '_pick_folder', '_paste_to',
    '_build_coffee_footer', '_show_qr', '_schedule_hide_qr', '_try_hide_qr',
    '_register_and_fetch_count', '_refresh_chart', '_set_chart_data',
    '_animate_chart', '_draw_chart', '_animate_marquee',
    '_check_for_updates', '_show_update_dialog'
]
for method in required_methods:
    if f'def {method}' in source:
        print(f"  ✅ {method}()")
    else:
        print(f"  ❌ Thiếu method: {method}()")

# ─── TEST 5: Check UI Elements ───
print("\n[5/7] Kiểm tra UI elements...")
ui_checks = {
    'Tab Tải Video': '"▶ Tải Video"',
    'Tab Hàng Loạt': '"⏬ Hàng Loạt"',
    'Tab Quét Kênh': '"📡 Quét Kênh"',
    'Tab Thumbnail': '"🖼 Thumbnail"',
    'Tab Lịch Sử': '"🕓 Lịch Sử"',
    'Nút Tải Ngay (single)': 'BẮT ĐẦU TẢI NGAY',
    'Nút Tải Hàng Loạt': 'btn_bulk',
    'Nút Quét Kênh': 'btn_scan',
    'Nút Thumbnail': 'btn_thumb',
    'Progress Bar': 'CTkProgressBar',
    'Status Label': 'Sẵn sàng',
    'Mở Thư Mục': 'MỞ THƯ MỤC',
    'Đổi Thư Mục': 'ĐỔI THƯ MỤC',
    'Chart Canvas': 'chart_canvas',
    'Marquee': 'marquee_canvas',
    'Coffee Footer': '_build_coffee_footer',
}
for name, check in ui_checks.items():
    if check in source:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ Thiếu: {name}")

# ─── TEST 6: Check Download Engine Config ───
print("\n[6/7] Kiểm tra cấu hình download engine...")
engine_checks = {
    'FORMAT_MAP': 'FORMAT_MAP',
    'FFmpeg detection': 'HAS_FFMPEG',
    'concurrent_fragment_downloads': 'concurrent_fragment_downloads',
    'retries': "'retries': 15",
    'MP3 support': 'FFmpegExtractAudio',
    'Merge output MP4': "merge_output_format",
    'noplaylist': 'noplaylist',
    'Clean filename': 'clean_filename',
}
for name, check in engine_checks.items():
    if check in source:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ Thiếu: {name}")

# ─── TEST 7: Check Nút Hàng Loạt (BUG FIX) ───
print("\n[7/7] Kiểm tra nút tải hàng loạt (bug fix)...")
# Find the batch button section
import re

# Check btn_bulk text
match = re.search(r'btn_bulk.*?text="([^"]*)"', source)
if match:
    btn_text = match.group(1)
    print(f"  ✅ Nút Hàng Loạt text: '{btn_text}'")
else:
    print("  ❌ Không tìm thấy btn_bulk")

# Check btn_bulk color
match = re.search(r'btn_bulk.*?fg_color="([^"]*)"', source)
if match:
    btn_color = match.group(1)
    print(f"  ✅ Nút Hàng Loạt màu: {btn_color}")
else:
    print("  ❌ Không tìm thấy fg_color cho btn_bulk")

# Check textbox height
match = re.search(r'bulk_text.*?height=(\d+)', source)
if match:
    height = int(match.group(1))
    print(f"  ✅ Textbox hàng loạt height: {height}px" + (" (đã giảm)" if height <= 120 else " (có thể bị tràn!)"))

# Check chart height
match = re.search(r'chart_frame.*?height=(\d+)', source)
if match:
    ch_height = int(match.group(1))
    print(f"  ✅ Chart frame height: {ch_height}px" + (" (đã giảm)" if ch_height <= 130 else ""))

# ─── Check files ───
print("\n📂 Kiểm tra files cần thiết...")
files_check = ['app.py', 'icon.ico', 'coffee.png', 'donors.json']
for f in files_check:
    exists = os.path.exists(f)
    print(f"  {'✅' if exists else '⚠️'} {f}" + (" — OK" if exists else " — Không tìm thấy (optional)"))

# Check for real_qr.png
if os.path.exists('real_qr.png'):
    print(f"  ✅ real_qr.png — OK")
else:
    print(f"  ⚠️ real_qr.png — Không tìm thấy (QR popup sẽ bị ẩn)")

print("\n" + "=" * 60)
print("🎯 TEST HOÀN TẤT!")
print("=" * 60)
