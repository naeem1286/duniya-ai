
import os
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Duniya AI",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 Duniya AI")
st.caption("آپ کا اپنا AI اسسٹنٹ — اردو، ہندی اور انگریزی میں")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    st.warning(
        "Duniya AI کو چلانے کے لیے Gemini API Key درکار ہے۔ "
        "اسے Streamlit Secrets میں محفوظ کریں۔"
    )
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("اپنا سوال یہاں لکھیں...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Duniya AI جواب تیار کر رہا ہے..."):
            try:
                response = client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Duniya AI, a helpful and honest assistant. "
                                "Reply in the language the user uses, including Urdu, "
                                "Hindi, and English. Be clear and accurate."
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

            except Exception:
                st.error(
                    "AI سے رابطہ نہیں ہو سکا۔ API Key، ماڈل یا سروس کی "
                    "ترتیبات چیک کریں۔"
                )
