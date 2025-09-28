print("------------------------------------------------------------")
print("> Python Script is running :D")
from google import genai
from google.genai import types
import wave

# Global variables
API_KEY = "AIzaSyCjLWCS3pluFJUJD4znbqCNFkX2O5l2QSU"
MODEL_ID = "gemini-2.5-flash-preview-tts"
text_prompt = 'Say cheerfully: Hello World.'

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    print("> Setting up out.wav")
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    print("> Finished setting up out.wav")

# Only run this block for Gemini Developer API
client = genai.Client(api_key=API_KEY)
print("> Gemini client started")

'''
response = client.models.generate_content(
    model=MODEL_ID,
    contents=text_prompt,
    config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
               voice_name='Kore',
            )
         )
      ),
   )
)
print("> Gemini response generated")

data = response.candidates[0].content.parts[0].inline_data.data

file_name='out.wav'
wave_file(file_name, data) # Saves the file to current directory
print("> Audio saved into out.wav")
'''
# --- Play out.wav from Python (no PHP) ---
import sys, os, subprocess, platform

wav_path = os.path.abspath("out.wav")

def try_simpleaudio():
    try:
        import simpleaudio as sa  # pip install simpleaudio
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        return True
    except Exception:
        return False

def try_platform_player():
    try:
        system = platform.system()
        if system == "Darwin":     # macOS
            return subprocess.call(["afplay", wav_path]) == 0
        elif system == "Windows":
            import winsound
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
            return True
        else:                      # Linux/*nix
            # Try common CLI players in order
            for player in (["ffplay", "-nodisp", "-autoexit", wav_path],
                           ["aplay", wav_path],
                           ["paplay", wav_path]):
                try:
                    if subprocess.call(player, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                        return True
                except FileNotFoundError:
                    continue
        return False
    except Exception:
        return False

played = try_simpleaudio() or try_platform_player()
print("> Played locally from Python" if played else "> Could not autoplay locally (no suitable player found)")
# --- end playback block ---

# Close the sync client to release resources.
client.close()
print("> End script")