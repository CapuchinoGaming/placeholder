print("------------------------------------------------------------")
print("> Python Script is running :D")
from google import genai
from google.genai import types
import wave

# Global variables
API_KEY = "AIzaSyCjLWCS3pluFJUJD4znbqCNFkX2O5l2QSU"
MODEL_ID = "gemini-2.5-flash-preview-tts"

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    print("> Setting up out.wav")
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    print("> Finished setting up wave file")

# Only run this block for Gemini Developer API
client = genai.Client(api_key=API_KEY)
print("> Gemini client started")

response = client.models.generate_content(
    model=MODEL_ID,
    contents='Say cheerfully: Hello World.',
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
print("> File saved")

# Close the sync client to release resources.
client.close()
print("> End script")