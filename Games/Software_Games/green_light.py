# Phoomiphat Kittisuphat 29/4/2023
# Modified version with comprehensive data extraction for ADHD training analysis

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
import time
import pygame
import threading
import json
import csv
from datetime import datetime
from database import GameDatabase
from pose_engine import PoseEngine
from backend_api import create_session, save_green_light_trials, save_summary
from collections import deque
import numpy as np

# تهيئة pygame للأصوات
pygame.mixer.init()

# تحميل ملفات الصوت
try:
    green_sound = pygame.mixer.Sound(os.path.join(_script_dir, "Green_light.mp3"))
    red_sound = pygame.mixer.Sound(os.path.join(_script_dir, "Red_Light.mp3"))
except:
    print("ملاحظة: ملفات الصوت غير موجودة، سيتم تشغيل البرنامج بدون صوت")
    green_sound = None
    red_sound = None


def play_sound(sound_file):
    """تشغيل الصوت في خيط منفصل"""
    if sound_file:
        threading.Thread(target=sound_file.play, daemon=True).start()


class MotionDetector:
    def __init__(self, threshold=15):
        self.threshold = threshold
        self.pose_engine = PoseEngine(smooth_factor=5)
        self.previous_landmarks = None
        self.start_time = None
        self.motion_history = deque(maxlen=100)  # حفظ تاريخ الحركة
        self.motion_magnitude_history = deque(maxlen=100)  # شدة الحركة
        self.last_raw_landmarks = None
        
    def detect_motion(self, frame):
        smoothed_landmarks, raw_landmarks = self.pose_engine.process_frame(frame, mirrored=True)
        self.last_raw_landmarks = raw_landmarks
        
        if smoothed_landmarks is None:
            self.previous_landmarks = None
            return False, 0.0

        if self.previous_landmarks is None:
            self.previous_landmarks = smoothed_landmarks
            self.start_time = time.time()
            return False, 0.0

        # Calculate displacement of key joints
        joints_to_track = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        total_displacement = 0.0
        count = 0
        
        for j in joints_to_track:
            if j in smoothed_landmarks and j in self.previous_landmarks:
                if smoothed_landmarks[j][3] > 0.5 and self.previous_landmarks[j][3] > 0.5:
                    dist = np.linalg.norm(smoothed_landmarks[j][:2] - self.previous_landmarks[j][:2])
                    total_displacement += dist
                    count += 1
                    
        if count > 0:
            motion_magnitude = total_displacement * 1000.0
        else:
            motion_magnitude = 0.0
            
        self.motion_magnitude_history.append(motion_magnitude)
        
        motion_detected = motion_magnitude >= self.threshold
        
        if motion_detected:
            self.motion_history.append({
                'time': time.time(),
                'magnitude': motion_magnitude,
                'area': 0,
                'num_contours': count
            })
            
        self.previous_landmarks = smoothed_landmarks
        return motion_detected, motion_magnitude


class GameDataCollector:
    def __init__(self, child_id="CHILD001", session_id=None):
        self.child_id = child_id
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # بيانات الجلسة
        self.session_start = time.time()
        self.session_data = {
            'session_info': {
                'child_id': child_id,
                'session_id': self.session_id,
                'start_time': datetime.now().isoformat(),
                'green_light_duration': 0,
                'red_light_duration': 0
            },
            'trials': [],
            'reaction_times': [],
            'false_moves': [],
            'false_stops': [],
            'freeze_durations': [],
            'movement_data': [],
            'phase_performance': {
                'green': {'total_time': 0, 'motion_count': 0, 'avg_magnitude': 0},
                'red': {'total_time': 0, 'motion_count': 0, 'avg_magnitude': 0}
            },
            'summary': {}
        }
        
        # متغيرات تتبع الأداء
        self.current_trial = {
            'phase': None,
            'start_time': None,
            'expected_duration': None,
            'motion_detected': False,
            'motion_time': None
        }
        
        # للتتبع المستمر
        self.consecutive_success = 0
        self.max_consecutive_success = 0
        self.last_error_time = None
        self.freeze_start = None
        self.is_frozen = False
        
    def start_phase(self, phase, duration):
        """بدء مرحلة جديدة (أخضر/أحمر)"""
        self.current_trial = {
            'phase': phase,
            'start_time': time.time(),
            'expected_duration': duration,
            'motion_detected': False,
            'motion_time': None,
            'motion_magnitude': 0,
            'motion_area': 0
        }
        
        if phase == 'red':
            self.freeze_start = time.time()
            self.is_frozen = True
            
    def end_phase(self, phase):
        """إنهاء المرحلة الحالية وتسجيل البيانات"""
        if self.current_trial['phase'] != phase:
            return
            
        end_time = time.time()
        actual_duration = end_time - self.current_trial['start_time']
        
        # تسجيل المحاولة
        trial_data = {
            'phase': phase,
            'start_time': self.current_trial['start_time'],
            'end_time': end_time,
            'expected_duration': self.current_trial['expected_duration'],
            'actual_duration': actual_duration,
            'motion_detected': self.current_trial['motion_detected'],
            'motion_time': self.current_trial['motion_time'],
            'motion_magnitude': self.current_trial['motion_magnitude'],
            'motion_area': self.current_trial['motion_area'],
            'success': not (phase == 'red' and self.current_trial['motion_detected'])
        }
        
        self.session_data['trials'].append(trial_data)
        
        # تحديث الإحصائيات
        if phase == 'red':
            if self.is_frozen and self.freeze_start:
                freeze_duration = end_time - self.freeze_start
                if not self.current_trial['motion_detected']:
                    self.session_data['freeze_durations'].append(freeze_duration)
            
            if self.current_trial['motion_detected']:
                # خطأ: تحرك في الأحمر
                self.session_data['false_moves'].append({
                    'time': self.current_trial['motion_time'],
                    'reaction_time': self.current_trial['motion_time'] - self.current_trial['start_time']
                })
                self.consecutive_success = 0
                self.last_error_time = time.time()
            else:
                # نجاح: لم يتحرك في الأحمر
                self.consecutive_success += 1
                if self.consecutive_success > self.max_consecutive_success:
                    self.max_consecutive_success = self.consecutive_success
                    
        elif phase == 'green':
            if self.current_trial['motion_detected']:
                # تأخر في الاستجابة للحركة
                reaction_time = self.current_trial['motion_time'] - self.current_trial['start_time']
                self.session_data['reaction_times'].append({
                    'time': self.current_trial['motion_time'],
                    'reaction_time': reaction_time
                })
            else:
                # خطأ: لم يتحرك في الأخضر
                self.session_data['false_stops'].append({
                    'time': end_time
                })
        
        self.is_frozen = False
        
    def record_motion(self, motion_detected, magnitude, area=0):
        """تسجيل حدث حركة"""
        if motion_detected and self.current_trial['phase']:
            current_time = time.time()
            if not self.current_trial['motion_detected']:
                self.current_trial['motion_detected'] = True
                self.current_trial['motion_time'] = current_time
                self.current_trial['motion_magnitude'] = magnitude
                self.current_trial['motion_area'] = area
                
        # تسجيل بيانات الحركة المستمرة
        self.session_data['movement_data'].append({
            'time': time.time(),
            'magnitude': magnitude,
            'phase': self.current_trial['phase'] if self.current_trial['phase'] else 'none'
        })
        
    def generate_summary(self):
        """توليد ملخص الجلسة والمؤشرات المركبة"""
        trials = self.session_data['trials']
        if not trials:
            return
            
        # إحصائيات أساسية
        red_trials = [t for t in trials if t['phase'] == 'red']
        green_trials = [t for t in trials if t['phase'] == 'green']
        
        false_moves = len(self.session_data['false_moves'])
        false_stops = len([t for t in green_trials if not t['motion_detected']])
        total_trials = len(red_trials) + len(green_trials)
        
        # مؤشر الاندفاعية (Impulsivity Index)
        impulsivity_index = (false_moves / len(red_trials)) * 100 if red_trials else 0
        
        # مؤشر التحكم الحركي
        if self.session_data['freeze_durations']:
            avg_freeze = sum(self.session_data['freeze_durations']) / len(self.session_data['freeze_durations'])
            expected_freeze = sum(t['expected_duration'] for t in red_trials) / len(red_trials) if red_trials else 1
            motor_control_score = (avg_freeze / expected_freeze) * 100
        else:
            motor_control_score = 0
            
        # متوسط زمن الاستجابة
        avg_reaction_time = 0
        if self.session_data['reaction_times']:
            avg_reaction_time = sum(r['reaction_time'] for r in self.session_data['reaction_times']) / len(self.session_data['reaction_times'])
            
        # درجة التشتت (تباين زمن الاستجابة)
        distraction_score = 0
        if len(self.session_data['reaction_times']) > 1:
            times = [r['reaction_time'] for r in self.session_data['reaction_times']]
            distraction_score = np.std(times) if times else 0
            
        # تحديث phase_performance
        for phase in ['green', 'red']:
            phase_trials = [t for t in trials if t['phase'] == phase]
            if phase_trials:
                total_time = sum(t['actual_duration'] for t in phase_trials)
                motion_count = sum(1 for t in phase_trials if t['motion_detected'])
                avg_magnitude = np.mean([t['motion_magnitude'] for t in phase_trials if t['motion_magnitude'] > 0]) if motion_count > 0 else 0
                
                self.session_data['phase_performance'][phase] = {
                    'total_time': total_time,
                    'motion_count': motion_count,
                    'avg_magnitude': avg_magnitude,
                    'trial_count': len(phase_trials)
                }
        
        self.session_data['summary'] = {
            'session_duration': time.time() - self.session_start,
            'total_trials': total_trials,
            'false_moves': false_moves,
            'false_stops': false_stops,
            'success_rate': max(0.0, ((total_trials - min(total_trials, false_moves) - false_stops) / total_trials * 100)) if total_trials > 0 else 0,
            'avg_reaction_time': avg_reaction_time,
            'impulsivity_index': impulsivity_index,
            'motor_control_score': motor_control_score,
            'distraction_score': distraction_score,
            'max_consecutive_success': self.max_consecutive_success,
            'time_before_first_error': self.calculate_time_to_first_error()
        }
        
    def calculate_time_to_first_error(self):
        """حساب الوقت قبل أول خطأ"""
        if self.last_error_time:
            return self.last_error_time - self.session_start
        return time.time() - self.session_start
        
    def save_data(self):
        """حفظ البيانات في ملفات"""
        # إنشاء مجلد للبيانات إذا لم يكن موجوداً
        if not os.path.exists('session_data'):
            os.makedirs('session_data')
            
        # حفظ بصيغة JSON
        json_filename = f"session_data/{self.child_id}_{self.session_id}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            
        # حفظ بصيغة CSV للملخص
        csv_filename = f"session_data/{self.child_id}_{self.session_id}_summary.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in self.session_data['summary'].items():
                writer.writerow([key, value])
                
        # حفظ بيانات المحاولات في CSV منفصل
        trials_csv = f"session_data/{self.child_id}_{self.session_id}_trials.csv"
        with open(trials_csv, 'w', newline='', encoding='utf-8') as f:
            if self.session_data['trials']:
                writer = csv.DictWriter(f, fieldnames=self.session_data['trials'][0].keys())
                writer.writeheader()
                writer.writerows(self.session_data['trials'])
                
        # حفظ في قاعدة البيانات الموحدة SQLite
        try:
            db = GameDatabase()
            summary = self.session_data['summary']
            session_summary = {
                "child_id": self.child_id,
                "session_id": self.session_id,
                "game_name": "Green Light",
                "start_time": datetime.fromtimestamp(self.session_start).isoformat(),
                "duration_minutes": round((time.time() - self.session_start) / 60, 2),
                "total_trials": summary.get('total_trials', 0),
                "success_rate": round(summary.get('success_rate', 0.0), 2),
                "impulsivity_index": round(summary.get('impulsivity_index', 0.0), 2),
                "motor_control_score": round(summary.get('motor_control_score', 0.0), 2),
                "distraction_score": round(summary.get('distraction_score', 0.0), 2),
                "avg_reaction_time": round(summary.get('avg_reaction_time', 0.0), 2),
                "max_consecutive_success": summary.get('max_consecutive_success', 0),
                "false_moves": summary.get('false_moves', 0),
                "false_stops": summary.get('false_stops', 0),
                "red_phase_errors": summary.get('false_moves', 0),
                "green_phase_errors": summary.get('false_stops', 0)
            }
            db.save_session(session_summary, sync_remote=False)
            
            # حفظ المحاولات الفردية
            for trial in self.session_data['trials']:
                success = 1 if trial['success'] else 0
                react = 0.0
                if trial['motion_time'] and trial['phase'] == 'green':
                    react = round(trial['motion_time'] - trial['start_time'], 2)
                db.save_round(
                    self.session_id,
                    self.child_id,
                    "Green Light",
                    trial['phase'].capitalize() + " Light",
                    react,
                    success,
                    round(trial['actual_duration'], 2) if not trial['motion_detected'] else 0.0,
                    1 if (trial['phase'] == 'red' and trial['motion_detected']) else 0,
                    stability=0.0,
                    is_premature=0
                )
            print("💾 SQLite Database: Session & trials successfully saved!")
        except Exception as e:
            print(f"⚠️ خطأ أثناء حفظ البيانات في قاعدة البيانات: {e}")

        print(f"\n✅ تم حفظ البيانات في:")
        print(f"   - {json_filename}")
        print(f"   - {csv_filename}")
        print(f"   - {trials_csv}")
        
        return json_filename


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

mouse_pos = (0, 0)
mouse_click_pos = None

def mouse_callback(event, x, y, flags, param):
    global mouse_click_pos, mouse_pos
    mouse_pos = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_click_pos = (x, y)


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


def draw_glowing_circle(img, center, radius, color, glow_color, thickness=3, pulse_speed=5):
    """Draws a stunning glowing neon orb with concentric circles for ambient bloom"""
    t = time.time() * pulse_speed
    pulse = np.sin(t) * 4
    r = int(radius + pulse)
    
    # Ambient glow rings
    overlay = img.copy()
    cv2.circle(overlay, center, r + 25, glow_color, 8, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.08, img, 0.92, 0, img)
    
    overlay = img.copy()
    cv2.circle(overlay, center, r + 15, glow_color, 12, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)
    
    overlay = img.copy()
    cv2.circle(overlay, center, r + 5, glow_color, -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.25, img, 0.75, 0, img)
    
    # Core circle
    cv2.circle(img, center, r, color, -1, cv2.LINE_AA)
    cv2.circle(img, center, r, COLOR_WHITE, 2, cv2.LINE_AA)


def draw_circular_progress(img, center, radius, progress, color, thickness=4):
    """Draws a circular progress ring for the active phase remaining duration"""
    end_angle = int(360 * progress) - 90
    cv2.ellipse(img, center, (radius, radius), 0, -90, end_angle, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, center, (radius, radius), 0, -90, 270, (40, 40, 40), 1, cv2.LINE_AA)


def draw_motion_visualizer(img, x, y, w, h, magnitude, max_val=50, threshold=15, bg_color=(20, 20, 20)):
    """Draws a sleek motion visualizer bar with live color shift from safe Green to alert Red"""
    draw_glass_panel(img, x, y, w, h, bg_color, (80, 80, 80), 0.5, 1, 8)
    
    mag = min(max_val, magnitude)
    fill_w = int((mag / max_val) * (w - 20))
    
    if fill_w > 0:
        if magnitude >= threshold:
            color = COLOR_ROSE
            if int(time.time() * 10) % 2 == 0:
                cv2.rectangle(img, (x + 10, y + 5), (x + 10 + fill_w, y + h - 5), (150, 100, 255), -1, cv2.LINE_AA)
        elif magnitude >= threshold * 0.6:
            color = COLOR_AMBER
        else:
            color = COLOR_EMERALD
            
        cv2.rectangle(img, (x + 10, y + 5), (x + 10 + fill_w, y + h - 5), color, -1, cv2.LINE_AA)
        
    thresh_x = x + 10 + int((threshold / max_val) * (w - 20))
    if thresh_x < x + w - 10:
        cv2.line(img, (thresh_x, y + 2), (thresh_x, y + h - 2), COLOR_WHITE, 2, cv2.LINE_AA)
        cv2.putText(img, "ALERT LIMIT", (thresh_x - 45, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.35, COLOR_WHITE, 1, cv2.LINE_AA)


def draw_end_screen(img, state, summary_data):
    """Draws a beautifully structured post-session performance analytics summary"""
    h, w, _ = img.shape
    
    # Fade screen background
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), COLOR_DARK, -1)
    cv2.addWeighted(overlay, 0.82, img, 0.18, 0, img)
    
    # Metrics Container Card
    card_w, card_h = 750, 480
    card_x, card_y = (w - card_w) // 2, (h - card_h) // 2
    
    if state == "WIN":
        title_text = "SURVIVED! SENSORY HERO"
        title_color = COLOR_EMERALD
        border_color = COLOR_EMERALD
        desc_text = "Exceptional self-control! You successfully bypassed all red lights."
    else:
        title_text = "FOCUS PRACTICE COMPLETED"
        title_color = COLOR_ROSE
        border_color = COLOR_ROSE
        desc_text = "Movement detected during Red Light. Continuous training builds focus!"
        
    draw_glass_panel(img, card_x, card_y, card_w, card_h, (20, 20, 20), border_color, 0.65, 2, 20)
    
    # Title & subtitle
    cv2.putText(img, title_text, (card_x + 50, card_y + 65), cv2.FONT_HERSHEY_SIMPLEX, 1.2, title_color, 3, cv2.LINE_AA)
    cv2.putText(img, desc_text, (card_x + 50, card_y + 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_GRAY, 1, cv2.LINE_AA)
    cv2.line(img, (card_x + 50, card_y + 130), (card_x + card_w - 50, card_y + 130), (70, 70, 70), 1, cv2.LINE_AA)
    
    # Analytics Grid Data
    metrics = [
        ("Session Duration", f"{summary_data.get('session_duration', 0):.1f}s", COLOR_WHITE),
        ("Total Trials", f"{summary_data.get('total_trials', 0)}", COLOR_WHITE),
        ("Red Phase Deviations", f"{summary_data.get('false_moves', 0)}", COLOR_ROSE),
        ("Green Phase Stops", f"{summary_data.get('false_stops', 0)}", COLOR_AMBER),
        ("Motor Control Rating", f"{summary_data.get('motor_control_score', 0):.1f}%", COLOR_EMERALD),
        ("Overall Success Rate", f"{summary_data.get('success_rate', 0):.1f}%", COLOR_LIGHT_INDIGO),
    ]
    
    grid_x = card_x + 50
    grid_y = card_y + 175
    row_h = 55
    col_w = 320
    
    for i, (name, val, val_color) in enumerate(metrics):
        r = i % 3
        c = i // 3
        curr_x = grid_x + c * col_w
        curr_y = grid_y + r * row_h
        
        draw_glass_panel(img, curr_x, curr_y - 20, col_w - 20, 42, (10, 10, 10), (50, 50, 50), 0.5, 1, 6)
        cv2.putText(img, name, (curr_x + 12, curr_y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 160, 160), 1, cv2.LINE_AA)
        val_size = cv2.getTextSize(val, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 2)[0]
        cv2.putText(img, val, (curr_x + col_w - 35 - val_size[0], curr_y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, val_color, 2, cv2.LINE_AA)
        
    # Closing interaction
    cv2.line(img, (card_x + 50, card_y + card_h - 80), (card_x + card_w - 50, card_y + card_h - 80), (70, 70, 70), 1, cv2.LINE_AA)
    cv2.putText(img, "Press 'Q' or any key to return to Dashboard...", (card_x + 50, card_y + card_h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_INDIGO, 2, cv2.LINE_AA)


# ========== إعدادات اللعبة ==========
import sys
GREEN_LIGHT_DURATION = 5.5
RED_LIGHT_DURATION = 3.5
COUNTDOWN_TIME = 60
CHILD_ID = "CHILD001"  # يمكن تغييره لكل طفل
if len(sys.argv) > 1:
    CHILD_ID = sys.argv[1]
# ======================================

# تهيئة الكائنات
md = MotionDetector()
data_collector = GameDataCollector(child_id=CHILD_ID)

cap = cv2.VideoCapture(3)

# Difficulty Selection and Mistake Parameters
game_state = "DIFFICULTY_SELECT"
selected_difficulty = "MEDIUM"
allowed_mistakes = 1
mistakes_count = 0
last_mistake_time = 0

start_time = cv2.getTickCount()
countdown_time = COUNTDOWN_TIME
elapsed_time = 0
game_over = False
motiond = 0
end = 0

last_color_change_time = time.time()
current_phase = "green"

# تحديث مدة الجلسة في data_collector
data_collector.session_data['session_info']['green_light_duration'] = GREEN_LIGHT_DURATION
data_collector.session_data['session_info']['red_light_duration'] = RED_LIGHT_DURATION

# إعدادات الزر (Centered and Floating Bottom-Center)
button_x, button_y = 490, 520
button_width, button_height = 300, 65
button_text = "SURVIVED! CLICK TO WIN"

cv2.namedWindow('ADHD Training Game')
cv2.setMouseCallback('ADHD Training Game', mouse_callback)


def _send_green_light_to_api(data_collector):
    """Send Green Light session data to .NET backend API"""
    child_id = data_collector.child_id
    trials_raw = data_collector.session_data.get('trials', [])
    summary = data_collector.session_data.get('summary', {})

    api_trials = []
    for i, t in enumerate(trials_raw):
        phase_name = "GreenLight" if t['phase'] == 'green' else "RedLight"
        trial = {
            "trialIndex": i + 1,
            "phase": phase_name,
            "stopSignalDelayMs": None,
            "movementIntensity": None,
            "stopReactionTimeMs": None,
            "freezeQuality": None,
            "falseStart": None
        }
        if t['phase'] == 'green':
            trial["stopSignalDelayMs"] = 0
            trial["movementIntensity"] = round(min(1.0, t.get('motion_magnitude', 0) / 50.0), 4)
            if t['motion_detected'] and t['motion_time'] and t['start_time']:
                trial["stopReactionTimeMs"] = int((t['motion_time'] - t['start_time']) * 1000)
        else:
            if t['motion_detected']:
                trial["falseStart"] = True
                if t['motion_time'] and t['start_time']:
                    trial["stopSignalDelayMs"] = int((t['motion_time'] - t['start_time']) * 1000)
            else:
                trial["falseStart"] = False
                actual = t.get('actual_duration', 0)
                expected = t.get('expected_duration', 1)
                if expected > 0:
                    trial["freezeQuality"] = round(min(1.0, actual / expected), 4)
        api_trials.append(trial)

    api_session_id = create_session(child_id, "green_light")
    if api_session_id:
        if api_trials:
            save_green_light_trials(api_session_id, api_trials)
        avg_react_ms = summary.get('avg_reaction_time', 0) * 1000
        total_trials = summary.get('total_trials', 0)
        false_moves = summary.get('false_moves', 0)

        # Compute average freeze quality from trials
        freeze_qualities = [t.get("freezeQuality") for t in api_trials if t.get("freezeQuality") is not None]
        avg_freeze_quality = round(sum(freeze_qualities) / len(freeze_qualities), 4) if freeze_qualities else None

        # Compute overall movement intensity from trials
        intensities = [t.get("movementIntensity") for t in api_trials if t.get("movementIntensity") is not None]
        avg_movement_intensity = round(sum(intensities) / len(intensities), 4) if intensities else None

        save_summary(api_session_id, {
            "totalTrials": total_trials,
            "averageStopReactionTimeMs": round(avg_react_ms, 0),
            "falseStartCount": false_moves,
            "averageFreezeQuality": avg_freeze_quality,
            "movementIntensityOverall": avg_movement_intensity
        })


def put_centered_text(img, text, cx, cy, font, scale, color, thickness):
    """Utility to draw perfectly centered text around a target coordinate"""
    size = cv2.getTextSize(text, font, scale, thickness)[0]
    tx = cx - size[0] // 2
    ty = cy + size[1] // 2
    cv2.putText(img, text, (tx, ty), font, scale, color, thickness, cv2.LINE_AA)


# ========== GAMEPLAY LOOP ==========
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))
    # Flip camera horizontally for intuitive user coordination mirror effect
    frame = cv2.flip(frame, 1)

    if game_state == "DIFFICULTY_SELECT":
        h, w, _ = frame.shape
        
        # Dark overlay background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), COLOR_DARK, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Central Dialog Container
        draw_glass_panel(frame, w//4, h//8, w//2, 3*h//4, (15, 15, 15), COLOR_INDIGO, 0.75, 2, 20)
        
        put_centered_text(frame, "SELECT DIFFICULTY LEVEL", w//2, h//8 + 45, cv2.FONT_HERSHEY_SIMPLEX, 0.85, COLOR_WHITE, 3)
        put_centered_text(frame, "اختر مستوى الصعوبة لبدء التدريب", w//2, h//8 + 85, cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_GRAY, 1)
        
        # Difficulty Buttons coordinates
        btn_w, btn_h = 440, 75
        btn_x = (w - btn_w) // 2
        
        # Buttons definitions: (y, label, desc, color, difficulty_id)
        buttons_info = [
            (h//8 + 140, "EASY - سهل", "Sensitivity: Low (30) | Mistakes allowed: 3", COLOR_EMERALD, "EASY"),
            (h//8 + 245, "MEDIUM - متوسط", "Sensitivity: Medium (15) | Mistakes allowed: 1", COLOR_AMBER, "MEDIUM"),
            (h//8 + 350, "HARD - صعب", "Sensitivity: High (8) | Mistakes allowed: 0", COLOR_ROSE, "HARD")
        ]
        
        # Check mouse hover and click
        button_clicked = None
        for y, label, desc, color, diff in buttons_info:
            is_hovered = (btn_x <= mouse_pos[0] <= btn_x + btn_w and y <= mouse_pos[1] <= y + btn_h)
            btn_border = COLOR_LIGHT_INDIGO if is_hovered else color
            btn_alpha = 0.85 if is_hovered else 0.55
            
            draw_glass_panel(frame, btn_x, y, btn_w, btn_h, (20, 20, 20), btn_border, btn_alpha, 2 if is_hovered else 1, 15)
            put_centered_text(frame, label, w//2, y + btn_h//2 - 12, cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2)
            put_centered_text(frame, desc, w//2, y + btn_h//2 + 18, cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLOR_GRAY, 1)
            
            if is_hovered and mouse_click_pos is not None:
                button_clicked = diff
                
        # Clear click position
        if mouse_click_pos is not None:
            mouse_click_pos = None
            
        if button_clicked is not None:
            selected_difficulty = button_clicked
            if button_clicked == "EASY":
                md.threshold = 30.0
                allowed_mistakes = 3
            elif button_clicked == "MEDIUM":
                md.threshold = 15.0
                allowed_mistakes = 1
            else:
                md.threshold = 8.0
                allowed_mistakes = 0
                
            # Transition to playing state
            game_state = "PLAYING"
            start_time = cv2.getTickCount()
            last_color_change_time = time.time()
            data_collector.session_start = time.time()
            data_collector.start_phase(current_phase, GREEN_LIGHT_DURATION)
            play_sound(green_sound)
            
        cv2.imshow('ADHD Training Game', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # Detect movement sensor values
    motion_detected, motion_magnitude = md.detect_motion(frame)
    data_collector.record_motion(motion_detected, motion_magnitude)

    # Draw Pose Skeleton Overlay
    if hasattr(md, 'last_raw_landmarks') and md.last_raw_landmarks is not None:
        if current_phase == "red":
            skeleton_state = "error" if motion_detected else "success"
        else:
            skeleton_state = "success"
        md.pose_engine.draw_landmarks(frame, md.last_raw_landmarks, match_state=skeleton_state)

    current_time = time.time()

    # Get duration of current state
    if current_phase == "green":
        phase_duration = GREEN_LIGHT_DURATION
    else:
        phase_duration = RED_LIGHT_DURATION

    # Check phase timers for transitioning
    if current_time - last_color_change_time > phase_duration:
        data_collector.end_phase(current_phase)
        last_color_change_time = current_time

        if current_phase == "green":
            current_phase = "red"
            play_sound(red_sound)
        else:
            current_phase = "green"
            play_sound(green_sound)
            
        data_collector.start_phase(current_phase, phase_duration)

    phase_time_left = max(0.0, phase_duration - (current_time - last_color_change_time))

    # Overall timer countdown
    if not game_over:
        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        remaining_time = max(0, countdown_time - int(elapsed_time))
        if remaining_time <= 0 or motiond == 1:
            game_over = True
    else:
        remaining_time = max(0, countdown_time - int(elapsed_time))

    # --- Draw Glassmorphic HUD ---

    # 1. Top Header panel
    draw_glass_panel(frame, 20, 15, 1240, 55, (15, 15, 15), COLOR_INDIGO, 0.45, 1, 10)
    cv2.putText(frame, f"ADHD SENSORY TRAINING: {selected_difficulty}", (45, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_WHITE, 2, cv2.LINE_AA)
    
    # Draw mistakes count in red if mistake made, otherwise white
    mistakes_str = f"MISTAKES: {mistakes_count} / {allowed_mistakes + 1}"
    cv2.putText(frame, mistakes_str, (700, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_ROSE if mistakes_count > 0 else COLOR_WHITE, 2, cv2.LINE_AA)
    
    timer_str = f"TIME LEFT: {remaining_time}s"
    timer_size = cv2.getTextSize(timer_str, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    cv2.putText(frame, timer_str, (1230 - timer_size[0], 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2, cv2.LINE_AA)

    # Pick colors based on active phase
    if current_phase == "green":
        active_border = COLOR_EMERALD
        active_core = COLOR_EMERALD
        active_glow = (120, 230, 120)
        phase_label = "GREEN LIGHT: GO!"
    else:
        active_border = COLOR_ROSE
        active_core = COLOR_ROSE
        active_glow = (120, 120, 255)
        phase_label = "RED LIGHT: FREEZE!"

    # 2. Left Traffic status widget
    draw_glass_panel(frame, 20, 85, 300, 340, (20, 20, 20), active_border, 0.5, 2, 15)
    put_centered_text(frame, "TRAFFIC STATUS", 170, 115, cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_GRAY, 1)
    put_centered_text(frame, phase_label, 170, 145, cv2.FONT_HERSHEY_SIMPLEX, 0.65, active_core, 2)
    
    # Glowing Light Orb
    draw_glowing_circle(frame, (170, 240), 50, active_core, active_glow, 3)
    
    # Circular phase timeline track
    phase_pct = max(0.0, min(1.0, phase_time_left / phase_duration))
    draw_circular_progress(frame, (170, 240), 65, phase_pct, active_core, 4)
    
    put_centered_text(frame, f"{phase_time_left:.1f}s left", 170, 335, cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_WHITE, 1)
    put_centered_text(frame, f"ROUND {len(data_collector.session_data['trials']) + 1}", 170, 365, cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_GRAY, 1)

    # 3. Update summary metrics live and draw Analytics widget
    data_collector.generate_summary()
    summary = data_collector.session_data['summary']

    draw_glass_panel(frame, 960, 85, 300, 340, (20, 20, 20), COLOR_INDIGO, 0.5, 1, 15)
    put_centered_text(frame, "PERFORMANCE ANALYTICS", 1110, 115, cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_GRAY, 1)

    if summary:
        success_rate = summary.get('success_rate', 100.0)
        motor_control = summary.get('motor_control_score', 100.0)
        impulsivity = summary.get('impulsivity_index', 0.0)
        avg_react = summary.get('avg_reaction_time', 0.0)

        # Success Rate Slider
        cv2.putText(frame, f"Success Rate: {success_rate:.0f}%", (990, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1, cv2.LINE_AA)
        cv2.rectangle(frame, (990, 172), (1230, 178), (40, 40, 40), -1)
        cv2.rectangle(frame, (990, 172), (990 + int(success_rate * 2.4), 178), COLOR_EMERALD, -1)

        # Stillness Index (Motor Control)
        cv2.putText(frame, f"Stillness Rating: {motor_control:.0f}%", (990, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1, cv2.LINE_AA)
        cv2.rectangle(frame, (990, 227), (1230, 233), (40, 40, 40), -1)
        cv2.rectangle(frame, (990, 227), (990 + int(motor_control * 2.4), 233), COLOR_INDIGO, -1)

        # Impulsivity Score
        cv2.putText(frame, f"Impulsivity Score: {impulsivity:.0f}%", (990, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1, cv2.LINE_AA)
        cv2.rectangle(frame, (990, 282), (1230, 288), (40, 40, 40), -1)
        cv2.rectangle(frame, (990, 282), (990 + int(impulsivity * 2.4), 288), COLOR_ROSE, -1)

        # Average Reaction duration
        cv2.putText(frame, f"Avg Reaction: {avg_react:.2f}s", (990, 325), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1, cv2.LINE_AA)
        cv2.rectangle(frame, (990, 337), (1230, 343), (40, 40, 40), -1)
        cv2.rectangle(frame, (990, 337), (990 + min(240, int(avg_react * 80)), 343), COLOR_AMBER, -1)

    # 4. Check hover states and draw Center Rounded Interactive Button
    is_btn_hovered = (button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height)
    btn_border = COLOR_LIGHT_INDIGO if is_btn_hovered else COLOR_INDIGO
    btn_alpha = 0.75 if is_btn_hovered else 0.5

    draw_glass_panel(frame, button_x, button_y, button_width, button_height, (15, 15, 15), btn_border, btn_alpha, 2 if is_btn_hovered else 1, 15)
    put_centered_text(frame, button_text, button_x + button_width // 2, button_y + button_height // 2, cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WHITE, 2)

    # 5. Draw Bottom Real-Time Stillness Sensor visualizer bar
    draw_motion_visualizer(frame, 20, 630, 1240, 60, motion_magnitude, max_val=max(50.0, md.threshold * 2.5), threshold=md.threshold)

    # Trigger game over on Red Phase violation after exceeding allowed mistakes
    if motion_detected and current_phase == "red":
        if current_time - last_mistake_time > 2.0:
            mistakes_count += 1
            last_mistake_time = current_time
            
            # Log false move for data analytics
            data_collector.session_data['false_moves'].append({
                'time': current_time,
                'reaction_time': current_time - last_color_change_time
            })
            
            # Record last error time in data collector
            data_collector.last_error_time = current_time
            data_collector.consecutive_success = 0
            
            # Check if game over
            if mistakes_count > allowed_mistakes:
                motiond = 1
                game_over = True

    # Draw live warning flash for 2.0 seconds after mistake
    if current_time - last_mistake_time < 2.0 and mistakes_count > 0 and not game_over:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (1280, 720), (0, 0, 100), -1)
        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
        
        warning_msg = f"WARNING! YOU MOVED! ({mistakes_count}/{allowed_mistakes + 1})"
        put_centered_text(frame, warning_msg, 640, 360, cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLOR_ROSE, 3)

    # Check button presses / mouse clicks
    button_clicked = False
    if mouse_click_pos is not None:
        x_click, y_click = mouse_click_pos
        if (button_x <= x_click <= button_x + button_width and button_y <= y_click <= button_y + button_height):
            button_clicked = True
        mouse_click_pos = None

    # Win State Execution Flow
    if (cv2.waitKey(1) & 0xFF == ord('k')) or button_clicked:
        # Wrap session metadata
        data_collector.end_phase(current_phase)
        data_collector.generate_summary()
        data_collector.save_data()
        _send_green_light_to_api(data_collector)
        
        # Display Final Overlay
        while True:
            draw_end_screen(frame, "WIN", data_collector.session_data['summary'])
            cv2.imshow('ADHD Training Game', frame)
            key = cv2.waitKey(1) & 0xFF
            if key != 255:
                break
        end = 1
        break

    # Lose State Execution Flow
    if game_over and end == 0:
        data_collector.end_phase(current_phase)
        data_collector.generate_summary()
        data_collector.save_data()
        _send_green_light_to_api(data_collector)
        
        # Display Final Overlay
        while True:
            draw_end_screen(frame, "LOSE", data_collector.session_data['summary'])
            cv2.imshow('ADHD Training Game', frame)
            key = cv2.waitKey(1) & 0xFF
            if key != 255:
                break
        end = 1
        break

    cv2.imshow('ADHD Training Game', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Final summary prints
print("\n" + "="*50)
print("📊 ملخص الجلسة النهائي")
print("="*50)
summary = data_collector.session_data['summary']
for key, value in summary.items():
    if isinstance(value, float):
        print(f"{key}: {value:.2f}")
    else:
        print(f"{key}: {value}")

cap.release()
cv2.destroyAllWindows()