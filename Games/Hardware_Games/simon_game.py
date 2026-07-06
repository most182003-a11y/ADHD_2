import sys
import time
import random
import json
import os
import board
import neopixel
import RPi.GPIO as GPIO
import pygame

# Parse Child ID from CLI arguments (consistent with other games)
CHILD_ID = "CHILD001"
if len(sys.argv) > 1:
    CHILD_ID = sys.argv[1]

# ---------- AUDIO ----------
pygame.mixer.init()
button_sound = pygame.mixer.Sound("Button_Sound.mp3")
lose_sound = pygame.mixer.Sound("Lose_sound.mp3")
pass_sound = pygame.mixer.Sound("pass_sound.mp3")
win_sound = pygame.mixer.Sound("win_sound.mp3")

def play(sound):
    sound.play()

# ---------- LED SETUP ----------
PIXEL_PIN = board.D18
NUM_PIXELS = 6
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.4, auto_write=False, pixel_order=neopixel.GRB)

# ---------- BUTTON SETUP ----------
BUTTON_PINS = [5, 6, 13, 19, 26, 21]
GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ---------- COLORS ----------
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255)
]

# ---------- EFFECTS ----------
def flash_led(index, speed):
    pixels.fill((0, 0, 0))
    pixels[index] = COLORS[index]
    pixels.show()
    play(button_sound)
    time.sleep(speed)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.12)

def wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbow_animation():
    for j in range(255):
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(0.004)

def show_sequence(sequence, speed):
    time.sleep(0.7)
    for index in sequence:
        pixels.fill((0, 0, 0))
        pixels[index] = COLORS[index]
        pixels.show()
        time.sleep(speed)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.15)

def wait_for_button(speed):
    """Wait for a button press and return button index. Also measures reaction time."""
    start = time.time()
    while True:
        for i, pin in enumerate(BUTTON_PINS):
            if GPIO.input(pin) == GPIO.LOW:
                time.sleep(0.03)  # debounce
                if GPIO.input(pin) == GPIO.LOW:
                    reaction = time.time() - start
                    flash_led(i, speed)
                    while GPIO.input(pin) == GPIO.LOW:
                        time.sleep(0.01)
                    return i, reaction
        time.sleep(0.005)

def game_over_effect():
    play(lose_sound)
    for _ in range(4):
        pixels.fill((255, 0, 0))
        pixels.show()
        time.sleep(0.3)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.3)
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(0.5)
    pixels.fill((0, 0, 0))
    pixels.show()

# ---------- DATA COLLECTION ----------
session_data = {
    "gameType": "SimonMemory",
    "startTime": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "levels": [],
    "finalLevel": 0,
    "totalCorrectSteps": 0,
    "totalSteps": 0,
    "prematurePressesDuringShow": 0,  # new
    "endStatus": "completed"           # "completed", "lost", "quit"
}

def save_json(data):
    try:
        with open("session_metrics.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Metrics saved to session_metrics.json")
    except Exception as e:
        print(f"Error saving session_metrics.json: {e}")

def _send_simon_to_api():
    try:
        from backend_api import create_session, save_simon_trials, save_summary
    except ImportError:
        print("Warning: backend_api.py not found. Could not sync with API.")
        return

    print("Syncing Simon Memory data to API...")
    # 1. Create a session on the API
    api_session_id = create_session(CHILD_ID, "SimonMemory")
    if not api_session_id:
        print("Failed to create session on API.")
        return

    # 2. Extract trials (flatten level/step structure)
    api_trials = []
    for lvl in session_data["levels"]:
        for stp in lvl["steps"]:
            api_trials.append({
                "level": lvl["level"],
                "sequenceLength": lvl["sequenceLength"],
                "speed": lvl["speed"],
                "step": stp["step"],
                "expected": stp["expected"],
                "pressed": stp["pressed"],
                "correct": stp["correct"],
                "reactionTimeMs": stp["reactionTimeMs"]
            })

    # 3. Save trials
    if api_trials:
        save_simon_trials(api_session_id, api_trials)

    # 4. Save summary
    summary = {
        "totalTrials": len(api_trials),
        "finalLevel": session_data["finalLevel"],
        "totalCorrectSteps": session_data["totalCorrectSteps"],
        "totalSteps": session_data["totalSteps"],
        "prematurePressesDuringShow": session_data["prematurePressesDuringShow"],
        "endStatus": session_data["endStatus"]
    }
    save_summary(api_session_id, summary)
    print("Simon Memory data sync completed.")

def save_session_data(current_level=None):
    # Dynamically compute totals from whatever is in levels to be safe
    total_steps = 0
    total_correct = 0
    for lvl in session_data["levels"]:
        total_steps += len(lvl["steps"])
        total_correct += sum(1 for s in lvl["steps"] if s["correct"])
    session_data["totalSteps"] = total_steps
    session_data["totalCorrectSteps"] = total_correct
    session_data["prematurePressesDuringShow"] = premature_presses
    
    if current_level is not None:
        session_data["finalLevel"] = current_level
    elif not session_data.get("finalLevel"):
        session_data["finalLevel"] = len(session_data["levels"]) if session_data["levels"] else 1
        
    save_json(session_data)
    _send_simon_to_api()

# ---------- MAIN GAME ----------
print("Simon Memory Game Started")

try:
    sequence = []
    BASE_LENGTH = 3
    BASE_SPEED = 0.6
    premature_presses = 0

    for level in range(1, 11):
        print("Level", level)

        # Increase sequence length
        while len(sequence) < BASE_LENGTH + level - 1:
            sequence.append(random.randint(0, NUM_PIXELS - 1))

        # Increase speed
        speed = BASE_SPEED - (level * 0.04)
        if speed < 0.2:
            speed = 0.2

        rainbow_animation()

        # Show sequence while listening for premature presses
        time.sleep(0.7)  # initial pause
        for idx, led_idx in enumerate(sequence):
            # Light on
            pixels.fill((0, 0, 0))
            pixels[led_idx] = COLORS[led_idx]
            pixels.show()

            # Check for button press during LED on (simple polling)
            led_start = time.time()
            while time.time() - led_start < speed:
                for i, pin in enumerate(BUTTON_PINS):
                    if GPIO.input(pin) == GPIO.LOW:
                        time.sleep(0.03)
                        if GPIO.input(pin) == GPIO.LOW:
                            # Premature press detected
                            premature_presses += 1
                            play(button_sound)  # feedback sound
                            while GPIO.input(pin) == GPIO.LOW:
                                time.sleep(0.01)
                time.sleep(0.01)

            # Light off
            pixels.fill((0, 0, 0))
            pixels.show()
            time.sleep(0.15)

        # Reproduction phase
        level_data = {
            "level": level,
            "sequenceLength": len(sequence),
            "speed": round(speed, 3),
            "steps": []
        }

        for step, expected in enumerate(sequence):
            # Record reaction time: from now until correct press (or wrong)
            pressed, reaction = wait_for_button(speed)

            step_info = {
                "step": step + 1,
                "expected": expected,
                "pressed": pressed,
                "correct": pressed == expected,
                "reactionTimeMs": round(reaction * 1000, 1)
            }

            if not step_info["correct"]:
                # Wrong press → game over
                level_data["steps"].append(step_info)
                session_data["levels"].append(level_data)
                session_data["endStatus"] = "lost"
                save_session_data(level)
                print("Game Over")
                game_over_effect()
                raise SystemExit

            # Correct step
            level_data["steps"].append(step_info)
            time.sleep(0.1)  # small gap between presses

        play(pass_sound)
        session_data["levels"].append(level_data)

    # All levels completed
    session_data["endStatus"] = "completed"
    save_session_data(10)

    print("YOU WIN!")
    pixels.fill((0, 255, 0))
    pixels.show()
    play(win_sound)
    time.sleep(2)

except KeyboardInterrupt:
    # Quit early
    session_data["endStatus"] = "quit"
    current_level = level if 'level' in locals() else None
    save_session_data(current_level)

finally:
    pixels.fill((0, 0, 0))
    pixels.show()
    GPIO.cleanup()
()