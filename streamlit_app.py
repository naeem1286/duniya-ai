
import os
import streamlit as st
from openai import OpenAI

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Duniya AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DESIGN AND FONTS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Nastaliq+Urdu&display=swap');

:root {
    --bg: #0b1020;
    --panel: #111827;
    --border: #334155;
    --text: #f8fafc;
    --muted: #cbd5e1;
    --blue: #93c5fd;
    --purple: #c4b5fd;
    --urdu: "Jameel Noori Nastaleeq", "Noto Nastaliq Urdu", serif;
    --latin: "Inter", Arial, sans-serif;
}

/* Main page */
.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: var(--latin), var(--urdu);
}

[data-testid="stHeader"] {
    background: rgba(11, 16, 32, 0.96);
}

[data-testid="stAppViewContainer"] {
    background: var(--bg);
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* General text */
h1, h2, h3, p, label, li {
    color: var(--text);
}

h1, h2, h3 {
    font-family: var(--latin), var(--urdu);
}

.stMarkdown, [data-testid="stCaptionContainer"] {
    color: var(--muted);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0e1728;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

[data-testid="stSidebar"] .stMarkdown {
    line-height: 1.9;
}

/* All buttons */
.stButton > button {
    background: #17243a;
    color: #ffffff !important;
    border: 1px solid #3b4d6b;
    border-radius: 12px;
    min-height: 44px;
    font-family: var(--urdu), var(--latin);
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #243957;
    border-color: #93c5fd;
    color: #ffffff !important;
}

/* Chat input container */
[data-testid="stChatInput"] {
    background: #111827 !important;
    border: 1px solid #64748b !important;
    border-radius: 18px !important;
    box-shadow: 0 5px 22px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

/* Typed text */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background: #111827 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    font-family: "Jameel Noori Nastaleeq",
                 "Noto Nastaliq Urdu", serif !important;
    font-size: 19px !important;
    line-height: 2.1 !important;
    opacity: 1 !important;
}

/* Placeholder text */
[data-testid="stChatInput"] textarea::placeholder {
    color: #cbd5e1 !important;
    -webkit-text-fill-color: #cbd5e1 !important;
    opacity: 1 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #111827;
    border: 1px solid #26354d;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}

[data-testid="stChatMessage"] p {
    color: #f8fafc;
    font-family: "Jameel Noori Nastaleeq",
                 "Noto Nastaliq Urdu", "Inter", sans-serif;
    font-size: 18px;
    line-height: 2;
}

/* Hero section */
.hero {
    background: linear-gradient(135deg, #17243e, #252044);
    border: 1px solid #3b4b70;
    border-radius: 24px;
    padding: 30px 24px;
    margin-bottom: 24px;
    text-align: center;
}

.hero-title {
    color: #ffffff;
    font-family: "Inter", sans-serif;
    font-size: clamp(32px, 5vw, 48px);
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 8px;
}

.hero-subtitle {
    color: #dbeafe;
    font-family: "Jameel Noori Nastaleeq",
                 "Noto Nastaliq Urdu", serif;
    font-size: 23px;
    line-height: 2;
}

.hero-note {
    color: #cbd5e1;
    font-size: 14px;
    margin-top: 8px;
}

/* Footer */
.footer {
    color: #94a3b8;
    font-size: 12px;
    text-align: center;
    margin-top: 35px;
    padding: 12px;
}

/* Mobile layout */
@media (max-width: 640px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 24px 12px;
    }

    [data-testid="stChatMessage"] p {
        font-size: 17px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- API KEY ----------------
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

api_key = api_key.strip() if api_key else ""

# ---------------- CHAT MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🌍 Duniya AI")
    st.caption("آپ کا اپنا AI اسسٹنٹ")

    if st.button("＋ نئی چیٹ", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.divider()

    st.markdown("### ✨ خصوصیات")
    st.markdown("""
    - اردو، ہندی اور انگریزی میں گفتگو
    - سوالات کے جواب
    - لکھنے اور سیکھنے میں مدد
    - پروگرامنگ اور کوڈنگ میں مدد
    """)

    st.divider()
    st.caption("Duniya AI • آپ کا ڈیجیٹل ساتھی")

# ---------------- WELCOME SCREEN ----------------
if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <div class="hero-title">🌍 Duniya AI</div>
        <div class="hero-subtitle">
            خوش آمدید! آج آپ کیا سیکھنا چاہتے ہیں؟
        </div>
        <div class="hero-note">
            اردو، ہندی یا انگریزی میں اپنا سوال لکھیں۔
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💡 کچھ نیا سیکھیں", use_container_width=True):
            st.session_state.pending_prompt = (
                "مجھے کوئی نئی چیز آسان الفاظ میں سکھائیں۔"
            )
            st.rerun()

    with col2:
        if st.button("✍️ لکھنے میں مدد", use_container_width=True):
            st.session_state.pending_prompt = (
                "مجھے لکھنے میں مدد کریں۔"
            )
            st.rerun()

    with col3:
        if st.button("💻 کوڈنگ میں مدد", use_container_width=True):
            st.session_state.pending_prompt = (
                "مجھے پروگرامنگ آسان الفاظ میں سمجھائیں۔"
            )
            st.rerun()

else:
    st.markdown("### 💬 آپ کی گفتگو")

# ---------------- SHOW CHAT HISTORY ----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHECK API KEY ----------------
if not api_key:
    st.error("Gemini API Key موجود نہیں ہے۔")
    st.info(
        "Streamlit میں اپنی ایپ کھولیں، "
        "Settings → Secrets میں جائیں اور "
        "GEMINI_API_KEY چیک کریں۔"
    )
    st.stop()

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Duniya AI سے کچھ بھی پوچھیں...")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

# ---------------- GENERATE RESPONSE ----------------
if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("✨ Duniya AI جواب تیار کر رہا ہے..."):
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url=(
                        "https://generativelanguage.googleapis.com/"
                        "v1beta/openai/"
                    ),
                    timeout=60.0,
                    max_retries=1
                )

                response = client.chat.completions.create(
                   model="gemini-2.5-flash",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Duniya AI, a helpful and honest "
                                "assistant. Reply in the user's language, "
                                "including Urdu, Hindi, and English. "
                                "Use clear formatting and simple language. "
                                "For Urdu, use natural and respectful "
                                "language. Never claim certainty when "
                                "you are unsure."
                            )
                        }
                    ] + st.session_state.messages,
                    max_tokens=1400
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "معذرت، اس وقت جواب نہیں مل سکا۔"

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error("Duniya AI سے رابطے میں مسئلہ آیا۔")
                st.caption("خرابی کی تفصیل:")
                st.code(str(e))

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
AI کے جوابات میں غلطی ممکن ہے؛ اہم معلومات کی تصدیق کریں۔
</div>
""", unsafe_allow_html=True)


 
