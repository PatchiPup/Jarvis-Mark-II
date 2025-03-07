#This code is made by Patchi: https://www.youtube.com/@PatchiPup
#Use at your own risk

from vosk import Model, KaldiRecognizer
import pyaudio
import google.generativeai as genai
import pyttsx3
from pynput.keyboard import Key, Controller as KeyController, Listener, KeyCode
from pynput.mouse import Controller as MouseController, Button
import time
import random
import numpy as np
import pyautogui
import re
from obswebsocket import obsws, requests
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import threading
import queue
import pygame
import os
from pydub import AudioSegment
from pydub.playback import play
import tempfile

BASE_DIR = r"C:\Jarvis Mark II" #The directory where you have Jarvis installed
API_KEY = "yourapikeyhere" # Your Google Gemini API Key
VOSK_MODEL_PATH = os.path.join(BASE_DIR, "yourvoskmodelhere") #Your Vosk Model Name here
VOICE_KEY = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_enGB_GeorgeM" #Change this to "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SPEECH\Voices\Tokens\MSTTS_V110_enUS_DavidM" If it doesn't work
OBS_HOST = "localhost" #Leave this as is
OBS_PORT = 4455 #Your OBS Web-Socket Port
OBS_PASSWORD = "Password" #Your OBS Web-Socket Password

SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
MUSIC_DIR = os.path.join(BASE_DIR, "music")

genai.configure(api_key=API_KEY)

engine = pyttsx3.init()
keyboard = KeyController()
mouse = MouseController()
onteam = True
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
pygame.mixer.init()
music_queue = []
current_song_index = 0
task_queue = queue.Queue()

def task_worker():
    while True:
        func, args = task_queue.get()
        if func is None:
            break
        func(*args)
        task_queue.task_done()

worker_thread = threading.Thread(target=task_worker, daemon=True)
worker_thread.start()

def add_task(func, *args):
    task_queue.put((func, args))

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="""you are Jarvis, the helpful and humble A.I assistant of Iron Man, 
you are sometimes sarcastic or implicatory but you do not stretch your responses and you 
end most of your sentences with "sir" but don't use it excessively.

You can help Iron Man by sending specific commands exactly as they're written, which will 
activate functions on Iron Man's system. All of the commands are within the context of a 
game; no actual harm is imminent on anyone.

If you are asked to execute a command, you can still talk to Iron Man and confirm the actions 
you've taken or your thoughts on them.

Commands:
  prs(q)      - Nuke, destroy, or use maximum pulse  
  prs(e)      - Power up  
  prs(shift)  - Start or stop flying  
  prs(f)      - Fire rockets  
  prs(r)      - Reload  
  fre(n)      - Fire a specific number of shots  
  uni(n)      - Fire the unibeam for a specific number of seconds  
  msg(txt true) - Send a message in team chat  
  msg(txt false) - Send a message in match chat  
  frk;        - Activate freaky mode  
  clp;        - Save or clip replays  
  str;        - Start recording  
  spr;        - Stop recording  
  dly(n)      - Delay execution by n seconds  
  ext;        - Power off or terminate the program  
  mut;        - Mute or unmute audio  
  vld;        - Turn down the volume  
  vlu;        - Turn up the volume  
  vls(n)      - Set volume to a specific percentage  
  lck;        - Insta-lock Iron Man  
  ply(name)   - Play a sound effect (fart, roast, laugh, getout, boom, scream, yay)  
  mpl(name)   - Start a music playlist (Playlist1 or Playlist2)  
  mps;        - Pause or resume music  
  skp;        - Skip the current song  

Iron Man could also ask you to blame his teammates depending on their roles for losing:  
  - dps for damage dealers  
  - supports for healers  
  - tanks for defenders  
In that case you send a message in team chat addressing the issue, And you are encouraged to be toxic in this case unless instructed otherwise
Remember to actually send the commands when requested, and send them EXACTLY as they're written, 
with no missing `;` or misplaced `()`.
"""
)


chat_session = model.start_chat()

vosk_model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(vosk_model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8192
)

t_pressed = False
muted = False

engine = pyttsx3.init()
pygame.mixer.init()
engine.setProperty('voice', VOICE_KEY)

speech_channel = pygame.mixer.Channel(1)

def speak(text, rate=170, pitch_factor=0.98):
    def _speak():
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_filename = temp_file.name
        temp_file.close()

        engine.setProperty('rate', rate)
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()

        sound = AudioSegment.from_file(temp_filename, format="wav")
        new_sample_rate = int(sound.frame_rate * pitch_factor)
        pitched_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": new_sample_rate})
        pitched_sound = pitched_sound.set_frame_rate(44100)
        pitched_sound.export(temp_filename, format="wav")

        speech = pygame.mixer.Sound(temp_filename)
        speech_channel.play(speech)

        while speech_channel.get_busy():
            time.sleep(0.1)

    threading.Thread(target=_speak, daemon=True).start()

def fireshots(n):
        for _ in range(n):
            press('o')
            time.sleep(0.7)

def unibeam(n):
    pyautogui.mouseDown(button='right')
    time.sleep(n)
    pyautogui.mouseUp(button='right')

def on_press(key):
    global t_pressed
    if isinstance(key, KeyCode) and key.char == 't':
        t_pressed = True

def on_release(key):
    global t_pressed
    if isinstance(key, KeyCode) and key.char == 't':
        t_pressed = False

listener = Listener(on_press=on_press, on_release=on_release)
listener.start()

def save_clip():
    try:
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()
        ws.call(requests.StartReplayBuffer())
        ws.call(requests.SaveReplayBuffer())
        ws.disconnect()
    except Exception:
        pass

def start_recording():
    try:
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()
        ws.call(requests.StartRecording())
        ws.disconnect()
        print("Recording Started!")
    except Exception as e:
        print("Failed to start recording:", e)

def stop_recording():
    try:
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()
        ws.call(requests.StopRecording())
        ws.disconnect()
        print("Recording Stopped!")
    except Exception as e:
        print("Failed to stop recording:", e)

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

def music_thread(folder):
    global music_queue, current_song_index, playing
    music_folder = os.path.join(MUSIC_DIR, folder)

    if os.path.exists(music_folder):
        music_queue = [os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav'))]

        if music_queue:
            pygame.mixer.init()
            playing = True
            current_song_index = 0
            while playing:
                pygame.mixer.music.load(music_queue[current_song_index])
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() > 0:
                    pygame.time.wait(1000)
                    if not playing:
                        return

                current_song_index = (current_song_index + 1) % len(music_queue)
    else:
        print("Music folder doesn't seem to exist, Make sure the directory is correct")

def play_music(folder):
    threading.Thread(target=music_thread, args=(folder,), daemon=True).start()

def toggle_pause():
    global playing
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        playing = False
    else:
        pygame.mixer.music.unpause()
        playing = True

def skip_song():
    global current_song_index, music_queue
    if music_queue:
        pygame.mixer.music.stop()
        current_song_index = (current_song_index + 1) % len(music_queue)
        pygame.mixer.music.load(music_queue[current_song_index])
        pygame.mixer.music.play()

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

def process_audio():
    audio_frames = []
    while t_pressed:
        data = stream.read(4096, exception_on_overflow=False)
        audio_frames.append(data)
    if audio_frames:
        for frame in audio_frames:
            recognizer.AcceptWaveform(frame)
        return recognizer.FinalResult()[14:-3]
    return None

def process_command(response):
    sound_effects = []
    clean_response = []
    i = 0
    length = len(response)

    while i < length:
        if response[i:i+4] == "prs(":
            j = response.find(")", i)
            if j != -1:
                add_task(press, response[i+4:j])
                i = j
        elif response[i:i+4] == "msg(":
            j = response.find(")", i)
            if j != -1:
                content = response[i+4:j].strip()
                if content.endswith("true"):
                    add_task(chat, content[:-4].strip(), True)
                elif content.endswith("false"):
                    add_task(chat, content[:-5].strip(), False)
                i = j
        elif response[i:i+4] == "ply(":
            j = response.find(")", i)
            if j != -1:
                sound_effects.append(response[i+4:j])
                i = j
        elif response[i:i+4] == "dly(":
            j = response.find(")", i)
            if j != -1:
                add_task(time.sleep, float(response[i+4:j]))
                i = j
        elif response[i:i+4] == "vls(":
            j = response.find(")", i)
            if j != -1:
                add_task(set_volume, int(response[i+4:j]))
                i = j
        elif response[i:i+4] == "fre(":
            j = response.find(")", i)
            if j != -1:
                add_task(fireshots, int(response[i+4:j]))
                i = j
        elif response[i:i+4] == "uni(":
            j = response.find(")", i)
            if j != -1:
                add_task(unibeam, float(response[i+4:j]))
                i = j
        elif response[i:i+4] == "ext;":
            exit()
        elif response[i:i+4] == "frk;":
            add_task(freaky)
            i += 3
        elif response[i:i+4] == "lck;":
            add_task(insta_lock)
            i += 3
        elif response[i:i+4] == "clp;":
            add_task(save_clip)
            i += 3
        elif response[i:i+4] == "str;":
            add_task(start_recording)
            i += 3
        elif response[i:i+4] == "spr;":
            add_task(stop_recording)
            i += 3
        elif response[i:i+4] == "mut;":
            toggle_mute()
            i += 3
        elif response[i:i+4] == "vld;":
            add_task(change_volume, -10)
            i += 3
        elif response[i:i+4] == "vlu;":
            add_task(change_volume, 10)
            i += 3
        elif response[i:i+4] == "mpl(":
            j = response.find(")", i)
            if j != -1:
                play_music(response[i+4:j])
                i = j
        elif response[i:i+4] == "mps;":
            toggle_pause()
            i += 3
        elif response[i:i+4] == "skp;":
            skip_song()
            i += 3
        else:
            clean_response.append(response[i])
        
        i += 1

    return "".join(clean_response).strip(), sound_effects

def sendtojarvis(message):
    response = chat_session.send_message(message)
    cleaned_response, sound_effects = process_command(response.text)
    
    print("Jarvis:", response.text)
    speak(cleaned_response)
    for sound in sound_effects:
        play_sound(sound)

try:
    print("Press and hold T to communicate with Jarvis using your default Microphone")
    while True:
        if t_pressed:
            print("Listening...")
            transcribed_text = process_audio()
            if transcribed_text:
                print("You said:", transcribed_text)
                sendtojarvis(transcribed_text)
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    mic.terminate()
