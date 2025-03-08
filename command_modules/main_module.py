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
from config import SOUNDS_DIR
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

command_handlers = {
        "prs": lambda content: (press, (content)),
        "msg": lambda content: (chat, (content.strip()[:-4].strip(' ",'), content.lower().endswith("true"))),
        "ply": lambda content: (play_sound, (content)),
        "dly": lambda content: (time.sleep, (float(content))),
        "vls": lambda content: (set_volume, (int(content))),
        "fre": lambda content: (fireshots, (int(content))),
        "uni": lambda content: (unibeam, (float(content))),
        "frk": lambda _: (freaky, ()),
        "lck": lambda _: (insta_lock, ()),
        "mut": lambda _: (toggle_mute, ()),
        "vld": lambda _: (change_volume, (-10)),
        "vlu": lambda _: (change_volume, (10)),
        "ext": lambda _: (exit_program, ()),
    }

commands_string = """
  prs(q)      - Nuke, destroy, or use maximum pulse  
  prs(e)      - Power up  
  prs(shift)  - Start or stop flying  
  prs(f)      - Fire rockets  
  prs(r)      - Reload  
  fre(n)      - Fire a specific number of shots  
  uni(n)      - Fire the unibeam for a specific number of seconds  
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
            press('o')
            time.sleep(0.7)

def unibeam(n):
    pyautogui.mouseDown(button='right')
    time.sleep(n)
    pyautogui.mouseUp(button='right')

def freaky():
    for _ in range(50):
        keyboard.press('u')
        time.sleep(0.01)
        keyboard.release('u')
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
    volume.SetMasterVolumeLevelScalar(level / 100.0, None)

def change_volume(amount):
    current = volume.GetMasterVolumeLevelScalar() * 100
    new_level = max(0, min(100, current + amount))
    volume.SetMasterVolumeLevelScalar(new_level / 100.0, None)

def insta_lock():
    tx, ty = 1800, 650
    duration = 0.5
    steps = 50

    sx, sy = mouse.position
    p1 = (sx + 300, sy - 200)
    p2 = (tx - 100, ty + 200)
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

# endregion
