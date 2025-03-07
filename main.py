import time
from input_listener import is_t_pressed
from audio import process_audio, speak, close_audio
from chat import send_to_jarvis
from commands import process_command, play_sound
from config import INPUT_START_KEY

def main():
    print(f"Press and hold {INPUT_START_KEY} to communicate with Jarvis using your default microphone")
    try:
        while True:
            if is_t_pressed():
                print("Listening...")
                transcribed_text = process_audio(is_t_pressed)
                if transcribed_text:
                    print("You said:", transcribed_text)
                    send_to_jarvis(transcribed_text, process_command, speak, play_sound)
    except KeyboardInterrupt:
        pass
    finally:
        close_audio()

if __name__ == '__main__':
    main()
