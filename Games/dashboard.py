# ADHD Game Dashboard & Launcher
import os
import sys
import subprocess
import time
import urllib.request
import json
import threading

# Add current directory to path
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Try importing CustomTkinter and Pillow, with clean Tkinter fallbacks
USE_CUSTOM_TK = False
try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    USE_CUSTOM_TK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    print("Warning: customtkinter package not found. Falling back to standard Tkinter.")

USE_PIL = False
try:
    from PIL import Image, ImageTk
    USE_PIL = True
except ImportError:
    print("Warning: PIL (Pillow) package not found. Image previews will be disabled.")

# Configuration
API_BASE_URL = os.getenv("ADHD_API_BASE_URL", "http://localhost:5131")
DEVICE_KEY = os.getenv("GAME_DEVICE_API_KEY", "dev-game-device-key-change-me")

# Colors matching charcoal-and-indigo theme
COLOR_BG = "#121212"
COLOR_CARD = "#1e1e1e"
COLOR_ACCENT = "#5e3ff4"  # Indigo
COLOR_ACCENT_HOVER = "#492ed4"
COLOR_TEXT = "#ffffff"
COLOR_MUTED = "#8a8a8a"
COLOR_SUCCESS = "#10b981"
COLOR_ERROR = "#ef4444"

# Global session variables
current_child_id = None
current_child_name = "Guest User"
api_online = False

def check_api_status():
    """Check if the backend API is live."""
    global api_online
    try:
        url = f"{API_BASE_URL}/api/Children"
        req = urllib.request.Request(url)
        req.add_header("X-Game-Device-Key", DEVICE_KEY)
        with urllib.request.urlopen(req, timeout=2.5) as response:
            if response.status in [200, 201, 204]:
                api_online = True
                return True
    except Exception:
        pass
    api_online = False
    return False

def get_all_children():
    """Fetch all children from the backend API."""
    try:
        url = f"{API_BASE_URL}/api/Children"
        req = urllib.request.Request(url)
        req.add_header("X-Game-Device-Key", DEVICE_KEY)
        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and data.get("succeeded"):
                return data.get("data", [])
    except Exception as e:
        print(f"Error fetching children: {e}")
    return []

def validate_child_id(child_id):
    """Validate Child ID against the backend API."""
    global current_child_name
    if not child_id.strip():
        return False, "Please enter a valid Child ID."
    
    # Try fetching children list from API
    try:
        url = f"{API_BASE_URL}/api/Children"
        req = urllib.request.Request(url)
        req.add_header("X-Game-Device-Key", DEVICE_KEY)
        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and data.get("succeeded"):
                children_list = data.get("data", [])
                for child in children_list:
                    if child.get("id") == child_id:
                        current_child_name = child.get("name", "Child User")
                        return True, f"Welcome back, {current_child_name}!"
                return False, f"Child ID '{child_id}' not found in database."
    except Exception as e:
        print(f"API Connection Error: {e}")
        # If API is offline, allow bypass in Offline Mode
        current_child_name = f"Offline Kid ({child_id})"
        return True, "Offline Mode: Proceeding with local profile."
    
    return False, "Unknown verification error."

# --- CustomTkinter GUI Implementation ---
if USE_CUSTOM_TK:
    class CustomApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("ADHD Sensory Game Suite")
            self.geometry("960x650")
            self.resizable(False, False)
            self.configure(fg_color=COLOR_BG)
            
            # Load images
            self.images = {}
            self.load_preview_images()
            
            # Show Login Screen
            self.show_login_screen()

        def load_preview_images(self):
            if not USE_PIL:
                return
            asset_mapping = {
                "simon": "assets/simon.png",
                "reaction": "assets/lightreaction.png",
                "redlight": "assets/redlight.png",
                "mirrorme": "assets/mirrorme.png"
            }
            for key, relative_path in asset_mapping.items():
                full_path = os.path.join(_script_dir, relative_path)
                if os.path.exists(full_path):
                    try:
                        pil_img = Image.open(full_path)
                        # Resize to fit card
                        pil_img = pil_img.resize((180, 110), Image.Resampling.LANCZOS)
                        self.images[key] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(180, 110))
                    except Exception as e:
                        print(f"Error loading image {relative_path}: {e}")

        def show_login_screen(self):
            # Clear window
            for widget in self.winfo_children():
                widget.destroy()

            # Main container centered
            self.login_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15, width=420, height=380)
            self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.login_frame.pack_propagate(False)

            # Title
            title = ctk.CTkLabel(self.login_frame, text="ADHD SENSORY PLAY", font=("Inter", 24, "bold"), text_color=COLOR_TEXT)
            title.pack(pady=(35, 5))
            
            subtitle = ctk.CTkLabel(self.login_frame, text="CENTRAL GAME SUITE", font=("Inter", 12), text_color=COLOR_ACCENT)
            subtitle.pack(pady=(0, 20))

            # Dropdown label
            entry_lbl = ctk.CTkLabel(self.login_frame, text="Select Child Profile:", font=("Inter", 13), text_color=COLOR_MUTED)
            entry_lbl.pack(anchor="w", padx=45, pady=0)
            
            # Combobox
            self.children_map = {}
            self.child_combobox = ctk.CTkComboBox(self.login_frame, values=["Loading children..."], width=330, height=40,
                                                  fg_color="#121212", border_color=COLOR_MUTED, text_color=COLOR_TEXT,
                                                  command=self.on_combobox_select)
            self.child_combobox.pack(pady=(5, 15))

            # Hidden entry field for manual ID entry fallback
            self.child_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter ID manually", width=330, height=40, 
                                            fg_color="#121212", border_color=COLOR_MUTED, text_color=COLOR_TEXT)
            self.child_entry.bind("<Return>", lambda e: self.attempt_login())

            # Status Message
            self.status_lbl = ctk.CTkLabel(self.login_frame, text="", font=("Inter", 12), text_color=COLOR_SUCCESS)
            self.status_lbl.pack(pady=5)

            # Login Button
            self.login_btn = ctk.CTkButton(self.login_frame, text="Log In", width=330, height=45, 
                                           fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                                           font=("Inter", 14, "bold"), command=self.attempt_login)
            self.login_btn.pack(pady=(10, 10))

            # Fetch children and update connection status
            def load_data():
                online = check_api_status()
                children = []
                if online:
                    self.status_lbl.configure(text="Connected. Loading children...", text_color=COLOR_SUCCESS)
                    children = get_all_children()
                
                # If API online and we got children
                if children:
                    values = []
                    for child in children:
                        display_str = f"{child.get('name', 'Unknown')} ({child.get('id')})"
                        values.append(display_str)
                        self.children_map[display_str] = child
                    values.append("Manual ID Entry...")
                    
                    self.status_lbl.configure(text="Connected to Backend API", text_color=COLOR_SUCCESS)
                    self.child_combobox.configure(values=values)
                    if values:
                        self.child_combobox.set(values[0])
                else:
                    # Offline fallback options
                    values = [
                        "Offline Kid 1 (OFFLINE001)",
                        "Offline Kid 2 (OFFLINE002)",
                        "Offline Guest (GUEST)",
                        "Manual ID Entry..."
                    ]
                    self.children_map = {
                        "Offline Kid 1 (OFFLINE001)": {"id": "OFFLINE001", "name": "Offline Kid 1"},
                        "Offline Kid 2 (OFFLINE002)": {"id": "OFFLINE002", "name": "Offline Kid 2"},
                        "Offline Guest (GUEST)": {"id": "GUEST", "name": "Offline Guest"}
                    }
                    msg = "Offline Mode (Select offline child or enter ID manually)"
                    self.status_lbl.configure(text=msg, text_color=COLOR_MUTED)
                    self.child_combobox.configure(values=values)
                    self.child_combobox.set(values[0])

            threading.Thread(target=load_data, daemon=True).start()

        def on_combobox_select(self, value):
            if value == "Manual ID Entry...":
                self.login_frame.configure(height=440)
                self.child_entry.pack(after=self.child_combobox, pady=(5, 15))
                self.child_entry.focus()
            else:
                self.child_entry.pack_forget()
                self.login_frame.configure(height=380)

        def attempt_login(self):
            selected = self.child_combobox.get()
            if selected == "Loading children...":
                return
            
            global current_child_id, current_child_name
            
            if selected == "Manual ID Entry...":
                child_id = self.child_entry.get().strip()
                if not child_id:
                    self.status_lbl.configure(text="Please enter a valid Child ID.", text_color=COLOR_ERROR)
                    return
                
                self.login_btn.configure(state="disabled", text="Validating...")
                
                def run_val():
                    global current_child_id
                    success, msg = validate_child_id(child_id)
                    if success:
                        current_child_id = child_id
                        self.status_lbl.configure(text=msg, text_color=COLOR_SUCCESS)
                        self.after(1000, self.show_main_dashboard)
                    else:
                        self.status_lbl.configure(text=msg, text_color=COLOR_ERROR)
                        self.login_btn.configure(state="normal", text="Log In")
                
                threading.Thread(target=run_val, daemon=True).start()
            else:
                child_data = self.children_map.get(selected)
                if child_data:
                    current_child_id = child_data.get("id")
                    current_child_name = child_data.get("name")
                    msg = f"Welcome back, {current_child_name}!"
                    self.status_lbl.configure(text=msg, text_color=COLOR_SUCCESS)
                    self.after(500, self.show_main_dashboard)

        def show_main_dashboard(self):
            # Clear window
            for widget in self.winfo_children():
                widget.destroy()

            # Header Frame
            header_frame = ctk.CTkFrame(self, height=80, fg_color=COLOR_CARD, corner_radius=0)
            header_frame.pack(fill="x", side="top")
            
            welcome_lbl = ctk.CTkLabel(header_frame, text=f"Welcome, {current_child_name}", font=("Inter", 18, "bold"), text_color=COLOR_TEXT)
            welcome_lbl.pack(side="left", padx=30, pady=25)

            id_tag = ctk.CTkLabel(header_frame, text=f"ID: {current_child_id}", font=("Inter", 12), text_color=COLOR_ACCENT)
            id_tag.pack(side="left", padx=10, pady=25)

            logout_btn = ctk.CTkButton(header_frame, text="Log Out", width=90, height=32, 
                                       fg_color="transparent", border_color=COLOR_MUTED, border_width=1,
                                       hover_color="#333333", text_color=COLOR_TEXT, font=("Inter", 12),
                                       command=self.show_login_screen)
            logout_btn.pack(side="right", padx=30, pady=25)

            # Subtitle/Instruct
            info_lbl = ctk.CTkLabel(self, text="Select a game to start your ADHD sensory training session:", 
                                    font=("Inter", 14), text_color=COLOR_MUTED)
            info_lbl.pack(anchor="w", padx=50, pady=(35, 10))

            # Grid Container
            grid_frame = ctk.CTkFrame(self, fg_color="transparent")
            grid_frame.pack(fill="both", expand=True, padx=40, pady=(10, 20))

            # Configure columns
            grid_frame.columnconfigure((0, 1), weight=1, uniform="equal")
            grid_frame.rowconfigure((0, 1), weight=1, uniform="equal")

            games = [
                {
                    "title": "Mirror Me",
                    "desc": "OpenCV-based posture replication and attention builder.",
                    "platform": "Software (Webcam Required)",
                    "script": "Software_Games/mirror_me.py",
                    "img_key": "mirrorme",
                    "col": 0, "row": 0
                },
                {
                    "title": "Red Light Green Light",
                    "desc": "OpenCV movement control and motor stabilization trainer.",
                    "platform": "Software (Webcam Required)",
                    "script": "Software_Games/green_light.py",
                    "img_key": "redlight",
                    "col": 1, "row": 0
                },
                {
                    "title": "Simon Memory",
                    "desc": "Memory retention and LED pattern repetition trainer.",
                    "platform": "Hardware (Simulated/Raspberry Pi)",
                    "script": "Hardware_Games/simon_game.py",
                    "img_key": "simon",
                    "col": 0, "row": 1
                },
                {
                    "title": "Reaction Time",
                    "desc": "Action speed and motor reaction training game.",
                    "platform": "Hardware (Simulated/Raspberry Pi)",
                    "script": "Hardware_Games/reaction_time.py",
                    "img_key": "reaction",
                    "col": 1, "row": 1
                }
            ]

            for g in games:
                card = ctk.CTkFrame(grid_frame, fg_color=COLOR_CARD, corner_radius=12, border_color="#2b2b2b", border_width=1)
                card.grid(column=g["col"], row=g["row"], padx=15, pady=15, sticky="nsew")
                
                # Layout card internally
                card.columnconfigure(0, weight=1)
                card.columnconfigure(1, weight=2)
                
                # Image column
                img_lbl = ctk.CTkLabel(card, text="")
                img_lbl.grid(column=0, row=0, rowspan=4, padx=(15, 10), pady=15)
                if g["img_key"] in self.images:
                    img_lbl.configure(image=self.images[g["img_key"]])
                else:
                    # Flat color replacement placeholder
                    img_lbl.configure(text=g["title"][:2].upper(), font=("Inter", 24, "bold"), 
                                      fg_color="#333333", width=180, height=110, corner_radius=8)

                # Info columns
                title_lbl = ctk.CTkLabel(card, text=g["title"], font=("Inter", 16, "bold"), text_color=COLOR_TEXT, anchor="w")
                title_lbl.grid(column=1, row=0, padx=(10, 15), pady=(15, 2), sticky="w")

                plat_lbl = ctk.CTkLabel(card, text=g["platform"], font=("Inter", 11, "bold"), text_color=COLOR_ACCENT, anchor="w")
                plat_lbl.grid(column=1, row=1, padx=(10, 15), pady=0, sticky="w")

                desc_lbl = ctk.CTkLabel(card, text=g["desc"], font=("Inter", 11), text_color=COLOR_MUTED, anchor="w", 
                                        wraplength=220, justify="left")
                desc_lbl.grid(column=1, row=2, padx=(10, 15), pady=2, sticky="w")

                play_btn = ctk.CTkButton(card, text="Play Game", width=120, height=32, 
                                         fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                                         font=("Inter", 12, "bold"),
                                         command=lambda s=g["script"]: self.launch_game_subprocess(s))
                play_btn.grid(column=1, row=3, padx=(10, 15), pady=(5, 15), sticky="w")

            # Status bar
            status_bar = ctk.CTkFrame(self, height=35, fg_color="#181818", corner_radius=0)
            status_bar.pack(fill="x", side="bottom")
            
            status_indicator = "Connected" if api_online else "Offline"
            status_color = COLOR_SUCCESS if api_online else COLOR_MUTED
            stat_lbl = ctk.CTkLabel(status_bar, text=f"API Status: {status_indicator}", font=("Inter", 11), text_color=status_color)
            stat_lbl.pack(side="left", padx=20, pady=5)
            
            ver_lbl = ctk.CTkLabel(status_bar, text="ADHD Sensory Suite v1.0", font=("Inter", 11), text_color=COLOR_MUTED)
            ver_lbl.pack(side="right", padx=20, pady=5)

        def launch_game_subprocess(self, script_path):
            self.withdraw()  # Hide dashboard
            
            def run_game():
                try:
                    python_exe = sys.executable
                    working_dir = os.path.dirname(os.path.join(_script_dir, script_path))
                    script_name = os.path.basename(script_path)
                    
                    # Launch subprocess
                    proc = subprocess.Popen([python_exe, script_name, current_child_id], cwd=working_dir)
                    proc.wait()
                except Exception as e:
                    print(f"Error launching game subprocess: {e}")
                
                # Restore dashboard on main thread
                self.after(100, self.deiconify)
                self.after(200, self.show_main_dashboard)

            threading.Thread(target=run_game, daemon=True).start()

    app = CustomApp()
    app.mainloop()

# --- Standard Tkinter Fallback Implementation ---
else:
    class StandardApp:
        def __init__(self, root):
            self.root = root
            self.root.title("ADHD Sensory Game Suite")
            self.root.geometry("960x650")
            self.root.resizable(False, False)
            self.root.configure(bg=COLOR_BG)
            
            # Configure custom theme style for TTK
            self.style = ttk.Style()
            self.style.theme_use('clam')
            self.style.configure('TFrame', background=COLOR_BG)
            self.style.configure('Card.TFrame', background=COLOR_CARD, relief='flat')
            
            self.images = {}
            self.load_preview_images()
            self.show_login_screen()

        def load_preview_images(self):
            if not USE_PIL:
                return
            asset_mapping = {
                "simon": "assets/simon.png",
                "reaction": "assets/lightreaction.png",
                "redlight": "assets/redlight.png",
                "mirrorme": "assets/mirrorme.png"
            }
            for key, relative_path in asset_mapping.items():
                full_path = os.path.join(_script_dir, relative_path)
                if os.path.exists(full_path):
                    try:
                        pil_img = Image.open(full_path)
                        pil_img = pil_img.resize((180, 110), Image.Resampling.LANCZOS)
                        self.images[key] = ImageTk.PhotoImage(pil_img)
                    except Exception as e:
                        print(f"Error loading image {relative_path}: {e}")

        def show_login_screen(self):
            for widget in self.root.winfo_children():
                widget.destroy()

            # Center login box
            self.login_frame = tk.Frame(self.root, bg=COLOR_CARD, width=420, height=380)
            self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.login_frame.pack_propagate(False)

            title = tk.Label(self.login_frame, text="ADHD SENSORY PLAY", font=("Helvetica", 22, "bold"), fg=COLOR_TEXT, bg=COLOR_CARD)
            title.pack(pady=(35, 5))
            
            subtitle = tk.Label(self.login_frame, text="CENTRAL GAME SUITE", font=("Helvetica", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_CARD)
            subtitle.pack(pady=(0, 20))

            entry_lbl = tk.Label(self.login_frame, text="Select Child Profile:", font=("Helvetica", 11), fg=COLOR_MUTED, bg=COLOR_CARD)
            entry_lbl.pack(anchor="w", padx=50, pady=0)

            # Combobox
            self.children_map = {}
            self.child_combobox = ttk.Combobox(self.login_frame, values=["Loading children..."], font=("Helvetica", 11), width=30, state="readonly")
            self.child_combobox.set("Loading children...")
            self.child_combobox.pack(pady=(5, 15))
            self.child_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

            # Hidden Entry box
            self.child_entry = tk.Entry(self.login_frame, font=("Helvetica", 12), width=32, bg="#121212", fg=COLOR_TEXT, 
                                        insertbackground=COLOR_TEXT, relief='flat', bd=5)
            self.child_entry.bind("<Return>", lambda e: self.attempt_login())

            self.status_lbl = tk.Label(self.login_frame, text="", font=("Helvetica", 10), fg=COLOR_SUCCESS, bg=COLOR_CARD)
            self.status_lbl.pack(pady=5)

            # Flat button style
            self.login_btn = tk.Button(self.login_frame, text="Log In", font=("Helvetica", 12, "bold"), 
                                       bg=COLOR_ACCENT, fg=COLOR_TEXT, activebackground=COLOR_ACCENT_HOVER, 
                                       activeforeground=COLOR_TEXT, relief='flat', width=28, height=2,
                                       command=self.attempt_login)
            self.login_btn.pack(pady=(10, 10))

            def load_data():
                online = check_api_status()
                children = []
                if online:
                    self.status_lbl.config(text="Connected. Loading children...", fg=COLOR_SUCCESS)
                    children = get_all_children()
                
                if children:
                    values = []
                    for child in children:
                        display_str = f"{child.get('name', 'Unknown')} ({child.get('id')})"
                        values.append(display_str)
                        self.children_map[display_str] = child
                    values.append("Manual ID Entry...")
                    
                    self.status_lbl.config(text="Connected to Backend API", fg=COLOR_SUCCESS)
                    self.child_combobox['values'] = values
                    self.child_combobox.set(values[0])
                else:
                    values = [
                        "Offline Kid 1 (OFFLINE001)",
                        "Offline Kid 2 (OFFLINE002)",
                        "Offline Guest (GUEST)",
                        "Manual ID Entry..."
                    ]
                    self.children_map = {
                        "Offline Kid 1 (OFFLINE001)": {"id": "OFFLINE001", "name": "Offline Kid 1"},
                        "Offline Kid 2 (OFFLINE002)": {"id": "OFFLINE002", "name": "Offline Kid 2"},
                        "Offline Guest (GUEST)": {"id": "GUEST", "name": "Offline Guest"}
                    }
                    self.status_lbl.config(text="Offline Mode (Select offline child or enter ID manually)", fg=COLOR_MUTED)
                    self.child_combobox['values'] = values
                    self.child_combobox.set(values[0])

            threading.Thread(target=load_data, daemon=True).start()

        def on_combobox_select(self, event=None):
            val = self.child_combobox.get()
            if val == "Manual ID Entry...":
                self.login_frame.config(height=440)
                self.child_entry.pack(after=self.child_combobox, pady=(5, 15))
                self.child_entry.focus_set()
            else:
                self.child_entry.pack_forget()
                self.login_frame.config(height=380)

        def attempt_login(self):
            selected = self.child_combobox.get()
            if selected == "Loading children...":
                return
            
            global current_child_id, current_child_name
            
            if selected == "Manual ID Entry...":
                child_id = self.child_entry.get().strip()
                if not child_id:
                    self.status_lbl.config(text="Please enter a valid Child ID.", fg=COLOR_ERROR)
                    return
                
                self.login_btn.config(state="disabled", text="Validating...")
                
                def run_val():
                    global current_child_id
                    success, msg = validate_child_id(child_id)
                    if success:
                        current_child_id = child_id
                        self.status_lbl.config(text=msg, fg=COLOR_SUCCESS)
                        self.root.after(1000, self.show_main_dashboard)
                    else:
                        self.status_lbl.config(text=msg, fg=COLOR_ERROR)
                        self.login_btn.config(state="normal", text="Log In")
                
                threading.Thread(target=run_val, daemon=True).start()
            else:
                child_data = self.children_map.get(selected)
                if child_data:
                    current_child_id = child_data.get("id")
                    current_child_name = child_data.get("name")
                    msg = f"Welcome back, {current_child_name}!"
                    self.status_lbl.config(text=msg, fg=COLOR_SUCCESS)
                    self.root.after(500, self.show_main_dashboard)

        def show_main_dashboard(self):
            for widget in self.root.winfo_children():
                widget.destroy()

            # Header Frame
            header_frame = tk.Frame(self.root, height=80, bg=COLOR_CARD)
            header_frame.pack(fill="x", side="top")
            header_frame.pack_propagate(False)
            
            welcome_lbl = tk.Label(header_frame, text=f"Welcome, {current_child_name}", font=("Helvetica", 16, "bold"), fg=COLOR_TEXT, bg=COLOR_CARD)
            welcome_lbl.pack(side="left", padx=30, pady=25)

            id_tag = tk.Label(header_frame, text=f"ID: {current_child_id}", font=("Helvetica", 11), fg=COLOR_ACCENT, bg=COLOR_CARD)
            id_tag.pack(side="left", padx=10, pady=28)

            logout_btn = tk.Button(header_frame, text="Log Out", font=("Helvetica", 10), 
                                   bg=COLOR_CARD, fg=COLOR_TEXT, activebackground="#333333", 
                                   activeforeground=COLOR_TEXT, relief='flat', highlightbackground=COLOR_MUTED,
                                   highlightthickness=1, width=10, command=self.show_login_screen)
            logout_btn.pack(side="right", padx=30, pady=25)

            # Subtitle
            info_lbl = tk.Label(self.root, text="Select a game to start your ADHD sensory training session:", 
                                font=("Helvetica", 12), fg=COLOR_MUTED, bg=COLOR_BG)
            info_lbl.pack(anchor="w", padx=50, pady=(35, 10))

            # Grid Container
            grid_frame = tk.Frame(self.root, bg=COLOR_BG)
            grid_frame.pack(fill="both", expand=True, padx=40, pady=(10, 20))

            # Configure grid structure
            grid_frame.columnconfigure((0, 1), weight=1, uniform="equal")
            grid_frame.rowconfigure((0, 1), weight=1, uniform="equal")

            games = [
                {
                    "title": "Mirror Me",
                    "desc": "OpenCV-based posture replication and attention builder.",
                    "platform": "Software (Webcam Required)",
                    "script": "Software_Games/mirror_me.py",
                    "img_key": "mirrorme",
                    "col": 0, "row": 0
                },
                {
                    "title": "Red Light Green Light",
                    "desc": "OpenCV movement control and motor stabilization trainer.",
                    "platform": "Software (Webcam Required)",
                    "script": "Software_Games/green_light.py",
                    "img_key": "redlight",
                    "col": 1, "row": 0
                },
                {
                    "title": "Simon Memory",
                    "desc": "Memory retention and LED pattern repetition trainer.",
                    "platform": "Hardware (Simulated/Raspberry Pi)",
                    "script": "Hardware_Games/simon_game.py",
                    "img_key": "simon",
                    "col": 0, "row": 1
                },
                {
                    "title": "Reaction Time",
                    "desc": "Action speed and motor reaction training game.",
                    "platform": "Hardware (Simulated/Raspberry Pi)",
                    "script": "Hardware_Games/reaction_time.py",
                    "img_key": "reaction",
                    "col": 1, "row": 1
                }
            ]

            for g in games:
                card = tk.Frame(grid_frame, bg=COLOR_CARD)
                card.grid(column=g["col"], row=g["row"], padx=15, pady=15, sticky="nsew")
                
                # internal grid configurations
                card.columnconfigure(0, weight=1)
                card.columnconfigure(1, weight=2)
                card.rowconfigure((0,1,2,3), weight=1)
                
                # Image column
                img_lbl = tk.Label(card, bg="#333333")
                img_lbl.grid(column=0, row=0, rowspan=4, padx=(15, 10), pady=15, sticky="nsew")
                if g["img_key"] in self.images:
                    img_lbl.config(image=self.images[g["img_key"]])
                else:
                    img_lbl.config(text=g["title"][:2].upper(), font=("Helvetica", 20, "bold"), fg=COLOR_TEXT, width=12, height=5)

                # Info columns
                title_lbl = tk.Label(card, text=g["title"], font=("Helvetica", 14, "bold"), fg=COLOR_TEXT, bg=COLOR_CARD, anchor="w")
                title_lbl.grid(column=1, row=0, padx=(10, 15), pady=(15, 2), sticky="w")

                plat_lbl = tk.Label(card, text=g["platform"], font=("Helvetica", 10, "bold"), fg=COLOR_ACCENT, bg=COLOR_CARD, anchor="w")
                plat_lbl.grid(column=1, row=1, padx=(10, 15), pady=0, sticky="w")

                desc_lbl = tk.Label(card, text=g["desc"], font=("Helvetica", 9), fg=COLOR_MUTED, bg=COLOR_CARD, anchor="w", 
                                    wraplength=220, justify="left")
                desc_lbl.grid(column=1, row=2, padx=(10, 15), pady=2, sticky="w")

                play_btn = tk.Button(card, text="Play Game", font=("Helvetica", 10, "bold"), 
                                     bg=COLOR_ACCENT, fg=COLOR_TEXT, activebackground=COLOR_ACCENT_HOVER, 
                                     activeforeground=COLOR_TEXT, relief='flat', width=12, height=1,
                                     command=lambda s=g["script"]: self.launch_game_subprocess(s))
                play_btn.grid(column=1, row=3, padx=(10, 15), pady=(5, 15), sticky="w")

            # Status bar
            status_bar = tk.Frame(self.root, height=35, bg="#181818")
            status_bar.pack(fill="x", side="bottom")
            status_bar.pack_propagate(False)
            
            status_indicator = "Connected" if api_online else "Offline"
            status_color = COLOR_SUCCESS if api_online else COLOR_MUTED
            stat_lbl = tk.Label(status_bar, text=f"API Status: {status_indicator}", font=("Helvetica", 9), fg=status_color, bg="#181818")
            stat_lbl.pack(side="left", padx=20, pady=8)
            
            ver_lbl = tk.Label(status_bar, text="ADHD Sensory Suite v1.0 (Fallback UI)", font=("Helvetica", 9), fg=COLOR_MUTED, bg="#181818")
            ver_lbl.pack(side="right", padx=20, pady=8)

        def launch_game_subprocess(self, script_path):
            self.root.withdraw()  # Hide dashboard
            
            def run_game():
                try:
                    python_exe = sys.executable
                    working_dir = os.path.dirname(os.path.join(_script_dir, script_path))
                    script_name = os.path.basename(script_path)
                    
                    # Launch subprocess
                    proc = subprocess.Popen([python_exe, script_name, current_child_id], cwd=working_dir)
                    proc.wait()
                except Exception as e:
                    print(f"Error launching game subprocess: {e}")
                
                # Restore dashboard
                self.root.after(100, self.root.deiconify)
                self.root.after(200, self.show_main_dashboard)

            threading.Thread(target=run_game, daemon=True).start()

    main_root = tk.Tk()
    app = StandardApp(main_root)
    main_root.mainloop()
