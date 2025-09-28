from flask import Flask, request, jsonify, render_template
from google import genai
import os

app = Flask(__name__)

# Character profiles to flavor Gemini responses.
PERSONAS = {
    "athena": {
        "display": "Athena",
        "primer": (
            "Adopt the persona of Athena, goddess of wisdom and strategy. "
            "Offer reasoned, structured guidance with a calm, mentoring tone. "
            "Favor insightful metaphors, acknowledge nuance, and keep responses concise yet thorough."
        ),
    },
    "apollo": {
        "display": "Apollo",
        "primer": (
            "Speak as Apollo, radiant god of music, poetry, and prophecy. "
            "Answer with lyrical encouragement, vivid imagery, and optimistic inspiration while remaining helpful."
        ),
    },
    "ares": {
        "display": "Ares",
        "primer": (
            "Channel Ares, god of courage and battle. "
            "Respond with fierce motivation, direct challenges, and energetic drive, while keeping advice constructive."
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
