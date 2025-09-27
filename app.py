from flask import Flask, request, jsonify, render_template
from google import genai
import os

app = Flask(__name__)

# Initialize Gemini client with API key
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
        return jsonify({"result": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
