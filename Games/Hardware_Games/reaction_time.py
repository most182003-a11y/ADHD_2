import sys
import time
import random
import json
import board
import neopixel
import RPi.GPIO as GPIO
import pygame

# Parse Child ID from CLI arguments (consistent with other games)
CHILD_ID = "CHILD001"
if len(sys.argv) > 1:
    CHILD_ID = sys.argv[1]

# ---------- إعدادات الصوت ----------
pygame.mixer.init()
# تأكد من وجود الملفات الصوتية أو استبدلها بأصوات افتراضية
start_beep = pygame.mixer.Sound("beep_start.wav")    # تنبيه بداية المحاولة
go_sound = pygame.mixer.Sound("go_sound.wav")         # صوت عند الإضاءة
wrong_sound = pygame.mixer.Sound("wrong_buzzer.wav")
miss_sound = pygame.mixer.Sound("miss_sound.wav")
end_session_sound = pygame.mixer.Sound("end_session.wav")

def play(sound):
    sound.play()

# ---------- إعدادات LED ----------
PIXEL_PIN = board.D18
NUM_PIXELS = 6
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.4, auto_write=False, pixel_order=neopixel.GRB)

# ---------- إعدادات الأزرار ----------
BUTTON_PINS = [5, 6, 13, 19, 26, 21]  # الترتيب يطابق مؤشرات الـ LED من 0 إلى 5
GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ألوان LED
COLORS = [
    (255, 0, 0),    # أحمر
    (0, 255, 0),    # أخضر
    (0, 0, 255),    # أزرق
    (255, 255, 0),  # أصفر
    (255, 0, 255),  # بنفسجي
    (0, 255, 255)   # سماوي
]

# ---------- دوال مساعدة ----------

def all_off():
    pixels.fill((0, 0, 0))
    pixels.show()

def light_led(index, color=None):
    """تضيء ليد واحد فقط"""
    all_off()
    if color is None:
        color = COLORS[index]
    pixels[index] = color
    pixels.show()

def wait_for_no_press(timeout=0.5):
    """تنتظر حتى لا يكون هناك زر مضغوط، لضمان نقطة بداية نظيفة"""
    start = time.time()
    while time.time() - start < timeout:
        if all(GPIO.input(pin) == GPIO.HIGH for pin in BUTTON_PINS):
            return True
        time.sleep(0.01)
    return False

def get_pressed_button():
    """ترجع مؤشر الزر المضغوط (0-5) أو None إذا لم يضغط شيء"""
    for i, pin in enumerate(BUTTON_PINS):
        if GPIO.input(pin) == GPIO.LOW:
            time.sleep(0.02)  # debounce
            if GPIO.input(pin) == GPIO.LOW:
                # انتظار حتى يترك الزر
                while GPIO.input(pin) == GPIO.LOW:
                    time.sleep(0.01)
                return i
    return None

# ---------- إعدادات الجلسة ----------
NUM_TRIALS = 15               # عدد المحاولات
MIN_DELAY = 1.5               # ثانية - أقل تأخير عشوائي قبل الإضاءة
MAX_DELAY = 4.0               # أقصى تأخير عشوائي
RESPONSE_TIMEOUT = 2.0        # المهلة للضغط بعد الإضاءة (ثواني)
IMPULSIVE_THRESHOLD = 0.5     # إذا ضغط الزر الخطأ خلال هذه المدة بعد الإضاءة يعتبر خطأ اندفاعي

# بيانات الجلسة للتخزين
session = {
    "gameType": "ReactionTime",
    "startTime": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "numTrials": NUM_TRIALS,
    "trials": [],
    "summary": {}
}

def save_session():
    try:
        with open("reaction_metrics.json", "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        print("تم حفظ البيانات في reaction_metrics.json")
    except Exception as e:
        print(f"Error saving reaction_metrics.json: {e}")

def _send_reaction_to_api():
    try:
        from backend_api import create_session, save_reaction_trials, save_summary
    except ImportError:
        print("Warning: backend_api.py not found. Could not sync with API.")
        return

    print("Syncing Reaction Time data to API...")
    # 1. Create a session on the API
    api_session_id = create_session(CHILD_ID, "ReactionTime")
    if not api_session_id:
        print("Failed to create session on API.")
        return

    # 2. Extract trials
    api_trials = []
    for t in session["trials"]:
        # Map pressedButton to -1 if None (since API expects non-nullable int)
        pressed_btn = t["pressedButton"] if t["pressedButton"] is not None else -1
        api_trials.append({
            "trial": t["trial"],
            "targetLED": t["targetLED"],
            "delay": t["delay"],
            "result": t["result"],
            "pressedButton": pressed_btn,
            "reactionTimeMs": t["reactionTimeMs"],
            "correct": t["correct"],
            "impulsiveError": t["impulsiveError"]
        })

    # 3. Save trials
    if api_trials:
        save_reaction_trials(api_session_id, api_trials)

    # 4. Save summary
    summary = {
        "totalTrials": session["summary"]["totalTrials"],
        "hits": session["summary"]["hits"],
        "falseStarts": session["summary"]["falseStarts"],
        "misses": session["summary"]["misses"],
        "impulsiveErrors": session["summary"]["impulsiveErrors"],
        "wrongButtons": session["summary"]["wrongButtons"],
        "averageReactionTimeMs": session["summary"]["averageReactionTimeMs"],
        "reactionTimeStdDevMs": session["summary"]["reactionTimeStdDevMs"],
        "impulsivityScore": session["summary"]["impulsivityScore"],
        "attentionScore": session["summary"]["attentionScore"]
    }
    save_summary(api_session_id, summary)
    print("Reaction Time data sync completed.")

def save_session_data(interrupted=False):
    # Compute summary stats dynamically
    trials_played = len(session["trials"])
    hits = [t for t in session["trials"] if t["result"] == "hit"]
    false_starts = [t for t in session["trials"] if t["result"] == "false_start"]
    misses = [t for t in session["trials"] if t["result"] == "miss"]
    impulsive_errors = [t for t in session["trials"] if t["result"] == "impulsive_error"]
    wrong_buttons = [t for t in session["trials"] if t["result"] == "wrong_button"]

    hit_rt = [t["reactionTimeMs"] for t in hits if t["reactionTimeMs"] is not None]
    avg_rt = sum(hit_rt)/len(hit_rt) if hit_rt else None
    rt_variability = (sum((x - avg_rt)**2 for x in hit_rt) / len(hit_rt))**0.5 if len(hit_rt) > 1 else 0

    total_denom = trials_played if trials_played > 0 else 1
    session["summary"] = {
        "totalTrials": trials_played,
        "hits": len(hits),
        "falseStarts": len(false_starts),
        "misses": len(misses),
        "impulsiveErrors": len(impulsive_errors),
        "wrongButtons": len(wrong_buttons),
        "averageReactionTimeMs": round(avg_rt, 1) if avg_rt else None,
        "reactionTimeStdDevMs": round(rt_variability, 1),
        "impulsivityScore": round((len(false_starts) + len(impulsive_errors)) / total_denom * 100, 1),
        "attentionScore": round((len(hits) / total_denom) * 100, 1)
    }
    if interrupted:
        session["summary"]["interrupted"] = True

    save_session()
    _send_reaction_to_api()

# ---------- اللعبة الأساسية ----------
print("=== لعبة زمن رد الفعل ===")
print("انتظر الإضاءة... اضغط الزر الصحيح بأسرع ما يمكن")
print("اضغط Ctrl+C للخروج المبكر\n")

try:
    all_off()
    time.sleep(1)

    for trial in range(1, NUM_TRIALS + 1):
        # اختيار LED عشوائي ليكون الهدف
        target_led = random.randint(0, NUM_PIXELS - 1)
        print(f"\nمحاولة {trial}: LED رقم {target_led} (لونه {COLORS[target_led]})")

        # تأخير عشوائي قبل الإضاءة (يمنع التوقع)
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"تأخير عشوائي: {delay:.2f} ثانية")
        
        # بداية مرحلة الانتظار – نتأكد أن الأزرار غير مضغوطة
        wait_for_no_press(0.5)
        all_off()
        
        # تشغيل صوت تنبيه بداية المحاولة (اختياري)
        play(start_beep)
        
        # ننتظر مدة التأخير مع مراقبة أي ضغط مبكر (False Start)
        premature = None
        start_wait = time.time()
        while time.time() - start_wait < delay:
            btn = get_pressed_button()
            if btn is not None:
                premature = btn
                break
            time.sleep(0.01)
        
        if premature is not None:
            # ضغط مبكر – اندفاعية شديدة
            play(wrong_sound)
            # وميض أحمر سريع
            for _ in range(3):
                light_led(premature, (255,0,0))
                time.sleep(0.1)
                all_off()
                time.sleep(0.1)
            
            trial_data = {
                "trial": trial,
                "targetLED": target_led,
                "delay": round(delay, 3),
                "result": "false_start",
                "pressedButton": premature,
                "reactionTimeMs": None,
                "correct": False,
                "impulsiveError": True
            }
            session["trials"].append(trial_data)
            print("❌ ضغط مبكر! نتيجة: اندفاع.")
            time.sleep(0.5)
            continue

        # لا يوجد ضغط مبكر -> نُضيء الـ LED الهدف
        light_led(target_led)
        play(go_sound)
        stimulus_time = time.time()

        # انتظار رد الفعل (ضغط أي زر)
        response_btn = None
        reaction_time = None
        while time.time() - stimulus_time < RESPONSE_TIMEOUT:
            btn = get_pressed_button()
            if btn is not None:
                reaction_time = time.time() - stimulus_time
                response_btn = btn
                break
            time.sleep(0.005)

        all_off()  # نطفئ الـ LED بمجرد الضغط أو انتهاء المهلة

        if response_btn is None:
            # لم يضغط أي زر خلال المهلة (فقدان انتباه)
            play(miss_sound)
            # وميض أصفر
            for _ in range(2):
                light_led(target_led, (255,255,0))
                time.sleep(0.2)
                all_off()
                time.sleep(0.2)
            
            trial_data = {
                "trial": trial,
                "targetLED": target_led,
                "delay": round(delay, 3),
                "result": "miss",
                "pressedButton": None,
                "reactionTimeMs": None,
                "correct": False,
                "impulsiveError": False
            }
            session["trials"].append(trial_data)
            print("⏰ لم يتم الضغط في الوقت المحدد (سهو)")
        else:
            # تحقق من صحة الزر
            correct = (response_btn == target_led)
            # تحديد ما إذا كان خطأ اندفاعي (ضغط خاطئ سريع جداً)
            impulsive = (not correct) and (reaction_time < IMPULSIVE_THRESHOLD)
            
            if correct:
                play(go_sound)  # أو صوت نجاح
                print(f"✅ صحيح! زمن رد الفعل: {reaction_time*1000:.0f} مللي ثانية")
                # وميض أخضر سريع
                light_led(target_led, (0,255,0))
                time.sleep(0.3)
                all_off()
            else:
                if impulsive:
                    play(wrong_sound)
                    print(f"⚠️ خطأ اندفاعي (ضغط زر خاطئ بسرعة)! زمن: {reaction_time*1000:.0f} مللي ثانية")
                else:
                    play(wrong_sound)
                    print(f"❌ خطأ (زر خاطئ) زمن: {reaction_time*1000:.0f} مللي ثانية")
                # وميض أحمر
                light_led(response_btn, (255,0,0))
                time.sleep(0.5)
                all_off()
            
            trial_data = {
                "trial": trial,
                "targetLED": target_led,
                "delay": round(delay, 3),
                "result": "hit" if correct else ("impulsive_error" if impulsive else "wrong_button"),
                "pressedButton": response_btn,
                "reactionTimeMs": round(reaction_time * 1000, 1),
                "correct": correct,
                "impulsiveError": impulsive
            }
            session["trials"].append(trial_data)
        
        time.sleep(0.8)  # استراحة بين المحاولات

    save_session_data(interrupted=False)
    play(end_session_sound)
    print("\n🏁 انتهت اللعبة بنجاح")

except KeyboardInterrupt:
    save_session_data(interrupted=True)
    print("\n⏹️ تم الخروج المبكر")

finally:
    all_off()
    GPIO.cleanup()
    pygame.quit()