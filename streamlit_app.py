
import os
import io
import base64
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from google import genai
from google.genai import types


# ------------------------------------------
# DUNIYA AI - MAIN CONFIGURATION
# ------------------------------------------

st.set_page_config(
    page_title="Duniya AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

CHAT_MODEL = os.getenv(
    "GEMINI_CHAT_MODEL", "gemini-3.8-flash"
)
IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL", "gemini-nano-banana-2.1"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f, #101b32);
    color: #f5f7fb;
}
section[data-testid="stSidebar"] {
    background: #0b1425;
}
h1, h2, h3 {
    color: #8ddcff;
}
div[data-testid="stChatMessage"] {
    border: 1px solid #253957;
    border-radius: 14px;
    padding: 12px;
}
.stButton > button {
    border-radius: 10px;
    border: 1px solid #2d86b9;
    min-height: 42px;
}
.small-note {
    color: #b5c3d8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------
# API KEY AND CLIENT
# ------------------------------------------

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


API_KEY = get_api_key()

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None


# ------------------------------------------
# SESSION STATE
# ------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

if "edited_image" not in st.session_state:
    st.session_state.edited_image = None


# ------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------

def image_to_bytes(image, fmt="PNG"):
    output = io.BytesIO()
    image.save(output, format=fmt)
    return output.getvalue()


def load_font(size):
    candidates = [
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    return ImageFont.load_default()


def make_client_ready():
    if not client:
        st.error(
            "GEMINI_API_KEY نہیں ملی۔ "
            "Streamlit Settings → Secrets میں API key چیک کریں۔"
        )
        return False
    return True


def get_image_from_upload(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        return Image.open(uploaded_file).convert("RGB")
    except Exception:
        st.error("یہ تصویر کھولی نہیں جا سکی۔ دوسری تصویر آزمائیں۔")
        return None


# ------------------------------------------
# SIDEBAR
# ------------------------------------------

with st.sidebar:
    st.title("🌍 Duniya AI")
    st.caption("Your AI assistant")

    st.markdown("---")
    st.subheader("Settings")

    response_language = st.selectbox(
        "جواب کی زبان / Response language",
        [
            "User's language",
            "Urdu",
            "English",
            "Hindi",
            "Arabic",
            "Roman Urdu",
        ],
        index=0,
    )

    use_web_search = st.checkbox(
        "Use Google Search for current information",
        value=False,
        help="Search may have usage limits or charges depending on your Google project.",
    )

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Available features**")
    st.write("💬 AI Chat")
    st.write("🖼️ Image Questions")
    st.write("🎨 AI Image Generation")
    st.write("✏️ Image Editor")

    st.markdown("---")
    st.markdown(
        '<p class="small-note">Duniya AI is an independent project. '
        'AI answers can contain mistakes.</p>',
        unsafe_allow_html=True,
    )


# ------------------------------------------
# HEADER
# ------------------------------------------

st.title("🌍 Duniya AI")
st.markdown(
    "### آپ کا AI اسسٹنٹ — سوال پوچھیں، تصاویر سمجھیں، اور نئی تصاویر بنائیں"
)

if not client:
    st.warning(
        "AI استعمال کرنے کے لیے Streamlit Secrets میں "
        "`GEMINI_API_KEY` سیٹ ہونا ضروری ہے۔"
    )


# ------------------------------------------
# MAIN TABS
# ------------------------------------------

chat_tab, editor_tab, image_tab = st.tabs(
    ["💬 AI Chat", "✏️ Image Editor", "🎨 AI Image Generator"]
)


# ==========================================
# TAB 1: CHAT
# ==========================================

with chat_tab:
    st.subheader("AI Chat Assistant")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("image") is not None:
                st.image(
                    message["image"],
                    caption="Uploaded image",
                    use_container_width=True,
                )

    uploaded_question_image = st.file_uploader(
        "تصویر اپلوڈ کریں (اختیاری)",
        type=["png", "jpg", "jpeg", "webp"],
        key="chat_upload",
    )

    prompt = st.chat_input("اپنا سوال یہاں لکھیں...")

    if prompt:
        if not make_client_ready():
            st.stop()

        uploaded_image = get_image_from_upload(
            uploaded_question_image
        )

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "image": uploaded_image,
        })

        with st.chat_message("user"):
            st.markdown(prompt)
            if uploaded_image is not None:
                st.image(
                    uploaded_image,
                    use_container_width=True,
                )

        with st.chat_message("assistant"):
            answer_placeholder = st.empty()

            language_instruction = {
                "User's language":
                    "Reply in the same language the user uses.",
                "Urdu":
                    "Reply in clear, simple Urdu.",
                "English":
                    "Reply in English.",
                "Hindi":
                    "Reply in Hindi.",
                "Arabic":
                    "Reply in Arabic.",
                "Roman Urdu":
                    "Reply in Roman Urdu using Latin letters.",
            }.get(response_language, "Reply in the user's language.")

            system_instruction = (
                "You are Duniya AI, a helpful, respectful, "
                "multilingual AI assistant. "
                "Give clear, accurate, useful answers. "
                "Explain technical tasks step by step for beginners. "
                "Be honest when uncertain and never invent sources. "
                + language_instruction
            )

            contents = []

            for old_message in st.session_state.messages[:-1]:
                contents.append({
                    "role": (
                        "model" if old_message["role"] == "assistant"
                        else "user"
                    ),
                    "parts": [{"text": old_message["content"]}],
                })

            current_parts = [{"text": prompt}]

            if uploaded_image is not None:
                current_parts.append(
                    types.Part.from_bytes(
                        data=image_to_bytes(uploaded_image),
                        mime_type="image/png",
                    )
                )

            contents.append({
                "role": "user",
                "parts": current_parts,
            })

            try:
                config_args = {
                    "system_instruction": system_instruction,
                    "temperature": 0.7,
                }

                if use_web_search:
                    config_args["tools"] = [
                        types.Tool(
                            google_search=types.GoogleSearch()
                        )
                    ]

                response = client.models.generate_content(
                    model=CHAT_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        **config_args
                    ),
                )

                answer = response.text or (
                    "معذرت، اس سوال کا جواب تیار نہیں ہو سکا۔"
                )

                answer_placeholder.markdown(answer)

                # Show available grounding sources if provided.
                grounding = getattr(
                    getattr(response, "candidates", [None])[0],
                    "grounding_metadata",
                    None,
                ) if getattr(response, "candidates", None) else None

                if grounding:
                    chunks = getattr(
                        grounding, "grounding_chunks", []
                    ) or []

                    source_links = []
                    for chunk in chunks:
                        web_item = getattr(chunk, "web", None)
                        if web_item:
                            uri = getattr(web_item, "uri", None)
                            title = getattr(web_item, "title", None)
                            if uri:
                                source_links.append(
                                    (title or uri, uri)
                                )

                    if source_links:
                        with st.expander("Web sources"):
                            for title, uri in source_links:
                                st.markdown(f"- [{title}]({uri})")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except Exception as exc:
                st.error(
                    "AI سے جواب حاصل نہیں ہو سکا۔ "
                    "API key، model access اور deployment logs چیک کریں۔"
                )
                st.caption(f"Technical details: {exc}")


# ==========================================
# TAB 2: IMAGE EDITOR
# ==========================================

with editor_tab:
    st.subheader("Image Editor")

    editor_upload = st.file_uploader(
        "اپنی تصویر اپلوڈ کریں",
        type=["png", "jpg", "jpeg", "webp"],
        key="editor_upload",
    )

    if editor_upload:
        original_image = get_image_from_upload(editor_upload)

        if original_image:
            left, right = st.columns(2)

            with left:
                st.image(
                    original_image,
                    caption="Original image",
                    use_container_width=True,
                )

            with right:
                st.markdown("**Image settings**")

                width = st.number_input(
                    "Width (pixels)",
                    min_value=100,
                    max_value=4096,
                    value=min(original_image.width, 1280),
                    step=100,
                )

                height = st.number_input(
                    "Height (pixels)",
                    min_value=100,
                    max_value=4096,
                    value=min(original_image.height, 1280),
                    step=100,
                )

                crop_square = st.checkbox(
                    "Crop to square",
                    value=False,
                )

                overlay_text = st.text_input(
                    "تصویر پر ٹیکسٹ (اختیاری)"
                )

                text_position = st.selectbox(
                    "Text position",
                    ["Bottom", "Top", "Center"],
                )

                text_size = st.slider(
                    "Text size",
                    min_value=12,
                    max_value=100,
                    value=36,
                )

                text_color = st.selectbox(
                    "Text color",
                    ["White", "Yellow", "Black"],
                )

                if st.button(
                    "Apply changes",
                    use_container_width=True,
                ):
                    result_image = original_image.copy()

                    if crop_square:
                        side = min(
                            result_image.width,
                            result_image.height,
                        )
                        x = (result_image.width - side) // 2
                        y = (result_image.height - side) // 2
                        result_image = result_image.crop(
                            (x, y, x + side, y + side)
                        )

                    result_image = result_image.resize(
                        (int(width), int(height)),
                        Image.Resampling.LANCZOS,
                    )

                    if overlay_text.strip():
                        draw = ImageDraw.Draw(result_image)
                        font = load_font(int(text_size))

                        bbox = draw.textbbox(
                            (0, 0),
                            overlay_text,
                            font=font,
                        )

                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]

                        margin = 20
                        x = max(
                            margin,
                            (result_image.width - text_width) // 2,
                        )

                        if text_position == "Top":
                            y = margin
                        elif text_position == "Center":
                            y = (
                                result_image.height - text_height
                            ) // 2
                        else:
                            y = (
                                result_image.height
                                - text_height
                                - margin
                            )

                        colors = {
                            "White": (255, 255, 255),
                            "Yellow": (255, 220, 0),
                            "Black": (0, 0, 0),
                        }

                        # Dark outline improves readability.
                        draw.text(
                            (x, y),
                            overlay_text,
                            font=font,
                            fill=colors[text_color],
                            stroke_width=2,
                            stroke_fill=(0, 0, 0),
                        )

                    st.session_state.edited_image = result_image

            if st.session_state.edited_image is not None:
                st.markdown("---")
                st.subheader("Edited result")
                st.image(
                    st.session_state.edited_image,
                    use_container_width=True,
                )

                st.download_button(
                    "⬇️ Download edited image",
                    data=image_to_bytes(
                        st.session_state.edited_image
                    ),
                    file_name="duniya_ai_edited.png",
                    mime="image/png",
                    use_container_width=True,
                )


# ==========================================
# TAB 3: AI IMAGE GENERATOR
# ==========================================

with image_tab:
    st.subheader("AI Image Generator")

    st.write(
        "اپنی تصویر کی تفصیل لکھیں۔ دستیاب ماڈل اور اکاؤنٹ کی "
        "اجازت کے مطابق AI تصویر بنانے کی کوشش کرے گا۔"
    )

    image_prompt = st.text_area(
        "Describe the image you want",
        placeholder=(
            "Example: A beautiful futuristic city at night, "
            "cinematic lighting, realistic details..."
        ),
        height=120,
        key="image_prompt",
    )

    aspect_ratio = st.selectbox(
        "Image aspect ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"],
        index=1,
    )

    image_style = st.selectbox(
        "Image style",
        [
            "Realistic",
            "Cinematic",
            "Digital art",
            "Anime",
            "Minimalist",
            "Product photography",
        ],
    )

    generate_clicked = st.button(
        "✨ Generate image",
        type="primary",
        use_container_width=True,
    )

    if generate_clicked:
        if not make_client_ready():
            st.stop()

        if not image_prompt.strip():
            st.warning("پہلے تصویر کی تفصیل لکھیں۔")
        else:
            full_prompt = (
                f"{image_prompt.strip()}. "
                f"Style: {image_style}. "
                "Create a high-quality image. "
                "Avoid unnecessary text, logos, and watermarks."
            )

            with st.spinner("AI تصویر بنا رہا ہے..."):
                try:
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

                    if output_image is not None:
                        image_data = output_image.data

                        if isinstance(image_data, str):
                            image_bytes = base64.b64decode(
                                image_data
                            )
                        else:
                            image_bytes = image_data

                        generated = Image.open(
                            io.BytesIO(image_bytes)
                        ).convert("RGB")

                        st.session_state.generated_image = generated

                    else:
                        st.error(
                            "ماڈل نے تصویر واپس نہیں کی۔ "
                            "Image model کی API documentation "
                            "اور access چیک کریں۔"
                        )

                except Exception as exc:
                    st.error(
                        "تصویر نہیں بن سکی۔ ممکن ہے ماڈل کا نام، "
                        "اکاؤنٹ کی اجازت یا SDK ورژن مسئلہ ہو۔"
                    )
                    st.caption(f"Technical details: {exc}")

    if st.session_state.generated_image is not None:
        st.markdown("---")
        st.subheader("Generated image")

        st.image(
            st.session_state.generated_image,
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download generated image",
            data=image_to_bytes(
                st.session_state.generated_image
            ),
            file_name="duniya_ai_generated.png",
            mime="image/png",
            use_container_width=True,
        )


# ------------------------------------------
# FOOTER
# ------------------------------------------

st.markdown("---")
st.caption(
    "Duniya AI • AI responses may be inaccurate. "
    "Check important information independently."
)

st.markdown("""
<style>

/* Load Jameel Noori Nastaleeq Urdu font */
@font-face {
    font-family: 'JameelNoori';
    src: url('app/static/JameelNooriNastaleeq.ttf');
    font-weight: normal;
    font-style: normal;
}

/* Main website */
.stApp {
    background: linear-gradient(135deg, #07111f, #101b32);
    color: #f5f7fb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0b1425;
}

/* Headings */
h1, h2, h3, h4 {
    color: #8ddcff;
}

/* Urdu font throughout chat and content */
div[data-testid="stChatMessageContent"],
div[data-testid="stMarkdownContainer"],
.stMarkdown,
.stText,
[data-testid="stChatMessage"] {
    font-family: 'JameelNoori', 'Noto Nastaliq Urdu',
                 'Noto Naskh Arabic', serif !important;
    line-height: 2 !important;
}

/* Chat input: dark background, white text */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] textarea,
.stChatInput textarea {
    background-color: #14233b !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-family: 'JameelNoori', 'Noto Nastaliq Urdu', serif !important;
    font-size: 19px !important;
    line-height: 1.9 !important;
    caret-color: #ffffff !important;
    direction: rtl;
    text-align: right;
}

/* Input placeholder */
[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder,
input::placeholder,
textarea::placeholder {
    color: #c7d4e8 !important;
    -webkit-text-fill-color: #c7d4e8 !important;
    opacity: 1 !important;
}

/* Other input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #14233b !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid #426080 !important;
    border-radius: 10px !important;
    font-family: 'JameelNoori', 'Noto Nastaliq Urdu', serif !important;
    font-size: 18px !important;
}

/* Dropdowns and selection fields */
.stSelectbox div[data-baseweb="select"],
.stSelectbox div[data-baseweb="select"] * {
    color: #ffffff !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
button[kind="primary"] {
    background-color: #1769aa !important;
    color: #ffffff !important;
    border: 1px solid #48a9e6 !important;
    border-radius: 10px !important;
    font-family: 'JameelNoori', 'Noto Nastaliq Urdu', serif !important;
    font-size: 17px !important;
    min-height: 42px;
}

/* Chat message cards */
div[data-testid="stChatMessage"] {
    background: #101e33;
    border: 1px solid #253957;
    border-radius: 14px;
    padding: 12px;
}

/* General text */
p, label, li {
    font-family: 'JameelNoori', 'Noto Nastaliq Urdu', serif;
    line-height: 1.9;
}

/* Keep English code readable */
code, pre {
    font-family: monospace !important;
    direction: ltr;
    text-align: left;
}

.small-note {
    color: #b5c3d8;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)




 
