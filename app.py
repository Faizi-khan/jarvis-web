from flask import Flask, request, jsonify, render_template, Response
from groq import Groq
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

SYSTEM_PROMPT = "You are Jarvis, a sharp, loyal, concise voice assistant inspired by Tony Stark's AI. Keep replies short and conversational since they'll be spoken aloud. A little witty, always helpful."

def get_recent_history(limit=10):
    if not supabase:
        return []
    try:
        res = supabase.table("messages").select("role,content").order("id", desc=True).limit(limit).execute()
        rows = list(reversed(res.data))
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception:
        return []

def get_memories():
    if not supabase:
        return []
    try:
        res = supabase.table("memories").select("content").order("id", desc=True).limit(20).execute()
        return [r["content"] for r in res.data]
    except Exception:
        return []

def save_message(role, content):
    if not supabase:
        return
    try:
        supabase.table("messages").insert({"role": role, "content": content}).execute()
    except Exception:
        pass

def maybe_save_memory(user_message, reply):
    if not supabase:
        return
    try:
        extraction = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "Extract one short durable fact worth remembering long-term from this exchange (name, preference, project, goal, etc). If nothing durable, reply exactly NONE."},
                {"role": "user", "content": f"User said: {user_message}\nAssistant replied: {reply}"},
            ],
        )
        fact = extraction.choices[0].message.content.strip()
        if fact and fact.upper() != "NONE":
            supabase.table("memories").insert({"content": fact}).execute()
    except Exception:
        pass

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "I didn't catch that."})

    history = get_recent_history()
    memories = get_memories()

    memory_block = ""
    if memories:
        memory_block = "Known facts about the user:\n" + "\n".join(f"- {m}" for m in memories)

    messages = [{"role": "system", "content": SYSTEM_PROMPT + ("\n\n" + memory_block if memory_block else "")}]
    messages += history
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
    )
    reply = response.choices[0].message.content

    save_message("user", user_message)
    save_message("assistant", reply)
    maybe_save_memory(user_message, reply)

    return jsonify({"reply": reply})

@app.route("/speak", methods=["POST"])
def speak():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        audio_response = client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice="daniel",
            input=text,
            response_format="wav",
        )
        return Response(audio_response.read(), mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
