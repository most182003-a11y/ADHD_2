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

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import cv2
import time
import pygame
import threading
import json
from datetime import datetime
from pose_engine import PoseEngine
from ui_utils import draw_glass_panel, put_centered_text, COLOR_DARK, COLOR_SLATE, COLOR_INDIGO, COLOR_LIGHT_INDIGO, COLOR_EMERALD, COLOR_ROSE, COLOR_AMBER, COLOR_WHITE, COLOR_GRAY
from collections import deque
import numpy as np

# تهيئة pygame للأصوات
try:
    pygame.mixer.init()
    green_sound = pygame.mixer.Sound(os.path.join(_script_dir, "Green_light.mp3"))
    red_sound = pygame.mixer.Sound(os.path.join(_script_dir, "Red_Light.mp3"))
except:
    print("[Sound] Audio files not found. Running without sound.")
    green_sound = None
    red_sound = None


def play_sound(sound_file):
    """تشغيل الصوت في خيط منفصل"""
    if sound_file:
        threading.Thread(target=sound_file.play, daemon=True).start()


class MotionDetector:
    def __init__(self, threshold=15):
        self.threshold = threshold
        self.pose_engine = PoseEngine(smooth_factor=0.3, model_complexity=1)
        self.previous_landmarks = None
        self.start_time = None
        self.motion_history = deque(maxlen=100)
        self.motion_magnitude_history = deque(maxlen=100)
        self.last_raw_landmarks = None
        self.frame_count = 0
        self.process_every_n_frames = 2
        
    def detect_motion(self, frame):
        self.frame_count += 1
        if self.frame_count % self.process_every_n_frames == 0:
            smoothed_landmarks, raw_landmarks = self.pose_engine.process_frame(frame, mirrored=True)
            if smoothed_landmarks is not None:
                self._cached_smoothed = smoothed_landmarks
                self._cached_raw = raw_landmarks
        else:
            smoothed_landmarks = getattr(self, '_cached_smoothed', None)
            raw_landmarks = getattr(self, '_cached_raw', None)
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
            # تعيين قيم افتراضية لتجنب الأخطاء
            self.session_data['summary'] = {
                'session_duration': 0,
                'total_trials': 0,
                'false_moves': 0,
                'false_stops': 0,
                'success_rate': 0,
                'avg_reaction_time': 0,
                'impulsivity_index': 0,
                'motor_control_score': 0,
                'distraction_score': 0,
                'max_consecutive_success': 0,
                'time_before_first_error': 0
            }
            return
            
        # إحصائيات أساسية
        red_trials = [t for t in trials if t['phase'] == 'red']
        green_trials = [t for t in trials if t['phase'] == 'green']
        
        false_moves = len(self.session_data['false_moves'])
        false_stops = len([t for t in green_trials if not t['motion_detected']])
        total_trials = len(red_trials) + len(green_trials)
        
        # مؤشر الاندفاعية (Impulsivity Index)
        impulsivity_index = (false_moves / len(red_trials)) * 100 if red_trials else 0
        
        # مؤشر التحكم الحركي - تجنب القسمة على صفر
        if self.session_data['freeze_durations'] and red_trials:
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
        """حفظ البيانات في ملف JSON مطابق للهيكل المطلوب"""
        if not os.path.exists('session_data'):
            os.makedirs('session_data')
        
        trials = self.session_data['trials']
        green_trials = [t for t in trials if t['phase'] == 'green']
        red_trials = [t for t in trials if t['phase'] == 'red']
        num_pairs = min(len(green_trials), len(red_trials))
        
        export_trials = []
        all_intensities = []
        all_stop_reactions = []
        all_freeze_qualities = []
        false_start_count = 0
        
        # الحصول على عتبة الحركة من MotionDetector (افتراضي إذا لم يتوفر)
        try:
            threshold = md.threshold
        except:
            threshold = 15.0  # القيمة الافتراضية
        
        for i in range(num_pairs):
            gt = green_trials[i]
            rt = red_trials[i]
            
            movement_intensity = round(min(1.0, gt.get('motion_magnitude', 0) / 50.0), 4)
            all_intensities.append(movement_intensity)
            false_start = rt.get('motion_detected', False)
            
            if false_start and rt.get('motion_time') and rt.get('start_time'):
                stop_reaction_ms = int(round((rt['motion_time'] - rt['start_time']) * 1000, 0))
            else:
                # محاولة حساب زمن التوقف من بيانات الحركة المسجلة
                red_mags = [
                    m['magnitude'] for m in self.session_data['movement_data']
                    if m['phase'] == 'red' and rt['start_time'] <= m['time'] <= rt['end_time']
                ]
                first_still = next((m for m in red_mags if m < threshold), None)
                if first_still is not None and red_mags:
                    still_idx = red_mags.index(first_still)
                    still_entry = [m for m in self.session_data['movement_data']
                                   if m['phase'] == 'red' and rt['start_time'] <= m['time'] <= rt['end_time']]
                    if still_idx < len(still_entry):
                        stop_reaction_ms = int(round((still_entry[still_idx]['time'] - rt['start_time']) * 1000, 0))
                    else:
                        stop_reaction_ms = 0
                else:
                    stop_reaction_ms = 0
            
            all_stop_reactions.append(stop_reaction_ms)
            
            red_magnitudes = [
                m['magnitude'] for m in self.session_data['movement_data']
                if m['phase'] == 'red' and rt['start_time'] <= m['time'] <= rt['end_time']
            ]
            freeze_quality = round(float(np.std(red_magnitudes)), 4) if len(red_magnitudes) > 1 else 0.0
            all_freeze_qualities.append(freeze_quality)
            
            if false_start:
                false_start_count += 1
            
            export_trials.append({
                "trialIndex": i + 1,
                "phase": "GreenLight",
                "stopSignalDelayMs": 0,
                "movementIntensity": movement_intensity,
                "transition": {
                    "stopReactionTimeMs": stop_reaction_ms,
                    "freezeQuality": freeze_quality,
                    "falseStart": false_start
                }
            })
        
        output = {
            "userId": self.child_id,
            "sessionId": self.session_id,
            "gameType": "RedLightGreenLight",
            "timestamp": datetime.now().isoformat(),
            "previousSessionsCount": 0,
            "trials": export_trials,
            "sessionSummary": {
                "averageStopReactionTimeMs": round(np.mean(all_stop_reactions), 0) if all_stop_reactions else 0,
                "falseStartCount": false_start_count,
                "averageFreezeQuality": round(np.mean(all_freeze_qualities), 4) if all_freeze_qualities else 0,
                "movementIntensityOverall": round(np.mean(all_intensities), 4) if all_intensities else 0,
                "totalTrials": num_pairs
            }
        }
        
        json_filename = f"session_data/{self.child_id}_{self.session_id}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nData saved to: {json_filename}")

        # API SYNC
        try:
            from backend_api import create_session, save_green_light_trials, save_summary
            print("Syncing Red Light Green Light session data to backend API...")
            api_session_id = create_session(self.child_id, "RedLightGreenLight")
            if api_session_id:
                api_trials = []
                for t in export_trials:
                    api_trials.append({
                        "TrialIndex": t["trialIndex"],
                        "Phase": t["phase"],
                        "StopSignalDelayMs": t["stopSignalDelayMs"],
                        "MovementIntensity": t["movementIntensity"],
                        "StopReactionTimeMs": t["transition"]["stopReactionTimeMs"],
                        "FreezeQuality": t["transition"]["freezeQuality"],
                        "FalseStart": t["transition"]["falseStart"]
                    })
                save_green_light_trials(api_session_id, api_trials)
                
                api_summary = {
                    "TotalTrials": output["sessionSummary"]["totalTrials"],
                    "AverageStopReactionTimeMs": output["sessionSummary"]["averageStopReactionTimeMs"],
                    "FalseStartCount": output["sessionSummary"]["falseStartCount"],
                    "AverageFreezeQuality": output["sessionSummary"]["averageFreezeQuality"],
                    "MovementIntensityOverall": output["sessionSummary"]["movementIntensityOverall"]
                }
                save_summary(api_session_id, api_summary)
                print("✅ Sync with API completed successfully!")
            else:
                print("❌ Could not create session on API.")
        except Exception as e:
            print(f"❌ Error syncing with API: {e}")
        
        return json_filename


_game_instance = None
mouse_pos = (0, 0)
mouse_click_pos = None

def mouse_callback(event, x, y, flags, param):
    global mouse_click_pos, mouse_pos
    mouse_pos = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_click_pos = (x, y)


def draw_glowing_circle(img, center, radius, color, glow_color, thickness=3, pulse_speed=5):
    t = time.time() * pulse_speed
    pulse = np.sin(t) * 4
    r = int(radius + pulse)
    
    overlay = img.copy()
    cv2.circle(overlay, center, r + 25, glow_color, 8, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.08, img, 0.92, 0, img)
    
    overlay = img.copy()
    cv2.circle(overlay, center, r + 15, glow_color, 12, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)
    
    overlay = img.copy()
    cv2.circle(overlay, center, r + 5, glow_color, -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.25, img, 0.75, 0, img)
    
    cv2.circle(img, center, r, color, -1, cv2.LINE_AA)
    cv2.circle(img, center, r, COLOR_WHITE, 2, cv2.LINE_AA)


def draw_circular_progress(img, center, radius, progress, color, thickness=4):
    end_angle = int(360 * progress) - 90
    cv2.ellipse(img, center, (radius, radius), 0, -90, end_angle, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, center, (radius, radius), 0, -90, 270, (40, 40, 40), 1, cv2.LINE_AA)


def draw_motion_visualizer(img, x, y, w, h, magnitude, max_val=50, threshold=15, bg_color=(20, 20, 20)):
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
    h, w, _ = img.shape
    
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), COLOR_DARK, -1)
    cv2.addWeighted(overlay, 0.82, img, 0.18, 0, img)
    
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
    
    cv2.putText(img, title_text, (card_x + 50, card_y + 65), cv2.FONT_HERSHEY_SIMPLEX, 1.2, title_color, 3, cv2.LINE_AA)
    cv2.putText(img, desc_text, (card_x + 50, card_y + 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_GRAY, 1, cv2.LINE_AA)
    cv2.line(img, (card_x + 50, card_y + 130), (card_x + card_w - 50, card_y + 130), (70, 70, 70), 1, cv2.LINE_AA)
    
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
        
    cv2.line(img, (card_x + 50, card_y + card_h - 80), (card_x + card_w - 50, card_y + card_h - 80), (70, 70, 70), 1, cv2.LINE_AA)
    cv2.putText(img, "Press 'Q' or any key to return to Dashboard...", (card_x + 50, card_y + card_h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_INDIGO, 2, cv2.LINE_AA)


class GreenLightGame:
    GREEN_LIGHT_DURATION = 3.0
    RED_LIGHT_DURATION = 6.0
    COUNTDOWN_TIME = 60

    def __init__(self, child_id="CHILD001"):
        self.child_id = child_id
        self.md = MotionDetector()
        self.data_collector = GameDataCollector(child_id=child_id)
        self.target_resolution = (640, 480)
        self.cap = self._init_camera()
        self.frame_count = 0
        self._lighting_status = "good"

        self.game_state = "DIFFICULTY_SELECT"
        self.selected_difficulty = "MEDIUM"
        self.allowed_mistakes = 1
        self.mistakes_count = 0
        self.last_mistake_time = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.game_over = False
        self.motiond = 0
        self.end = 0
        self.last_color_change_time = time.time()
        self.current_phase = "green"
        self.remaining_time = self.COUNTDOWN_TIME

        self.data_collector.session_data['session_info']['green_light_duration'] = self.GREEN_LIGHT_DURATION
        self.data_collector.session_data['session_info']['red_light_duration'] = self.RED_LIGHT_DURATION

        self.button_x, self.button_y = 490, 520
        self.button_width, self.button_height = 300, 65
        self.button_text = "SURVIVED! CLICK TO WIN"

    def _init_camera(self):
        for idx in range(5):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[0])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[1])
                    return cap
                cap.release()
        print("[ERROR] No camera detected. Using fallback index 0.")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("[CRITICAL] Camera failed to open. Please check connection.")
            sys.exit(1)
        return cap

    def run(self):
        global mouse_pos, mouse_click_pos
        cv2.namedWindow('ADHD Training Game')
        cv2.setMouseCallback('ADHD Training Game', mouse_callback)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera Lost! Please reconnect.", (300, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLOR_ROSE, 3, cv2.LINE_AA)
                cv2.imshow('ADHD Training Game', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            frame = cv2.resize(frame, (1280, 720))
            frame = cv2.flip(frame, 1)
            self.frame_count += 1

            if self.game_state == "DIFFICULTY_SELECT":
                self._handle_difficulty_select(frame)
                cv2.imshow('ADHD Training Game', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            motion_detected, motion_magnitude = self.md.detect_motion(frame)
            self.data_collector.record_motion(motion_detected, motion_magnitude)

            if hasattr(self.md, 'last_raw_landmarks') and self.md.last_raw_landmarks is not None:
                skeleton_state = "error" if (self.current_phase == "red" and motion_detected) else "success"
                self.md.pose_engine.draw_landmarks(frame, self.md.last_raw_landmarks, match_state=skeleton_state)

            current_time = time.time()
            phase_duration = self.GREEN_LIGHT_DURATION if self.current_phase == "green" else self.RED_LIGHT_DURATION

            if current_time - self.last_color_change_time > phase_duration:
                self.data_collector.end_phase(self.current_phase)
                self.last_color_change_time = current_time
                if self.current_phase == "green":
                    self.current_phase = "red"
                    play_sound(red_sound)
                else:
                    self.current_phase = "green"
                    play_sound(green_sound)
                self.data_collector.start_phase(self.current_phase, phase_duration)

            phase_time_left = max(0.0, phase_duration - (current_time - self.last_color_change_time))

            if not self.game_over:
                self.elapsed_time = (cv2.getTickCount() - self.start_time) / cv2.getTickFrequency()
                self.remaining_time = max(0, self.COUNTDOWN_TIME - int(self.elapsed_time))
                if self.remaining_time <= 0 or self.motiond == 1:
                    self.game_over = True

            self._draw_hud(frame, motion_detected, motion_magnitude, current_time, phase_time_left, phase_duration)

            if motion_detected and self.current_phase == "red":
                if current_time - self.last_mistake_time > 2.0:
                    self.mistakes_count += 1
                    self.last_mistake_time = current_time
                    self.data_collector.session_data['false_moves'].append({
                        'time': current_time,
                        'reaction_time': current_time - self.last_color_change_time
                    })
                    self.data_collector.last_error_time = current_time
                    self.data_collector.consecutive_success = 0
                    if self.mistakes_count > self.allowed_mistakes:
                        self.motiond = 1
                        self.game_over = True

            if current_time - self.last_mistake_time < 2.0 and self.mistakes_count > 0 and not self.game_over:
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (1280, 720), (0, 0, 100), -1)
                cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
                put_centered_text(frame, f"WARNING! YOU MOVED! ({self.mistakes_count}/{self.allowed_mistakes + 1})", 640, 360, cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLOR_ROSE, 3)

            button_clicked = False
            if mouse_click_pos is not None:
                xc, yc = mouse_click_pos
                if (self.button_x <= xc <= self.button_x + self.button_width and self.button_y <= yc <= self.button_y + self.button_height):
                    button_clicked = True
                mouse_click_pos = None

            if (cv2.waitKey(1) & 0xFF == ord('k')) or button_clicked:
                self._end_game("WIN", frame)
                break

            if self.game_over and self.end == 0:
                self._end_game("LOSE", frame)
                break

            cv2.imshow('ADHD Training Game', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self._print_summary()
        self.cap.release()
        cv2.destroyAllWindows()

    def _handle_difficulty_select(self, frame):
        global mouse_click_pos
        h, w, _ = frame.shape

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), COLOR_DARK, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        draw_glass_panel(frame, w//4, h//8, w//2, 3*h//4, (15, 15, 15), COLOR_INDIGO, 0.75, 2, 20)
        put_centered_text(frame, "SELECT DIFFICULTY LEVEL", w//2, h//8 + 45, cv2.FONT_HERSHEY_SIMPLEX, 0.85, COLOR_WHITE, 3)
        put_centered_text(frame, "Select difficulty level to begin training", w//2, h//8 + 85, cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_GRAY, 1)

        btn_w, btn_h = 440, 75
        btn_x = (w - btn_w) // 2
        buttons_info = [
            (h//8 + 140, "EASY", "Sensitivity: Medium (50) | Mistakes allowed: 3", COLOR_EMERALD, "EASY"),
            (h//8 + 245, "MEDIUM", "Sensitivity: Medium (35) | Mistakes allowed: 1", COLOR_AMBER, "MEDIUM"),
            (h//8 + 350, "HARD", "Sensitivity: Medium (20) | Mistakes allowed: 0", COLOR_ROSE, "HARD")
        ]

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

        if mouse_click_pos is not None:
            mouse_click_pos = None

        if button_clicked is not None:
            self.selected_difficulty = button_clicked
            config = {"EASY": (15.0, 3), "MEDIUM": (15.0, 1), "HARD": (15.0, 0)}
            self.md.threshold, self.allowed_mistakes = config[button_clicked]
            self.game_state = "PLAYING"
            self.start_time = cv2.getTickCount()
            self.last_color_change_time = time.time()
            self.data_collector.session_start = time.time()
            self.data_collector.start_phase(self.current_phase, self.GREEN_LIGHT_DURATION)
            play_sound(green_sound)

    def _draw_hud(self, frame, motion_detected, motion_magnitude, current_time, phase_time_left, phase_duration):
        fps = self.md.pose_engine.get_fps()
        fps_color = COLOR_EMERALD if fps >= 20 else (COLOR_AMBER if fps >= 10 else COLOR_ROSE)

        if self.frame_count % 30 == 0:
            _, self._lighting_status = self.md.pose_engine.estimate_lighting(frame)
        light_color = COLOR_EMERALD if self._lighting_status == 'good' else (COLOR_AMBER if self._lighting_status == 'low' else COLOR_ROSE)

        draw_glass_panel(frame, 20, 15, 1240, 55, (15, 15, 15), COLOR_INDIGO, 0.45, 1, 10)
        cv2.putText(frame, f"ADHD SENSORY TRAINING: {self.selected_difficulty}", (45, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_WHITE, 2, cv2.LINE_AA)
        cv2.putText(frame, f"FPS: {fps}", (480, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2, cv2.LINE_AA)
        cv2.putText(frame, f"LIGHT: {self._lighting_status}", (590, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, light_color, 2, cv2.LINE_AA)
        cv2.putText(frame, f"MISTAKES: {self.mistakes_count} / {self.allowed_mistakes + 1}", (750, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_ROSE if self.mistakes_count > 0 else COLOR_WHITE, 2, cv2.LINE_AA)
        timer_str = f"TIME LEFT: {self.remaining_time}s"
        timer_size = cv2.getTextSize(timer_str, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.putText(frame, timer_str, (1230 - timer_size[0], 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2, cv2.LINE_AA)

        active_core = COLOR_EMERALD if self.current_phase == "green" else COLOR_ROSE
        active_glow = (120, 230, 120) if self.current_phase == "green" else (120, 120, 255)
        phase_label = "GREEN LIGHT: GO!" if self.current_phase == "green" else "RED LIGHT: FREEZE!"
        active_border = active_core

        draw_glass_panel(frame, 20, 85, 300, 340, (20, 20, 20), active_border, 0.5, 2, 15)
        put_centered_text(frame, "TRAFFIC STATUS", 170, 115, cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_GRAY, 1)
        put_centered_text(frame, phase_label, 170, 145, cv2.FONT_HERSHEY_SIMPLEX, 0.65, active_core, 2)
        draw_glowing_circle(frame, (170, 240), 50, active_core, active_glow, 3)
        phase_pct = max(0.0, min(1.0, phase_time_left / phase_duration))
        draw_circular_progress(frame, (170, 240), 65, phase_pct, active_core, 4)
        put_centered_text(frame, f"{phase_time_left:.1f}s left", 170, 335, cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_WHITE, 1)
        put_centered_text(frame, f"ROUND {len(self.data_collector.session_data['trials']) + 1}", 170, 365, cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_GRAY, 1)

        self.data_collector.generate_summary()
        summary = self.data_collector.session_data['summary']

        draw_glass_panel(frame, 960, 85, 300, 340, (20, 20, 20), COLOR_INDIGO, 0.5, 1, 15)
        put_centered_text(frame, "PERFORMANCE ANALYTICS", 1110, 115, cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_GRAY, 1)

        if summary:
            for i, (key, label) in enumerate([("success_rate", "Success Rate"), ("motor_control_score", "Stillness Rating"), ("impulsivity_index", "Impulsivity Score")]):
                val = summary.get(key, 0)
                colors = [COLOR_EMERALD, COLOR_INDIGO, COLOR_ROSE]
                cv2.putText(frame, f"{label}: {val:.0f}%", (990, 160 + i*55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1, cv2.LINE_AA)
                cv2.rectangle(frame, (990, 172 + i*55), (1230, 178 + i*55), (40, 40, 40), -1)
                cv2.rectangle(frame, (990, 172 + i*55), (990 + int(min(val, 100) * 2.4), 178 + i*55), colors[i], -1)

            avg_react = summary.get('avg_reaction_time', 0)
            cv2.putText(frame, f"Avg Reaction: {avg_react:.2f}s", (990, 325), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1, cv2.LINE_AA)
            cv2.rectangle(frame, (990, 337), (1230, 343), (40, 40, 40), -1)
            cv2.rectangle(frame, (990, 337), (990 + min(240, int(avg_react * 80)), 343), COLOR_AMBER, -1)

        is_btn_hovered = (self.button_x <= mouse_pos[0] <= self.button_x + self.button_width and self.button_y <= mouse_pos[1] <= self.button_y + self.button_height)
        btn_border = COLOR_LIGHT_INDIGO if is_btn_hovered else COLOR_INDIGO
        draw_glass_panel(frame, self.button_x, self.button_y, self.button_width, self.button_height, (15, 15, 15), btn_border, 0.75 if is_btn_hovered else 0.5, 2 if is_btn_hovered else 1, 15)
        put_centered_text(frame, self.button_text, self.button_x + self.button_width // 2, self.button_y + self.button_height // 2, cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WHITE, 2)

        draw_motion_visualizer(frame, 20, 630, 1240, 60, motion_magnitude, max_val=max(50.0, self.md.threshold * 2.5), threshold=self.md.threshold)

    def _end_game(self, state, frame):
        self.data_collector.end_phase(self.current_phase)
        self.data_collector.generate_summary()
        self.data_collector.save_data()

        while True:
            draw_end_screen(frame, state, self.data_collector.session_data['summary'])
            cv2.imshow('ADHD Training Game', frame)
            key = cv2.waitKey(1) & 0xFF
            if key != 255:
                break
        self.end = 1

    def _print_summary(self):
        print("\n" + "="*50)
        print("FINAL SESSION SUMMARY")
        print("="*50)
        summary = self.data_collector.session_data['summary']
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")


if __name__ == "__main__":
    import sys
    child_id = "CHILD001"
    if len(sys.argv) > 1:
        child_id = sys.argv[1]
    game = GreenLightGame(child_id=child_id)
    game.run()