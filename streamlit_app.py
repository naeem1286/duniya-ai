
import os
import io
import base64
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from google import genai
from google.genai import types

# ==========================================
# DUNIYA AI - CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Duniya AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.8-flash")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-nano-banana-2.1")

# ==========================================
# LOAD URDU FONT
# Add this file to your repository:
# assets/JameelNooriNastaleeq.ttf
# ==========================================

FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "JameelNooriNastaleeq.ttf",
)

font_css = ""

if os.path.isfile(FONT_PATH):
    try:
        with open(FONT_PATH, "rb") as font_file:
            encoded_font = base64.b64encode(
                font_file.read()
            ).decode("ascii")

        font_css = f"""
        @font-face {{
            font-family: 'JameelNoori';
            src: url(data:font/ttf;base64,{encoded_font})
                 format('truetype');
            font-style: normal;
            font-weight: normal;
            font-display: swap;
        }}
        """
    except OSError:
        font_css = ""

# ==========================================
# WEBSITE DESIGN
# ==========================================

st.markdown(
    f"""
    <style>
    {font_css}

    :root {{
        --page-bg: #07111f;
        --panel-bg: #101d30;
        --input-bg: #000000;
        --input-border: #526780;
        --white: #ffffff;
        --muted: #d0d8e5;
        --accent: #42b8ff;
    }}

    .stApp {{
        background: linear-gradient(135deg, #07111f, #101b32);
        color: var(--white);
    }}

    section[data-testid="stSidebar"] {{
        background: #090f1c;
        border-right: 1px solid #293951;
    }}

    h1, h2, h3, h4 {{
        color: #8ddcff;
    }}

    /* Urdu text and chat messages */
    [data-testid="stChatMessageContent"],
    [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li {{
        font-family: 'JameelNoori', 'Noto Nastaliq Urdu',
                     'Noto Naskh Arabic', serif !important;
        font-size: 19px;
        line-height: 2.0 !important;
    }}

    /* Chat input: black background and white typing */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea,
    .stChatInput textarea {{
        background: #000000 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        border: 1px solid #526780 !important;
        border-radius: 12px !important;
        font-family: 'JameelNoori', 'Noto Nastaliq Urdu',
                     'Noto Naskh Arabic', serif !important;
        font-size: 19px !important;
        line-height: 1.9 !important;
        direction: rtl !important;
        text-align: right !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder,
    .stChatInput textarea::placeholder {{
        color: #d0d8e5 !important;
        -webkit-text-fill-color: #d0d8e5 !important;
        opacity: 1 !important;
    }}

    /* All other typing fields */
    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    .stNumberInput input {{
        background-color: #000000 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        border: 1px solid #526780 !important;
        border-radius: 10px !important;
        font-family: 'JameelNoori', 'Noto Nastaliq Urdu',
                     'Noto Naskh Arabic', serif !important;
        font-size: 18px !important;
        line-height: 1.9 !important;
    }}

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: #d0d8e5 !important;
        -webkit-text-fill-color: #d0d8e5 !important;
        opacity: 1 !important;
    }}

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {{
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #42b8ff !important;
        border-radius: 10px !important;
        min-height: 43px;
        font-family: 'JameelNoori', 'Noto Nastaliq Urdu',
                     'Noto Naskh Arabic', serif !important;
        font-size: 17px !important;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        border-color: #ffffff !important;
        background: #17263a !important;
    }}

    /* Chat cards */
    [data-testid="stChatMessage"] {{
        background: #101d30;
        border: 1px solid #293951;
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 12px;
    }}

    /* Labels and general Urdu text */
    .stApp label,
    .stApp p,
    .stApp li {{
        font-family: 'JameelNoori', 'Noto Nastaliq Urdu',
                     'Noto Naskh Arabic', serif;
    }}

    /* Code remains readable in English */
    code, pre {{
        font-family: monospace !important;
        direction: ltr !important;
        text-align: left !important;
    }}

    .info-note {{
        color: #d0d8e5;
        font-size: 14px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# API KEY
# ==========================================

def read_api_key():
    try:
        value = st.secrets.get("GEMINI_API_KEY", "")
        if value:
            return value
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


api_key = read_api_key()
client = genai.Client(api_key=api_key) if api_key else None


def require_client():
    if client is None:
        st.error(
            "GEMINI_API_KEY نہیں ملی۔ "
            "Streamlit Settings → Secrets میں اسے سیٹ کریں۔"
        )
        return False
    return True


def image_bytes(image, image_format="PNG"):
    output = io.BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


def open_uploaded_image(upload):
    if upload is None:
        return None

    try:
        return Image.open(upload).convert("RGB")
    except Exception:
        st.error("تصویر نہیں کھل سکی۔ دوسری تصویر اپلوڈ کریں۔")
        return None


def load_font(size):
    candidates = [
        FONT_PATH,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoNastaliqUrdu-Regular.ttf",
    ]

    for path in candidates:
        try:
            if os.path.isfile(path):
                return ImageFont.truetype(path, size)
        except OSError:
            continue

    return ImageFont.load_default()


# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "edited_image" not in st.session_state:
    st.session_state.edited_image = None

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.title("🌍 Duniya AI")
    st.caption("Your AI assistant")
    st.divider()

    language = st.selectbox(
        "جواب کی زبان",
        [
            "User's language",
            "Urdu",
            "English",
            "Hindi",
            "Arabic",
            "Roman Urdu",
        ],
    )

    web_search = st.checkbox(
        "Google Search استعمال کریں",
        value=False,
        help="ویب سرچ کی دستیابی اور ممکنہ چارجز آپ کے Google اکاؤنٹ پر منحصر ہیں۔",
    )

    if st.button("چیٹ صاف کریں", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### فیچرز")
    st.write("💬 AI چیٹ")
    st.write("🖼️ تصویر کے بارے میں سوال")
    st.write("✏️ تصویر ایڈیٹر")
    st.write("🎨 AI تصویر بنائیں")

    if os.path.isfile(FONT_PATH):
        st.success("اردو فونٹ فائل مل گئی")
    else:
        st.warning(
            "جمیل نوری فونٹ کی فائل assets فولڈر میں شامل کریں۔"
        )

# ==========================================
# HEADER
# ==========================================

st.title("🌍 Duniya AI")
st.markdown(
    "اپنا سوال لکھیں، معلومات حاصل کریں، تصاویر سمجھیں "
    "اور نئی تصاویر بنانے کی کوشش کریں۔"
)

if not client:
    st.warning(
        "AI چلانے کے لیے Streamlit Secrets میں "
        "`GEMINI_API_KEY` ضروری ہے۔"
    )

chat_tab, editor_tab, generator_tab = st.tabs(
    ["💬 AI Chat", "✏️ Image Editor", "🎨 Image Generator"]
)

# ==========================================
# TAB 1: AI CHAT
# ==========================================

with chat_tab:
    st.subheader("آپ کیا پوچھنا چاہتے ہیں؟")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("image") is not None:
                st.image(
                    message["image"],
                    use_container_width=True,
                )

    question_image_upload = st.file_uploader(
        "سوال کے ساتھ تصویر اپلوڈ کریں (اختیاری)",
        type=["png", "jpg", "jpeg", "webp"],
        key="question_image",
    )

    question = st.chat_input("اپنا سوال یہاں لکھیں...")

    if question:
        if not require_client():
            st.stop()

        question_image = open_uploaded_image(
            question_image_upload
        )

        st.session_state.messages.append({
            "role": "user",
            "content": question,
            "image": question_image,
        })

        with st.chat_message("user"):
            st.markdown(question)
            if question_image is not None:
                st.image(
                    question_image,
                    use_container_width=True,
                )

        with st.chat_message("assistant"):
            try:
                language_instructions = {
                    "User's language":
                        "Reply in the same language as the user.",
                    "Urdu":
                        "Reply in clear Urdu. Use natural Urdu wording.",
                    "English":
                        "Reply in English.",
                    "Hindi":
                        "Reply in Hindi.",
                    "Arabic":
                        "Reply in Arabic.",
                    "Roman Urdu":
                        "Reply in Roman Urdu using Latin characters.",
                }

                system_instruction = (
                    "You are Duniya AI, a helpful multilingual assistant. "
                    "Give clear, useful, accurate answers. "
                    "Explain technical tasks step by step for beginners. "
                    "If you are unsure, say so. Do not invent facts or sources. "
                    + language_instructions[language]
                )

                contents = []

                # Include previous chat messages as context.
                for old in st.session_state.messages[:-1]:
                    role = (
                        "model" if old["role"] == "assistant"
                        else "user"
                    )
                    parts = [{"text": old["content"]}]

                    if old.get("image") is not None:
                        parts.append(
                            types.Part.from_bytes(
                                data=image_bytes(old["image"]),
                                mime_type="image/png",
                            )
                        )

                    contents.append({
                        "role": role,
                        "parts": parts,
                    })

                current_parts = [{"text": question}]

                if question_image is not None:
                    current_parts.append(
                        types.Part.from_bytes(
                            data=image_bytes(question_image),
                            mime_type="image/png",
                        )
                    )

                contents.append({
                    "role": "user",
                    "parts": current_parts,
                })

                config = {
                    "system_instruction": system_instruction,
                    "temperature": 0.7,
                }

                if web_search:
                    config["tools"] = [
                        types.Tool(
                            google_search=types.GoogleSearch()
                        )
                    ]

                with st.spinner("جواب تیار ہو رہا ہے..."):
                    response = client.models.generate_content(
                        model=CHAT_MODEL,
                        contents=contents,
                        config=types.GenerateContentConfig(**config),
                    )

                answer = response.text or (
                    "معذرت، اس بار جواب موصول نہیں ہوا۔ دوبارہ کوشش کریں۔"
                )

                st.markdown(answer)

                # Show search sources if supplied by the API.
                candidates = getattr(response, "candidates", None) or []
                metadata = (
                    getattr(candidates[0], "grounding_metadata", None)
                    if candidates else None
                )

                if metadata:
                    chunks = getattr(metadata, "grounding_chunks", []) or []
                    links = []

                    for chunk in chunks:
                        web_item = getattr(chunk, "web", None)
                        if web_item:
                            url = getattr(web_item, "uri", None)
                            title = getattr(web_item, "title", None)
                            if url:
                                links.append((title or url, url))

                    if links:
                        with st.expander("معلومات کے ویب ذرائع"):
                            for title, url in links:
                                st.markdown(f"- [{title}]({url})")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except Exception as exc:
                st.error(
                    "جواب حاصل نہیں ہو سکا۔ API key، ماڈل کی اجازت "
                    "اور Streamlit Logs چیک کریں۔"
                )
                st.caption(f"Technical details: {exc}")

# ==========================================
# TAB 2: IMAGE EDITOR
# ==========================================

with editor_tab:
    st.subheader("تصویر ایڈیٹر")

    editor_upload = st.file_uploader(
        "تصویر منتخب کریں",
        type=["png", "jpg", "jpeg", "webp"],
        key="editor_image",
    )

    if editor_upload:
        original = open_uploaded_image(editor_upload)

        if original is not None:
            st.image(
                original,
                caption="اصل تصویر",
                use_container_width=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                out_width = st.number_input(
                    "چوڑائی",
                    min_value=100,
                    max_value=4096,
                    value=min(original.width, 1280),
                    step=100,
                )

                out_height = st.number_input(
                    "اونچائی",
                    min_value=100,
                    max_value=4096,
                    value=min(original.height, 1280),
                    step=100,
                )

                square_crop = st.checkbox(
                    "مربع تصویر بنائیں",
                    value=False,
                )

            with col2:
                text_overlay = st.text_input(
                    "تصویر پر لکھنے کے الفاظ"
                )

                overlay_position = st.selectbox(
                    "الفاظ کی جگہ",
                    ["نیچے", "درمیان", "اوپر"],
                )

                overlay_size = st.slider(
                    "الفاظ کا سائز",
                    min_value=14,
                    max_value=100,
                    value=36,
                )

            if st.button("تصویر تیار کریں", type="primary"):
                result = original.copy()

                if square_crop:
                    side = min(result.width, result.height)
                    left = (result.width - side) // 2
                    top = (result.height - side) // 2
                    result = result.crop(
                        (left, top, left + side, top + side)
                    )

                result = result.resize(
                    (int(out_width), int(out_height)),
                    Image.Resampling.LANCZOS,
                )

                if text_overlay.strip():
                    draw = ImageDraw.Draw(result)
                    font = load_font(overlay_size)

                    bbox = draw.textbbox(
                        (0, 0),
                        text_overlay,
                        font=font,
                        direction="rtl" if hasattr(draw, "textbbox") else None,
                    )

                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]

                    x = max(10, (result.width - tw) // 2)

                    if overlay_position == "اوپر":
                        y = 15
                    elif overlay_position == "درمیان":
                        y = (result.height - th) // 2
                    else:
                        y = result.height - th - 20

                    # Black outline for readable white text.
                    draw.text(
                        (x, y),
                        text_overlay,
                        font=font,
                        fill="white",
                        stroke_width=3,
                        stroke_fill="black",
                        direction="rtl",
                    )

                st.session_state.edited_image = result

            if st.session_state.edited_image is not None:
                st.markdown("### تیار شدہ تصویر")
                st.image(
                    st.session_state.edited_image,
                    use_container_width=True,
                )

                st.download_button(
                    "تصویر ڈاؤن لوڈ کریں",
                    data=image_bytes(st.session_state.edited_image),
                    file_name="duniya_ai_edited.png",
                    mime="image/png",
                    use_container_width=True,
                )

# ==========================================
# TAB 3: AI IMAGE GENERATOR
# ==========================================

with generator_tab:
    st.subheader("AI تصویر بنائیں")

    prompt = st.text_area(
        "آپ کیسی تصویر چاہتے ہیں؟",
        placeholder=(
            "مثال: ایک خوبصورت جدید شہر، رات کا منظر، "
            "سنیما جیسی روشنی اور حقیقت کے قریب تفصیلات"
        ),
        height=130,
    )

    aspect_ratio = st.selectbox(
        "تصویر کا تناسب",
        ["1:1", "16:9", "9:16", "4:3", "3:4"],
        index=1,
    )

    style = st.selectbox(
        "تصویر کا انداز",
        [
            "Realistic",
            "Cinematic",
            "Digital art",
            "Anime",
            "Minimalist",
            "Product photography",
        ],
    )

    if st.button(
        "AI تصویر بنائیں",
        type="primary",
        use_container_width=True,
    ):
        if not require_client():
            st.stop()

        if not prompt.strip():
            st.warning("پہلے تصویر کی تفصیل لکھیں۔")
        else:
            full_prompt = (
                f"{prompt.strip()}. Style: {style}. "
                "Create a high-quality image. "
                "Avoid unwanted text, logos, and watermarks."
            )

            try:
                with st.spinner("تصویر بن رہی ہے..."):
                    result = client.interactions.create(
                        model=IMAGE_MODEL,
                        input=full_prompt,
                        response_format={
                            "type": "image",
                            "mime_type": "image/png",
                            "aspect_ratio": aspect_ratio,
                        },
                    )

                output_image = getattr(
                    result, "output_image", None
                )

                if output_image is None or not output_image.data:
                    st.error(
                        "تصویر واپس نہیں ملی۔ ماڈل کی دستیابی "
                        "اور API access چیک کریں۔"
                    )
                else:
                    raw_data = output_image.data

                    if isinstance(raw_data, str):
                        raw_data = base64.b64decode(raw_data)

                    generated = Image.open(
                        io.BytesIO(raw_data)
                    ).convert("RGB")

                    st.session_state.generated_image = generated

            except Exception as exc:
                st.error(
                    "تصویر بنانے میں مسئلہ ہوا۔ ممکن ہے ماڈل، "
                    "API access یا SDK ورژن درست نہ ہو۔"
                )
                st.caption(f"Technical details: {exc}")

    if st.session_state.generated_image is not None:
        st.image(
            st.session_state.generated_image,
            caption="AI سے تیار کردہ تصویر",
            use_container_width=True,
        )

        st.download_button(
            "AI تصویر ڈاؤن لوڈ کریں",
            data=image_bytes(st.session_state.generated_image),
            file_name="duniya_ai_generated.png",
            mime="image/png",
            use_container_width=True,
        )

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption(
    "Duniya AI — AI کے جوابات میں غلطی ہو سکتی ہے۔ "
    "اہم معلومات کی تصدیق ضرور کریں۔"
)





 
