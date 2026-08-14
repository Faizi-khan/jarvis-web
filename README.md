# Jarvis 🎙️

A voice-activated AI assistant that runs entirely in the browser — tap the mic, ask a question, and hear Jarvis reply out loud.

## How it works

1. **Speech-to-text**: The browser's built-in SpeechRecognition API converts your voice into text
2. **AI response**: The text is sent to a Flask backend, which calls the [Groq API](https://groq.com) (Llama 3.3 70B) to generate a reply
3. **Text-to-speech**: The reply is spoken back using the browser's SpeechSynthesis API

No native app, no extra audio libraries — just a webpage and an API call.

## Tech stack

- **Backend**: Python, Flask, Groq API
- **Frontend**: HTML, JavaScript (Web Speech API)
- **Environment**: python-dotenv for secrets management

## Running it locally

```bash
git clone https://github.com/Faizi-khan/jarvis-web.git
cd jarvis-web
pip install -r requirements.txt
