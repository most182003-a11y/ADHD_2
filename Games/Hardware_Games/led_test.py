import time
import random
import board
import neopixel
import RPi.GPIO as GPIO
import pygame

# ---------- AUDIO ----------
pygame.mixer.init()
button_sound = pygame.mixer.Sound("Button_Sound.mp3")
lose_sound = pygame.mixer.Sound("Lose_sound.mp3")
pass_sound = pygame.mixer.Sound("pass_sound.mp3")
win_sound = pygame.mixer.Sound("win_sound.mp3")

def play(sound):
    sound.play()   # تشغيل بدون انتظار

# ---------- LED SETUP ----------
PIXEL_PIN = board.D18
NUM_PIXELS = 6

pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=0.4,
    auto_write=False,
    pixel_order=neopixel.GRB
)

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
    while True:
        for i, pin in enumerate(BUTTON_PINS):
            if GPIO.input(pin) == GPIO.LOW:
                time.sleep(0.03)  # debounce
                if GPIO.input(pin) == GPIO.LOW:
                    flash_led(i, speed)
                    while GPIO.input(pin) == GPIO.LOW:
                        time.sleep(0.01)
                    return i
        time.sleep(0.005)

def game_over():
    play(lose_sound)  # تشغيل الصوت أولاً
    
    # تأثير الخسارة مع الصوت
    for _ in range(4):  # 4 مرات عشان يتناسب مع طول الصوت
        pixels.fill((0, 255, 0))
        pixels.show()
        time.sleep(0.3)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.3)
    
    # نهاية سريعة مع ضوء أحمر ثابت
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.5)
    pixels.fill((0, 0, 0))
    pixels.show()

# ---------- MAIN GAME ----------
print("Simon Memory Game Started")

try:
    sequence = []
    BASE_LENGTH = 3
    BASE_SPEED = 0.6

    for level in range(1, 11):

        print("Level", level)

        # زيادة طول التسلسل
        while len(sequence) < BASE_LENGTH + level - 1:
            sequence.append(random.randint(0, NUM_PIXELS - 1))

        # زيادة السرعة
        speed = BASE_SPEED - (level * 0.04)
        if speed < 0.2:
            speed = 0.2

        rainbow_animation()
        show_sequence(sequence, speed)

        for expected in sequence:
            pressed = wait_for_button(speed)
            if pressed != expected:
                print("Game Over")
                game_over()
                raise SystemExit

        play(pass_sound)

    print("YOU WIN!")
    pixels.fill((0, 255, 0))
    pixels.show()
    play(win_sound)
    time.sleep(2)

except KeyboardInterrupt:
    pass

finally:
    pixels.fill((0, 0, 0))
    pixels.show()
    GPIO.cleanup()
