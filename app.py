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
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


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

        return jsonify({"result": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
