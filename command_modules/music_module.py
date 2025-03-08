import os
import pygame
import threading
import time
import random
from config import MUSIC_DIR

pygame.mixer.init()

music_queue = []
current_song_index = 0
playing = False

command_handlers = {
    "skp": lambda _: (skip_song, ()),
    "mps": lambda _: (toggle_pause, ()),
    "mpl": lambda content: (play_music, (content))
}

commands_string = """
 mpl(name)   - Start a music playlist (Playlist1 or Playlist2)  
 mps()        - Pause or resume music  
 skp()        - Skip the current song 
"""

def music_thread(folder):
    global music_queue, current_song_index, playing
    music_folder = os.path.join(MUSIC_DIR, folder)
    if os.path.exists(music_folder):
        music_queue = [os.path.join(music_folder, f) for f in os.listdir(music_folder)
                       if f.endswith(('.mp3', '.wav'))]
        if music_queue:
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
        print("Music folder doesn't exist. Check your config.")

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
