import streamlit as st
from transformers import pipeline
import base64
import streamlit.components.v1 as components
from gtts import gTTS
import random
import time

# ==============================
# 🔊 AUDIO FUNCTION (ADDED)
# ==============================
def play_audio(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    tts.save("temp.mp3")

    with open("temp.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    components.html(
        f'<audio autoplay><source src="data:audio/mp3;base64,{b64}"></audio>',
        height=0
    )

# ==============================
# 🌄 BACKGROUND (LOCAL IMAGE)
# ==============================
def set_bg():
    st.markdown("""
    <style>
    .stApp {
        background-image: url("./karnataka_bg.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .block-container {
        background-color: rgba(0,0,0,0.6);
        padding: 2rem;
        border-radius: 12px;
    }
    h1, h2, h3, p, div {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🤖 MODEL (LIGHTWEIGHT)
# ==============================
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis")

sentiment_model = load_model()

# ==============================
# SESSION STATE
# ==============================
if "lang" not in st.session_state:
    st.session_state.lang = None
if "user_text" not in st.session_state:
    st.session_state.user_text = ""
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

# ==============================
# UI
# ==============================
st.set_page_config(page_title="SAMVAAD AI", layout="centered")
set_bg()
title_text = {
    "en": "🏛️ SAMVAAD AI - Karnataka Government",
    "hi": "🏛️ संवाद एआई - कर्नाटक सरकार",
    "kn": "🏛️ ಸಂವಾದ ಎಐ - ಕರ್ನಾಟಕ ಸರ್ಕಾರ"
}

if st.session_state.lang is None:
    st.title("🏛️ SAMVAAD AI")
else:
    title_text = {
        "en": "🏛️ SAMVAAD AI",
        "hi": "🏛️ संवाद एआई",
        "kn": "🏛️ ಸಂವಾದ ಎಐ"
    }
    st.title(title_text[st.session_state.lang])

# ==============================
# 🌍 LANGUAGE SELECTION
# ==============================
if st.session_state.lang is None:

    # 🔊 WELCOME VOICE (ADDED)
    if "welcome_played" not in st.session_state:

        en_audio = gTTS("Welcome to 1092 helpline. Please choose your language.", lang="en")
        hi_audio = gTTS("1092 हेल्पलाइन में आपका स्वागत है। कृपया अपनी भाषा चुनें।", lang="hi")
        kn_audio = gTTS("1092 ಸಹಾಯವಾಣಿ ಗೆ ಸ್ವಾಗತ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ.", lang="kn")

        en_audio.save("en.mp3")
        hi_audio.save("hi.mp3")
        kn_audio.save("kn.mp3")

        def get_b64(file):
            with open(file, "rb") as f:
                return base64.b64encode(f.read()).decode()

        en_b64 = get_b64("en.mp3")
        hi_b64 = get_b64("hi.mp3")
        kn_b64 = get_b64("kn.mp3")

        components.html(f"""
        <audio id="a1" autoplay>
            <source src="data:audio/mp3;base64,{en_b64}">
        </audio>
        <audio id="a2">
            <source src="data:audio/mp3;base64,{hi_b64}">
        </audio>
        <audio id="a3">
            <source src="data:audio/mp3;base64,{kn_b64}">
        </audio>
        <script>
            const a1 = document.getElementById("a1");
            const a2 = document.getElementById("a2");
            const a3 = document.getElementById("a3");
            a1.onended = () => a2.play();
            a2.onended = () => a3.play();
        </script>
        """, height=0)

        st.session_state.welcome_played = True

    st.subheader("🌍 Select Language / भाषा चुने / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ")

    lang_choice = st.radio("", ["English", "Hindi", "Kannada"])

    if st.button("Confirm Language"):
        if lang_choice == "English":
            st.session_state.lang = "en"
        elif lang_choice == "Hindi":
            st.session_state.lang = "hi"
        else:
            st.session_state.lang = "kn"
        st.rerun()

# ==============================
# MAIN APP
# ==============================
else:
    lang = st.session_state.lang

    # 🔊 INSTRUCTION VOICE (ADDED)
    if "instruction_played" not in st.session_state:
        instruction_voice = {
            "en": "Please convey your problem by pressing speak or else enter your problem.",
            "hi": "कृपया 'स्पीक' बटन दबाकर अपनी समस्या बताएं या फिर अपनी समस्या दर्ज करें।",
            "kn": "ದಯವಿಟ್ಟು ಮಾತನಾಡುತ್ತಾರೆ ಒತ್ತುವ ಮೂಲಕ ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ತಿಳಿಸಿ, ಇಲ್ಲದಿದ್ದರೆ ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ನಮೂದಿಸಿ."
        }
        play_audio(instruction_voice[lang], lang)
        st.session_state.instruction_played = True

    # ==============================
    # 🎤 VOICE INPUT
    # ==============================
    speak_text = {
        "en": "🎤 Speak",
        "hi": "🎤 स्पीक",
        "kn": "🎤 ಮಾತನಾಡಿ"
    }
    
    voice_data = components.html(f"""
    <script>
    function startSpeech() {{
        var recognition = new webkitSpeechRecognition();
        recognition.lang = "{lang}-IN";
        recognition.start();
        recognition.onresult = function(event) {{
            let text = event.results[0][0].transcript;
            const textAreas = window.parent.document.querySelectorAll('textarea');
            if (textAreas.length > 0) {{
                let textarea = textAreas[0];
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, "value"
                ).set;
                nativeInputValueSetter.call(textarea, text);
                textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            window.parent.postMessage({{
                type: "streamlit:setComponentValue",
                value: text
            }}, "*");
        }};
    }}
    </script>
    <button onclick="startSpeech()" style="padding:10px;font-size:16px;">
    {speak_text[lang]}
    </button>
    """, height=100)

    if isinstance(voice_data, str) and voice_data.strip() != "":
        st.session_state.user_text = voice_data

    # ==============================
    # TEXT INPUT
    # ==============================
    input_text = {
        "en": "Enter your problem",
        "hi": "अपनी समस्या दर्ज करें",
        "kn": "ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ನಮೂದಿಸಿ"
    }

    user_input = st.text_area(
        input_text[lang],
        value=st.session_state.get("user_text", "")
    )

    st.session_state.user_text = user_input

    # ==============================
    # ANALYZE
    # ==============================
    if st.button("Analyze"):
        text = user_input.strip()
        if text == "":
            st.warning("Please enter your problem")
        else:
            sentiment = sentiment_model(text)[0]["label"]
            st.session_state.analyzed = True
            st.session_state.sentiment = sentiment

# ==============================
# RESULT (SMART GOVERNMENT ANALYSIS)
# ==============================
if st.session_state.analyzed:

    text = st.session_state.user_text.lower()

    if any(word in text for word in ["fire", "accident", "police", "theft", "hospital", "emergency", "ambulance","heart","atack"]):
        category = "emergency"
    else:
        category = "normal"

    dept = "General"

    if any(word in text for word in ["electricity", "power", "current", "light","powercut"]):
        dept = "Electricity Department"
    elif any(word in text for word in ["water", "drain", "sewage","dustbin"]):
        dept = "Municipal / Water Department"
    elif any(word in text for word in ["road", "street", "pothole"]):
        dept = "Roads & Buildings"
    elif any(word in text for word in ["ration", "card"]):
        dept = "Ration Department"
    elif any(word in text for word in ["bus", "transport"]):
        dept = "Transport Department"
    elif any(word in text for word in ["fire","gas","blast"]):
        dept = "Fire Department"
    elif any(word in text for word in ["police", "theft","robbery","murder","kidnap","cybercrime"]):
        dept = "Police Department"
    elif any(word in text for word in ["hospital", "health","ill"]):
        dept = "Health Department"

    dept_map = {
        "en": dept,
        "hi": {
            "Electricity Department": "बिजली विभाग",
            "Municipal / Water Department": "जल / नगर निगम विभाग",
            "Roads & Buildings": "सड़क और भवन विभाग",
            "Ration Department": "राशन विभाग",
            "Transport Department": "परिवहन विभाग",
            "Fire Department": "अग्निशमन विभाग",
            "Police Department": "पुलिस विभाग",
            "Health Department": "स्वास्थ्य विभाग",
            "General": "सामान्य"
        }.get(dept, dept),
        "kn": {
            "Electricity Department": "ವಿದ್ಯುತ್ ಇಲಾಖೆ",
            "Municipal / Water Department": "ನೀರು / ನಗರಸಭೆ",
            "Roads & Buildings": "ರಸ್ತೆ ಮತ್ತು ಕಟ್ಟಡ",
            "Ration Department": "ರೇಷನ್ ಇಲಾಖೆ",
            "Transport Department": "ಸಾರಿಗೆ ಇಲಾಖೆ",
            "Fire Department": "ಅಗ್ನಿಶಾಮಕ ಇಲಾಖೆ",
            "Police Department": "ಪೊಲೀಸ್ ಇಲಾಖೆ",
            "Health Department": "ಆರೋಗ್ಯ ಇಲಾಖೆ",
            "General": "ಸಾಮಾನ್ಯ"
        }.get(dept, dept)
    }

    dept = dept_map[lang]

    output_text = {
        "en": {"title": "📊 Problem Analysis","type": "Case Type","dept": "Department","summary": "Issue Summary"},
        "hi": {"title": "📊 समस्या विश्लेषण","type": "मामले का प्रकार","dept": "विभाग","summary": "समस्या विवरण"},
        "kn": {"title": "📊 ಸಮಸ್ಯೆ ವಿಶ್ಲೇಷಣೆ","type": "ಕೇಸ್ ಪ್ರಕಾರ","dept": "ವಿಭಾಗ","summary": "ಸಮಸ್ಯೆಯ ವಿವರ"}
    }

    st.subheader(output_text[lang]["title"])

    st.write(f"**{output_text[lang]['summary']}:** {st.session_state.user_text}")
    case_map = {
        "en": {"emergency": "Emergency", "normal": "Normal"},
        "hi": {"emergency": "आपातकालीन", "normal": "सामान्य"},
        "kn": {"emergency": "ತುರ್ತು", "normal": "ಸಾಮಾನ್ಯ"}
    }

    st.write(f"**{output_text[lang]['type']}:** {case_map[lang][category]}")
    st.write(f"**{output_text[lang]['dept']}:** {dept}")

    # 🔥 COMPLAINT ID (ADDED)
    if "complaint_id" not in st.session_state:
        st.session_state.complaint_id = "1092-" + str(random.randint(100000, 999999))

    cid_text = {
        "en": "Complaint ID",
        "hi": "शिकायत आईडी",
        "kn": "ದೂರು ಐಡಿ"
    }

    st.write(f"{cid_text[lang]}: {st.session_state.complaint_id}")
    # ==============================
    # CONFIRMATION
    # ==============================
    confirm_text = {
        "en": {"question": "Do you want to raise this complaint?","yes": "Yes","no": "No","success": "Your problem has been sent to the concerned authority. They will contact you shortly.","cancel": "Complaint not submitted."},
        "hi": {"question": "क्या आप इस शिकायत को दर्ज करना चाहते हैं?","yes": "हाँ","no": "नहीं","success": "आपकी समस्या संबंधित प्राधिकरण को भेज दी गई है। वे जल्द ही आपसे संपर्क करेंगे।","cancel": "शिकायत दर्ज नहीं की गई।"},
        "kn": {"question": "ನೀವು ಈ ದೂರನ್ನು ಸಲ್ಲಿಸಲು ಬಯಸುವಿರಾ?","yes": "ಹೌದು","no": "ಇಲ್ಲ","success": "ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ಸಂಬಂಧಿತ ಅಧಿಕಾರಿಗೆ ಕಳುಹಿಸಲಾಗಿದೆ. ಅವರು ಶೀಘ್ರದಲ್ಲೇ ನಿಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸುತ್ತಾರೆ.","cancel": "ದೂರು ಸಲ್ಲಿಸಲಾಗಿಲ್ಲ."}
    }

    

    # 🔊 CONFIRMATION VOICE (ADDED)
    if "confirm_voice" not in st.session_state:
        play_audio(confirm_text[lang]["question"], lang)
        st.session_state.confirm_voice = True

    choose_text = {
        "en": "Choose one",
        "hi": "एक विकल्प चुनें",
        "kn": "ಒಂದು ಆಯ್ಕೆಮಾಡಿ"
    }

    options = [
        choose_text[lang],
        confirm_text[lang]["yes"],
        confirm_text[lang]["no"]
    ]

    choice = st.radio(
        confirm_text[lang]["question"],
        options,
        index=0
    )

    if choice == confirm_text[lang]["yes"]:
        st.success(confirm_text[lang]["success"])
        play_audio(confirm_text[lang]["success"], lang)

    elif choice == confirm_text[lang]["no"]:
        st.warning(confirm_text[lang]["cancel"])
        play_audio(confirm_text[lang]["cancel"], lang)
