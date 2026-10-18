import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from google import genai
from google.genai import types

# ---------------- SETTINGS ----------------
st.set_page_config(
    page_title="Duniya AI",
    page_icon="🌍",
    layout="wide"
)

CHAT_MODEL = "gemini-3.8-flash"
IMAGE_MODEL = "gemini-nano-banana-2.1"

# ---------------- DESIGN ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Nastaliq+Urdu&display=swap');

:root {
    --urdu: "Jameel Noori Nastaleeq", "Noto Nastaliq Urdu", serif;
    --latin: "Inter", Arial, sans-serif;
}

.stApp {
    background: #0b1020;
    color: #f8fafc;
    font-family: var(--latin), var(--urdu);
}

[data-testid="stHeader"] {
    background: #0b1020;
}

.block-container {
    max-width: 1100px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #10192a;
    border-right: 1px solid #334155;
}

h1, h2, h3, p, label, li {
    color: #f8fafc;
}

.hero {
    background: linear-gradient(135deg, #17243e, #30234b);
    border: 1px solid #3b4b70;
    border-radius: 22px;
    padding: 26px 18px;
    margin-bottom: 20px;
    text-align: center;
}

.hero-title {
    font-family: var(--latin);
    font-size: 38px;
    font-weight: 800;
    color: white;
}

.hero-subtitle {
    font-family: var(--urdu);
    font-size: 22px;
    line-height: 2.1;
    color: #e2e8f0;
}

.stButton > button,
.stDownloadButton > button {
    background: #1c2b43;
    color: #ffffff !important;
    border: 1px solid #475b79;
    border-radius: 12px;
    min-height: 42px;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #2b4161;
    border-color: #93c5fd;
    color: white !important;
}

/* Fix typing box: dark background, visible white text */
[data-testid="stChatInput"] {
    background-color: #111827 !important;
    border: 1px solid #64748b !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background-color: #111827 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    font-family: var(--urdu) !important;
    font-size: 18px !important;
    line-height: 2.1 !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #cbd5e1 !important;
    -webkit-text-fill-color: #cbd5e1 !important;
    opacity: 1 !important;
}

[data-testid="stChatMessage"] {
    background: #111827;
    border: 1px solid #283650;
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 10px;
}

[data-testid="stChatMessage"] p {
    color: #ffffff;
    font-family: var(--urdu), var(--latin);
    font-size: 17px;
    line-height: 2;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: #111827 !important;
    color: #ffffff !important;
}

.footer {
    color: #94a3b8;
    text-align: center;
    font-size: 12px;
    padding-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API KEY ----------------
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY", "")

API_KEY = API_KEY.strip() if API_KEY else ""

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

if "edited_image" not in st.session_state:
    st.session_state.edited_image = None

# ---------------- CLIENT ----------------
def get_client():
    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY نہیں ملی۔ Streamlit Settings → Secrets چیک کریں۔"
        )
    return genai.Client(api_key=API_KEY)


# ---------------- IMAGE HELPERS ----------------
def image_to_bytes(image, fmt="PNG"):
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def load_uploaded_image(uploaded):
    if uploaded is None:
        return None
    image = Image.open(uploaded)
    return ImageOps.exif_transpose(image).convert("RGB")


def make_font(font_upload, size):
    if font_upload is not None:
        try:
            return ImageFont.truetype(
                io.BytesIO(font_upload.getvalue()), size=size
            )
        except Exception:
            pass

    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def fit_image(image, width, height, mode):
    if mode == "Crop / Fill":
        return ImageOps.fit(
            image, (width, height),
            method=Image.Resampling.LANCZOS
        )

    resized = ImageOps.contain(
        image, (width, height),
        method=Image.Resampling.LANCZOS
    )

    canvas = Image.new("RGB", (width, height), "#101827")
    x = (width - resized.width) // 2
    y = (height - resized.height) // 2
    canvas.paste(resized, (x, y))
    return canvas


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🌍 Duniya AI")
    st.caption("آپ کا اپنا AI اسسٹنٹ")

    if st.button("＋ نئی چیٹ", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### ✨ آپ کیا کر سکتے ہیں؟")
    st.markdown("""
    - AI سے سوال پوچھیں
    - تصویر اپ لوڈ کرکے سمجھیں
    - تصویر کا سائز بدلیں
    - YouTube بینر بنائیں
    - تصویر پر متن لکھیں
    - نئی AI تصویر بنانے کی کوشش کریں
    """)
    st.divider()
    st.caption("مفت ٹولز + دستیاب AI API")

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <div class="hero-title">🌍 Duniya AI</div>
    <div class="hero-subtitle">
        آپ کا اپنا ذہین اسسٹنٹ — چیٹ، تصاویر اور ڈیزائن
    </div>
</div>
""", unsafe_allow_html=True)

chat_tab, editor_tab, generate_tab = st.tabs([
    "💬 AI چیٹ",
    "🖼️ تصویر اور بینر ایڈیٹر",
    "✨ نئی AI تصویر"
])

# ==================================================
# TAB 1: CHAT AND IMAGE UNDERSTANDING
# ==================================================
with chat_tab:
    st.subheader("AI سے بات کریں")
    st.caption("اردو، ہندی یا انگریزی میں سوال لکھیں۔")

    chat_image = st.file_uploader(
        "سوال کے ساتھ تصویر بھی اپ لوڈ کر سکتے ہیں",
        type=["png", "jpg", "jpeg", "webp"],
        key="chat_image"
    )

    if chat_image:
        st.image(chat_image, caption="آپ کی اپ لوڈ کردہ تصویر", width=300)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Duniya AI سے کچھ بھی پوچھیں...")

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)
            if chat_image:
                st.image(chat_image, width=250)

        with st.chat_message("assistant"):
            with st.spinner("جواب تیار ہو رہا ہے..."):
                try:
                    client = get_client()
                    contents = []

                    # Include previous text messages as conversation history.
                    for item in st.session_state.messages[:-1]:
                        contents.append(
                            types.Content(
                                role=item["role"],
                                parts=[types.Part(text=item["content"])]
                            )
                        )

                    current_parts = []

                    if chat_image:
                        current_parts.append(
                            types.Part.from_bytes(
                                data=chat_image.getvalue(),
                                mime_type=chat_image.type
                            )
                        )

                    current_parts.append(types.Part(text=prompt))

                    contents.append(
                        types.Content(
                            role="user",
                            parts=current_parts
                        )
                    )

                    response = client.models.generate_content(
                        model=CHAT_MODEL,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are Duniya AI, a helpful, honest "
                                "multilingual assistant. Reply in the user's "
                                "language. Understand uploaded images when "
                                "provided. Explain things clearly and "
                                "respectfully. Do not claim to generate an "
                                "image unless an actual image was created."
                            )
                        )
                    )

                    answer = response.text or "معذرت، اس وقت جواب نہیں ملا۔"
                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:
                    st.error("AI سے جواب لینے میں مسئلہ آیا۔")
                    st.code(str(error))

# ==================================================
# TAB 2: IMAGE EDITOR
# ==================================================
with editor_tab:
    st.subheader("تصویر کا سائز، کراپ اور ٹیکسٹ")
    st.write(
        "یہ ٹول مفت ہے۔ آپ تصویر کو بینر، تھمب نیل یا دوسری شکل میں "
        "بدل سکتے ہیں۔"
    )

    uploaded_image = st.file_uploader(
        "اپنے کمپیوٹر سے تصویر منتخب کریں",
        type=["png", "jpg", "jpeg", "webp"],
        key="editor_image"
    )

    font_upload = st.file_uploader(
        "اختیاری: جمیل نوری نستعلیق کا TTF/OTF فونٹ اپ لوڈ کریں",
        type=["ttf", "otf"],
        key="urdu_font"
    )

    if uploaded_image:
        try:
            original = load_uploaded_image(uploaded_image)
            st.image(original, caption="اصل تصویر", use_container_width=True)

            preset = st.selectbox(
                "ڈیزائن منتخب کریں",
                [
                    "YouTube Banner (2560×1440)",
                    "YouTube Thumbnail (1280×720)",
                    "YouTube Shorts (1080×1920)",
                    "Square Post (1080×1080)",
                    "Custom Size"
                ]
            )

            presets = {
                "YouTube Banner (2560×1440)": (2560, 1440),
                "YouTube Thumbnail (1280×720)": (1280, 720),
                "YouTube Shorts (1080×1920)": (1080, 1920),
                "Square Post (1080×1080)": (1080, 1080)
            }

            if preset == "Custom Size":
                c1, c2 = st.columns(2)
                with c1:
                    out_width = st.number_input(
                        "چوڑائی (pixels)", 100, 4000, 1280
                    )
                with c2:
                    out_height = st.number_input(
                        "اونچائی (pixels)", 100, 4000, 720
                    )
                width, height = int(out_width), int(out_height)
            else:
                width, height = presets[preset]

            fit_mode = st.radio(
                "تصویر کیسے فٹ ہو؟",
                ["Crop / Fill", "Contain / پوری تصویر"],
                horizontal=True
            )

            overlay_text = st.text_input(
                "تصویر پر لکھنے کے لیے متن (اختیاری)",
                placeholder="مثلاً Duniya AI"
            )

            text_color = st.selectbox(
                "متن کا رنگ",
                ["White", "Yellow", "Black", "Light Blue"]
            )

            font_size = st.slider("متن کا سائز", 18, 150, 60)

            if st.button("تصویر تیار کریں", use_container_width=True):
                edited = fit_image(original, width, height, fit_mode)

                if overlay_text.strip():
                    draw = ImageDraw.Draw(edited)
                    font = make_font(font_upload, font_size)

                    color_map = {
                        "White": "#FFFFFF",
                        "Yellow": "#FFE66D",
                        "Black": "#000000",
                        "Light Blue": "#93C5FD"
                    }
                    color = color_map[text_color]

                    # Place text near the lower center with an outline.
                    x = width // 2
                    y = int(height * 0.82)

                    draw.text(
                        (x, y),
                        overlay_text,
                        font=font,
                        fill=color,
                        anchor="mm",
                        stroke_width=max(1, font_size // 18),
                        stroke_fill="#111111"
                    )

                st.session_state.edited_image = image_to_bytes(edited)

            if st.session_state.edited_image:
                final_image = Image.open(
                    io.BytesIO(st.session_state.edited_image)
                )
                st.success("تصویر تیار ہے۔")
                st.image(final_image, use_container_width=True)

                st.download_button(
                    "⬇️ تصویر ڈاؤن لوڈ کریں",
                    data=st.session_state.edited_image,
                    file_name="duniya_ai_design.png",
                    mime="image/png",
                    use_container_width=True
                )

        except Exception as error:
            st.error("تصویر تیار نہیں ہو سکی۔")
            st.code(str(error))

    else:
        st.info("ایڈیٹنگ شروع کرنے کے لیے پہلے تصویر اپ لوڈ کریں۔")

# ==================================================
# TAB 3: AI IMAGE GENERATION
# ==================================================
with generate_tab:
    st.subheader("AI سے نئی تصویر بنائیں")
    st.write(
        "یہ فیچر Gemini کے image-generation ماڈل کو استعمال کرنے کی "
        "کوشش کرے گا۔ یہ آپ کے اکاؤنٹ میں دستیاب ہونا ضروری ہے۔"
    )

    image_prompt = st.text_area(
        "آپ کیسی تصویر چاہتے ہیں؟",
        placeholder=(
            "مثلاً: پاکستان کے خوبصورت پہاڑ، نیلا آسمان، "
            "سنیما جیسا منظر، اعلیٰ معیار کی ڈیجیٹل آرٹ"
        ),
        height=120
    )

    if st.button("✨ تصویر بنانے کی کوشش کریں", use_container_width=True):
        if not image_prompt.strip():
            st.warning("پہلے تصویر کی تفصیل لکھیں۔")
        else:
            try:
                client = get_client()

                with st.spinner("AI تصویر بنانے کی کوشش کر رہا ہے..."):
                    response = client.models.generate_content(
                        model=IMAGE_MODEL,
                        contents=(
                            "Generate an image based on this description: "
                            + image_prompt
                        )
                    )

                    generated = None

                    for part in (response.parts or []):
                        if getattr(part, "inline_data", None):
                            generated = part.as_image()
                            break

                    if generated is None:
                        st.warning(
                            "AI نے قابلِ ڈاؤن لوڈ تصویر واپس نہیں کی۔ "
                            "ممکن ہے یہ ماڈل آپ کے اکاؤنٹ یا API کوٹے میں "
                            "دستیاب نہ ہو۔"
                        )
                        if response.text:
                            st.write(response.text)
                    else:
                        if not isinstance(generated, Image.Image):
                            generated = Image.open(generated)

                        generated = generated.convert("RGB")
                        st.session_state.generated_image = image_to_bytes(
                            generated
                        )
                        st.success("تصویر تیار ہو گئی!")
                        st.image(generated, use_container_width=True)

            except Exception as error:
                st.error(
                    "تصویر بنانے کی درخواست ناکام ہوئی۔ "
                    "ممکن ہے ماڈل دستیاب نہ ہو یا مفت کوٹہ ختم ہو گیا ہو۔"
                )
                st.code(str(error))

    if st.session_state.generated_image:
        st.download_button(
            "⬇️ AI تصویر ڈاؤن لوڈ کریں",
            data=st.session_state.generated_image,
            file_name="duniya_ai_generated.png",
            mime="image/png",
            use_container_width=True
        )

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
Duniya AI — AI کے جوابات میں غلطی ممکن ہے۔ اہم معلومات کی تصدیق کریں۔
</div>
""", unsafe_allow_html=True)






 
