import os, re, json, threading, time, tkinter as tk, urllib.request, webbrowser, shutil, uuid, hashlib, sys, tempfile, subprocess
from tkinter import messagebox, filedialog
import customtkinter as ctk
import yt_dlp
from PIL import Image

HAS_FFMPEG = shutil.which('ffmpeg') is not None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

DOWNLOAD_PATH = os.path.join(os.path.expanduser('~'), 'Downloads', 'VideoDownloader')
# --- App Data Path (Hidden) ---
DATA_DIR = os.path.join(os.path.expanduser('~'), '.pro_video_downloader')
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(DATA_DIR, 'download_history.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
VISITS_FILE = os.path.join(DATA_DIR, 'visits.json')
DEVICE_ID_FILE = os.path.join(DATA_DIR, 'device_id.txt')
BASE_VISITS = 0

# ============================================================
# COUNTER_API_URL: Dán URL Web App từ Google Apps Script vào đây
# (Sau khi Deploy > New deployment > Web App > Anyone)
# ============================================================
COUNTER_API_URL = "https://script.google.com/macros/s/AKfycbxkNRnQQjz57dU7arArG-GEsNKDMlxRhsXdD-A8Je5VpOzczJVthWIPb_V2quTizj6RCw/exec"

APP_VERSION = "1.9.10"
GITHUB_REPO = "Ducpt88/pro-video-downloader"

def load_visits():
    """Load visit records from local file."""
    try:
        if os.path.exists(VISITS_FILE):
            with open(VISITS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except: pass
    return []

def save_visits(visits):
    """Save visit records to local file."""
    try:
        with open(VISITS_FILE, 'w', encoding='utf-8') as f:
            json.dump(visits, f, ensure_ascii=False)
    except: pass

def record_visit(event_type='open'):
    """Record a visit: POST to Google Sheet API (centralized) + save locally."""
    # Save locally first (always works)
    visits = load_visits()
    visits.append({
        'event': event_type,
        'time': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    save_visits(visits)
    # POST to Google Sheet API (centralized tracking)
    api_result = None
    if COUNTER_API_URL:
        try:
            device_id = get_device_id()
            payload = json.dumps({'device_id': device_id, 'event': event_type}).encode('utf-8')
            req = urllib.request.Request(
                COUNTER_API_URL,
                data=payload,
                headers={'Content-Type': 'application/json', 'User-Agent': 'ProVideoDownloader'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                api_result = json.loads(resp.read().decode('utf-8'))
        except Exception:
            pass
    return visits, api_result

def fetch_global_stats():
    """GET tổng lượt sử dụng từ Google Sheet (tất cả users)."""
    if not COUNTER_API_URL:
        return None
    try:
        req = urllib.request.Request(
            COUNTER_API_URL,
            headers={'User-Agent': 'ProVideoDownloader'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def get_daily_breakdown_local(visits, base_visits=0):
    """Fallback: use exact local events only, no fake base count."""
    from datetime import datetime, timedelta
    daily = []
    for idx in range(30):
        d = datetime.now() - timedelta(days=29 - idx)
        date_str = d.strftime('%Y-%m-%d')
        label = d.strftime('%d/%m')
        real = sum(1 for v in visits if v.get('time', '').startswith(date_str))
        daily.append({'date': label, 'count': real})
    return daily

DONORS_FILE = resource_path('donors.json')

# Google Sheet URL (Published as CSV)
# Tạo Google Sheet → cột A = tên người donate
# File → Share → Publish to web → chọn Sheet1 + CSV → Publish → copy URL vào đây
DONORS_SHEET_URL = "https://docs.google.com/spreadsheets/d/1zdKjf5LgZYfctJC9BbvPv7U0E31p7HIGK4wlYF4gM_I/export?format=csv"

def load_donors():
    """Load donor names: try Google Sheet first, then local file."""
    # Try fetching from Google Sheet
    if DONORS_SHEET_URL:
        try:
            req = urllib.request.Request(DONORS_SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                csv_text = resp.read().decode('utf-8')
            names = []
            for line in csv_text.strip().split('\n'):
                name = line.strip().strip('"').strip()
                if name and name.lower() != 'name' and name.lower() != 'tên':
                    names.append(name)
            if names:
                # Save to local file as cache
                try:
                    with open(DONORS_FILE, 'w', encoding='utf-8') as f:
                        json.dump(names, f, ensure_ascii=False)
                except: pass
                return names
        except: pass
    # Fallback: local file
    try:
        if os.path.exists(DONORS_FILE):
            with open(DONORS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except: pass
    return []

def get_device_id():
    """Generate or load a persistent unique device ID."""
    if os.path.exists(DEVICE_ID_FILE):
        try:
            with open(DEVICE_ID_FILE, 'r') as f:
                did = f.read().strip()
                if did: return did
        except: pass
    raw = f"{os.getenv('COMPUTERNAME', 'pc')}-{os.getenv('USERNAME', 'user')}-{uuid.getnode()}"
    device_id = hashlib.sha256(raw.encode()).hexdigest()[:16]
    try:
        with open(DEVICE_ID_FILE, 'w') as f: f.write(device_id)
    except: pass
    return device_id

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

PLATFORMS = "YouTube • TikTok • Facebook • Instagram • Twitter/X • Reddit • Vimeo • Dailymotion • Bilibili • Twitch • SoundCloud • 1000+ sites"

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return []

def save_history(data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f: json.dump(data[-500:], f, ensure_ascii=False, indent=2)
    except: pass

# Format khi có ffmpeg: tải riêng video+audio rồi merge → chất lượng cao nhất
_FMT_FFMPEG = {
    "Tốt Nhất (Best)": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    "4K (2160p)":       "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best",
    "2K (1440p)":       "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1440]+bestaudio/best",
    "1080p":            "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best",
    "720p":             "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best",
    "480p":             "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best",
    "Chỉ Lấy Nhạc (MP3)": "bestaudio/best",
}
# Format khi KHÔNG có ffmpeg: chỉ dùng file đã pre-merged (mp4 gộp sẵn)
_FMT_NOFFMPEG = {
    "Tốt Nhất (Best)": "best[ext=mp4]/best[ext=webm]/best",
    "4K (2160p)":       "best[height<=2160][ext=mp4]/best[height<=2160]",
    "2K (1440p)":       "best[height<=1440][ext=mp4]/best[height<=1440]",
    "1080p":            "best[height<=1080][ext=mp4]/best[height<=1080]",
    "720p":             "best[height<=720][ext=mp4]/best[height<=720]",
    "480p":             "best[height<=480][ext=mp4]/best[height<=480]",
    "Chỉ Lấy Nhạc (MP3)": "bestaudio/best",
}
FORMAT_MAP = _FMT_FFMPEG if HAS_FFMPEG else _FMT_NOFFMPEG

def clean_filename(raw, fallback_id="x"):
    if not raw or len(raw) < 3: raw = f"video_{fallback_id}"
    if len(raw) > 150: raw = raw[:150]
    c = re.sub(r'[\\/*?:"<>|]', " ", raw)
    return " ".join(c.split()).strip() or f"video_{fallback_id}"

class VideoDownloaderApp(ctk.CTk):
    FONT = "Helvetica Neue"
    def __init__(self):
        super().__init__()
        self.title("⚡ Pro Video Downloader — by Hoàng Đức")
        self.geometry("540x880")
        self.resizable(False, False)
        # Set window icon for titlebar + taskbar
        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            try:
                # Fallback for some Windows versions
                self.wm_iconbitmap(icon_path)
            except: pass
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        cfg = load_config()
        saved_path = cfg.get('download_path', DOWNLOAD_PATH)
        self.download_path = saved_path if os.path.isdir(saved_path) else DOWNLOAD_PATH
        self.history = load_history()
        self._last_hook_time = 0
        self._donate_imgs = None
        self._qr_visible = False
        self._global_stats = None
        self.setup_ui()
        # Start user counter in background (non-blocking)
        threading.Thread(target=self._register_and_fetch_count, daemon=True).start()
        # Check for updates in background
        threading.Thread(target=self._check_for_updates, daemon=True).start()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # tabview expands (Row 2)

        # === HEADER LOGO & TITLE ===
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Stylized Canvas Logo (Compact)
        self.logo_canvas = tk.Canvas(header_frame, bg="#1a1a2e", highlightthickness=0, width=40, height=40)
        self.logo_canvas.pack(side="left", padx=(14, 8), pady=6)
        self.logo_canvas.create_oval(2, 2, 38, 38, outline="#00b894", width=2)
        self.logo_canvas.create_oval(6, 6, 34, 34, outline="#55efc4", width=1)
        self.logo_canvas.create_text(20, 20, text="⚡", fill="#f1c40f", font=(self.FONT, 22, "bold"))
        
        title_subframe = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_subframe.pack(side="left", pady=6)
        
        ctk.CTkLabel(title_subframe, text="PRO VIDEO DOWNLOADER", 
                     font=ctk.CTkFont(family=self.FONT, size=16, weight="bold"),
                     text_color="#00b894").pack(anchor="w")
        ctk.CTkLabel(title_subframe, text="ULTIMATE TURBO v1.9.10", 
                     font=ctk.CTkFont(family=self.FONT, size=9),
                     text_color="#55efc4").pack(anchor="w")

        # === MARQUEE (row 1) ===
        self.marquee_canvas = tk.Canvas(self, bg="#1a1a2e", highlightthickness=0, height=22)
        self.marquee_canvas.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self._marquee_x = 540
        self._marquee_str = "✨ Cảm ơn bạn đã sử dụng app của Đức!  ❤️  Hãy theo dõi để nhận thêm công cụ mới nha!  🚀  facebook.com/ducserving     •     "
        self._animate_marquee()

        self.tabview = ctk.CTkTabview(self, corner_radius=20, segmented_button_fg_color="#1a1a2e", 
                                     segmented_button_selected_color="#00b894", 
                                     segmented_button_selected_hover_color="#00a381",
                                     segmented_button_unselected_color="#2c3e50")
        self.tabview.grid(row=2, column=0, padx=16, pady=(8, 8), sticky="nsew")
        self.tabview.add("▶ Tải Video")
        self.tabview.add("⏬ Hàng Loạt")
        self.tabview.add("📡 Quét Kênh")
        self.tabview.add("🖼 Thumbnail")
        self.tabview.add("🕓 Lịch Sử")
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(family=self.FONT, size=12, weight="bold"))

        # === TAB 1: SINGLE ===
        t1 = self.tabview.tab("▶ Tải Video")
        t1.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t1, text=f"Hỗ trợ: {PLATFORMS}", font=ctk.CTkFont(family=self.FONT, size=10),
            text_color="#666", wraplength=460).pack(pady=(12, 4))
        
        uf = ctk.CTkFrame(t1, fg_color="transparent"); uf.pack(pady=(10, 10), fill="x", padx=20)
        self.single_url = ctk.CTkEntry(uf, placeholder_text="Dán link video tại đây...", height=50,
            font=ctk.CTkFont(family=self.FONT, size=14), corner_radius=10)
        self.single_url.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(uf, text="📋", width=50, height=50, command=lambda: self._paste_to(self.single_url),
            font=ctk.CTkFont(size=20), fg_color="#444", hover_color="#555", corner_radius=10).pack(side="right")
        
        qf = ctk.CTkFrame(t1, fg_color="transparent"); qf.pack(pady=(5, 15))
        ctk.CTkLabel(qf, text="Chất lượng:", font=ctk.CTkFont(family=self.FONT, size=13)).pack(side="left", padx=(0, 10))
        self.q_menu = ctk.CTkOptionMenu(qf, width=220, height=36, values=list(FORMAT_MAP.keys()), corner_radius=8, fg_color="#2c3e50")
        self.q_menu.pack(side="left")
        
        self.btn_single = ctk.CTkButton(t1, text="⚡  BẮT ĐẦU TẢI NGAY", command=self.on_single, width=280, height=54,
            font=ctk.CTkFont(family=self.FONT, size=16, weight="bold"), fg_color="#00b894", hover_color="#00a381", corner_radius=12)
        self.btn_single.pack(pady=(10, 10))

        # === TAB 2: BULK ===
        t2 = self.tabview.tab("⏬ Hàng Loạt")
        t2.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t2, text="Dán danh sách link (mỗi dòng 1 link)",
            font=ctk.CTkFont(family=self.FONT, size=14, weight="bold")).pack(pady=(10, 6))
        self.bulk_text = ctk.CTkTextbox(t2, width=480, height=110,
            font=ctk.CTkFont(family=self.FONT, size=12), corner_radius=10, border_width=1, border_color="#34495e")
        self.bulk_text.pack(pady=(0, 8), padx=20)
        self.q_bulk = ctk.CTkOptionMenu(t2, width=220, height=36, values=list(FORMAT_MAP.keys()), corner_radius=8, fg_color="#2c3e50")
        self.q_bulk.pack(pady=(0, 8))
        self.btn_bulk = ctk.CTkButton(t2, text="⚡  BẮT ĐẦU TẢI NGAY", command=self.on_bulk, width=320, height=52,
            font=ctk.CTkFont(family=self.FONT, size=16, weight="bold"), fg_color="#00b894", hover_color="#00a381", corner_radius=12)
        self.btn_bulk.pack(pady=(4, 8))

        # === TAB 3: CHANNEL SCAN ===
        t3 = self.tabview.tab("📡 Quét Kênh")
        t3.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t3, text="Hỗ trợ: Quét Video từ Kênh/Playlist", font=ctk.CTkFont(family=self.FONT, size=10),
            text_color="#666", wraplength=460).pack(pady=(12, 10))
        
        self.chan_url = ctk.CTkEntry(t3, placeholder_text="Dán URL kênh YouTube hoặc Playlist...",
            width=480, height=50, font=ctk.CTkFont(family=self.FONT, size=14), corner_radius=10)
        self.chan_url.pack(pady=(0, 15), padx=20)
        
        self.q_chan = ctk.CTkOptionMenu(t3, width=220, height=36, values=list(FORMAT_MAP.keys()), corner_radius=8, fg_color="#2c3e50")
        self.q_chan.pack(pady=(0, 15))
        
        cf = ctk.CTkFrame(t3, fg_color="transparent"); cf.pack(pady=(0, 15))
        ctk.CTkLabel(cf, text="Số lượng:", font=ctk.CTkFont(family=self.FONT, size=13)).pack(side="left", padx=(0, 8))
        self.chan_limit = ctk.CTkOptionMenu(cf, width=140, height=32, values=["Tất cả", "10 video", "20 video", "50 video", "100 video"], corner_radius=8)
        self.chan_limit.pack(side="left")
        bf = ctk.CTkFrame(t3, fg_color="transparent"); bf.pack(pady=(0, 10))
        self.btn_scan = ctk.CTkButton(bf, text="🔍 QUÉT KÊNH", command=self.on_scan, width=160, height=46,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold"), fg_color="#6c5ce7", hover_color="#5a4bd1", corner_radius=10)
        self.btn_scan.pack(side="left", padx=8)
        self.btn_chan_dl = ctk.CTkButton(bf, text="⏬ TẢI TẤT CẢ", command=self.on_chan_download, width=160, height=46,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold"), fg_color="#00b894", hover_color="#00a381", state="disabled", corner_radius=10)
        self.btn_chan_dl.pack(side="left", padx=8)
        self.chan_info = ctk.CTkLabel(t3, text="", font=ctk.CTkFont(family=self.FONT, size=11), text_color="#8cf", wraplength=460)
        self.chan_info.pack(pady=(4, 4))
        self.chan_list = ctk.CTkTextbox(t3, width=480, height=110, state="disabled",
            font=ctk.CTkFont(family=self.FONT, size=11))
        self.chan_list.pack(pady=(0, 6), padx=12)
        self._chan_videos = []

        # === TAB 4: THUMBNAIL ===
        t4 = self.tabview.tab("🖼 Thumbnail")
        t4.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t4, text="Hỗ trợ: Tải ảnh bìa chất lượng cao", font=ctk.CTkFont(family=self.FONT, size=10),
            text_color="#666", wraplength=460).pack(pady=(12, 10))
            
        self.thumb_url = ctk.CTkEntry(t4, placeholder_text="Dán link video muốn lấy ảnh...",
            width=480, height=50, font=ctk.CTkFont(family=self.FONT, size=14), corner_radius=10)
        self.thumb_url.pack(pady=(0, 15), padx=20)
        
        self.btn_thumb = ctk.CTkButton(t4, text="🖼  TẢI THUMBNAIL LẺ", command=self.on_thumb, width=260, height=50,
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold"), fg_color="#6c5ce7", hover_color="#5a4bd1", corner_radius=10)
        self.btn_thumb.pack(pady=(0, 15))
        
        self.thumb_info = ctk.CTkLabel(t4, text="", font=ctk.CTkFont(family=self.FONT, size=11),
            text_color="#8cf", wraplength=460)
        self.thumb_info.pack(pady=(0, 10))
        
        self.thumb_bulk = ctk.CTkTextbox(t4, width=480, height=100,
            font=ctk.CTkFont(family=self.FONT, size=12), corner_radius=10, border_width=1, border_color="#34495e")
        self.thumb_bulk.pack(pady=(0, 15), padx=20)
        
        self.btn_thumb_bulk = ctk.CTkButton(t4, text="🖼  TẢI HÀNG LOẠT THUMBNAIL", command=self.on_thumb_bulk,
            width=260, height=46, font=ctk.CTkFont(family=self.FONT, size=13, weight="bold"),
            fg_color="#6c5ce7", hover_color="#5a4bd1", corner_radius=10)
        self.btn_thumb_bulk.pack(pady=(0, 10))

        # === TAB 5: HISTORY ===
        t5 = self.tabview.tab("🕓 Lịch Sử")
        t5.grid_columnconfigure(0, weight=1)
        hh = ctk.CTkFrame(t5, fg_color="transparent"); hh.pack(fill="x", pady=(12, 8), padx=12)
        self.hist_count = ctk.CTkLabel(hh, text=f"📊 Đã tải: {len(self.history)} video",
            font=ctk.CTkFont(family=self.FONT, size=14, weight="bold"))
        self.hist_count.pack(side="left")
        ctk.CTkButton(hh, text="🗑 Xóa", width=76, height=32, fg_color="#e74c3c", hover_color="#c0392b",
            font=ctk.CTkFont(family=self.FONT, size=12), command=self.clear_history).pack(side="right")
        self.hist_text = ctk.CTkTextbox(t5, width=480, height=310, state="disabled",
            font=ctk.CTkFont(family=self.FONT, size=12))
        self.hist_text.pack(pady=(0, 8), padx=12)
        self._refresh_hist()

        # === USER CHART (bar chart) ===
        chart_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12, height=120)
        chart_frame.grid(row=3, column=0, padx=16, pady=(0, 4), sticky="ew")
        chart_frame.grid_propagate(False)
        chart_frame.grid_columnconfigure(0, weight=1)
        
        # Thêm Label tổng lượt sử dụng (Nổi bật)
        self.total_lbl = ctk.CTkLabel(chart_frame, text="Syncing usage count...",
                                     font=ctk.CTkFont(family=self.FONT, size=14, weight="bold"),
                                     text_color="#00b894")
        self.total_lbl.pack(pady=(6, 0))

        self.chart_canvas = tk.Canvas(chart_frame, bg="#1a1a2e", highlightthickness=0, height=75)
        self.chart_canvas.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self._chart_data = []
        self._chart_total = 0
        self.chart_canvas.bind("<Configure>", lambda e: self._draw_chart(1.0) if self._chart_data else None)

        # === STATUS BAR ===
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=4, column=0, padx=16, pady=(0, 6), sticky="ew"); sf.grid_columnconfigure(0, weight=1)
        self.pbar = ctk.CTkProgressBar(sf, width=490); self.pbar.set(0)
        self.pbar.grid(row=0, column=0, pady=(6, 2)); self.pbar.grid_remove()
        self.status = ctk.CTkLabel(sf, text="Sẵn sàng", font=ctk.CTkFont(family=self.FONT, size=13))
        self.status.grid(row=1, column=0, pady=(2, 6))
        fbf = ctk.CTkFrame(sf, fg_color="transparent"); fbf.grid(row=2, column=0, pady=(0, 4))
        ctk.CTkButton(fbf, text="📂  MỞ THƯ MỤC", command=lambda: os.startfile(self.download_path),
            fg_color="#2ecc71", hover_color="#27ae60", width=196, height=38,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(fbf, text="📁  ĐỔI THƯ MỤC", command=self._pick_folder,
            fg_color="#636e72", hover_color="#2d3436", width=196, height=38,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold")).pack(side="left")
        self.path_label = ctk.CTkLabel(sf, text=f"📍 {self.download_path}",
            font=ctk.CTkFont(family=self.FONT, size=10), text_color="#777", wraplength=490)
        self.path_label.grid(row=3, column=0, pady=(0, 4))

        # === COFFEE FOOTER with hover QR ===
        self._build_coffee_footer()
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)

    # ===== MARQUEE =====
    def _animate_marquee(self):
        """Scroll thank-you text from right to left."""
        c = self.marquee_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 10:
            w = 540
        c.create_text(self._marquee_x, 11, text=self._marquee_str,
                      fill="#f0c070", font=(self.FONT, 10), anchor="w")
        text_id = c.create_text(0, -100, text=self._marquee_str,
                                font=(self.FONT, 10), anchor="w")
        bbox = c.bbox(text_id)
        text_w = (bbox[2] - bbox[0]) if bbox else 400
        c.delete(text_id)
        self._marquee_x -= 1.5
        if self._marquee_x < -text_w:
            self._marquee_x = w
        self.after(30, self._animate_marquee)

    # ===== AUTO UPDATE CHECKER =====
    @staticmethod
    def _version_tuple(value):
        parts = re.findall(r'\d+', str(value or ''))
        return tuple(int(x) for x in parts[:4]) if parts else (0,)

    @staticmethod
    def _find_release_exe_asset(release_data):
        assets = release_data.get('assets') or []
        exe_assets = [a for a in assets if str(a.get('name', '')).lower().endswith('.exe')]
        if not exe_assets:
            return None
        preferred = [a for a in exe_assets if 'setup' not in str(a.get('name', '')).lower()]
        return (preferred or exe_assets)[0]

    def _check_for_updates(self):
        """Automatically install newer GitHub release when it contains an .exe asset."""
        try:
            time.sleep(3)
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(api_url, headers={
                'User-Agent': 'ProVideoDownloader',
                'Accept': 'application/vnd.github.v3+json'
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            latest_tag = data.get('tag_name', '').lstrip('v')
            if not latest_tag:
                return
            if self._version_tuple(latest_tag) <= self._version_tuple(APP_VERSION):
                return
            asset = self._find_release_exe_asset(data)
            if asset and asset.get('browser_download_url'):
                self.after(0, lambda: self.status.configure(text=f"Auto updating to v{latest_tag}...", text_color="#f0c070"))
                self._download_and_install_update(latest_tag, asset['browser_download_url'])
            else:
                release_url = data.get('html_url', f'https://github.com/{GITHUB_REPO}/releases/latest')
                self.after(0, lambda: self._show_update_missing_asset_dialog(latest_tag, release_url))
        except Exception:
            pass

    def _download_and_install_update(self, new_version, download_url):
        """Download new exe, then spawn a small updater script to replace this exe after exit."""
        try:
            current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            if not current_exe.lower().endswith('.exe'):
                self.after(0, lambda: self._show_update_dialog(new_version, download_url))
                return
            update_dir = os.path.join(tempfile.gettempdir(), 'pro_video_downloader_update')
            os.makedirs(update_dir, exist_ok=True)
            new_exe = os.path.join(update_dir, f'Pro_VideoDownloader_v{new_version}.exe')
            req = urllib.request.Request(download_url, headers={'User-Agent': 'ProVideoDownloader'})
            with urllib.request.urlopen(req, timeout=60) as resp, open(new_exe, 'wb') as f:
                shutil.copyfileobj(resp, f)
            if os.path.getsize(new_exe) < 1024 * 1024:
                raise RuntimeError('Downloaded update is too small')
            bat_path = os.path.join(update_dir, 'apply_update.bat')
            bat = """@echo off
setlocal
set "NEW_EXE={new_exe}"
set "TARGET_EXE={current_exe}"
set "PID={pid}"
:wait_loop
tasklist /FI "PID eq %PID%" | find "%PID%" >nul
if not errorlevel 1 (timeout /t 1 /nobreak >nul & goto wait_loop)
copy /Y "%NEW_EXE%" "%TARGET_EXE%"
start "" "%TARGET_EXE%"
del "%NEW_EXE%" >nul 2>nul
del "%~f0" >nul 2>nul
""".format(new_exe=new_exe, current_exe=current_exe, pid=os.getpid())
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat.replace('\n', '\r\n'))
            subprocess.Popen(['cmd', '/c', bat_path], close_fds=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.after(0, lambda: messagebox.showinfo('Updating', f'Downloaded v{new_version}. The app will restart automatically.'))
            self.after(700, self.destroy)
        except Exception as e:
            self.after(0, lambda err=str(e): self._show_update_error_dialog(new_version, download_url, err))

    def _show_update_missing_asset_dialog(self, new_version, release_url):
        messagebox.showwarning(
            'Missing update file',
            f'Version v{new_version} exists, but the GitHub release has no .exe asset, so auto-update cannot install it.\n\n'
            'Upload Pro_VideoDownloader_HoangDuc.exe to the release Assets for auto-update to work.'
        )
        webbrowser.open(release_url)

    def _show_update_error_dialog(self, new_version, download_url, error):
        msg = f'Could not auto-update to v{new_version}:\n{error}\n\nOpen the download page?'
        if messagebox.askyesno('Update failed', msg):
            webbrowser.open(download_url)

    def _show_update_dialog(self, new_version, download_url):
        """Manual fallback for non-frozen/dev runs."""
        msg = f'Current version: v{APP_VERSION}\nNew version: v{new_version}\n\nOpen the download page?'
        if messagebox.askyesno('Update available', msg):
            webbrowser.open(download_url)

    # ===== FOLDER PICKER =====
    def _pick_folder(self):
        chosen = filedialog.askdirectory(title="Chọn thư mục lưu video", initialdir=self.download_path)
        if chosen:
            self.download_path = os.path.normpath(chosen)
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
            self.path_label.configure(text=f"📍 {self.download_path}")
            save_config({'download_path': self.download_path})

    # ===== HISTORY =====
    def _refresh_hist(self):
        self.hist_text.configure(state="normal"); self.hist_text.delete("1.0", "end")
        if not self.history:
            self.hist_text.insert("1.0", "Chưa có video nào. Hãy tải video đầu tiên! 🎬")
        else:
            lines = []
            for i, h in enumerate(reversed(self.history[-100:]), 1):
                lines.append(f"{i}. {h.get('title','N/A')}\n   🔗 {h.get('url','')[:60]}...\n   📅 {h.get('time','')}  •  📁 {h.get('type','video')}")
            self.hist_text.insert("1.0", "\n\n".join(lines))
        self.hist_text.configure(state="disabled")
        self.hist_count.configure(text=f"📊 Đã tải: {len(self.history)} video")

    def clear_history(self):
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ lịch sử?"):
            self.history = []; save_history([]); self._refresh_hist()

    # ===== CHANNEL SCAN =====
    def on_scan(self):
        url = self.chan_url.get().strip()
        if not url: messagebox.showerror("Lỗi", "Nhập URL kênh!"); return
        self.btn_scan.configure(state="disabled"); self.chan_info.configure(text="🔍 Đang quét kênh...")
        self.chan_list.configure(state="normal"); self.chan_list.delete("1.0", "end"); self.chan_list.configure(state="disabled")
        threading.Thread(target=self._scan_worker, args=(url,), daemon=True).start()

    def _get_limit(self):
        v = self.chan_limit.get()
        if v == "Tất cả": return None
        return int(v.split()[0])

    def _scan_worker(self, url):
        try:
            limit = self._get_limit()
            opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'skip_download': True}
            if limit: opts['playlistend'] = limit
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [])
            if not entries and info.get('id'):
                entries = [info]
            self._chan_videos = []
            for e in entries:
                if e:
                    self._chan_videos.append({'url': e.get('url') or e.get('webpage_url', ''), 'title': e.get('title', 'N/A')})
            n = len(self._chan_videos)
            channel = info.get('channel', '') or info.get('uploader', '') or info.get('title', 'Kênh')
            self.after(0, lambda: self.chan_info.configure(text=f"✅ Tìm thấy {n} video trong kênh: {channel}"))
            self.after(0, lambda: self.btn_scan.configure(state="normal"))
            self.after(0, lambda: self.btn_chan_dl.configure(state="normal"))
            # Show list
            lines = [f"{i+1}. {v['title']}" for i, v in enumerate(self._chan_videos[:100])]
            txt = "\n".join(lines)
            if n > 100: txt += f"\n... và {n-100} video khác"
            self.after(0, lambda: (self.chan_list.configure(state="normal"), self.chan_list.delete("1.0","end"), self.chan_list.insert("1.0", txt), self.chan_list.configure(state="disabled")))
        except Exception as e:
            self.after(0, lambda: self.chan_info.configure(text=f"❌ Lỗi: {str(e)[:80]}"))
            self.after(0, lambda: self.btn_scan.configure(state="normal"))

    def on_chan_download(self):
        if not self._chan_videos: messagebox.showerror("Lỗi", "Quét kênh trước!"); return
        urls = [v['url'] for v in self._chan_videos if v['url']]
        q = self.q_chan.get()
        self.btn_chan_dl.configure(state="disabled")
        threading.Thread(target=self._download_engine, args=(urls, q, True), daemon=True).start()

    # ===== DOWNLOADS =====
    def on_single(self):
        url = self.single_url.get().strip()
        if not url: messagebox.showerror("Lỗi", "Nhập link!"); return
        self.btn_single.configure(state="disabled")
        threading.Thread(target=self._download_engine, args=([url], self.q_menu.get()), daemon=True).start()

    def on_bulk(self):
        txt = self.bulk_text.get("1.0", "end").strip()
        if not txt: messagebox.showerror("Lỗi", "Dán link!"); return
        urls = [u.strip() for u in txt.split('\n') if u.strip()]
        self.btn_bulk.configure(state="disabled")
        threading.Thread(target=self._download_engine, args=(urls, self.q_bulk.get()), daemon=True).start()

    def _paste_to(self, entry):
        """Quick-paste clipboard content into an entry field."""
        try:
            clip = self.clipboard_get()
            if clip:
                entry.delete(0, "end")
                entry.insert(0, clip.strip())
        except: pass

    def _download_engine(self, urls, quality, is_channel=False):
        total = len(urls); ok = 0; failures = []
        fmt = FORMAT_MAP.get(quality, "bestvideo+bestaudio/best")
        is_mp3 = quality == "Chỉ Lấy Nhạc (MP3)"
        ydl_opts = {
            'format': fmt, 'quiet': True, 'no_warnings': True,
            'progress_hooks': [self._hook], 'noplaylist': True,
            'concurrent_fragment_downloads': 8, # Tối ưu đa luồng
            'retries': 15,
            'fragment_retries': 15,
            'http_chunk_size': 10485760, # 10MB chunks để tải mượt hơn
            'socket_timeout': 45,
            'noprogress': True,
        }
        if HAS_FFMPEG:
            ydl_opts['merge_output_format'] = 'mp4'
        if is_mp3:
            if HAS_FFMPEG:
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
                ydl_opts.pop('merge_output_format', None)
            else:
                ydl_opts['format'] = 'bestaudio/best'

        self.after(0, lambda: (self.pbar.grid(), self.pbar.set(0)))
        # Reuse single yt-dlp instance for entire batch
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, url in enumerate(urls):
                try:
                    self.after(0, lambda idx=i+1, u=url: self.status.configure(
                        text=f"[{idx}/{total}] Đang tải: {u[:50]}...", text_color="white"))
                    tmp = os.path.join(self.download_path, f"_tmp_{threading.get_ident()}_{i}.%(ext)s")
                    ydl.params['outtmpl'] = {'default': tmp}
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        failures.append((url, "Không lấy được thông tin video"))
                        continue
                    raw = info.get('fulltitle') or info.get('title') or ''
                    if len(raw) < 5:
                        d = info.get('description', '')
                        if d: raw = d.split('\n')[0]
                    if not raw: raw = info.get('alt_title') or 'video'
                    clean = clean_filename(raw, info.get('id', 'x'))
                    src = ydl.prepare_filename(info)
                    if is_mp3:
                        mp3 = os.path.splitext(src)[0] + ".mp3"
                        if os.path.exists(mp3): src = mp3
                    ext = os.path.splitext(src)[1]
                    dst = os.path.join(self.download_path, f"{clean}{ext}")
                    if os.path.exists(src):
                        c = 1
                        while os.path.exists(dst):
                            dst = os.path.join(self.download_path, f"{clean} ({c}){ext}"); c += 1
                        os.rename(src, dst); ok += 1
                        self.history.append({"url": url, "title": clean, "type": "mp3" if is_mp3 else "video", "time": time.strftime("%Y-%m-%d %H:%M")})
                    else:
                        failures.append((url, "File không tồn tại sau khi tải"))
                except Exception as e:
                    err_short = str(e).split('\n')[0][:120]
                    failures.append((url, err_short))
                    self.after(0, lambda err=err_short: self.status.configure(
                        text=f"❌ {err[:70]}", text_color="#ff7675"))
        # Batch save history once
        save_history(self.history)
        # Record download visits (gửi lên Google Sheet + local)
        if ok > 0:
            for _ in range(ok):
                record_visit('download')
            self.after(0, self._refresh_chart)
        self.after(0, lambda: self._finish(ok, total, is_channel, failures))

    def _finish(self, ok, total, is_channel=False, failures=None):
        failures = failures or []
        self.btn_single.configure(state="normal"); self.btn_bulk.configure(state="normal"); self.btn_chan_dl.configure(state="normal")
        self.pbar.set(1.0 if ok > 0 else 0)
        self.status.configure(text=f"✅ Thành công {ok}/{total}!" if ok > 0 else f"❌ Thất bại {total}/{total}", text_color="white")
        self._refresh_hist()
        if ok > 0 and not failures:
            messagebox.showinfo("Kết quả", f"✅ Đã tải {ok}/{total} {'video từ kênh' if is_channel else 'video'}.\n📁 {self.download_path}")
        elif ok > 0 and failures:
            detail = "\n".join([f"❌ {u[:60]}\n   ↳ {e[:80]}" for u, e in failures[:8]])
            if len(failures) > 8: detail += f"\n... và {len(failures)-8} link khác thất bại"
            messagebox.showwarning("Kết quả", f"✅ Thành công: {ok}/{total}\n❌ Thất bại: {len(failures)}\n\n{detail}")
        elif failures:
            detail = "\n".join([f"❌ {u[:60]}\n   ↳ {e[:80]}" for u, e in failures[:6]])
            if len(failures) > 6: detail += f"\n... và {len(failures)-6} link khác"
            messagebox.showerror("Thất bại", f"Không tải được {total} video.\n\n{detail}\n\n💡 Kiểm tra lại link hoặc kết nối mạng.")
        elif total > 0:
            messagebox.showerror("Thất bại", "Không tải được video.\n💡 Kiểm tra link hoặc kết nối mạng.")

    def _hook(self, d):
        if d['status'] == 'downloading':
            now = time.time()
            if now - self._last_hook_time < 0.25: return
            self._last_hook_time = now
            try:
                p = float(d.get('_percent_str', '0%').replace('%', '').strip()) / 100
                spd = d.get('_speed_str', ''); eta = d.get('_eta_str', '')
                self.after(0, lambda: self.pbar.set(p))
                self.after(0, lambda: self.status.configure(text=f"Đang tải: {d.get('_percent_str','0%')} — {spd} — ETA: {eta}"))
            except: pass
        elif d['status'] == 'finished':
            self.after(0, lambda: (self.pbar.set(0.95), self.status.configure(text="Đang hoàn thiện...")))

    # ===== THUMBNAIL =====
    def on_thumb(self):
        url = self.thumb_url.get().strip()
        if not url: messagebox.showerror("Lỗi", "Nhập link!"); return
        self.btn_thumb.configure(state="disabled"); self.thumb_info.configure(text="⏳ Đang tải...")
        threading.Thread(target=self._thumb_work, args=([url],), daemon=True).start()

    def on_thumb_bulk(self):
        txt = self.thumb_bulk.get("1.0", "end").strip()
        urls = [u.strip() for u in txt.split('\n') if u.strip().startswith('http')]
        if not urls: messagebox.showerror("Lỗi", "Dán link!"); return
        self.btn_thumb_bulk.configure(state="disabled")
        threading.Thread(target=self._thumb_work, args=(urls,), daemon=True).start()

    def _thumb_work(self, urls):
        ok = 0
        # Reuse single yt-dlp instance for all thumbnails — much faster
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'skip_download': True, 'socket_timeout': 15}) as ydl:
            for i, url in enumerate(urls):
                try:
                    self.after(0, lambda idx=i+1: self.thumb_info.configure(text=f"⏳ [{idx}/{len(urls)}]..."))
                    info = ydl.extract_info(url, download=False)
                    thumb = info.get('thumbnail')
                    title = clean_filename(info.get('title', 'thumb'), info.get('id', 'x'))
                    vid_id = info.get('id', '')
                    if 'youtube' in info.get('extractor', '').lower() and vid_id:
                        thumb = f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg"
                    if thumb:
                        path = os.path.join(self.download_path, f"{title}_thumb.jpg")
                        c = 1
                        while os.path.exists(path): path = os.path.join(self.download_path, f"{title}_thumb ({c}).jpg"); c += 1
                        urllib.request.urlretrieve(thumb, path); ok += 1
                        self.history.append({"url": url, "title": title, "type": "thumbnail", "time": time.strftime("%Y-%m-%d %H:%M")})
                except: pass
        save_history(self.history)
        self.after(0, lambda: self.thumb_info.configure(text=f"✅ Đã tải {ok}/{len(urls)} thumbnail"))
        self.after(0, lambda: self.btn_thumb.configure(state="normal"))
        self.after(0, lambda: self.btn_thumb_bulk.configure(state="normal"))
        self.after(0, self._refresh_hist)

    # ===== COFFEE FOOTER =====
    def _build_coffee_footer(self):
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=5, column=0, pady=(0, 8), sticky="ew")
        foot.grid_columnconfigure(0, weight=1)
        foot.grid_columnconfigure(1, weight=1)
        foot.grid_columnconfigure(2, weight=1)

        # Dev Info (Bottom Left)
        dev_frame = ctk.CTkFrame(foot, fg_color="transparent")
        dev_frame.grid(row=0, column=0, sticky="sw", padx=16)
        
        dev_lbl = ctk.CTkLabel(dev_frame, text="💻 Dev by Hoàng Đức", font=ctk.CTkFont(family=self.FONT, size=12, weight="bold"), text_color="#3498db", cursor="hand2")
        dev_lbl.pack(anchor="w")
        dev_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://www.facebook.com/ducserving"))
        
        dev_sub = ctk.CTkLabel(dev_frame, text="Hỗ trợ & Góp ý", font=ctk.CTkFont(family=self.FONT, size=10), text_color="#7f8c8d", cursor="hand2")
        dev_sub.pack(anchor="w")
        dev_sub.bind("<Button-1>", lambda e: webbrowser.open("https://www.facebook.com/ducserving"))

        # Coffee Info (Centered)
        coffee_frame = ctk.CTkFrame(foot, fg_color="transparent")
        coffee_frame.grid(row=0, column=1)

        # Load coffee.png
        coffee_path = resource_path("coffee.png")
        try:
            ci = Image.open(coffee_path)
            self._coffee_img = ctk.CTkImage(light_image=ci, dark_image=ci, size=(60, 60))
        except:
            self._coffee_img = None
        # Coffee icon label
        if self._coffee_img:
            self.coffee_lbl = ctk.CTkLabel(coffee_frame, image=self._coffee_img, text="", fg_color="transparent", cursor="hand2")
        else:
            self.coffee_lbl = ctk.CTkLabel(coffee_frame, text="☕", font=ctk.CTkFont(size=36), text_color="#e67e22", cursor="hand2")
        self.coffee_lbl.pack()
        ctk.CTkLabel(coffee_frame, text="Mời cafe ☕", font=ctk.CTkFont(family=self.FONT, size=10), text_color="#665544").pack()

        # QR popup
        self._qr_popup = None
        # Load QR once
        self._qr_ctk_img = None
        try:
            qr_path = resource_path("real_qr.png")
            if os.path.exists(qr_path):
                qi = Image.open(qr_path)
                self._qr_ctk_img = ctk.CTkImage(light_image=qi, dark_image=qi, size=(200, 200))
        except: pass
        # Bind hover
        self.coffee_lbl.bind("<Enter>", self._show_qr)
        self.coffee_lbl.bind("<Leave>", self._schedule_hide_qr)

    def _show_qr(self, event=None):
        if self._qr_popup and self._qr_popup.winfo_exists():
            return
        if not self._qr_ctk_img:
            return
        p = ctk.CTkToplevel(self)
        p.overrideredirect(True)
        p.attributes('-topmost', True)
        p.configure(fg_color="#0d0906")
        # Build content
        ctk.CTkLabel(p, text="☕ Mời Cafe Tác Giả", font=ctk.CTkFont(family=self.FONT, size=16, weight="bold"),
            text_color="#f0c070").pack(pady=(12, 6))
        qf = ctk.CTkFrame(p, fg_color="white", corner_radius=10)
        qf.pack(padx=16, pady=6)
        ctk.CTkLabel(qf, image=self._qr_ctk_img, text="", fg_color="white").pack(padx=10, pady=10)
        ctk.CTkLabel(p, text="Quét mã QR để chuyển khoản ☕✨",
            font=ctk.CTkFont(family=self.FONT, size=11), text_color="#c0946a").pack(pady=(4, 10))
        # Position above coffee icon
        p.update_idletasks()
        pw, ph = p.winfo_reqwidth(), p.winfo_reqheight()
        cx = self.coffee_lbl.winfo_rootx() + self.coffee_lbl.winfo_width() // 2 - pw // 2
        cy = self.coffee_lbl.winfo_rooty() - ph - 8
        p.geometry(f"+{cx}+{cy}")
        self._qr_popup = p
        # Keep popup alive while mouse is on it
        p.bind("<Enter>", lambda e: None)
        p.bind("<Leave>", self._schedule_hide_qr)

    def _schedule_hide_qr(self, event=None):
        self.after(300, self._try_hide_qr)

    def _try_hide_qr(self):
        if not self._qr_popup or not self._qr_popup.winfo_exists():
            return
        try:
            mx, my = self.winfo_pointerx(), self.winfo_pointery()
            cx, cy = self.coffee_lbl.winfo_rootx(), self.coffee_lbl.winfo_rooty()
            cw, ch = self.coffee_lbl.winfo_width(), self.coffee_lbl.winfo_height()
            if cx <= mx <= cx + cw and cy <= my <= cy + ch:
                return
            px, py = self._qr_popup.winfo_rootx(), self._qr_popup.winfo_rooty()
            pw, ph = self._qr_popup.winfo_width(), self._qr_popup.winfo_height()
            if px <= mx <= px + pw and py <= my <= py + ph:
                return
        except: pass
        self._qr_popup.destroy()
        self._qr_popup = None

    # ===== USER CHART =====
    def _register_and_fetch_count(self):
        """Record 'open' visit → POST lên Google Sheet → hiển thị tổng toàn cầu."""
        # Record this app open (POST to API + local)
        _, api_result = record_visit('open')
        # If API returned data, use it directly
        if api_result and 'total_visits' in api_result:
            total = int(api_result.get('total_visits') or 0)
            daily = api_result.get('daily', [])
            self._global_stats = api_result
            self.after(0, lambda: self._set_chart_data(daily, total, source="sheet"))
        else:
            # Fallback to local
            self.after(0, self._refresh_chart)
        # Auto-refresh chart every 60 seconds (fetch from API)
        self._auto_refresh_chart()

    def _auto_refresh_chart(self):
        """Periodically refresh chart from Google Sheet API."""
        threading.Thread(target=self._refresh_chart_from_api, daemon=True).start()
        self.after(60000, self._auto_refresh_chart)

    def _refresh_chart_from_api(self):
        """Fetch global stats from API in background thread."""
        stats = fetch_global_stats()
        if stats and 'total_visits' in stats:
            total = int(stats.get('total_visits') or 0)
            daily = stats.get('daily', [])
            self._global_stats = stats
            self.after(0, lambda: self._set_chart_data(daily, total, source="sheet"))
        else:
            self.after(0, self._refresh_chart)

    def _refresh_chart(self):
        """Fallback: đọc local visits khi không có mạng."""
        visits = load_visits()
        total = len(visits)
        daily = get_daily_breakdown_local(visits, 0)
        self._set_chart_data(daily, total, source="local")

    def _set_chart_data(self, daily, total, source="sheet"):
        """Set chart data and start animation."""
        self._chart_data = daily
        self._chart_total = total
        try:
            label = f"{total:,} uses from Google Sheet" if source == "sheet" else f"{total:,} local uses (Sheet not connected)"
            self.total_lbl.configure(text=label)
        except: pass
        self._chart_anim = 0.0
        self._animate_chart()

    def _animate_chart(self):
        """Animate bars growing up."""
        if self._chart_anim < 1.0:
            self._chart_anim = min(1.0, self._chart_anim + 0.06)
            self._draw_chart(self._chart_anim)
            self.after(25, self._animate_chart)
        else:
            self._draw_chart(1.0)

    def _draw_chart(self, progress):
        """Draw the bar chart matching the reference style."""
        c = self.chart_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 80 or h < 60:
            return

        BAR_COLOR = "#56B4D9"
        GRID_COLOR = "#2a2a40"

        data = self._chart_data
        if not data:
            c.create_text(w // 2, h // 2, text="Chờ kết nối...", fill="#555",
                          font=(self.FONT, 11))
            return

        n = len(data)
        max_val = max((d.get('count', 0) for d in data), default=1) or 1
        chart_top = 8
        chart_bottom = h - 8
        chart_h = chart_bottom - chart_top
        pad_x = 16
        total_w = w - pad_x * 2
        gap = max(1, total_w // (n * 5))  # thin gaps
        bar_w = max(3, (total_w - gap * (n - 1)) // n)
        start_x = pad_x + (total_w - (bar_w + gap) * n + gap) // 2

        # Horizontal grid lines
        for j in range(1, 4):
            gy = chart_top + chart_h * j // 4
            c.create_line(pad_x, gy, w - pad_x, gy, fill=GRID_COLOR, width=1)

        # Draw bars
        for i, d in enumerate(data):
            count = d.get('count', 0)
            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w

            bar_h = (count / max_val) * (chart_h - 6) * progress
            if count > 0 and bar_h < 2:
                bar_h = 2
            y_top = chart_bottom - bar_h

            if bar_h > 0:
                c.create_rectangle(x1, y_top, x2, chart_bottom,
                                   fill=BAR_COLOR, outline="", width=0)

        # Base line
        c.create_line(pad_x, chart_bottom, w - pad_x,
                      chart_bottom, fill="#3a3a55", width=1)

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()

