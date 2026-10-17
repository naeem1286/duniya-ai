
import os
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Duniya AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Nastaliq+Urdu&display=swap');

.stApp {
    background: linear-gradient(135deg, #0b1020, #111827 55%, #17132d);
    color: #f3f4f6;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: #0a0f1c;
    border-right: 1px solid #263047;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

.hero {
    text-align: center;
    padding: 48px 12px 25px 12px;
}

.logo {
    font-size: 48px;
    margin-bottom: 8px;
}

.hero h1 {
    font-size: clamp(34px, 5vw, 54px);
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #f0abfc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.hero p {
    color: #aab4ca;
    font-size: 16px;
}

div[data-testid="stChatMessage"] {
    background: rgba(30, 41, 59, 0.70);
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
}

[data-testid="stChatInput"] {
    border: 1px solid #475569;
    border-radius: 18px;
    background: #111827;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff;
}

.stButton button {
    border-radius: 12px;
    border: 1px solid #475569;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    font-weight: 600;
    padding: 10px 14px;
    transition: 0.2s;
}

.stButton button:hover {
    border-color: #a78bfa;
    color: white;
}

div[data-testid="stMarkdownContainer"] {
    line-height: 1.8;
}

.urdu {
    font-family: 'Noto Nastaliq Urdu', serif;
    direction: rtl;
    text-align: center;
    color: #cbd5e1;
    line-height: 2.3;
}

.footer {
    text-align: center;
    color: #7f8ba3;
    font-size: 12px;
    padding: 20px 0;
}

</style>
""", unsafe_allow_html=True)

# API key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

api_key = api_key.strip() if api_key else ""

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.markdown("## 🌍 Duniya AI")
    st.caption("آپ کا اپنا AI اسسٹنٹ")

    if st.button("＋  نئی چیٹ", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### ✨ خصوصیات")
    st.markdown("""
    - 💬 سوالات اور جوابات
    - 🌐 اردو، ہندی اور انگریزی
    - 💻 کوڈنگ میں مدد
    - ✍️ لکھنے اور پڑھنے میں مدد
    """)

    st.divider()
    st.caption("Duniya AI • آپ کا ڈیجیٹل ساتھی")

# Main screen
if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <div class="logo">🌍</div>
        <h1>Duniya AI</h1>
        <p>آپ کا اپنا AI اسسٹنٹ — اردو، ہندی اور انگریزی میں</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p class="urdu">السلام علیکم! آج میں آپ کی کیا مدد کر سکتا ہوں؟</p>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💡 ایک نئی چیز سیکھیں", use_container_width=True):
            st.session_state.pending_prompt = "مجھے کوئی نئی اور دلچسپ چیز آسان الفاظ میں سکھائیں۔"
            st.rerun()

    with col2:
        if st.button("✍️ لکھنے میں مدد", use_container_width=True):
            st.session_state.pending_prompt = "مجھے لکھنے میں مدد کریں اور ایک مختصر مثال دیں۔"
            st.rerun()

    with col3:
        if st.button("💻 کوڈنگ میں مدد", use_container_width=True):
            st.session_state.pending_prompt = "مجھے پروگرامنگ آسان الفاظ میں سمجھائیں۔"
            st.rerun()

else:
    st.markdown("## 💬 آپ کی گفتگو")

# Show conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# API key check
if not api_key:
    st.warning("Gemini API Key موجود نہیں۔ Streamlit Settings → Secrets چیک کریں۔")
    st.stop()

# User input
prompt = st.chat_input("Duniya AI سے کچھ بھی پوچھیں...")

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("✨ Duniya AI جواب تیار کر رہا ہے..."):
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    timeout=60.0,
                    max_retries=1
                )

                response = client.chat.completions.create(
                    model="gemini-3.8-flash",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Duniya AI, a helpful and honest assistant. "
                                "Reply in the language the user uses, including Urdu, "
                                "Hindi, and English. Give clear, useful answers."
                            )
                        }
                    ] + st.session_state.messages,
                    max_tokens=1400
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "معذرت، اس وقت جواب نہیں مل سکا۔"

                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error("Duniya AI سے رابطے میں مسئلہ آیا۔")
                st.code(str(e))

st.markdown(
    '<div class="footer">Duniya AI can make mistakes. Important information should be verified.</div>',
    unsafe_allow_html=True
)
 
