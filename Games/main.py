import os
import sys
import threading
import json
import urllib.request
import urllib.error
import base64
import ssl

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr is not None:
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ["OPENBLAS_NUM_THREADS"] = "1"

# Base paths
_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_DASHBOARD_DIR)  # CV-FinalProject
_ASSETS_DIR = os.path.join(_PROJECT_ROOT, "assets")
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import customtkinter as ctk
from PIL import Image

# Professional Theme Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Professional Color Palette
BG_COLOR = "#0a0a0a"
SIDEBAR_COLOR = "#121212"
CARD_COLOR = "#1a1a1a"
ACCENT_COLOR = "#6366f1"
ACCENT_LIGHT = "#818cf8"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
SUCCESS_COLOR = "#22c55e"
SUCCESS_DIM = "#166534"
WARNING_COLOR = "#eab308"
WARNING_DIM = "#854d0e"
ERROR_COLOR = "#ef4444"
ERROR_DIM = "#991b1b"
INFO_COLOR = "#06b6d4"

FONT_FAMILY = "Cairo"

class GameDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("مركز ADHD للتدريب الحسي والحركي")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.user_data = {
            "id": "",
            "name": "",
        }

        self.sessions_cache = []
        self.backend_client = BackendClient()
        self.login_frame = LoginFrame(self, self.login_callback, self.backend_client)
        self.dashboard_frame = None
        self.loading_frame = None

        self.show_login()

    def show_login(self):
        if self.dashboard_frame:
            self.dashboard_frame.grid_forget()
        if self.loading_frame:
            self.loading_frame.grid_forget()
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    def login_callback(self, user_id, user_name="عمر محمد"):
        self.user_data["id"] = user_id
        self.user_data["name"] = user_name
        self.login_frame.grid_forget()
        self.loading_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.loading_frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.loading_frame, text="🧠", font=ctk.CTkFont(size=60)).pack(expand=True)
        ctk.CTkLabel(self.loading_frame, text="جاري تحميل بيانات التدريب...",
                     font=ctk.CTkFont(family=FONT_FAMILY, size=16)).pack()
        threading.Thread(target=self._load_and_show_dashboard, args=(user_id,), daemon=True).start()

    def _load_and_show_dashboard(self, child_id):
        self.sessions_cache = []
        stats = {"sessions_completed": 0, "focus_score": 0, "motor_control": 0, "impulse_control": 0}

        if self.backend_client.is_online:
            success, sessions = self.backend_client.get_sessions(child_id)
            if success and sessions:
                self.sessions_cache = sessions
                total = len(sessions)
                success_rates = [s.get("successRate", 0) for s in sessions if s.get("successRate") is not None]
                avg_rate = round(sum(success_rates) / len(success_rates), 1) if success_rates else 0
                stats["sessions_completed"] = total
                stats["focus_score"] = avg_rate
                stats["motor_control"] = min(avg_rate + 8, 100)
                stats["impulse_control"] = max(avg_rate - 5, 0)

        self.user_data.update(stats)
        self.after(0, self._finish_show_dashboard)

    def _finish_show_dashboard(self):
        if self.loading_frame:
            self.loading_frame.grid_forget()
            self.loading_frame = None
        self.dashboard_frame = DashboardFrame(self, self.user_data, self.sessions_cache)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")

class BackendClient:
    API_BASE_URL = "http://localhost:5131"
    DEVICE_KEY = "dev-game-device-key-change-me"

    def __init__(self):
        self.token = None
        self.user_id = None
        self.user_role = None
        self.is_online = False

    def _url(self, path):
        return f"{self.API_BASE_URL}/{path.lstrip('/')}"

    def _headers(self, with_auth=True, extra=None):
        headers = {
            "Content-Type": "application/json",
            "X-Game-Device-Key": self.DEVICE_KEY,
        }
        if with_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method, path, body=None, with_auth=True, timeout=8):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(
            self._url(path), data=data, headers=self._headers(with_auth), method=method
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                resp_body = json.loads(resp.read().decode("utf-8"))
                return True, resp_body
        except Exception:
            return False, None

    def check_connection(self):
        success, _ = self._request("GET", "/api/Games", with_auth=False, timeout=4)
        self.is_online = success
        return success

    def login(self, email, password):
        success, data = self._request(
            "POST",
            "/api/Account/login",
            {"email": email, "password": password},
            with_auth=False,
        )
        if success and data and data.get("succeeded"):
            login_data = data["data"]
            self.token = login_data["token"]
            try:
                payload_b64 = self.token.split(".")[1]
                padding = 4 - len(payload_b64) % 4
                if padding != 4:
                    payload_b64 += "=" * padding
                payload = json.loads(base64.b64decode(payload_b64))
                self.user_id = payload.get("sub", "")
                self.user_role = payload.get(
                    "role", payload.get("http://schemas.microsoft.com/ws/2008/06/identity/claims/role", "Parent")
                )
            except Exception:
                pass
            return True, login_data
        msg = "بيانات الدخول غير صحيحة"
        if data:
            msg = data.get("message", msg)
        return False, msg

    def get_children(self, parent_id=None):
        if not parent_id and self.user_role == "Parent":
            parent_id = self.user_id
        path = f"/api/Children?parentId={parent_id}" if parent_id else "/api/Children"
        success, data = self._request("GET", path)
        if success and data and data.get("succeeded"):
            return True, data.get("data", [])
        return False, []

    def get_sessions(self, child_id):
        success, data = self._request("GET", f"/api/sessions?childId={child_id}")
        if success and data and data.get("succeeded"):
            return True, data.get("data", [])
        return False, []


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, login_callback, backend_client=None):
        super().__init__(master, fg_color=BG_COLOR)
        self.login_callback = login_callback
        self.backend = backend_client or BackendClient()
        self.child_profiles = []

        # Background Ambient Glows
        self.canvas = ctk.CTkCanvas(self, width=1100, height=750, bg=BG_COLOR, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.draw_glows()

        # Modern Glassmorphism Card
        self.card = ctk.CTkFrame(self, width=440, height=580, corner_radius=24, 
                                 fg_color=CARD_COLOR, border_width=1, border_color="#2a2a2a")
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Top accent line on card
        self.card_accent = ctk.CTkFrame(self.card, height=3, corner_radius=0, fg_color=ACCENT_COLOR)
        self.card_accent.pack(fill="x")

        # Main Card Content Container (to allow easy switching of states)
        self.content_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=30, pady=40)

        self.show_loading_state("جاري الاتصال بقاعدة البيانات...")

        threading.Thread(target=self._load_children, daemon=True).start()

    def _load_children(self):
        is_online = self.backend.check_connection()
        if is_online:
            ok, children = self.backend.get_children()
            if ok and children:
                self.child_profiles = children
                self.after(0, self.show_child_selection)
            else:
                self.after(0, self.show_manual_state)
        else:
            self.after(0, self.show_manual_state)

    def draw_glows(self):
        # Top Left Glow
        self.canvas.create_oval(-200, -200, 400, 400, fill="#1e1b4b", outline="")
        # Bottom Right Glow
        self.canvas.create_oval(800, 400, 1300, 900, fill="#1e1b4b", outline="")

    def show_loading_state(self, message="جاري تجهيز جلسة التدريب وتحميل بيانات الطفل..."):
        self.clear_container()

        self.logo_label = ctk.CTkLabel(self.content_container, text="🌌", font=ctk.CTkFont(size=60))
        self.logo_label.pack(pady=(20, 10))

        self.title_label = ctk.CTkLabel(self.content_container, text="مركز ADHD للتدريب", 
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=32, weight="bold"))
        self.title_label.pack(pady=(10, 5))

        self.loader_label = ctk.CTkLabel(self.content_container, text=message, 
                                         text_color=TEXT_SECONDARY, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.loader_label.pack(pady=(30, 5))

        self.loader_sub = ctk.CTkLabel(self.content_container, text="برجاء الانتظار قليلاً", 
                                       text_color="#4a4a6a", font=ctk.CTkFont(family=FONT_FAMILY, size=11))
        self.loader_sub.pack(pady=(0, 30))

        self.spinner = ctk.CTkProgressBar(self.content_container, width=220, height=4, corner_radius=2, fg_color="#1e293b", progress_color=ACCENT_COLOR)
        self.spinner.pack()
        self.spinner.start()

    def clear_container(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def show_child_selection(self):
        self.clear_container()

        self.logo_label = ctk.CTkLabel(self.content_container, text="🧒", font=ctk.CTkFont(size=44))
        self.logo_label.pack(pady=(0, 4))

        self.title_label = ctk.CTkLabel(self.content_container, text="مركز ADHD للتدريب", 
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold"))
        self.title_label.pack(pady=(2, 2))

        self.subtitle = ctk.CTkLabel(self.content_container, text="اختر طفلاً لبدء جلسة التدريب", 
                                     text_color=TEXT_SECONDARY, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.subtitle.pack(pady=(0, 10))

        status = ctk.CTkLabel(self.content_container, text="🟢 متصل بالخادم", 
                              text_color=SUCCESS_COLOR, font=ctk.CTkFont(family=FONT_FAMILY, size=10))
        status.pack(pady=(0, 10))

        scroll_container = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent", height=280)
        scroll_container.pack(fill="x", padx=5, pady=(0, 16))

        for child in self.child_profiles:
            cid = child.get("id", "")
            cname = child.get("name", cid)
            age = child.get("age", "")

            child_card = ctk.CTkFrame(scroll_container, fg_color=CARD_COLOR, corner_radius=12, 
                                      border_width=1, border_color="#2a2a2a")
            child_card.pack(fill="x", pady=4)

            row_inner = ctk.CTkFrame(child_card, fg_color="transparent")
            row_inner.pack(fill="both", expand=True, padx=14, pady=10)

            info_frame = ctk.CTkFrame(row_inner, fg_color="transparent")
            info_frame.pack(side="right", fill="both", expand=True)

            ctk.CTkLabel(info_frame, text=cname, 
                         font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")).pack(anchor="e")
            meta = f"المعرف: {cid}"
            if age:
                meta += f" | العمر: {age}"
            ctk.CTkLabel(info_frame, text=meta, text_color=TEXT_SECONDARY,
                         font=ctk.CTkFont(family=FONT_FAMILY, size=11)).pack(anchor="e")

            select_btn = ctk.CTkButton(row_inner, text="اختيار", width=70, height=32, corner_radius=8,
                                       fg_color=ACCENT_COLOR, hover_color=ACCENT_LIGHT,
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                                       command=lambda cid=cid, cname=cname: self.login_callback(cid, cname))
            select_btn.pack(side="left", padx=(0, 8))

            ctk.CTkLabel(row_inner, text="👤", font=ctk.CTkFont(size=28)).pack(side="left", padx=(0, 6))

    def show_manual_state(self):
        self.clear_container()

        self.logo_label = ctk.CTkLabel(self.content_container, text="⚠️", font=ctk.CTkFont(size=44))
        self.logo_label.pack(pady=(0, 4))

        self.title_label = ctk.CTkLabel(self.content_container, text="مركز ADHD للتدريب", 
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold"))
        self.title_label.pack(pady=(2, 2))
        
        self.subtitle = ctk.CTkLabel(self.content_container, text="الاتصال بالخادم غير متوفر - إدخال يدوي", 
                                     text_color=ERROR_COLOR, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.subtitle.pack(pady=(0, 10))

        input_container = ctk.CTkFrame(self.content_container, fg_color="transparent")
        input_container.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(input_container, text="معرف الطفل", text_color=TEXT_SECONDARY, 
                     font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(anchor="e", padx=5)

        self.manual_id_entry = ctk.CTkEntry(input_container, placeholder_text="CHILD001", 
                                            width=340, height=42, corner_radius=10,
                                            fg_color="#0f0f0f", border_color="#2d3748",
                                            font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.manual_id_entry.pack(pady=(4, 8))

        ctk.CTkLabel(input_container, text="اسم الطفل", text_color=TEXT_SECONDARY, 
                     font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(anchor="e", padx=5)

        self.manual_name_entry = ctk.CTkEntry(input_container, placeholder_text="الاسم (اختياري)", 
                                              width=340, height=42, corner_radius=10,
                                              fg_color="#0f0f0f", border_color="#2d3748",
                                              font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.manual_name_entry.insert(0, "عمر محمد")
        self.manual_name_entry.pack(pady=(4, 12))

        self.login_button = ctk.CTkButton(self.content_container, text="بدء الجلسة", command=self.on_login_manual, 
                                          width=340, height=48, corner_radius=10, 
                                          fg_color=ACCENT_COLOR, hover_color=ACCENT_LIGHT,
                                          font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"))
        self.login_button.pack(pady=(12, 8))

        ctk.CTkButton(self.content_container, text="إعادة المحاولة", command=self._retry_connection, 
                      width=340, height=36, corner_radius=8, 
                      fg_color="transparent", hover_color="#1a1a2e", text_color=TEXT_SECONDARY,
                      font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(pady=(4, 0))

    def _retry_connection(self):
        self.show_loading_state("جاري إعادة الاتصال بقاعدة البيانات...")
        threading.Thread(target=self._load_children, daemon=True).start()

    def on_login_manual(self):
        child_id = self.manual_id_entry.get().strip()
        name = self.manual_name_entry.get().strip()
        if child_id:
            self.login_callback(child_id, name or child_id)

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, user_data, sessions=None):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master
        self.sessions = sessions or []

        from datetime import datetime, timedelta
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        week_ago = today - timedelta(days=today.weekday())

        today_sessions = [s for s in self.sessions if s.get("startTime", "").startswith(today_str)]
        week_sessions = [s for s in self.sessions if s.get("startTime", "") >= week_ago.strftime("%Y-%m-%d")]
        success_rates = [s.get("successRate", 0) for s in self.sessions if s.get("successRate") is not None]
        avg_rate = round(sum(success_rates) / len(success_rates), 1) if success_rates else 0

        self.summary_data = {
            "today": f"{len(today_sessions)} جلسات" if len(today_sessions) > 1 else (f"{len(today_sessions)} جلسة" if today_sessions else "لا يوجد"),
            "week": f"{len(week_sessions)} جلسات" if len(week_sessions) > 1 else (f"{len(week_sessions)} جلسة" if week_sessions else "لا يوجد"),
            "avg": f"{avg_rate}%",
        }

        weekly_target = 5
        weekly_progress = min(len(week_sessions) / weekly_target, 1.0)
        self.weekly_progress_pct = round(weekly_progress * 100)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        # Profile Area
        self.profile_area = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.profile_area.pack(pady=40, padx=20, fill="x")

        info_box = ctk.CTkFrame(self.profile_area, fg_color="transparent")
        info_box.pack(side="right", fill="both")
        
        ctk.CTkLabel(info_box, text=user_data['name'], 
                     font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold")).pack(anchor="e")
        ctk.CTkLabel(info_box, text=f"المعرف: {user_data['id']}", 
                     text_color=ACCENT_COLOR, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(anchor="e")

        self.avatar = ctk.CTkLabel(self.profile_area, text="👤", font=ctk.CTkFont(size=40))
        self.avatar.pack(side="right", padx=(10, 0))

        # Stats List
        self.stats_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.stats_container.pack(fill="x", padx=16, pady=(10, 0))

        stats_data = [
            ("الجلسات المكتملة", f"{user_data['sessions_completed']}", ACCENT_COLOR),
            ("مستوى التركيز", f"{user_data['focus_score']}%", SUCCESS_COLOR),
            ("التحكم الحركي", f"{user_data['motor_control']}%", INFO_COLOR),
            ("التحكم بالاندفاع", f"{user_data['impulse_control']}%", WARNING_COLOR),
        ]
        for label, value, color in stats_data:
            self.create_stat_card(label, value, color)

        # Weekly progress
        divider = ctk.CTkFrame(self.sidebar, height=1, fg_color="#2a2a2a")
        divider.pack(fill="x", padx=20, pady=(15, 10))

        progress_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))

        progress_header = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_header.pack(fill="x")
        ctk.CTkLabel(progress_header, text="التقدم الأسبوعي", text_color=TEXT_SECONDARY,
                     font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="right")
        ctk.CTkLabel(progress_header, text=f"{self.weekly_progress_pct}%", text_color=ACCENT_LIGHT,
                     font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(side="left")
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=6, corner_radius=3,
                                                fg_color="#1e293b", progress_color=ACCENT_COLOR)
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.set(self.weekly_progress_pct / 100.0)

        # Main Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True, padx=40, pady=40)

        # Header with greeting
        header_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 8))

        greeting = ctk.CTkLabel(header_frame, text=f"مرحباً {user_data['name']} 👋", 
                                font=ctk.CTkFont(family=FONT_FAMILY, size=14), text_color=TEXT_SECONDARY)
        greeting.pack(anchor="e")

        self.header = ctk.CTkLabel(header_frame, text="لوحة التدريب الحسي", 
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=30, weight="bold"))
        self.header.pack(anchor="e")

        # Quick summary row
        summary_row = ctk.CTkFrame(self.content, fg_color="transparent")
        summary_row.pack(fill="x", pady=(16, 20))

        summary_items = [
            ("اليوم", self.summary_data["today"], ACCENT_COLOR),
            ("هذا الأسبوع", self.summary_data["week"], SUCCESS_COLOR),
            ("المعدل", self.summary_data["avg"], INFO_COLOR),
        ]
        for i, (label, value, color) in enumerate(summary_items):
            if i > 0:
                sep = ctk.CTkFrame(summary_row, width=1, height=30, fg_color="#2a2a2a")
                sep.pack(side="left", padx=16)
            item = ctk.CTkFrame(summary_row, fg_color="transparent")
            item.pack(side="left")
            ctk.CTkLabel(item, text=value, text_color=color,
                         font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")).pack(anchor="e")
            ctk.CTkLabel(item, text=label, text_color=TEXT_SECONDARY,
                         font=ctk.CTkFont(family=FONT_FAMILY, size=11)).pack(anchor="e")

        # Training Description
        self.desc_label = ctk.CTkLabel(self.content, text="تمارين التفاعل الحسي الحركي - اختر التمرين المناسب لمستوى الطفل",
                                       text_color=TEXT_SECONDARY, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.desc_label.pack(anchor="e", pady=(0, 16))

        # Games Grid
        self.scrollable = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True)
        
        self.games_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        self.games_frame.pack(fill="both", expand=True)

        _software_games_dir = os.path.join(_DASHBOARD_DIR, "Software_Games")
        self.games_data = [
            {"name": "الضوء الأخضر", "desc": "تدريب التحكم الحركي والاندفاعية - توقف عند الضوء الأحمر وانطلق عند الأخضر", "img": os.path.join(_ASSETS_DIR, "redlight.png"), "script": os.path.join(_software_games_dir, "green_light.py"), "difficulty": "متوسط", "duration": "5-10 دقائق"},
            {"name": "انعكاس النمط", "desc": "تدريب التنسيق الحسي الحركي - قم بمحاكاة الحركات الظاهرة بدقة وثبات", "img": os.path.join(_ASSETS_DIR, "mirrorme.png"), "script": os.path.join(_software_games_dir, "mirror_me.py"), "difficulty": "متوسط", "duration": "10-15 دقائق"},
            {"name": "سرعة الاستجابة", "desc": "قياس سرعة رد الفعل والتشتت - استجابة سريعة للمؤثرات البصرية", "img": os.path.join(_ASSETS_DIR, "lightreaction.png"), "script": None, "difficulty": "سهل", "duration": "3-5 دقائق"}
        ]

        # Recent Sessions Section
        self.history_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        self.history_frame.pack(fill="x", pady=(30, 0))

        history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        history_header.pack(fill="x")
        ctk.CTkLabel(history_header, text="آخر الجلسات", 
                     font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold")).pack(side="right")
        ctk.CTkLabel(history_header, text="عرض الكل", text_color=ACCENT_COLOR,
                     font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left")

        focus_colors = {"ممتاز": SUCCESS_COLOR, "جيد": INFO_COLOR, "متوسط": WARNING_COLOR, "ضعيف": ERROR_COLOR}
        focus_bg = {"ممتاز": SUCCESS_DIM, "جيد": "#0e3a4a", "متوسط": WARNING_DIM, "ضعيف": ERROR_DIM}

        def get_focus_label(rate):
            if rate >= 90: return "ممتاز"
            if rate >= 75: return "جيد"
            if rate >= 50: return "متوسط"
            return "ضعيف"

        def format_date(iso_str):
            if not iso_str: return "-"
            try:
                from datetime import datetime
                d = datetime.fromisoformat(iso_str.replace("Z", ""))
                months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                          "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
                return f"{d.day} {months[d.month - 1]}"
            except:
                return iso_str[:10]

        game_name_map = {
            "cfefe7e7-f858-4d27-8dba-b356f35de22c": "الضوء الأخضر",
            "06bc62cb-4d0c-4f74-b3a3-e569bd4163ad": "انعكاس النمط",
            "54bd242c-6a43-4d99-866e-74809e8c5201": "لعبة سايمون",
            "7dce4e9e-d20b-40a7-a2d5-6e3c9f0cda5e": "سرعة الاستجابة",
        }

        recent = sorted(self.sessions, key=lambda s: s.get("startTime", ""), reverse=True)[:5]
        if not recent:
            empty_lbl = ctk.CTkLabel(self.history_frame, text="لا توجد جلسات سابقة", text_color=TEXT_SECONDARY,
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=12))
            empty_lbl.pack(pady=10)
        else:
            for session in recent:
                rate = session.get("successRate", 0)
                focus = get_focus_label(rate)
                fc = focus_colors.get(focus, TEXT_SECONDARY)
                fb = focus_bg.get(focus, "#1a1a1a")

                game_name = session.get("gameName") or game_name_map.get(session.get("gameId", ""), "تمرين")
                duration = f"{session.get('durationMinutes', 0)} دقائق"
                date_str = format_date(session.get("startTime"))

                row = ctk.CTkFrame(self.history_frame, fg_color=CARD_COLOR, corner_radius=10, height=52)
                row.pack(fill="x", pady=4)
                row.pack_propagate(False)

                inner = ctk.CTkFrame(row, fg_color="transparent")
                inner.pack(fill="both", expand=True, padx=14, pady=6)

                result_box = ctk.CTkFrame(inner, fg_color="transparent")
                result_box.pack(side="left")
                ctk.CTkLabel(result_box, text=f"{rate}%",
                             font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")).pack(anchor="e")
                ctk.CTkLabel(result_box, text="نجاح", text_color=TEXT_SECONDARY,
                             font=ctk.CTkFont(family=FONT_FAMILY, size=10)).pack(anchor="e")

                focus_badge = ctk.CTkFrame(inner, fg_color=fb, corner_radius=6)
                focus_badge.pack(side="left", padx=(10, 0))
                ctk.CTkLabel(focus_badge, text=focus, text_color=fc,
                             font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold")).pack(padx=8, pady=2)

                ctk.CTkLabel(inner, text=duration, text_color=TEXT_SECONDARY,
                             font=ctk.CTkFont(family=FONT_FAMILY, size=11)).pack(side="left", padx=(10, 0))

                ctk.CTkLabel(inner, text=date_str, text_color=TEXT_SECONDARY,
                             font=ctk.CTkFont(family=FONT_FAMILY, size=11)).pack(side="right", padx=6)
                ctk.CTkLabel(inner, text=game_name,
                             font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).pack(side="right", padx=6)

        self.master.bind("<Configure>", self.on_window_resize)
        self.render_games(2)

    def create_stat_card(self, label, value, color):
        card = ctk.CTkFrame(self.stats_container, fg_color=CARD_COLOR, corner_radius=10, height=56)
        card.pack(fill="x", pady=4)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=8)

        value_label = ctk.CTkLabel(inner, text=value, text_color=color,
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"))
        value_label.pack(side="left")

        ctk.CTkLabel(inner, text=label, text_color=TEXT_SECONDARY,
                     font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="right", padx=(0, 6))

        # Extract numeric value for progress bar
        try:
            num = int(value.replace("%", "").replace("عملة", "").strip())
        except:
            num = 0
        bar_color = color
        bar = ctk.CTkProgressBar(card, height=3, corner_radius=0, fg_color="#1e293b",
                                 progress_color=bar_color, border_width=0)
        bar.pack(fill="x", padx=14, pady=(0, 6))
        bar.set(min(num / 100.0, 1.0))

    def on_window_resize(self, event):
        if event.widget == self.master:
            width = event.width
            content_width = width - 260
            new_cols = 1 if content_width < 700 else (2 if content_width < 1100 else 3)
            
            if not hasattr(self, 'current_cols') or self.current_cols != new_cols:
                self.current_cols = new_cols
                self.render_games(new_cols)

    def render_games(self, columns):
        for widget in self.games_frame.winfo_children():
            widget.destroy()

        for i in range(columns):
            self.games_frame.grid_columnconfigure(i, weight=1)

        for i, game in enumerate(self.games_data):
            row, col = i // columns, i % columns
            self.create_game_card(game, row, col)

    def start_session(self, game):
        import subprocess
        import sys
        import os
        
        script = game.get("script")
        if script and os.path.exists(script):
            print(f"[Dashboard] Starting {game['name']} ({script})...")
            subprocess.Popen([sys.executable, script, self.master.user_data["id"]])

    def create_game_card(self, game, row, col):
        diff_colors = {"سهل": SUCCESS_COLOR, "متوسط": WARNING_COLOR, "صعب": ERROR_COLOR}
        diff_bg = {"سهل": SUCCESS_DIM, "متوسط": WARNING_DIM, "صعب": ERROR_DIM}
        diff_color = diff_colors.get(game.get("difficulty", "متوسط"), ACCENT_COLOR)
        diff_bg_color = diff_bg.get(game.get("difficulty", "متوسط"), "#1e1b4b")

        card = ctk.CTkFrame(self.games_frame, height=210, corner_radius=16, 
                            fg_color=CARD_COLOR, border_width=1, border_color="#2a2a2a")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Top accent bar
        accent_bar = ctk.CTkFrame(card, height=3, corner_radius=0, fg_color=diff_color)
        accent_bar.pack(fill="x")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=16)

        # Top row: difficulty badge + icon
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        badge = ctk.CTkFrame(top, fg_color=diff_bg_color, corner_radius=6)
        badge.pack(side="left")
        ctk.CTkLabel(badge, text=game.get("difficulty", ""), text_color=diff_color,
                     font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold")).pack(padx=8, pady=3)

        duration_label = ctk.CTkLabel(top, text=game.get("duration", ""), text_color=TEXT_SECONDARY,
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=11))
        duration_label.pack(side="left", padx=(8, 0))

        icon_box = ctk.CTkFrame(top, width=56, height=56, corner_radius=10, fg_color=SIDEBAR_COLOR)
        icon_box.pack(side="right")
        icon_box.pack_propagate(False)

        try:
            img = ctk.CTkImage(light_image=Image.open(game["img"]), dark_image=Image.open(game["img"]), size=(44, 44))
            ctk.CTkLabel(icon_box, image=img, text="").pack(expand=True)
        except Exception:
            ctk.CTkLabel(icon_box, text="🎮", font=ctk.CTkFont(size=24)).pack(expand=True)

        # Info section
        info = ctk.CTkFrame(content, fg_color="transparent")
        info.pack(fill="both", expand=True, pady=(12, 0))

        ctk.CTkLabel(info, text=game["name"], font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold")).pack(anchor="e")

        ctk.CTkLabel(info, text=game["desc"], text_color=TEXT_SECONDARY, 
                      font=ctk.CTkFont(family=FONT_FAMILY, size=12), wraplength=180, justify="right").pack(anchor="e", pady=(6, 0))

        ctk.CTkButton(info, text="بدء التمرين", height=36, corner_radius=8, 
                      fg_color="#2d3748", hover_color=diff_color,
                      font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                      command=lambda g=game: self.start_session(g)).pack(anchor="e", pady=(12, 0))

if __name__ == "__main__":
    app = GameDashboard()
    app.mainloop()
