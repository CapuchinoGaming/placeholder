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

        # ----------------- Audio section -----------------
        
        from google.genai import types
        import wave

        API_KEY = "AIzaSyCjLWCS3pluFJUJD4znbqCNFkX2O5l2QSU"
        TTS_MODEL_ID = "gemini-2.5-flash-preview-tts"
        prefix = 'Say cheerfully: '
        text_prompt = prefix + text

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
        tts_client = genai.Client(api_key=API_KEY)
        print("> Gemini client started")

        tts_response = tts_client.models.generate_content(
            model=TTS_MODEL_ID,
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

        tts_data = tts_response.candidates[0].content.parts[0].inline_data.data

        file_name='out.wav'
        wave_file(file_name, tts_data) # Saves the file to current directory
        print("> Audio saved into out.wav")

        # --- Play out.wav from Python (no PHP) ---
        import sys, os, subprocess, platform

        wav_path = os.path.abspath("out.wav")

        def try_platform_player():
            print("> Running try_platform_player()")
            try:
                system = platform.system()
                if system == "Darwin":     # macOS
                    return subprocess.call(["afplay", wav_path]) == 0
                elif system == "Windows":
                    import winsound
                    print("> Playing sound")
                    winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                    print("> Sound was played")
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

        played = try_platform_player()
        print("> Played locally from Python" if played else "> Could not autoplay locally (no suitable player found)")
        # --- end playback block ---

        # Close the sync client to release resources.
        tts_client.close()
        print("> End script")

        return jsonify({"result": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
