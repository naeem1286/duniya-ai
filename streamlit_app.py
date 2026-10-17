
import os
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Duniya AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Premium design ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Nastaliq+Urdu:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b1020;
    --panel: #111a2b;
    --border: #283650;
    --text: #f1f5ff;
    --muted: #a8b4cb;
    --blue: #82b4ff;
    --purple: #b9a0ff;
    --urdu: "Jameel Noori Nastaleeq", "Noto Nastaliq Urdu", serif;
    --latin: "Inter", Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at top, #172448 0%, transparent 48%),
        var(--bg);
    color: var(--text);
    font-family: var(--latin);
}

[data-testid="stHeader"] {
    background: rgba(11,16,32,.88);
}

[data-testid="stSidebar"] {
    background: #0a0f1c;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

.brand {
    text-align: center;
    padding: 30px 8px 24px;
}

.brand-icon {
    font-size: 54px;
    line-height: 1.5;
}

.brand h1 {
    font-family: var(--latin);
    font-size: clamp(34px, 5vw, 54px);
    font-weight: 700;
    letter-spacing: -1.5px;
    background: linear-gradient(90deg, #7dc8ff, #b8a1ff, #f0b5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.brand p {
    font-family: var(--urdu);
    font-size: 18px;
    line-height: 2.4;
    color: var(--muted);
    margin-top: 12px;
}

.welcome {
    font-family: var(--urdu);
    direction: rtl;
    text-align: center;
    font-size: 23px;
    line-height: 2.5;
    color: #e3eaff;
    padding: 14px 0 24px;
}

div[data-testid="stChatMessage"] {
    background: rgba(17,26,43,.94);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 20px 22px;
    margin: 14px 0;
    box-shadow: 0 8px 26px rgba(0,0,0,.13);
}

div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    color: var(--text);
}

div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li {
    font-family: var(--urdu);
    font-size: 19px;
    font-weight: 400;
    line-height: 2.35;
    text-align: start;
    unicode-bidi: plaintext;
    overflow-wrap: anywhere;
}

div[data-testid="stChatMessage"] h1,
div[data-testid="stChatMessage"] h2,
div[data-testid="stChatMessage"] h3 {
    font-family: var(--urdu);
    color: var(--blue);
    line-height: 2.1;
}

div[data-testid="stChatMessage"] strong {
    color: #c6b6ff;
    font-weight: 700;
}

div[data-testid="stChatMessage"] pre,
div[data-testid="stChatMessage"] code {
    font-family: Consolas, "Courier New", monospace;
    direction: ltr;
    text-align: left;
    line-height: 1.7;
}

[data-testid="stChatInput"] {
    border: 1px solid #425475;
    border-radius: 18px;
    background: #10192a;
}

[data-testid="stChatInput"] textarea {
    font-family: var(--urdu);
    font-size: 18px;
    line-height: 2.2;
    color: #ffffff;
}

.stButton button {
    min-height: 44px;
    border: 1px solid #39496b;
    border-radius: 13px;
    color: #f4f6ff;
    background: linear-gradient(110deg, #182d50, #29234c);
    font-family: var(--urdu);
    font-size: 16px;
    transition: border-color .2s, background .2s;
}

.stButton button:hover {
    border-color: #a99aff;
    color: white;
    background: #26365a;
}

[data-testid="stCaptionContainer"] {
    color: var(--muted);
}

.footer {
    text-align: center;
    color: #8290a9;
    font-family: var(--latin);
    font-size: 12px;
    padding: 26px 8px 12px;
}

@media (max-width: 700px) {
    .brand { padding-top: 18px; }
    .brand p { font-size: 16px; }
    div[data-testid="stChatMessage"] { padding: 15px; }
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li {
        font-size: 18px;
        line-height: 2.25;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------- API settings ----------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

api_key = api_key.strip() if api_key else ""

# ---------- Conversation state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🌍 Duniya AI")
    st.caption("آپ کا اپنا AI اسسٹنٹ")

    if st.button("＋  نئی چیٹ", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.divider()
    st.markdown("### ✨ خصوصیات")
    st.markdown("""
    اردو، ہندی اور انگریزی میں مدد

    سوالات کے جواب

    لکھنے اور پڑھنے میں مدد

    پروگرامنگ اور کوڈنگ
    """)

    st.divider()
    st.caption("Duniya AI • آپ کا ڈیجیٹل ساتھی")


# ---------- Welcome screen ----------
if not st.session_state.messages:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">🌍</div>
        <h1>Duniya AI</h1>
        <p>آپ کا اپنا AI اسسٹنٹ — اردو، ہندی اور انگریزی میں</p>
    </div>
    <div class="welcome">السلام علیکم! آج میں آپ کی کیا مدد کر سکتا ہوں؟</div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("💡 کچھ نیا سیکھیں", use_container_width=True):
            st.session_state.pending_prompt = "مجھے کوئی نئی چیز آسان الفاظ میں سکھائیں۔"
            st.rerun()

    with c2:
        if st.button("✍️ لکھنے میں مدد", use_container_width=True):
            st.session_state.pending_prompt = "مجھے لکھنے میں مدد کریں۔"
            st.rerun()

    with c3:
        if st.button("💻 کوڈنگ میں مدد", use_container_width=True):
            st.session_state.pending_prompt = "مجھے پروگرامنگ آسان الفاظ میں سمجھائیں۔"
            st.rerun()

else:
    st.markdown("### 💬 گفتگو")


# ---------- Display previous messages ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------- API key check ----------
if not api_key:
    st.warning(
        "Gemini API Key موجود نہیں۔ "
        "Streamlit Settings → Secrets میں GEMINI_API_KEY چیک کریں۔"
    )
    st.stop()


# ---------- Chat ----------
prompt = st.chat_input("Duniya AI سے کچھ بھی پوچھیں...")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

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
                    model="gemini-2.5-flash",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Duniya AI, a helpful and honest assistant. "
                                "Reply in the user's language, including Urdu, Hindi, "
                                "and English. Use clear formatting, short paragraphs, "
                                "helpful headings and lists when appropriate. "
                                "For Urdu, use natural and respectful language."
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
                st.caption("خرابی کی تفصیل:")
                st.code(str(e))

st.markdown(
    '<div class="footer">AI کے جوابات میں غلطی ممکن ہے؛ اہم معلومات کی تصدیق کریں۔</div>',
    unsafe_allow_html=True
)

 
