import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Keep API keys on the server. Never place them in browser JavaScript.
API_KEY = os.getenv("AI_API_KEY", "")
BASE_URL = os.getenv("AI_BASE_URL", "").strip() or None
MODEL = os.getenv("AI_MODEL", "gpt-4.1-mini")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL) if API_KEY else None

SYSTEM_PROMPT = """
You are Duniya AI, a helpful, honest, safety-conscious assistant.
Reply in the language the user uses (including Urdu, Hindi, and English).
Be clear about uncertainty; never invent facts, sources, or capabilities.
Do not provide actionable instructions that facilitate serious wrongdoing,
violence, cyber abuse, fraud, or other illegal harm. Where possible, redirect
to lawful, safe, educational alternatives. You may answer benign questions
about law, safety, prevention, and general awareness.
Do not claim you have browsed the internet, created files, deployed websites,
or performed real-world actions unless a connected tool actually did so.
Protect privacy and do not ask for passwords, API keys, or unnecessary personal data.
"""

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/status")
def status():
    return jsonify({"configured": bool(client), "model": MODEL})

@app.post("/api/chat")
def chat():
    if not client:
        return jsonify({
            "error": "Duniya AI ابھی AI سروس سے منسلک نہیں ہے۔ ویب سائٹ کے سرور پر AI_API_KEY سیٹ کرنے کے بعد چیٹ کام کرے گی۔"
        }), 503

    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "براہِ کرم اپنا سوال لکھیں۔"}), 400

    # Keep requests bounded and accept only user/assistant text messages.
    cleaned = []
    for item in messages[-16:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            continue
        content = content.strip()[:6000]
        if content:
            cleaned.append({"role": role, "content": content})

    if not cleaned or cleaned[-1]["role"] != "user":
        return jsonify({"error": "براہِ کرم ایک نیا سوال بھیجیں۔"}), 400

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + cleaned,
            temperature=0.4,
            max_tokens=1400,
        )
        answer = response.choices[0].message.content or "معذرت، جواب تیار نہیں ہو سکا۔"
        return jsonify({"reply": answer})
    except Exception:
        app.logger.exception("AI provider request failed")
        return jsonify({
            "error": "AI سروس سے رابطہ نہیں ہو سکا۔ سرور کی API key، model name، اور provider settings چیک کریں۔"
        }), 502

if __name__ == "__main__":
    # Local testing only. Production hosting should run a production server.
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
