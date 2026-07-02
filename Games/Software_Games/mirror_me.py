import os
import sys

# Ensure project paths are in sys.path (works regardless of launch directory)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_games_dir = os.path.dirname(_script_dir)  # Games/
# Primary: resolve modules from Software_Games (backend_api, pose_engine, database)
for _p in (_script_dir, _games_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)
# Primary: resolve modules from Software_Games (backend_api, pose_engine, database)
for _p in (_script_dir, _games_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import cv2
import numpy as np
import pygame
import time
import random
import uuid
from pose_engine import PoseEngine
from datetime import datetime
from database import GameDatabase
from backend_api import create_session, save_mirror_me_trials, save_summary

# Get asset directory (Games/assets)
SCRIPT_DIR = _script_dir
ASSETS_DIR = os.path.join(_games_dir, "assets")

# Initialize Pygame for sound
pygame.init()
pygame.mixer.init()

# Visual Constants
# BGR Color Palette (OpenCV BGR Format)
COLOR_DARK = (10, 10, 10)
COLOR_SLATE = (59, 41, 30)
COLOR_INDIGO = (241, 102, 99)       # Primary Accent Indigo
COLOR_LIGHT_INDIGO = (248, 140, 129) # Hover Accent
COLOR_EMERALD = (129, 185, 16)      # Safe Green Light Color
COLOR_ROSE = (94, 63, 244)          # Danger Red Light Color
COLOR_AMBER = (11, 158, 245)         # Warning Amber Color
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (200, 200, 200)

COLORS = {
    'background': COLOR_DARK,
    'text': COLOR_WHITE,
    'success': COLOR_EMERALD,
    'warning': COLOR_AMBER,
    'error': COLOR_ROSE,
    'accent': COLOR_INDIGO,
    'button_idle': COLOR_SLATE,
    'button_hover': COLOR_LIGHT_INDIGO,
    'button_active': COLOR_INDIGO,
    'overlay': (10, 10, 10, 160)
}

def draw_glass_panel(img, x, y, w, h, bg_color=(20, 20, 20), border_color=COLOR_INDIGO, alpha=0.45, border_thickness=1, corner_radius=15):
    """Draws a beautiful semi-transparent glass panel with rounded corners and a border"""
    overlay = img.copy()
    r = corner_radius
    
    # Draw rounded rectangle on overlay
    cv2.circle(overlay, (x + r, y + r), r, bg_color, -1)
    cv2.circle(overlay, (x + w - r, y + r), r, bg_color, -1)
    cv2.circle(overlay, (x + r, y + h - r), r, bg_color, -1)
    cv2.circle(overlay, (x + w - r, y + h - r), r, bg_color, -1)
    cv2.rectangle(overlay, (x + r, y), (x + w - r, y + h), bg_color, -1)
    cv2.rectangle(overlay, (x, y + r), (x + w, y + h - r), bg_color, -1)
    
    # Apply alpha transparency
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Draw border on frame with anti-aliasing
    cv2.ellipse(img, (x + r, y + r), (r, r), 180, 0, 90, border_color, border_thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + w - r, y + r), (r, r), 270, 0, 90, border_color, border_thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + w - r, y + h - r), (r, r), 0, 0, 90, border_color, border_thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + r, y + h - r), (r, r), 90, 0, 90, border_color, border_thickness, cv2.LINE_AA)
    
    cv2.line(img, (x + r, y), (x + w - r, y), border_color, border_thickness, cv2.LINE_AA)
    cv2.line(img, (x + w, y + r), (x + w, y + h - r), border_color, border_thickness, cv2.LINE_AA)
    cv2.line(img, (x + r, y + h), (x + w - r, y + h), border_color, border_thickness, cv2.LINE_AA)
    cv2.line(img, (x, y + r), (x, y + h - r), border_color, border_thickness, cv2.LINE_AA)

def draw_glowing_circle(img, center, radius, color, thickness=2, glow_factor=3):
    """Draws a circular element with a smooth glowing outer ring"""
    for i in range(glow_factor, 0, -1):
        alpha = 0.15 / i
        overlay = img.copy()
        cv2.circle(overlay, center, radius + i*3, color, thickness + i*2, cv2.LINE_AA)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    cv2.circle(img, center, radius, color, thickness, cv2.LINE_AA)

class Button:
    def __init__(self, x, y, w, h, text, callback_val=None, color=COLORS['button_idle'], hover_color=COLORS['button_hover']):
        self.rect = (x, y, w, h)
        self.text = text
        self.callback_val = callback_val
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.hover_start_time = 0
        self.click_ready = False
        self.pose_hover_active = False

    def draw(self, frame, pose_hover=False):
        x, y, w, h = self.rect
        is_hovered = self.is_hovered or pose_hover
        bg = (25, 20, 20) if is_hovered else COLOR_DARK
        border = COLOR_LIGHT_INDIGO if is_hovered else COLOR_INDIGO
        thickness = 2 if is_hovered else 1
        alpha = 0.8 if is_hovered else 0.5
        
        # Draw glass panel for the button
        draw_glass_panel(frame, x, y, w, h, bg, border, alpha, thickness, 12)
        
        # Text centering
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.65
        text_thickness = 2
        text_size = cv2.getTextSize(self.text, font, font_scale, text_thickness)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, self.text, (text_x, text_y), font, font_scale, COLOR_WHITE, text_thickness, cv2.LINE_AA)
        
        # Draw hold progress bar if being hovered by pose
        if self.pose_hover_active:
            progress = min(1.0, (time.time() - self.hover_start_time) / 1.0)
            if progress > 0:
                prog_w = int((w - 20) * progress)
                cv2.rectangle(frame, (x + 10, y + h - 6), (x + 10 + prog_w, y + h - 3), COLOR_EMERALD, -1, cv2.LINE_AA)

    def check_interaction(self, mouse_pos, pose_pos=None):
        x, y, w, h = self.rect
        mx, my = mouse_pos
        
        # Mouse Hover
        self.is_hovered = (x <= mx <= x + w and y <= my <= y + h)
        
        # Pose Hover (landmark position)
        self.pose_hover_active = False
        if pose_pos:
            px, py = pose_pos
            if x <= px <= x + w and y <= py <= y + h:
                self.pose_hover_active = True
                if self.hover_start_time == 0:
                    self.hover_start_time = time.time()
                elif time.time() - self.hover_start_time > 1.0: # Hold for 1s to click
                    self.click_ready = True
            else:
                self.hover_start_time = 0
                self.click_ready = False
        
        return self.is_hovered or self.click_ready


EASY_MOVEMENTS = [
    "Raise Right Hand",
    "Raise Left Hand",
    "Hands on Hips",
    "Touch Knees",
    "Put Hand Above Head"
]

MEDIUM_MOVEMENTS = [
    "Raise Both Hands",
    "Cross Arms on Chest",
    "Arms Out to Sides",
    "Flex Muscles",
    "One Hand Up, One Hand on Hip"
]

HARD_MOVEMENTS = [
    "Archer Pose",
    "The Surfer",
    "Crouching Tiger",
    "Tree Pose",
    "Arms Forming a Circle"
]

MOVEMENTS = EASY_MOVEMENTS # Default

class MirrorMeGame:
    def __init__(self, child_id="CHILD001"):
        self.cap = self._init_camera()
        self.engine = PoseEngine()
        self.db = GameDatabase()
        self.child_id = child_id
        self.session_id = str(uuid.uuid4())[:8]
        self.game_start_timestamp = time.time()
        
        self.state = "CALIBRATION"
        self.round_number = 0
        self.total_rounds = 10
        self.score = 0
        self.mirror_video = True # Default to mirror mode
        
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.buttons = []
        self.state_init = None
        # cv2.namedWindow("Mirror Me") # Handled by Tkinter
        # cv2.setMouseCallback("Mirror Me", self._mouse_callback)
        
        self.available_movements = EASY_MOVEMENTS
        self.current_movement = None
        self.start_time = 0
        self.hold_start_time = 0
        self.hold_duration_required = 2.0 # Default
        
        self.last_feedback = ""
        self.feedback_color = COLORS['text']
        self.feedback_timer = 0
        
        self.stats = [] # Store results for final summary
        self.trial_results = [] # Agent-Request-style per-trial data
        self.round_attention_frames = 0
        self.round_total_frames = 0
        
        # Difficulty Settings
        self.difficulties = {
            'EASY': {'timeout': 10.0, 'hold': 1.5, 'desc': 'Easy: Relaxed pace'},
            'MEDIUM': {'timeout': 7.0, 'hold': 2.5, 'desc': 'Medium: Standard challenge'},
            'HARD': {'timeout': 5.0, 'hold': 4.0, 'desc': 'Hard: Pro reflection'}
        }
        self.difficulty = 'MEDIUM' # Default
        
        self.total_reaction_time = 0
        
        self.reset_stats()
        self._load_current_ref_images()

    @staticmethod
    def _init_camera():
        """Tries camera indices 0-4 and returns the first working one."""
        for idx in range(5):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    print(f"[Camera] Using camera index {idx}")
                    return cap
                cap.release()
        print("[Camera] No working camera found. Using fallback (index 0).")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        return cap

    def reset_stats(self):
        """Resets statistics for a new game session."""
        self.state = "CALIBRATION"
        self.round_number = 0
        self.score = 0
        self.start_time = 0
        self.hold_start_time = 0
        self.last_feedback = ""
        self.feedback_timer = 0
        self.stats = []
        self.trial_results = []
        self.round_attention_frames = 0
        self.round_total_frames = 0
        self.direction_errors_count = 0
        self.premature_moves_count = 0
        self.tracking_loss_total_time = 0
        self.consecutive_success = 0
        self.max_consecutive_success = 0
        self.hold_stability_data = [] 
        self.total_reaction_time = 0
        self.body_scale_factors = [] # To normalize movement by distance
        self.session_saved = False
        self.state_init = None
        self.current_movement = None

        
        # Load reference images
        self.ref_images = {}
        self.img_mapping = {
            "Raise Right Hand": os.path.join(ASSETS_DIR, "raise_right_hand.png"),
            "Raise Left Hand": os.path.join(ASSETS_DIR, "raise_left_hand.png"),
            "Hands on Hips": os.path.join(ASSETS_DIR, "nano_banana_hands_on_hips.png"),
            "Touch Knees": os.path.join(ASSETS_DIR, "touch_knees.png"),
            "Put Hand Above Head": os.path.join(ASSETS_DIR, "hand_above_head.png"),
            "Raise Both Hands": os.path.join(ASSETS_DIR, "raise_both_hands.png"),
            "Cross Arms on Chest": os.path.join(ASSETS_DIR, "cross_arms.png"),
            "Arms Out to Sides": os.path.join(ASSETS_DIR, "arms_out.png"),
            "Flex Muscles": os.path.join(ASSETS_DIR, "flex_muscles.png"),
            "One Hand Up, One Hand on Hip": os.path.join(ASSETS_DIR, "one_up_one_hip.png"),
            "Archer Pose": os.path.join(ASSETS_DIR, "archer.png"),
            "The Surfer": os.path.join(ASSETS_DIR, "surfer.png"),
            "The Flamingo": os.path.join(ASSETS_DIR, "flamingo.png"),
            "Crouching Tiger": os.path.join(ASSETS_DIR, "tiger.png"),
            "Tree Pose": os.path.join(ASSETS_DIR, "tree_pose.png"),
            "Arms Forming a Circle": os.path.join(ASSETS_DIR, "circle_arms.png")
        }
        self._load_current_ref_images()

    def _load_current_ref_images(self):
        """Loads reference images for the current movement set."""
        self.ref_images = {}
        for move in self.available_movements:
            path = self.img_mapping.get(move)
            if path:
                img = cv2.imread(path)
                if img is not None:
                    self.ref_images[move] = cv2.resize(img, (200, 200))

    def _show_camera_error(self):
        """Creates an error frame when camera is unavailable."""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[:] = COLOR_DARK
        msg = "Camera not available!"
        sub = "Please check your camera connection and restart."
        cv2.putText(frame, msg, (1280//2 - 250, 720//2 - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLOR_ROSE, 3, cv2.LINE_AA)
        cv2.putText(frame, sub, (1280//2 - 200, 720//2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_GRAY, 2, cv2.LINE_AA)
        cv2.putText(frame, "Press ESC or Q to exit", (1280//2 - 150, 720//2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_AMBER, 2, cv2.LINE_AA)
        return frame

    def update(self):
        """Single update step, returns the frame to display."""
        ret, frame = self.cap.read()
        if not ret:
            return self._show_camera_error()
        
        frame = cv2.resize(frame, (1280, 720)) # Resize to HD resolution
        if self.mirror_video:
            frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        smoothed_lms, raw_lms = self.engine.process_frame(frame, mirrored=self.mirror_video)
        
        if self.state == "CALIBRATION":
            self._handle_calibration(frame, smoothed_lms)
        elif self.state == "DIFFICULTY":
            self._handle_difficulty_selection(frame, smoothed_lms)
        elif self.state == "HOLD_SELECTION":
            self._handle_hold_selection(frame, smoothed_lms)
        elif self.state == "INSTRUCTION":
            self._handle_instruction()
        elif self.state == "TRACKING":
            self._handle_tracking(smoothed_lms)
        elif self.state == "FEEDBACK":
            self._handle_feedback()
        elif self.state == "SUMMARY":
            self._handle_summary(frame, smoothed_lms)
            return frame # Show summary frame

        # Reset click for next frame
        self.mouse_clicked = False

        # Drawing
        self._draw_ui(frame, raw_lms)
        return frame

    def restart(self):
        """Restarts the game stats."""
        self.reset_stats()
        self.game_start_timestamp = time.time()
        self.session_id = str(uuid.uuid4())[:8]

    def release(self):
        """Releases the camera."""
        if self.cap.isOpened():
            self.cap.release()

    def cleanup(self):
        """Standard cleanup method."""
        self.release()

    def _mouse_callback(self, event, x, y, flags, param):
        self.mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_clicked = True

    def _handle_calibration(self, frame, landmarks):
        h, w, _ = frame.shape
        if self.start_time == 0:
            self.start_time = time.time()
        
        elapsed = time.time() - self.start_time
        
        # Draw full screen glass overlay
        draw_glass_panel(frame, w//4, h//4, w//2, h//2, (15, 15, 15), COLOR_INDIGO, 0.7, 2, 20)
        
        # Center progress wheel
        center_x, center_y = w//2, h//2
        radius = 60
        progress = min(1.0, elapsed / 3.0)
        
        # Draw outer circle
        cv2.circle(frame, (center_x, center_y), radius, COLOR_SLATE, 2, cv2.LINE_AA)
        # Draw filled arc
        angle = int(360 * progress)
        cv2.ellipse(frame, (center_x, center_y), (radius, radius), -90, 0, angle, COLOR_EMERALD, 5, cv2.LINE_AA)
        
        # Text inside circle
        countdown = max(0, 3 - int(elapsed))
        cv2.putText(frame, str(countdown), (center_x - 12, center_y + 12), cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLOR_WHITE, 3, cv2.LINE_AA)
        
        # Instruction text
        cv2.putText(frame, "STAND STILL & READY", (w//2 - 160, h//2 - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_INDIGO, 2, cv2.LINE_AA)
        cv2.putText(frame, "Please center yourself and stay stable to begin", (w//2 - 240, h//2 + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_GRAY, 1, cv2.LINE_AA)
        
        if elapsed < 3.0:
            self.last_feedback = f"Calibration: Stand still... {int(3 - elapsed)}"
            self.feedback_color = COLORS['warning']
        else:
            self.state = "DIFFICULTY"
            self.start_time = 0

    def _handle_difficulty_selection(self, frame, landmarks):
        h, w, _ = frame.shape
        # Create buttons if they don't exist for this state
        if not self.buttons or self.state_init != "DIFFICULTY":
            btn_w, btn_h = 200, 50
            start_y = h // 4 + 100
            self.buttons = [
                Button(w//2 - btn_w//2, start_y, btn_w, btn_h, "EASY", "EASY"),
                Button(w//2 - btn_w//2, start_y + 70, btn_w, btn_h, "MEDIUM", "MEDIUM"),
                Button(w//2 - btn_w//2, start_y + 140, btn_w, btn_h, "HARD", "HARD")
            ]
            self.state_init = "DIFFICULTY"

        # Draw a beautiful glass panel overlay for difficulty
        draw_glass_panel(frame, w//4, h//4, w//2, h//2 + 50, (15, 15, 15), COLOR_INDIGO, 0.65, 2, 20)
        
        cv2.putText(frame, "SELECT DIFFICULTY", (w//2 - 150, h//4 + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLORS['accent'], 3, cv2.LINE_AA)

        # Pose interaction point (using index finger or nose)
        pose_pt = None
        if landmarks:
            # Using Index Finger Tip (19 or 20)
            target = landmarks[19] if self.mirror_video else landmarks[20]
            if target[3] > 0.5:
                pose_pt = (int(target[0] * w), int(target[1] * h))
                cv2.circle(frame, pose_pt, 10, COLORS['accent'], -1)

        for btn in self.buttons:
            interacted = btn.check_interaction(self.mouse_pos, pose_pt)
            btn.draw(frame, pose_hover=interacted)
            
            if (self.mouse_clicked and btn.is_hovered) or btn.click_ready:
                self.difficulty = btn.callback_val
                self.available_movements = {
                    'EASY': EASY_MOVEMENTS,
                    'MEDIUM': MEDIUM_MOVEMENTS,
                    'HARD': HARD_MOVEMENTS
                }[self.difficulty]
                self.hold_duration_required = self.difficulties[self.difficulty]['hold']
                self.state = "HOLD_SELECTION"
                self.buttons = [] # Clear for next state
                self.last_feedback = f"Level Set: {self.difficulty}"
                self.feedback_color = COLORS['success']
                break

    def _handle_hold_selection(self, frame, landmarks):
        h, w, _ = frame.shape
        if not self.buttons or self.state_init != "HOLD_SELECTION":
            btn_w, btn_h = 60, 50
            start_y = h // 4 + 150
            self.buttons = [
                Button(w//2 - 100, start_y, btn_w, btn_h, "-", "DEC"),
                Button(w//2 + 40, start_y, btn_w, btn_h, "+", "INC"),
                Button(w//2 - 100, start_y + 80, 200, 50, "START GAME", "START")
            ]
            self.state_init = "HOLD_SELECTION"

        # Draw a beautiful glass panel overlay for hold adjustment
        draw_glass_panel(frame, w//4, h//4, w//2, h//2 + 100, (15, 15, 15), COLOR_AMBER, 0.65, 2, 20)
        
        cv2.putText(frame, "ADJUST HOLD TIME", (w//2 - 150, h//4 + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLORS['warning'], 3, cv2.LINE_AA)
        
        cv2.putText(frame, f"{self.hold_duration_required:.1f}s", (w//2 - 30, h//4 + 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['success'], 3, cv2.LINE_AA)

        pose_pt = None
        if landmarks:
            target = landmarks[19] if self.mirror_video else landmarks[20]
            if target[3] > 0.5:
                pose_pt = (int(target[0] * w), int(target[1] * h))
                cv2.circle(frame, pose_pt, 10, COLORS['accent'], -1)

        for btn in self.buttons:
            interacted = btn.check_interaction(self.mouse_pos, pose_pt)
            btn.draw(frame, pose_hover=interacted)
            
            if (self.mouse_clicked and btn.is_hovered) or btn.click_ready:
                if btn.callback_val == "DEC":
                    self.hold_duration_required = max(0.5, self.hold_duration_required - 0.5)
                elif btn.callback_val == "INC":
                    self.hold_duration_required = min(10.0, self.hold_duration_required + 0.5)
                elif btn.callback_val == "START":
                    self.state = "INSTRUCTION"
                    self._load_current_ref_images()
                    self.last_feedback = f"Hold Time: {self.hold_duration_required}s"
                    self.feedback_color = COLORS['success']
                    self.start_time = time.time()
                    self.buttons = []
                    break


    def _handle_instruction(self):
        if self.current_movement is None:
            self.current_movement = random.choice(self.available_movements)
            self.start_time = time.time()
            self.last_feedback = f"Get Ready: {self.current_movement}"
            self.feedback_color = COLORS['text']
            self.already_doing_pose = False # Reset for this round
            
        # Impulsivity Check: Is the user already in the pose before the tracking starts?
        # We'll check this once near the end of the instruction phase
        instruction_elapsed = time.time() - self.start_time
        if 1.5 < instruction_elapsed < 2.0 and not self.already_doing_pose:
            # Check if they are already doing the pose (passing a "virtual" mirrored state)
            # We briefly peek at the engine's last landmarks
            last_lms = self.engine.history[-1] if self.engine.history else None
            correct, _ = self.engine.get_movement_check(self.current_movement, last_lms, mirrored=self.mirror_video)
            if correct:
                self.already_doing_pose = True
                self.premature_moves_count += 1

        if instruction_elapsed > 2.0:
            self.state = "TRACKING"
            self.start_time = time.time() # Start timer for reaction
            self.current_round_positions = [] # To track stability for Motor Control


    def _compute_pose_similarity(self, movement, landmarks):
        """Returns a 0-1 similarity score for how well the user matches the target pose."""
        if not landmarks:
            return 0.0
        try:
            m = self.mirror_video
            l_wrist = landmarks[16] if m else landmarks[15]
            r_wrist = landmarks[15] if m else landmarks[16]
            l_shldr = landmarks[12] if m else landmarks[11]
            r_shldr = landmarks[11] if m else landmarks[12]
            l_elbow = landmarks[14] if m else landmarks[13]
            r_elbow = landmarks[13] if m else landmarks[14]
            nose = landmarks[0]

            if movement == "Raise Right Hand":
                ang = np.degrees(PoseEngine.angle_between(r_shldr, r_elbow, r_wrist))
                score = (1.0 - min(ang / 90.0, 1.0)) * 0.6
                score += 0.4 if r_wrist[1] < r_shldr[1] - 0.1 else 0.0
                return min(score, 1.0)
            elif movement == "Raise Left Hand":
                ang = np.degrees(PoseEngine.angle_between(l_shldr, l_elbow, l_wrist))
                score = (1.0 - min(ang / 90.0, 1.0)) * 0.6
                score += 0.4 if l_wrist[1] < l_shldr[1] - 0.1 else 0.0
                return min(score, 1.0)
            elif movement == "Hands on Hips":
                dl = np.linalg.norm(l_wrist[:2] - landmarks[24 if m else 23][:2])
                dr = np.linalg.norm(r_wrist[:2] - landmarks[23 if m else 24][:2])
                score = (1.0 - min(dl / 0.3, 1.0)) * 0.5 + (1.0 - min(dr / 0.3, 1.0)) * 0.5
                return max(0.0, score)
            elif movement == "Touch Knees":
                dl = np.linalg.norm(l_wrist[:2] - landmarks[26 if m else 25][:2])
                dr = np.linalg.norm(r_wrist[:2] - landmarks[25 if m else 26][:2])
                score = (1.0 - min(dl / 0.2, 1.0)) * 0.5 + (1.0 - min(dr / 0.2, 1.0)) * 0.5
                return max(0.0, score)
            elif movement == "Put Hand Above Head":
                r_up = max(0, 1.0 - (r_wrist[1] / nose[1]) * 2) if nose[1] > 0 else 0
                l_up = max(0, 1.0 - (l_wrist[1] / nose[1]) * 2) if nose[1] > 0 else 0
                return max(r_up, l_up)
            elif movement == "Raise Both Hands":
                la = np.degrees(PoseEngine.angle_between(l_shldr, l_elbow, l_wrist))
                ra = np.degrees(PoseEngine.angle_between(r_shldr, r_elbow, r_wrist))
                score = (1.0 - min(la / 90.0, 1.0)) * 0.3 + (1.0 - min(ra / 90.0, 1.0)) * 0.3
                score += 0.2 if l_wrist[1] < l_shldr[1] - 0.1 else 0.0
                score += 0.2 if r_wrist[1] < r_shldr[1] - 0.1 else 0.0
                return min(score, 1.0)
            elif movement == "Cross Arms on Chest":
                dl = np.linalg.norm(l_wrist[:2] - r_shldr[:2])
                dr = np.linalg.norm(r_wrist[:2] - l_shldr[:2])
                score = (1.0 - min(dl / 0.3, 1.0)) * 0.5 + (1.0 - min(dr / 0.3, 1.0)) * 0.5
                return max(0.0, score)
            elif movement == "Arms Out to Sides":
                sl = abs(l_wrist[0] - l_shldr[0])
                sr = abs(r_wrist[0] - r_shldr[0])
                score = min(sl / 0.4, 1.0) * 0.5 + min(sr / 0.4, 1.0) * 0.5
                return max(0.0, score)
            elif movement == "Flex Muscles":
                elbows_out = (1.0 - min(abs(l_shldr[1] - l_elbow[1]) / 0.15, 1.0)) * 0.5
                wrists_up = (1.0 - min(abs(l_wrist[1] - l_elbow[1]) / 0.15, 1.0)) * 0.5
                return elbows_out + wrists_up
            elif movement == "One Hand Up, One Hand on Hip":
                rh_up = max(0, 1.0 - r_wrist[1] / r_shldr[1]) if r_shldr[1] > 0 else 0
                lh_hip = max(0, 1.0 - np.linalg.norm(l_wrist[:2] - landmarks[24 if m else 23][:2]) / 0.3)
                lh_up = max(0, 1.0 - l_wrist[1] / l_shldr[1]) if l_shldr[1] > 0 else 0
                rh_hip = max(0, 1.0 - np.linalg.norm(r_wrist[:2] - landmarks[23 if m else 24][:2]) / 0.3)
                return max(rh_up * 0.5 + lh_hip * 0.5, lh_up * 0.5 + rh_hip * 0.5)
            elif movement == "Archer Pose":
                r_arm_forward = max(0, 1.0 - abs(r_wrist[0] - r_shldr[0]) / 0.4)
                l_ear_dist = max(0, 1.0 - np.linalg.norm(l_wrist[:2] - landmarks[8 if m else 7][:2]) / 0.3)
                l_arm_forward = max(0, 1.0 - abs(l_wrist[0] - l_shldr[0]) / 0.4)
                r_ear_dist = max(0, 1.0 - np.linalg.norm(r_wrist[:2] - landmarks[7 if m else 8][:2]) / 0.3)
                return max(r_arm_forward * 0.5 + l_ear_dist * 0.5, l_arm_forward * 0.5 + r_ear_dist * 0.5)
            elif movement == "Arms Forming a Circle":
                both_up = (1.0 - min(r_wrist[1] / nose[1], 1.0)) * 0.4 + (1.0 - min(l_wrist[1] / nose[1], 1.0)) * 0.4
                hands_close = max(0, 1.0 - np.linalg.norm(l_wrist[:2] - r_wrist[:2]) / 0.3) * 0.2
                return both_up + hands_close
            correct, _ = self.engine.get_movement_check(movement, landmarks, mirrored=self.mirror_video)
            return 1.0 if correct else 0.0
        except Exception:
            return 0.0

    def _handle_tracking(self, landmarks):
        elapsed = time.time() - self.start_time
        timeout = self.difficulties[self.difficulty]['timeout']
        self.round_total_frames += 1
        
        if elapsed > timeout + 2.0: # 2s instruction + difficulty-based timeout
            self.round_attention_frames = self.round_total_frames
            self._save_round_data(False, elapsed, False, 0, 0.0, 0.0, 0.0)
            self.state = "FEEDBACK"
            return

        correct, dir_err = self.engine.get_movement_check(self.current_movement, landmarks, mirrored=self.mirror_video)
        
        # Tracking Distraction (Tracking loss)
        if landmarks is None:
            self.tracking_loss_total_time += 1.0/30.0
        else:
            self.round_attention_frames += 1
        
        if correct:
            if self.hold_start_time == 0:
                self.hold_start_time = time.time()
            hold_elapsed = time.time() - self.hold_start_time
            
            # Motor Control: Save landmark positions during hold to check stability later
            if landmarks:
                lp = [landmarks[15][:2], landmarks[16][:2]]
                self.current_round_positions.append(lp)
                s_dist = np.linalg.norm(landmarks[11][:2] - landmarks[12][:2])
                if s_dist > 0.05:
                    self.body_scale_factors.append(s_dist)
            
            self.last_feedback = f"Holding... {hold_elapsed:.1f}/{self.hold_duration_required:.1f}s"
            self.feedback_color = COLORS['success']
            
            if hold_elapsed >= self.hold_duration_required:
                self.score += 1
                current_stability = 0
                pose_sim = self._compute_pose_similarity(self.current_movement, landmarks)
                fidget = 0.0
                if self.current_round_positions:
                    raw_var = float(np.var(self.current_round_positions, axis=0).mean())
                    avg_scale = np.mean(self.body_scale_factors) if self.body_scale_factors else 0.2
                    current_stability = raw_var / (avg_scale ** 2)
                    self.hold_stability_data.append(current_stability)
                    fidget = min(1.0, current_stability * 2.0)
                
                attention_pct = 1.0
                if self.round_total_frames > 0:
                    attention_pct = self.round_attention_frames / self.round_total_frames
                
                self._save_round_data(True, elapsed, dir_err, hold_elapsed, current_stability, pose_sim, fidget, attention_pct)
                self.state = "FEEDBACK"
        else:
            self.hold_start_time = 0
            if dir_err:
                self.direction_errors_count += 1
                self.last_feedback = "Wrong Side! Use your other hand."
                self.feedback_color = COLORS['error']
            else:
                self.last_feedback = "Follow the instruction!"
                self.feedback_color = COLORS['text']


    def _handle_feedback(self):
        if self.feedback_timer == 0:
            self.feedback_timer = time.time()
        
        if time.time() - self.feedback_timer > 2.0:
            self.round_number += 1
            if self.round_number >= self.total_rounds:
                self.state = "SUMMARY"
            else:
                self.state = "INSTRUCTION"
                self.current_movement = None
                self.hold_start_time = 0
                self.feedback_timer = 0

    def _save_round_data(self, correct, reaction, dir_err, hold, stability=0, pose_similarity=0.0, fidget_score=0.0, attention_percent=1.0):
        is_premature = 1 if (correct and self.already_doing_pose) else 0
        self.db.save_round(
            self.session_id, 
            self.child_id,
            "Mirror Me",
            self.current_movement, 
            round(reaction, 2), 
            1 if correct else 0, 
            round(hold, 2), 
            1 if dir_err else 0,
            stability=round(stability, 6),
            is_premature=is_premature,
            target_pose_id=f"pose-{self.round_number+1}",
            pose_similarity=round(pose_similarity, 4),
            fidget_score=round(fidget_score, 4),
            attention_percent=round(attention_percent, 4)
        )
        self.stats.append({
            'num': self.round_number + 1,
            'move': self.current_movement,
            'correct': correct,
            'reaction': reaction,
            'dir_err': dir_err,
            'stability': stability,
            'is_premature': is_premature,
            'pose_similarity': pose_similarity,
            'fidget_score': fidget_score,
            'attention_percent': attention_percent
        })
        
        # Store in Agent Request format
        self.trial_results.append({
            "trialIndex": self.round_number + 1,
            "targetPoseId": f"pose-{self.round_number+1}",
            "reactionTimeMs": round(reaction * 1000, 0),
            "poseSimilarity": round(pose_similarity, 2),
            "holdingDurationMs": round(hold * 1000, 0),
            "fidgetScore": round(fidget_score, 2),
            "prematureMovement": bool(is_premature),
            "attentionPercent": round(attention_percent, 2)
        })
        
        if correct:
            self.consecutive_success += 1
            self.max_consecutive_success = max(self.max_consecutive_success, self.consecutive_success)
        else:
            self.consecutive_success = 0


    def _draw_ui(self, frame, raw_lms):
        h, w, _ = frame.shape
        
        # 1. Beautiful semi-transparent header bar
        draw_glass_panel(frame, 20, 15, 1240, 55, (15, 15, 15), COLOR_INDIGO, 0.55, 1, 10)
        header_text = f"ADHD SENSORY TRAINING: PATTERN REFLECTION"
        cv2.putText(frame, header_text, (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_WHITE, 2, cv2.LINE_AA)
        
        cv2.putText(frame, "|  LEVEL: " + self.difficulty, (520, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_LIGHT_INDIGO, 2, cv2.LINE_AA)
        
        stats_text = f"ROUND: {self.round_number+1}/{self.total_rounds}   SCORE: {self.score}"
        text_size = cv2.getTextSize(stats_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.putText(frame, stats_text, (1240 - 20 - text_size[0], 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2, cv2.LINE_AA)
        
        # 2. Left Panel: Active Pose Instruction
        if self.state in ["INSTRUCTION", "TRACKING"]:
            draw_glass_panel(frame, 20, 85, 340, 520, (15, 15, 15), COLOR_INDIGO, 0.55, 2, 15)
            cv2.putText(frame, "TARGET MOVEMENT", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_LIGHT_INDIGO, 2, cv2.LINE_AA)
            cv2.line(frame, (35, 135), (345, 135), COLOR_SLATE, 1, cv2.LINE_AA)
            
            # Show current movement name
            if self.current_movement:
                move_words = self.current_movement.split()
                y_pos = 170
                for word in move_words[:3]:
                    cv2.putText(frame, word, (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_WHITE, 2, cv2.LINE_AA)
                    y_pos += 30
                if len(move_words) > 3:
                    cv2.putText(frame, " ".join(move_words[3:]), (40, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_WHITE, 2, cv2.LINE_AA)
            
            # Reference image inside Left Panel
            if self.current_movement in self.ref_images:
                ref_img = self.ref_images[self.current_movement]
                ref_h, ref_w, _ = ref_img.shape
                x_offset = 20 + (340 - ref_w) // 2
                y_offset = 360
                
                # Draw white frame around ref image
                cv2.rectangle(frame, (x_offset - 4, y_offset - 4), (x_offset + ref_w + 4, y_offset + ref_h + 4), COLOR_WHITE, -1)
                frame[y_offset:y_offset+ref_h, x_offset:x_offset+ref_w] = ref_img
                cv2.rectangle(frame, (x_offset - 4, y_offset - 4), (x_offset + ref_w + 4, y_offset + ref_h + 4), COLOR_INDIGO, 2, cv2.LINE_AA)
                cv2.putText(frame, "REFERENCE", (x_offset, y_offset - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_LIGHT_INDIGO, 1, cv2.LINE_AA)

        # 3. Right Panel: Active hold tracker and countdown
        if self.state == "TRACKING":
            is_holding = (self.hold_start_time > 0)
            panel_border = COLOR_EMERALD if is_holding else COLOR_AMBER
            draw_glass_panel(frame, 920, 85, 340, 520, (15, 15, 15), panel_border, 0.55, 2, 15)
            
            cv2.putText(frame, "MATCH DETECTOR", (940, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, panel_border, 2, cv2.LINE_AA)
            cv2.line(frame, (935, 135), (1245, 135), COLOR_SLATE, 1, cv2.LINE_AA)
            
            # Draw holding progress circle
            center_x, center_y = 1090, 260
            radius = 70
            
            if is_holding:
                hold_elapsed = time.time() - self.hold_start_time
                progress = min(1.0, hold_elapsed / self.hold_duration_required)
                
                draw_glowing_circle(frame, (center_x, center_y), radius, COLOR_EMERALD, 4, 3)
                
                angle = int(360 * progress)
                cv2.ellipse(frame, (center_x, center_y), (radius, radius), -90, 0, angle, COLOR_WHITE, 6, cv2.LINE_AA)
                
                rem_seconds = max(0.0, self.hold_duration_required - hold_elapsed)
                cv2.putText(frame, f"{rem_seconds:.1f}s", (center_x - 30, center_y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_WHITE, 2, cv2.LINE_AA)
                cv2.putText(frame, "HOLDING", (940, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_EMERALD, 2, cv2.LINE_AA)
            else:
                cv2.circle(frame, (center_x, center_y), radius, COLOR_SLATE, 2, cv2.LINE_AA)
                cv2.circle(frame, (center_x, center_y), 8, COLOR_AMBER, -1)
                cv2.putText(frame, "MATCHING", (940, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_AMBER, 2, cv2.LINE_AA)
            
            cv2.putText(frame, "Stability Level:", (940, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_GRAY, 1, cv2.LINE_AA)
            stability_str = "EXCELLENT" if is_holding else "CALIBRATING"
            cv2.putText(frame, stability_str, (940, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_EMERALD if is_holding else COLOR_WHITE, 2, cv2.LINE_AA)

        # 4. Bottom Feedback & Navigation Area
        draw_glass_panel(frame, 20, 620, 1240, 85, (15, 15, 15), COLOR_INDIGO, 0.55, 1, 12)
        
        pulse_color = self.feedback_color
        cv2.circle(frame, (50, 662), 8, pulse_color, -1, cv2.LINE_AA)
        cv2.circle(frame, (50, 662), 14, pulse_color, 2, cv2.LINE_AA)
        
        cv2.putText(frame, self.last_feedback, (85, 655), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_WHITE, 2, cv2.LINE_AA)
        
        sub_feedback = "Align your body with the target pose card"
        if "Wrong" in self.last_feedback:
            sub_feedback = "Mirror alignment error! Match the active hand/pose side."
        elif "Ready" in self.last_feedback:
            sub_feedback = "Excellent lock! Prepare for the next posture..."
        elif "Success" in self.last_feedback or "Match" in self.last_feedback:
            sub_feedback = "Pose Matched! Stay extremely still to lock success."
            
        cv2.putText(frame, sub_feedback, (85, 685), cv2.FONT_HERSHEY_SIMPLEX, 0.52, COLOR_GRAY, 1, cv2.LINE_AA)
        
        # Draw interactive overlay buttons if they exist
        for btn in getattr(self, 'buttons', []):
            btn.draw(frame)

        # 5. Skeleton Rendering
        if raw_lms:
            state = "search"
            if self.state == "TRACKING":
                if self.hold_start_time > 0:
                    state = "success"
                else:
                    if "Wrong" in self.last_feedback:
                        state = "error"
                    else:
                        state = "holding"
            elif self.state == "FEEDBACK":
                state = "success" if self.feedback_color == COLORS['success'] else "error"
            
            self.engine.draw_landmarks(frame, raw_lms, match_state=state)

    def _handle_summary(self, frame, landmarks):
        h, w, _ = frame.shape

        avg_react = np.mean([s['reaction'] for s in self.stats]) if self.stats else 0
        avg_similarity = np.mean([s['pose_similarity'] for s in self.stats]) if self.stats else 0
        avg_fidget = np.mean([s['fidget_score'] for s in self.stats]) if self.stats else 0
        avg_attention = np.mean([s['attention_percent'] for s in self.stats]) if self.stats else 0

        if not self.session_saved:
            # Save to local SQLite (sync_remote=False to avoid duplicate API session)
            self.db.save_session({
                "child_id": self.child_id,
                "session_id": self.session_id,
                "game_name": "Mirror Me",
                "difficulty": self.difficulty,
                "start_time": datetime.fromtimestamp(self.game_start_timestamp).isoformat(),
                "duration_minutes": round((time.time() - self.game_start_timestamp) / 60, 2),
                "total_trials": self.total_rounds,
                "success_rate": round((self.score / self.total_rounds * 100) if self.total_rounds > 0 else 0, 2),
                "avg_reaction_time": round(avg_react, 4),
                "max_consecutive_success": self.max_consecutive_success,
                "false_moves": self.direction_errors_count,
                "false_stops": 0,
                "red_phase_errors": 0,
                "green_phase_errors": 0,
                "impulsivity_index": round((self.premature_moves_count / self.total_rounds * 100) if self.total_rounds > 0 else 0, 2),
                "motor_control_score": round(float(np.mean(self.hold_stability_data)) * 100 if self.hold_stability_data else 0, 2),
                "distraction_score": round(self.tracking_loss_total_time, 2),
                "average_similarity": round(float(avg_similarity), 2),
                "total_fidget_score": round(float(avg_fidget), 2),
                "attention_overall": round(float(avg_attention), 2)
            }, sync_remote=False)

            # Send to .NET backend API via backend_api.py (single sync path)
            api_session_id = create_session(self.child_id, "mirror_me")
            if api_session_id:
                save_mirror_me_trials(api_session_id, self.trial_results)
                save_summary(api_session_id, {
                    "totalTrials": self.total_rounds,
                    "averageReactionTimeMs": round(avg_react * 1000, 0),
                    "averageSimilarity": round(avg_similarity, 2),
                    "totalFidgetScore": round(avg_fidget, 2),
                    "attentionOverall": round(avg_attention, 2)
                })

            self.session_saved = True

        draw_glass_panel(frame, 50, 30, 1180, 660, (10, 10, 10), COLOR_INDIGO, 0.75, 2, 20)

        cv2.putText(frame, "MIRROR ME: SESSION REPORT", (90, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_WHITE, 2, cv2.LINE_AA)
        session_info = f"Child: {self.child_id} | Diff: {self.difficulty} | Duration: {round((time.time()-self.game_start_timestamp)/60, 1)}m"
        cv2.putText(frame, session_info, (90, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_GRAY, 1, cv2.LINE_AA)

        avg_react_ms = round(avg_react * 1000, 0)
        xl, yt, cw, ch, gx, gy = 70, 115, 185, 75, 10, 8

        cards = [
            ("TOTAL TRIALS", f"{self.total_rounds}", COLOR_EMERALD, f"completed: {self.score}"),
            ("AVG REACTION", f"{avg_react_ms:.0f}ms", COLOR_INDIGO, f"per trial average"),
            ("AVG SIMILARITY", f"{avg_similarity:.2f}", COLOR_AMBER, f"0.0 = poor, 1.0 = perfect"),
            ("FIDGET SCORE", f"{avg_fidget:.2f}", COLOR_ROSE, f"0.0 = stable, 1.0 = restless"),
            ("ATTENTION", f"{avg_attention:.0%}", COLOR_WHITE, f"overall focus during session"),
        ]

        for idx, (title, val, color, desc) in enumerate(cards):
            r, c = idx // 3, idx % 3
            cx = xl + c * (cw + gx)
            cy = yt + r * (ch + gy)
            draw_glass_panel(frame, cx, cy, cw, ch, (15, 15, 15), color, 0.45, 1, 8)
            cv2.line(frame, (cx + 8, cy + 2), (cx + cw - 8, cy + 2), color, 2, cv2.LINE_AA)
            cv2.putText(frame, title, (cx + 10, cy + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.35, COLOR_GRAY, 1, cv2.LINE_AA)
            cv2.putText(frame, val, (cx + 10, cy + 48), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA)
            cv2.putText(frame, desc, (cx + 10, cy + 68), cv2.FONT_HERSHEY_SIMPLEX, 0.3, COLOR_GRAY, 1, cv2.LINE_AA)

        xt, yt2, trial_h = 675, 120, 28
        trial_header_color = COLOR_INDIGO
        cols = [("T", 30), ("Pose", 140), ("React", 78), ("Simil", 72), ("Fidget", 72), ("Attn", 62), ("Hold", 72)]
        xo = xt
        cv2.putText(frame, "TRIAL DETAILS", (xt, yt2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_WHITE, 1, cv2.LINE_AA)
        for col_name, col_w in cols:
            cv2.putText(frame, col_name, (xo, yt2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, trial_header_color, 1, cv2.LINE_AA)
            xo += col_w + 2

        for i, trial in enumerate(self.trial_results):
            row_y = yt2 + 22 + i * trial_h
            if row_y > h - 60:
                break
            xo = xt
            cv2.rectangle(frame, (xt, row_y), (xt + 540, row_y + trial_h - 2), (25, 25, 25), 1, cv2.LINE_AA)

            t_color = COLOR_EMERALD if trial["poseSimilarity"] > 0.7 else (COLOR_AMBER if trial["poseSimilarity"] > 0.4 else COLOR_ROSE)

            vals = [
                str(trial["trialIndex"]),
                trial.get("targetPoseId", ""),
                f'{trial["reactionTimeMs"]:.0f}ms',
                f'{trial["poseSimilarity"]:.2f}',
                f'{trial["fidgetScore"]:.2f}',
                f'{trial["attentionPercent"]:.0%}',
                f'{trial["holdingDurationMs"]:.0f}ms'
            ]
            for vi, (_, col_w) in enumerate(cols):
                vc = t_color if vi == 3 else COLOR_WHITE
                cv2.putText(frame, vals[vi], (xo + 4, row_y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.35, vc, 1, cv2.LINE_AA)
                xo += col_w + 2

        footer_y = h - 80
        cv2.line(frame, (70, footer_y - 5), (1210, footer_y - 5), COLOR_SLATE, 1, cv2.LINE_AA)
        cv2.putText(frame, "Press ESC or Q to return to Dashboard", (w//2 - 200, footer_y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_AMBER, 1, cv2.LINE_AA)


    def run(self):
        cv2.namedWindow("Mirror Me", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Mirror Me", self._mouse_callback)
        while True:
            frame = self.update()
            if frame is None:
                break
            cv2.imshow("Mirror Me", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'): # ESC or q
                break
        self.cleanup()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    child_id = "CHILD001"
    if len(sys.argv) > 1:
        child_id = sys.argv[1]
    game = MirrorMeGame(child_id=child_id)
    game.run()
