from flask import Flask, request, jsonify, render_template
from google import genai
import os

app = Flask(__name__)

# Initialize Gemini client with API key
client = genai.Client(api_key="AIzaSyCjLWCS3pluFJUJD4znbqCNFkX2O5l2QSU")

@app.route("/")
def index():
    return render_template("website copy.html")  # serves our webpage

@app.route("/prompt", methods=["POST"])
def prompt_gemini():
    data = request.get_json()
    user_prompt = data.get("prompt", "")

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt
        )

        # Extract text from Gemini’s response
        text = response.candidates[0].content.parts[0].text

# -------------------------------------------------- Start of Audio section --------------------------------------------------
        # Import libraries related to audio
        from google.genai import types
        import os, subprocess, platform, time
        import wave

        # Global variables
        API_KEY = "AIzaSyCjLWCS3pluFJUJD4znbqCNFkX2O5l2QSU"
        TTS_MODEL_ID = "gemini-2.5-flash-preview-tts"
        MALE_VOICE = "charon"
        WOMAN_VOICE = "callirrhoe"

        # The "text" variable should be provided by Joshuan's Gemini
        prefix = "Say cheerfully: "
        text = "This is the first sentence. This is the other sentence. This is the third sentence."

        # Split into sentences, strip whitespace, and remove empty entries
        text_list = [sentence.strip() + "." for sentence in text.split(".") if sentence.strip()]

        # Create a Gemini client for TTS (Text to Speech)
        tts_client = genai.Client(api_key=API_KEY)
        print("> Gemini client started")

        # Function to save PCM data to a wav file
        def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
            print(f"> Setting up {filename}")
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(rate)
                wf.writeframes(pcm)
            print(f"> Finished setting up {filename}")

        # Loop through text_list
        for i, line in enumerate(text_list):
            text_prompt = prefix + line

            # Call TTS model
            tts_response = tts_client.models.generate_content(
                model=TTS_MODEL_ID,
                contents=text_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=MALE_VOICE,
                            )
                        )
                    ),
                ),
            )
            print(f"> Gemini response {i} generated")

            # Extract audio data
            tts_data = tts_response.candidates[0].content.parts[0].inline_data.data

            # Save each file as out0.wav, out1.wav, ...
            file_name = f"out{i}.wav"
            wave_file(file_name, tts_data)
            print(f"> Audio saved into {file_name}")

        # --- Play out.wav from Python (no PHP) ---
        wav_path = os.path.abspath("out.wav")

        # This function takes an audio file, then plays it
        def try_platform_player(filename):
            print("> Running try_platform_player()")
            try:
                system = platform.system()
                if system == "Darwin":     # macOS
                    return subprocess.call(["afplay", filename]) == 0
                elif system == "Windows":
                    import winsound
                    print("> Playing sound")
                    winsound.PlaySound(filename, winsound.SND_FILENAME)
                    print("> Sound was played")
                    return True
                else:                      # Linux/*nix
                    # Try common CLI players in order
                    for player in (["ffplay", "-nodisp", "-autoexit", filename],
                                ["aplay", filename],
                                ["paplay", filename]):
                        try:
                            if subprocess.call(player, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                                return True
                        except FileNotFoundError:
                            continue
                return False
            except Exception:
                return False

        # Loop through all generated wav files
        for i in range(len(text_list)):
            file_name = f"out{i}.wav"
            played = try_platform_player(file_name)
            print(f"> Played {file_name}" if played else f"> Could not autoplay {file_name} (no suitable player found)")
            time.sleep(0.5)  # pause 0.5 seconds before next playback

        # Close the tts_client to release resources.
        tts_client.close()
        print("> End script")

# --------------------------------------------------- End of Audio section ---------------------------------------------------

        return jsonify({"result": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
