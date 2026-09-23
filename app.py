from flask import Flask, request, jsonify, render_template, Response
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    if not user_message:
        return jsonify({"reply": "I didn't catch that."})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are Jarvis, a helpful and concise voice assistant. Keep replies short and conversational, since they'll be spoken out loud."},
            {"role": "user", "content": user_message},
        ],
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/speak", methods=["POST"])
def speak():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    audio_response = client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",
        voice="autumn",
        input=text,
        response_format="wav",
    )
    return Response(audio_response.read(), mimetype="audio/wav")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
