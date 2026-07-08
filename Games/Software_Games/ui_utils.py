import cv2
import numpy as np
import time

COLOR_DARK = (10, 10, 10)
COLOR_SLATE = (59, 41, 30)
COLOR_INDIGO = (241, 102, 99)
COLOR_LIGHT_INDIGO = (248, 140, 129)
COLOR_EMERALD = (129, 185, 16)
COLOR_ROSE = (94, 63, 244)
COLOR_AMBER = (11, 158, 245)
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
    overlay = img.copy()
    r = corner_radius

    cv2.circle(overlay, (x + r, y + r), r, bg_color, -1)
    cv2.circle(overlay, (x + w - r, y + r), r, bg_color, -1)
    cv2.circle(overlay, (x + r, y + h - r), r, bg_color, -1)
    cv2.circle(overlay, (x + w - r, y + h - r), r, bg_color, -1)
    cv2.rectangle(overlay, (x + r, y), (x + w - r, y + h), bg_color, -1)
    cv2.rectangle(overlay, (x, y + r), (x + w, y + h - r), bg_color, -1)

    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    cv2.ellipse(img, (x + r, y + r), (r, r), 180, 0, 90, border_color, border_thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + w - r, y + r), (r, r), 270, 0, 90, border_color, border_thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + w - r, y + h - r), (r, r), 0, 0, 90, border_color, border_thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + r, y + h - r), (r, r), 90, 0, 90, border_color, border_thickness, cv2.LINE_AA)

    cv2.line(img, (x + r, y), (x + w - r, y), border_color, border_thickness, cv2.LINE_AA)
    cv2.line(img, (x + w, y + r), (x + w, y + h - r), border_color, border_thickness, cv2.LINE_AA)
    cv2.line(img, (x + r, y + h), (x + w - r, y + h), border_color, border_thickness, cv2.LINE_AA)
    cv2.line(img, (x, y + r), (x, y + h - r), border_color, border_thickness, cv2.LINE_AA)

def draw_glowing_circle(img, center, radius, color, thickness=2, glow_factor=3):
    for i in range(glow_factor, 0, -1):
        alpha = 0.15 / i
        overlay = img.copy()
        cv2.circle(overlay, center, radius + i*3, color, thickness + i*2, cv2.LINE_AA)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    cv2.circle(img, center, radius, color, thickness, cv2.LINE_AA)

def put_centered_text(img, text, cx, cy, font, scale, color, thickness):
    size = cv2.getTextSize(text, font, scale, thickness)[0]
    tx = cx - size[0] // 2
    ty = cy + size[1] // 2
    cv2.putText(img, text, (tx, ty), font, scale, color, thickness, cv2.LINE_AA)

def draw_fps_counter(img, fps, x=10, y=30):
    fps_color = COLOR_EMERALD if fps >= 20 else (COLOR_AMBER if fps >= 10 else COLOR_ROSE)
    cv2.putText(img, f"FPS: {fps}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2, cv2.LINE_AA)

def draw_lighting_indicator(img, status, x=120, y=30):
    light_color = COLOR_EMERALD if status == 'good' else (COLOR_AMBER if status == 'low' else COLOR_ROSE)
    cv2.putText(img, f"LIGHT: {status}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, light_color, 2, cv2.LINE_AA)
