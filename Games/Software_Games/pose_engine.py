import cv2
import mediapipe as mp
import numpy as np
from mediapipe.python.solutions import pose as mp_pose
from mediapipe.python.solutions import drawing_utils as mp_drawing
from collections import deque

class PoseEngine:
    def __init__(self, smooth_factor=0.3, use_advanced_preprocessing=True):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            smooth_segmentation=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.smooth_factor = smooth_factor
        self.use_advanced_preprocessing = use_advanced_preprocessing
        self._smoothed_prev = None
        self.last_raw_landmarks = None
        self.history = []

    def process_frame(self, frame, mirrored=True):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.use_advanced_preprocessing:
            rgb_frame = self._preprocess(rgb_frame)

        results = self.pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = self._extract_landmarks(results.pose_landmarks)

            if not self._validate_landmarks(landmarks):
                return None, None

            self.last_raw_landmarks = landmarks
            self.history.append(landmarks)
            if len(self.history) > 5:
                self.history.pop(0)

            smoothed_landmarks = self._apply_smoothing(landmarks)
            self.last_mirrored = mirrored
            return smoothed_landmarks, results.pose_landmarks
        return None, None

    def _preprocess(self, rgb_frame):
        lab = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        rgb_frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2RGB)
        rgb_frame = cv2.bilateralFilter(rgb_frame, 5, 50, 50)
        return rgb_frame

    def _validate_landmarks(self, landmarks):
        l_shldr = landmarks.get(11)
        r_shldr = landmarks.get(12)
        if l_shldr is not None and r_shldr is not None:
            shoulder_width = np.linalg.norm(l_shldr[:2] - r_shldr[:2])
            if shoulder_width < 0.05 or shoulder_width > 0.8:
                return False
        return True

    def _extract_landmarks(self, pose_landmarks):
        """Converts MediaPipe landmarks to a dictionary of coordinates."""
        landmarks = {}
        for idx, landmark in enumerate(pose_landmarks.landmark):
            landmarks[idx] = np.array([landmark.x, landmark.y, landmark.z, landmark.visibility])
        return landmarks

    def _apply_smoothing(self, landmarks):
        if self._smoothed_prev is None:
            self._smoothed_prev = landmarks
            return landmarks

        smoothed = {}
        alpha = self.smooth_factor
        for idx in landmarks.keys():
            prev = self._smoothed_prev.get(idx)
            if prev is None:
                smoothed[idx] = landmarks[idx]
            else:
                smoothed[idx] = alpha * landmarks[idx] + (1 - alpha) * prev
        self._smoothed_prev = smoothed
        return smoothed

    @staticmethod
    def angle_between(a, b, c):
        ba = a[:2] - b[:2]
        bc = c[:2] - b[:2]
        cos_ang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        return np.arccos(np.clip(cos_ang, -1, 1))

    @staticmethod
    def get_movement_check(movement_name, landmarks, mirrored=True):
        """Checks if a specific movement is currently being performed."""
        if not landmarks:
            return False, False # (correct, direction_error)

        # Referencing MP Pose Landmarks: 
        # Left: Wrist(15), Shoulder(11), Elbow(13), Knee(25), Hip(23)
        # Right: Wrist(16), Shoulder(12), Elbow(14), Knee(26), Hip(24)
        # Nose: 0
        
        if mirrored:
            # Swap left and right indices for mirrored logic
            # Left: Wrist(15), Shoulder(11), Elbow(13), Knee(25), Hip(23), Ear(7)
            # Right: Wrist(16), Shoulder(12), Elbow(14), Knee(26), Hip(24), Ear(8)
            l_wrist = landmarks[16]
            r_wrist = landmarks[15]
            l_shldr = landmarks[12]
            r_shldr = landmarks[11]
            l_elbow = landmarks[14]
            r_elbow = landmarks[13]
            l_knee = landmarks[26]
            r_knee = landmarks[25]
            l_hip = landmarks[24]
            r_hip = landmarks[23]
            l_ear = landmarks[8]
            r_ear = landmarks[7]
            l_ankle = landmarks[28]
            r_ankle = landmarks[27]
        else:
            l_wrist = landmarks[15]
            r_wrist = landmarks[16]
            l_shldr = landmarks[11]
            r_shldr = landmarks[12]
            l_elbow = landmarks[13]
            r_elbow = landmarks[14]
            l_knee = landmarks[25]
            r_knee = landmarks[26]
            l_hip = landmarks[23]
            r_hip = landmarks[24]
            l_ear = landmarks[7]
            r_ear = landmarks[8]
            l_ankle = landmarks[27]
            r_ankle = landmarks[28]
        
        nose = landmarks[0]
        thresh = 0.5
        
        def is_visible(idx_list):
            return all(landmarks[idx][3] >= thresh for idx in idx_list)

        if movement_name == "Raise Right Hand":
            if not is_visible([16, 12, 11, 15]): return False, False
            elbow_angle = PoseEngine.angle_between(r_shldr, r_elbow, r_wrist)
            arm_straight_up = np.degrees(elbow_angle) < 40
            wrist_above_shldr = r_wrist[1] < r_shldr[1] - 0.1
            correct = arm_straight_up and wrist_above_shldr and l_wrist[1] > l_shldr[1]
            dir_err = l_wrist[1] < l_shldr[1] - 0.1 and r_wrist[1] > r_shldr[1]
            return correct, dir_err

        elif movement_name == "Raise Left Hand":
            if not is_visible([15, 11, 12, 16]): return False, False
            elbow_angle = PoseEngine.angle_between(l_shldr, l_elbow, l_wrist)
            arm_straight_up = np.degrees(elbow_angle) < 40
            wrist_above_shldr = l_wrist[1] < l_shldr[1] - 0.1
            correct = arm_straight_up and wrist_above_shldr and r_wrist[1] > r_shldr[1]
            dir_err = r_wrist[1] < r_shldr[1] - 0.1 and l_wrist[1] > l_shldr[1]
            return correct, dir_err

        elif movement_name == "Hands on Hips":
            if not is_visible([15, 23, 16, 24]): return False, False
            # Hands on Hips: Wrists close to hips (23, 24)
            dist_l = np.linalg.norm(l_wrist[:2] - l_hip[:2])
            dist_r = np.linalg.norm(r_wrist[:2] - r_hip[:2])
            # Check if wrists are near hips and significantly below shoulders
            correct = dist_l < 0.2 and dist_r < 0.2 and l_wrist[1] > l_shldr[1] + 0.1 and r_wrist[1] > r_shldr[1] + 0.1
            return correct, False

        elif movement_name == "Touch Knees":
            if not is_visible([15, 25, 16, 26]): return False, False
            # Wrists close to knees
            dist_l = np.linalg.norm(l_wrist[:2] - l_knee[:2])
            dist_r = np.linalg.norm(r_wrist[:2] - r_knee[:2])
            correct = dist_l < 0.15 and dist_r < 0.15
            return correct, False

        elif movement_name == "Put Hand Above Head":
            # Either hand above nose
            r_up = r_wrist[3] > thresh and r_wrist[1] < nose[1]
            l_up = l_wrist[3] > thresh and l_wrist[1] < nose[1]
            return r_up or l_up, False

        elif movement_name == "Raise Both Hands":
            if not is_visible([15, 11, 16, 12]): return False, False
            l_angle = np.degrees(PoseEngine.angle_between(l_shldr, l_elbow, l_wrist))
            r_angle = np.degrees(PoseEngine.angle_between(r_shldr, r_elbow, r_wrist))
            both_straight = l_angle < 40 and r_angle < 40
            both_above = r_wrist[1] < r_shldr[1] - 0.1 and l_wrist[1] < l_shldr[1] - 0.1
            return both_straight and both_above, False

        elif movement_name == "Cross Arms on Chest":
            if not is_visible([15, 12, 16, 11]): return False, False
            # Left wrist near right shoulder AND right wrist near left shoulder
            dist_l_r_shldr = np.linalg.norm(l_wrist[:2] - r_shldr[:2])
            dist_r_l_shldr = np.linalg.norm(r_wrist[:2] - l_shldr[:2])
            correct = dist_l_r_shldr < 0.2 and dist_r_l_shldr < 0.2
            return correct, False

        elif movement_name == "Arms Out to Sides":
            if not is_visible([15, 11, 16, 12]): return False, False
            # Wrists at shoulder level but far away horizontally
            same_level = abs(l_wrist[1] - l_shldr[1]) < 0.15 and abs(r_wrist[1] - r_shldr[1]) < 0.15
            far_out = abs(l_wrist[0] - l_shldr[0]) > 0.2 and abs(r_wrist[0] - r_shldr[0]) > 0.2
            correct = same_level and far_out
            return correct, False

        elif movement_name == "Flex Muscles":
            if not is_visible([15, 13, 11, 16, 14, 12]): return False, False
            # Both elbows out, wrists above elbows
            elbows_out = abs(l_shldr[1] - l_elbow[1]) < 0.1 and abs(r_shldr[1] - r_elbow[1]) < 0.1
            wrists_up = l_wrist[1] < l_elbow[1] - 0.1 and r_wrist[1] < r_elbow[1] - 0.1
            correct = elbows_out and wrists_up
            return correct, False

        elif movement_name == "One Hand Up, One Hand on Hip":
            r_up_l_hip = r_wrist[3] > thresh and r_wrist[1] < r_shldr[1] - 0.1 and \
                         l_wrist[3] > thresh and np.linalg.norm(l_wrist[:2] - l_hip[:2]) < 0.2
            l_up_r_hip = l_wrist[3] > thresh and l_wrist[1] < l_shldr[1] - 0.1 and \
                         r_wrist[3] > thresh and np.linalg.norm(r_wrist[:2] - r_hip[:2]) < 0.2
            return r_up_l_hip or l_up_r_hip, False

        elif movement_name == "Archer Pose":
            # Archer Right: Right arm forward, Left hand near Left ear
            archer_r = r_wrist[3] > thresh and r_wrist[0] < r_shldr[0] - 0.2 and \
                       l_wrist[3] > thresh and np.linalg.norm(l_wrist[:2] - l_ear[:2]) < 0.2
            # Archer Left: Left arm forward, Right hand near Right ear
            archer_l = l_wrist[3] > thresh and l_wrist[0] > l_shldr[0] + 0.2 and \
                       r_wrist[3] > thresh and np.linalg.norm(r_wrist[:2] - r_ear[:2]) < 0.2
            return archer_r or archer_l, False

        elif movement_name == "The Surfer":
            if not is_visible([27, 28, 15, 16, 11, 12, 0]): return False, False
            # Sideways wide stance, knees bent, arms out
            wide = abs(l_ankle[0] - r_ankle[0]) > 0.4
            crouching = nose[1] > min(l_shldr[1], r_shldr[1]) + 0.05
            arms_extended = abs(l_wrist[0] - r_wrist[0]) > 0.6
            return wide and crouching and arms_extended, False

        elif movement_name == "Crouching Tiger":
            if not is_visible([0, 11, 15, 16]): return False, False
            deep_crouch = nose[1] > l_shldr[1] + 0.1
            hands_forward = np.linalg.norm(l_wrist[:2] - nose[:2]) < 0.3 and np.linalg.norm(r_wrist[:2] - nose[:2]) < 0.3
            return deep_crouch and hands_forward, False

        elif movement_name == "Tree Pose":
            l_on_r = l_ankle[3] > thresh and r_knee[3] > thresh and np.linalg.norm(l_ankle[:2] - r_knee[:2]) < 0.15
            r_on_l = r_ankle[3] > thresh and l_knee[3] > thresh and np.linalg.norm(r_ankle[:2] - l_knee[:2]) < 0.15
            return l_on_r or r_on_l, False

        elif movement_name == "Arms Forming a Circle":
            if not is_visible([15, 16, 0]): return False, False
            above_head = r_wrist[1] < nose[1] - 0.1 and l_wrist[1] < nose[1] - 0.1
            hands_close = np.linalg.norm(l_wrist[:2] - r_wrist[:2]) < 0.15
            return above_head and hands_close, False

        return False, False

    def draw_landmarks(self, frame, pose_landmarks, match_state="search"):
        """Draws a premium glowing neon skeleton on the frame."""
        if not pose_landmarks:
            return
            
        h, w, _ = frame.shape
        
        # Determine glowing colors based on match_state
        # BGR Format
        if match_state == "success":
            color = (16, 185, 129)       # Emerald Green
            glow_color = (80, 230, 170)
        elif match_state == "holding":
            color = (11, 158, 245)       # Amber Orange
            glow_color = (100, 200, 250)
        elif match_state == "error":
            color = (94, 63, 244)        # Rose Red
            glow_color = (150, 120, 250)
        else:
            color = (241, 102, 99)       # Indigo
            glow_color = (250, 150, 150)
            
        # Draw Connections
        landmarks = pose_landmarks.landmark
        
        # Key connections to draw
        connections = [
            # Arms
            (11, 13), (13, 15), (12, 14), (14, 16),
            # Torso
            (11, 12), (11, 23), (12, 24), (23, 24),
            # Legs
            (23, 25), (25, 27), (24, 26), (26, 28)
        ]
        
        # 1. Draw glowing lines first (thick, semi-transparent blur)
        overlay = frame.copy()
        for p1_idx, p2_idx in connections:
            if p1_idx >= len(landmarks) or p2_idx >= len(landmarks):
                continue
            p1 = landmarks[p1_idx]
            p2 = landmarks[p2_idx]
            if p1.visibility > 0.5 and p2.visibility > 0.5:
                pt1 = (int(p1.x * w), int(p1.y * h))
                pt2 = (int(p2.x * w), int(p2.y * h))
                cv2.line(overlay, pt1, pt2, glow_color, 8, cv2.LINE_AA)
                cv2.line(overlay, pt1, pt2, color, 3, cv2.LINE_AA)
        
        # Apply the glow line overlay with transparency
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
        
        # 2. Draw stylish joints (glowing circles)
        joints_to_draw = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        for idx in joints_to_draw:
            if idx >= len(landmarks):
                continue
            p = landmarks[idx]
            if p.visibility > 0.5:
                pt = (int(p.x * w), int(p.y * h))
                # Outer glow
                cv2.circle(frame, pt, 7, glow_color, -1, cv2.LINE_AA)
                # Core solid dot
                cv2.circle(frame, pt, 3, (255, 255, 255), -1, cv2.LINE_AA)
