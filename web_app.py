import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are Lead Hunter AI, a sharp B2B sales strategist for the Nigerian market "
    "(Abuja: Maitama, Wuse, Utako, Guzape, etc.). Your users are ambitious professionals, "
    "service providers, and real estate entrepreneurs. "
    "Give direct, actionable answers only. Maximum 3 short steps or points. "
    "Include ONE ready-to-use pitch line or script snippet, no more. "
    "Keep the entire response under 150 words. No long intros, no restating the question, "
    "no multiple sections or headers. Get straight to the strategy."
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please send a message."}), 400
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"{SYSTEM_PROMPT}\n\nUser Request: {user_message}"
        )
        reply = response.text
    except Exception as e:
        reply = f"Error: {str(e)}"
    return jsonify({"reply": reply})

@app.route("/", methods=["GET"])
def home():
    return "Lead Hunter AI web service is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
