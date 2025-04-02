import pyttsx3
import time
import random
import pyautogui
import pygame
import os
import numpy as np
from pynput.keyboard import Key, Controller as KeyController
from pynput.mouse import Controller as MouseController, Button
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from config import SOUNDS_DIR, LANGUAGE, update_personality
from exit import exit_program

engine = pyttsx3.init()
keyboard = KeyController()
mouse = MouseController()
onteam = True
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
pygame.mixer.init()
muted = False

def get_personality_names():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    personalities_dir = os.path.join(parent_dir, "personalities")
    return [os.path.splitext(filename)[0] for filename in os.listdir(personalities_dir) if filename.endswith(".json")]

available_personalities = ", ".join(get_personality_names())

command_handlers = {
        "prs": lambda content: (press, (content)),
        "msg": lambda content: (chat, (content.strip()[:-(5 if content.lower().endswith("false") else 4)].strip(' ",'), content.lower().endswith("true"))),
        "ply": lambda content: (play_sound, (content)),
        "dly": lambda content: (time.sleep, (float(content))),
        "vls": lambda content: (set_volume, (int(content))),
        "fre": lambda content: (fireshots, (int(content))),
        "uni": lambda content: (unibeam, (float(content))),
        "per": lambda content: (load_personality, (content)),
        "frk": lambda _: (freaky, ()),
        "lck": lambda _: (insta_lock, ()),
        "mut": lambda _: (toggle_mute, ()),
        "vld": lambda _: (change_volume, (-10)),
        "vlu": lambda _: (change_volume, (10)),
        "ext": lambda _: (exit_program, ()),
    }

commands_string = f"""
  prs(q)      - Nuke, destroy, or use maximum pulse  
  prs(e)      - Power up  
  prs(shift)  - Start or stop flying  
  prs(f)      - Fire rockets  
  prs(r)      - Reload  
  fre(n)      - Fire a specific number of shots  
  uni(n)      - Fire the unibeam for a specific number of seconds  
  per(personality) - Load a new personality. Available personalities: {available_personalities}
  msg(txt true) - Send a message in team chat  
  msg(txt false) - Send a message in match chat  
  frk()        - Activate freaky mode  
  dly(n)      - Delay execution by n seconds  
  ext()        - Power off or terminate the program  
  mut()        - Mute or unmute audio  
  vld()        - Turn down the volume  
  vlu()        - Turn up the volume  
  vls(n)      - Set volume to a specific percentage  
  lck()        - Insta-lock Iron Man  
  ply(name)   - Play a sound effect (fart, roast, laugh, getout, boom, scream, yay)  
  """

additional_info = """
Iron Man could also ask you to blame his teammates depending on their roles for losing:  
  - dps for damage dealers  
  - supports for healers  
  - tanks for defenders 
"""
# region Methods for Commands
def fireshots(n):
        for _ in range(n):
            pyautogui.mouseDown(button='left')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='left')
            time.sleep(0.1)

def unibeam(n):
    pyautogui.mouseDown(button='right')
    time.sleep(n)
    pyautogui.mouseUp(button='right')

def freaky():
    for _ in range(50):
        mouse.press(Button.right)
        time.sleep(0.02)
        mouse.release(Button.right)
        time.sleep(0.05)

def press(key):
    if key.lower() == "shift":
        keyboard.press(Key.shift)
        time.sleep(random.uniform(0.1, 0.2))
        keyboard.release(Key.shift)
    else:
        keyboard.press(key)
        time.sleep(random.uniform(0.1, 0.2))
        keyboard.release(key)

def play_sound(sound):
    sound_path = os.path.join(SOUNDS_DIR, f"{sound}.mp3")
    if os.path.exists(sound_path):
        pygame.mixer.Sound(sound_path).play()

def toggle_mute():
    global muted
    muted = not muted
    volume.SetMute(muted, None)

def set_volume(level):
    pygame.mixer.music.set_volume(level / 100.0)

def change_volume(amount):
    current = pygame.mixer.music.get_volume()
    change = amount / 100.0
    new_level = current + change
    new_level = max(0.0, min(new_level, 1.0))
    pygame.mixer.music.set_volume(new_level)

def insta_lock():
    screen_width, screen_height = pyautogui.size()
    
    # Calculate target position using relative positions (93.75% of screen width, 60.19% of screen height)
    tx = int(screen_width * 0.9375)  # 1800/1920 ≈ 0.9375
    ty = int(screen_height * 0.6019)  # 650/1080 ≈ 0.6019
    
    duration = 0.5
    steps = 50

    sx, sy = mouse.position
    offset_x = int(screen_width * 0.15625) # 300/1920 ≈ 0.15625
    offset_y = int(screen_height * 0.18519) # 200/1080 ≈ 0.18519
    
    p1 = (sx + offset_x, sy - offset_y)
    p2 = (tx - offset_x, ty + offset_y)
    p3 = (tx, ty)

    t_values = np.linspace(0, 1, steps)
    curve = [
        (
            (1 - t) ** 3 * sx + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
            (1 - t) ** 3 * sy + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        )
        for t in t_values
    ]

    step_time = duration / steps
    for x, y in curve:
        mouse.position = (int(x), int(y))
        time.sleep(step_time)

    mouse.scroll(0, -1)
    mouse.scroll(0, -1)
    time.sleep(0.1)
    mouse.click(Button.left, 2)

def typerandom(message):
    for char in message:
        keyboard.press(char)
        time.sleep(random.uniform(0.02, 0.08))
        keyboard.release(char)

def chat(message, target):
    global onteam

    if target and not onteam:
        pyautogui.press("enter")
        press("\t")
        time.sleep(0.2)
        typerandom(message)
        pyautogui.press("enter")
        onteam = True
    elif not target and onteam:
        pyautogui.press("enter")
        press("\t")
        time.sleep(0.2)
        typerandom(message)
        pyautogui.press("enter")
        onteam = False
    else:
        pyautogui.press("enter")
        time.sleep(0.2)
        typerandom(message)
        pyautogui.press("enter")

def load_personality(personality):
    update_personality(personality)
    exit_program()

# endregion
