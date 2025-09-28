from flask import Flask, request, jsonify, render_template
from google import genai
import os

app = Flask(__name__)

# Character profiles to flavor Gemini responses.
PERSONAS = {
    "eurydice": {
        "display": "Eurydice",
        "primer": (
            "Adopt the voice of Eurydice, the nymph who twice crossed the veil of the underworld. "
            "Speak with quiet strength and lyrical hope, referencing life with Orpheus and your time below. "
            "When you recount your own story, feel free to go in depth but deliver it in segments of three to four sentences, ending each segment by asking if the listener would like to hear more. "
            "For every other topic, keep your guidance to two or three sentences while offering steady reassurance drawn from hardship."
            "Keep sentences brief, try to limit yourself to 10 words."
        ),
    },
    "pandora": {
        "display": "Pandora",
        "primer": (
            "Respond as Pandora, the curious bearer of the jar of sorrows. "
            "Blend inquisitive warmth with the lessons learned from unleashing trials, always leaving room for hope. "
            "Share your myth in richer detail when asked, but pause every three to four sentences to ask if they would like you to continue. "
            "Keep all other replies to two or three sentences so the conversation can flow."
            "Keep sentences brief, try to limit yourself to 10 words."
        ),
    },
    "medusa": {
        "display": "Medusa",
        "primer": (
            "Channel Medusa, once priestess and now guardian crowned with serpents. "
            "Speak with fierce honesty and protective strength, reclaiming your story from those who twisted it. "
            "When narrating your past, let the tale unfold in deeper layers, but stop every three to four sentences to ask whether the seeker wishes to hear more before continuing. "
            "For other discussions, respond in two or three sentences while staying concise and empowering."
            "Keep sentences brief, try to limit yourself to 10 words."
        ),
    },
}

# Initialize Gemini client with API key
client = genai.Client(api_key="AIzaSyCmr26qMYKYEOJxmyCRl3FtJjSQ6--frNg")


@app.route("/")
def index():
    return render_template("website copy.html")  # serves our webpage


@app.route("/prompt", methods=["POST"])
def prompt_gemini():
    data = request.get_json()
    user_prompt = data.get("prompt", "").strip()
    persona_key = (data.get("persona") or "").lower()

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    persona = PERSONAS.get(persona_key)
    composed_prompt = user_prompt

    if persona:
        composed_prompt = (
            f"{persona['primer']}\n\n"
            f"Question from the seeker: {user_prompt}\n"
            f"Answer as {persona['display']} and stay firmly in character."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=composed_prompt
        )

        candidate = response.candidates[0] if response.candidates else None
        parts = candidate.content.parts if candidate and candidate.content else []
        text = next((part.text for part in parts if getattr(part, "text", None)), "")

        if not text:
            return jsonify({"error": "No response returned from Gemini."}), 502

# -------------------------------------------------- Start of Audio section --------------------------------------------------
        # Import libraries related to audio
        from google.genai import types
        import os, subprocess, platform, time, traceback
        import wave

        # Global variables
        API_KEY = "AIzaSyCmr26qMYKYEOJxmyCRl3FtJjSQ6--frNg"
        TTS_MODEL_ID = "gemini-2.5-flash-preview-tts"
        MALE_VOICE = "charon"
        WOMAN_VOICE = "zephyr"
        WOMAN_VOICE = "kore"
        ORACLE_VOICE = "gacrux"

        # The "text" variable should be provided by Joshuan's Gemini
        prefix = "Say cheerfully: "

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
            print(f"Entered for loop for the {i}th time")
            
            text_prompt = prefix + line

            # Call TTS model
            try:
                tts_response = tts_client.models.generate_content(
                    model=TTS_MODEL_ID,
                    contents=text_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="kore",
                                )
                            )
                        ),
                    ),
                )
                print(f"> Gemini response {i} generated")
            except Exception as e:
                print("Error during TTS generate_content call:", str(e))
                print(traceback.format_exc())
                tts_response = None  # optional: so code after this can check if it's None

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

        # Close the tts_client to release resources.
        tts_client.close()
        print("> End script")

# --------------------------------------------------- End of Audio section ---------------------------------------------------

        return jsonify({"result": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
