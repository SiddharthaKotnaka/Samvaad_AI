import streamlit as st
from transformers import pipeline
import base64
import streamlit.components.v1 as components
from gtts import gTTS
import random
import time
import base64
import os
import sqlite3
from datetime import datetime
import pandas as pd

# ==============================
# 🗄 DATABASE CONNECTION
# ==============================

conn = sqlite3.connect("samvaad_ai.db", check_same_thread=False)

cursor = conn.cursor()

# ==============================
# 📋 CREATE TABLE
# ==============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT,
    complaint_text TEXT,
    language TEXT,
    department TEXT,
    case_type TEXT,
    ip_address TEXT,
    location TEXT,
    timestamp TEXT
)
""")

conn.commit()

# ==============================
# 🔊 AUDIO FUNCTION (ADDED)
# ==============================
def play_audio(text, lang="en"):

    try:

        filename = "temp_audio.mp3"

        tts = gTTS(text=text, lang=lang)
        tts.save(filename)

        audio_file = open(filename, "rb")
        audio_bytes = audio_file.read()

        b64 = base64.b64encode(audio_bytes).decode()

        audio_html = f'''
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        '''

        st.markdown(audio_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Audio Error: {e}")

# ==============================
# 🌄 BACKGROUND (LOCAL IMAGE)
# ==============================
def set_bg():

    with open("karnataka_bg.jpg", "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Main App Background */
        .stApp {{
            background: linear-gradient(
                rgba(0,0,0,0.45),
                rgba(0,0,0,0.45)
            ),
            url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Blur Layer */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            z-index: 0;
        }}
        /* Main Container */
        .main .block-container {{
            position: relative;
            z-index: 1;
            max-width: 700px;
            margin-top: 40px;
            margin-bottom: 40px;
            background: rgba(0, 0, 0, 0.65);
            padding: 3rem;
            border-radius: 25px;
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }}
        /* Text */
        h1, h2, h3, h4, h5, h6, p, div, label {{
            color: white !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
        }}
        /* Title */
        h1 {{
            text-align: center;
            font-size: 52px !important;
            font-weight: 800 !important;
        }}
        /* Buttons */
        .stButton>button {{
            width: 100%;
            border-radius: 14px;
            height: 50px;
            font-size: 18px;
            font-weight: bold;
            background-color: #1f4e79;
            color: white;
            border: none;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #2563eb;
            color: white;
        }}
        /* Radio Buttons */
        .stRadio label {{
            font-size: 18px !important;
        }}
        /* Text Area */
        textarea {{
            border-radius: 15px !important;
            background-color: rgba(255,255,255,0.08) !important;
            color: white !important;
            font-size: 17px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

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

# ✅ ADD THIS
if "language_confirmed" not in st.session_state:
    st.session_state.language_confirmed = False


# ==============================
# 🔐 ADMIN SESSION
# ==============================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "admin_page" not in st.session_state:
    st.session_state.admin_page = False

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

if not st.session_state.language_confirmed:

    # MAIN TITLE
    st.title("🏛️ SAMVAAD AI")

    # SUBTITLE
    st.markdown(
        """
        <h4 style='text-align:center;color:white;'>
        AI Powered Government Complaint & Emergency Assistance System
        </h4>
        """,
        unsafe_allow_html=True
    )

    # SMALL CAPTION
    st.markdown(
        """
        <p style='text-align:center;color:#d1d5db;font-size:16px;'>
        Government of Karnataka SamvaadAI Prototype
        </p>
        """,
        unsafe_allow_html=True
    )

else:

    title_text = {
        "en": "🏛️ SAMVAAD AI",
        "hi": "🏛️ संवाद एआई",
        "kn": "🏛️ ಸಂವಾದ ಎಐ"
    }

    current_lang = st.session_state.get("lang", "en")

    if current_lang is None:
        current_lang = "en"

    st.title(title_text[current_lang])

# ==============================
# 📊 PROFESSIONAL ADMIN DASHBOARD
# ==============================

if st.session_state.admin_logged_in:

    st.markdown("""
    <style>
    [data-testid="stDataFrame"] {
        background-color: rgba(0,0,0,0.6);
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📊 SAMVAAD AI Dashboard")

    # ==============================
    # TOP BUTTONS
    # ==============================

    col1, col2 = st.columns(2)

    with col1:

        if st.button("🏠 Home"):

            st.session_state.admin_logged_in = False
            st.session_state.admin_page = False

            st.rerun()

    with col2:

        if st.button("🚪 Logout"):

            st.session_state.admin_logged_in = False
            st.session_state.admin_page = False

            st.rerun()

    st.markdown("---")

    # ==============================
    # DATABASE DATA
    # ==============================

    columns = [

        "ID",
        "Complaint ID",
        "Complaint Text",
        "Language",
        "Department",
        "Case Type",
        "IP Address",
        "Location",
        "Timestamp"
    ]

    # ==============================
    # 🚨 EMERGENCY COMPLAINTS
    # ==============================

    st.subheader("🚨 Emergency Complaints")

    emergency_data = cursor.execute("""
    SELECT * FROM complaints
    WHERE case_type='emergency'
    """).fetchall()

    emergency_df = pd.DataFrame(emergency_data, columns=columns)

    edited_emergency_df = st.data_editor(
        emergency_df,

        use_container_width=True,
        num_rows="dynamic",

        key="emergency_editor",

        column_config={

            "ID": st.column_config.NumberColumn(
                "ID",
                disabled=True
            ),

            "Complaint ID": st.column_config.TextColumn(
                "Complaint ID"
            ),

            "Complaint Text": st.column_config.TextColumn(
                "Complaint Text",
                width="large"
            ),

            "Language": st.column_config.SelectboxColumn(
                "Language",
                options=["en", "hi", "kn"]
            ),

            "Department": st.column_config.TextColumn(
                "Department"
            ),

            "Case Type": st.column_config.SelectboxColumn(
                "Case Type",
                options=["normal", "emergency"]
            ),

            "IP Address": st.column_config.TextColumn(
                "IP Address"
            ),

            "Location": st.column_config.TextColumn(
                "Location"
            ),

            "Timestamp": st.column_config.TextColumn(
                "Timestamp"
            )
        }
    )

    st.markdown("---")

    # ==============================
    # 📝 NORMAL COMPLAINTS
    # ==============================

    st.subheader("📝 Normal Complaints")

    normal_data = cursor.execute("""
    SELECT * FROM complaints
    WHERE case_type='normal'
    """).fetchall()

    normal_df = pd.DataFrame(normal_data, columns=columns)

    edited_normal_df = st.data_editor(
        normal_df,

        use_container_width=True,
        num_rows="dynamic",

        key="normal_editor",

        column_config={

            "ID": st.column_config.NumberColumn(
                "ID",
                disabled=True
            ),

            "Complaint ID": st.column_config.TextColumn(
                "Complaint ID"
            ),

            "Complaint Text": st.column_config.TextColumn(
                "Complaint Text",
                width="large"
            ),

            "Language": st.column_config.SelectboxColumn(
                "Language",
                options=["en", "hi", "kn"]
            ),

            "Department": st.column_config.TextColumn(
                "Department"
            ),

            "Case Type": st.column_config.SelectboxColumn(
                "Case Type",
                options=["normal", "emergency"]
            ),

            "IP Address": st.column_config.TextColumn(
                "IP Address"
            ),

            "Location": st.column_config.TextColumn(
                "Location"
            ),

            "Timestamp": st.column_config.TextColumn(
                "Timestamp"
            )
        }
    )

    # ==============================
    # DASHBOARD SUMMARY
    # ==============================

    st.markdown("---")

    total_cases = len(emergency_df) + len(normal_df)

    col1, col2, col3 = st.columns(3)

    col1.metric("🚨 Emergency Cases", len(emergency_df))

    col2.metric("📝 Normal Cases", len(normal_df))

    col3.metric("📦 Total Complaints", total_cases)

    st.stop()

# ==============================
# 🌍 LANGUAGE SELECTION
# ==============================
if not st.session_state.language_confirmed:

    # ==============================
    # 🔐 ADMIN LOGIN PAGE
    # ==============================

    if st.session_state.admin_page:

        st.title("🔐 SAMVAAD AI Admin Login")

        if st.button("🏠 Back"):

            st.session_state.admin_page = False

            st.rerun()

        username = st.text_input("Username")

        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username == "admin" and password == "samvaad123":

                st.session_state.admin_logged_in = True

                # IMPORTANT
                st.session_state.admin_page = False

                st.success("Login Successful")

                st.rerun()

            else:

                st.error("Invalid Username or Password")

        st.stop()

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

    lang_choice = st.radio("", ["English", "हिंदी", "ಕನ್ನಡ"])

    if st.button("Confirm Language"):

        if lang_choice == "English":
            st.session_state.lang = "en"

            play_audio(
                "English language selected. You can now use the speak button or type your complaint.",
                "en"
            )

        elif lang_choice == "हिंदी":
            st.session_state.lang = "hi"

            play_audio(
                "हिंदी भाषा चुनी गई है। अब आप बोल सकते हैं या अपनी शिकायत लिख सकते हैं।",
                "hi"
            )

        else:
            st.session_state.lang = "kn"

            play_audio(
                "ಕನ್ನಡ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ. ಈಗ ನೀವು ಮಾತನಾಡಬಹುದು ಅಥವಾ ನಿಮ್ಮ ದೂರನ್ನು ಟೈಪ್ ಮಾಡಬಹುದು.",
                "kn"
            )

        success_text = {
            "en": "Language Selected Successfully",
            "hi": "भाषा सफलतापूर्वक चुनी गई",
            "kn": "ಭಾಷೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ"
        }
        
        st.success(success_text[st.session_state.lang])

        import time

        # wait for audio to finish
        if st.session_state.lang == "en":
            time.sleep(6)
        
        elif st.session_state.lang == "hi":
            time.sleep(7)
        
        elif st.session_state.lang == "kn":
            time.sleep(9)

        # auto redirect
        st.session_state.language_confirmed = True

        st.rerun()

    # ==============================
    # 🔐 ADMIN LOGIN BUTTON
    # ==============================

    st.markdown("---")

    if st.button("🔐 Admin Login"):

        st.session_state.admin_page = True

        st.rerun()


        st.subheader("🚨 Emergency Complaints")

        emergency_data = cursor.execute("""
        SELECT * FROM complaints
        WHERE case_type='emergency'
        """).fetchall()

        import pandas as pd

        columns = [

            "ID",
            "Complaint ID",
            "Complaint Text",
            "Language",
            "Department",
            "Case Type",
            "IP Address",
            "Location",
            "Timestamp"

        ]

        emergency_df = pd.DataFrame(emergency_data, columns=columns)

        st.dataframe(emergency_df)

        st.subheader("📝 Normal Complaints")

        normal_data = cursor.execute("""
        SELECT * FROM complaints
        WHERE case_type='normal'
        """).fetchall()

        normal_df = pd.DataFrame(normal_data, columns=columns)

        st.dataframe(normal_df)

        st.stop()

# ==============================
# MAIN APP
# ==============================
else: 

    home_btn_text = {
        "en": "🏠 Home",
        "hi": "🏠 होम",
        "kn": "🏠 ಮುಖಪುಟ"
    }
    
    analyze_btn_text = {
        "en": "Analyze",
        "hi": "विश्लेषण",
        "kn": "ವಿಶ್ಲೇಷಿಸಿ"
    }

    # ==============================
    # 🏠 BACK BUTTON
    # ==============================

    if st.button(home_btn_text[st.session_state.lang], key="home_btn"):

        st.session_state.lang = None
        st.session_state.user_text = ""
        st.session_state.analyzed = False
        st.session_state.language_confirmed = False
    
        if "complaint_id" in st.session_state:
            del st.session_state["complaint_id"]
    
        if "confirm_voice" in st.session_state:
            del st.session_state["confirm_voice"]
    
        if "instruction_played" in st.session_state:
            del st.session_state["instruction_played"]
    
        if "welcome_played" in st.session_state:
            del st.session_state["welcome_played"]
    
        st.rerun()

    lang = st.session_state.get("lang")

    if lang is None:
        st.stop()

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
    if st.button(analyze_btn_text[st.session_state.lang]):
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

    # ==============================
    # 🚨 EMERGENCY DETECTION
    # ==============================

    emergency_keywords = [

        # FIRE
        "fire", "आग", "ಬೆಂಕಿ",

        # ACCIDENT
        "accident", "दुर्घटना", "ಅಪಘಾತ",

        # AMBULANCE
        "ambulance", "एम्बुलेंस", "ಆಂಬ್ಯುಲೆನ್ಸ್",

        # HEART ATTACK
        "heart attack", "दिल का दौरा", "ಹೃದಯಾಘಾತ",

        # MURDER
        "murder", "हत्या", "ಕೊಲೆ",

        # KIDNAP
        "kidnap", "अपहरण", "ಅಪಹರಣ",

        # ROBBERY/THEFT
        "robbery", "theft",
        "चोरी", "डकैती",
        "ಕಳ್ಳತನ", "ದರೋಡೆ",

        # BLOOD / INJURY
        "blood", "injury",
        "खून", "चोट",
        "ರಕ್ತ", "ಗಾಯ",

        # GAS LEAK
        "gas leak", "गैस रिसाव", "ಗ್ಯಾಸ್ ಸೋರಿಕೆ",

        # FLOOD
        "flood", "बाढ़", "ನೆರೆ",

        # EARTHQUAKE
        "earthquake", "भूकंप", "ಭೂಕಂಪ",

        # CRIME
        "crime", "अपराध", "ಅಪರಾಧ",

        # CYBERCRIME
        "cybercrime", "साइबर अपराध", "ಸೈಬರ್ ಅಪರಾಧ",

        # HARASSMENT
        "harassment", "उत्पीड़न", "ಉತ್ಪೀಡನೆ",

        # WOMEN SAFETY
        "women safety", "महिला सुरक्षा", "ಮಹಿಳಾ ಸುರಕ್ಷತೆ",

        # MISSING
        "missing", "लापता", "ಕಾಣೆಯಾಗಿದೆ"
    ]

    if any(word in text for word in emergency_keywords):
        category = "emergency"
    else:
        category = "normal"

    # ==============================
    # 🏢 DEPARTMENT ROUTING
    # ==============================

    dept = "General Department"

    # ==============================
    # ⚡ ELECTRICITY
    # ==============================

    if any(word in text for word in [

            # English
            "electricity", "power", "current",
            "light", "powercut", "transformer",
            "wire", "electric pole", "short circuit",
            "voltage", "eb bill", "shock",
            "electric spark", "no current",

            # Hindi
            "बिजली", "करंट", "लाइट",
            "ट्रांसफार्मर", "शॉर्ट सर्किट",
            "तार", "बिजली बिल", "झटका",

            # Kannada
            "ವಿದ್ಯುತ್", "ಕರಂಟ್", "ಲೈಟ್",
            "ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್", "ಶಾರ್ಟ್ ಸರ್ಕ್ಯೂಟ್",
            "ತಂತಿ", "ವಿದ್ಯುತ್ ಬಿಲ್", "ಶಾಕ್"

        ]):
            dept = "Electricity Department"
    
    # ==============================
    # 🔥 FIRE
    # ==============================

    elif any(word in text for word in [

        # English
        "fire", "gas leak", "gas leakage", "blast",
        "smoke", "burn", "cylinder",
        "explosion", "short circuit fire",

        # Hindi
        "आग", "गैस", "धमाका",
        "धुआं", "जलना", "सिलेंडर",
        "विस्फोट",

        # Kannada
        "ಬೆಂಕಿ", "ಗ್ಯಾಸ್", "ಸ್ಫೋಟ",
        "ಹೊಗೆ", "ಸುಟ್ಟು", "ಸಿಲಿಂಡರ್",
        "ವಿಸ್ಫೋಟ"

    ]):
        dept = "Fire Department"

    # ==============================
    # 💧 WATER / MUNICIPAL
    # ==============================

    elif any(word in text for word in [

        # English
        "water", "drain", "drainage",
        "sewage", "dustbin", "garbage",
        "water leakage", "pipeline", "dirty water",
        "water problem", "overflow",
        "sanitation", "waste", "municipality",
        "water tank", "public toilet",

        # Hindi
        "पानी", "नाली", "जल निकासी",
        "सीवेज", "कचरा", "लीकेज",
        "पाइपलाइन", "गंदा पानी",
        "सफाई", "नगरपालिका",
        "सार्वजनिक शौचालय",

        # Kannada
        "ನೀರು", "ಚರಂಡಿ", "ನೀರಿನ ಸಮಸ್ಯೆ",
        "ಮಲಿನ ನೀರು", "ಕಸ", "ಸೋರಿಕೆ",
        "ಪೈಪ್‌ಲೈನ್", "ಸ್ವಚ್ಛತೆ",
        "ನಗರಸಭೆ", "ಸಾರ್ವಜನಿಕ ಶೌಚಾಲಯ"

    ]):
        dept = "Municipal / Water Department"

    # ==============================
    # 🛣 ROADS
    # ==============================

    elif any(word in text for word in [

        # English
        "road", "street", "pothole",
        "bridge", "highway", "traffic road",
        "damaged road", "road crack",
        "streetlight", "footpath",
        "signal problem",

        # Hindi
        "सड़क", "गड्ढा", "पुल",
        "हाईवे", "टूटी सड़क",
        "स्ट्रीटलाइट", "फुटपाथ",
        "सिग्नल समस्या",

        # Kannada
        "ರಸ್ತೆ", "ಗುಂಡಿ", "ಸೇತುವೆ",
        "ಹೆದ್ದಾರಿ", "ಹಾಳಾದ ರಸ್ತೆ",
        "ರಸ್ತೆ ದೀಪ", "ಫುಟ್‌ಪಾತ್",
        "ಸಿಗ್ನಲ್ ಸಮಸ್ಯೆ"

    ]):
        dept = "Roads & Buildings Department"

    # ==============================
    # 🍚 RATION
    # ==============================

    elif any(word in text for word in [

        # English
        "ration", "card", "rice",
        "food supply", "pds", "ration shop",
        "food grains", "aadhar link",
        "subsidy",

        # Hindi
        "राशन", "कार्ड", "चावल",
        "खाद्य आपूर्ति", "सब्सिडी",
        "राशन दुकान",

        # Kannada
        "ರೇಷನ್", "ಕಾರ್ಡ್", "ಅಕ್ಕಿ",
        "ಆಹಾರ ಸರಬರಾಜು", "ಸಬ್ಸಿಡಿ",
        "ರೇಷನ್ ಅಂಗಡಿ"

    ]):
        dept = "Ration Department"

    # ==============================
    # 🚌 TRANSPORT
    # ==============================

    elif any(word in text for word in [

        # English
        "bus", "transport", "rtc",
        "metro", "train", "auto",
        "traffic", "vehicle", "driver",
        "license", "accident vehicle",
        "bike", "car", "truck",

        # Hindi
        "बस", "परिवहन", "मेट्रो",
        "ट्रेन", "ऑटो", "यातायात",
        "वाहन", "ड्राइवर",
        "लाइसेंस", "कार", "ट्रक",

        # Kannada
        "ಬಸ್", "ಸಾರಿಗೆ", "ಮೆಟ್ರೋ",
        "ರೈಲು", "ಆಟೋ", "ಟ್ರಾಫಿಕ್",
        "ವಾಹನ", "ಚಾಲಕ",
        "ಲೈಸೆನ್ಸ್", "ಕಾರ್", "ಟ್ರಕ್"

    ]):
        dept = "Transport Department"

    # ==============================
    # 🏥 HEALTH
    # ==============================

    elif any(word in text for word in [

        # English
        "hospital", "health", "ill",
        "fever", "covid", "doctor",
        "ambulance", "medicine", "panic attack",
        "heart attack", "injury",
        "blood", "virus", "infection",
        "food poisoning", "pregnancy",
        "emergency health",

        # Hindi
        "अस्पताल", "स्वास्थ्य", "बीमार",
        "बुखार", "कोविड", "डॉक्टर",
        "एम्बुलेंस", "दवा",
        "दिल का दौरा", "चोट",
        "खून", "संक्रमण",
        "गर्भावस्था",

        # Kannada
        "ಆಸ್ಪತ್ರೆ", "ಆರೋಗ್ಯ", "ಅನಾರೋಗ್ಯ",
        "ಜ್ವರ", "ಕೋವಿಡ್", "ಡಾಕ್ಟರ್",
        "ಆಂಬ್ಯುಲೆನ್ಸ್", "ಔಷಧಿ",
        "ಹೃದಯಾಘಾತ", "ಗಾಯ",
        "ರಕ್ತ", "ಸಂಕ್ರಮಣ",
        "ಗರ್ಭಧಾರಣೆ"

    ]):
        dept = "Health Department"

    # ==============================
    # 👮 POLICE
    # ==============================

    elif any(word in text for word in [

        # English
        "police", "theft", "robbery",
        "murder", "kidnap", "cybercrime",
        "fraud", "violence", "rape",
        "harassment",
        "fight", "drugs", "crime",
        "mobile stolen", "chain snatching",
        "missing", "terrorist",

        # Hindi
        "पुलिस", "चोरी", "डकैती",
        "हत्या", "अपहरण", "साइबर अपराध",
        "धोखाधड़ी", "हिंसा", "बलात्कार",
        "उत्पीड़न", "हमला",
        "लड़ाई", "अपराध",
        "मोबाइल चोरी", "लापता",

        # Kannada
        "ಪೊಲೀಸ್", "ಕಳ್ಳತನ", "ದರೋಡೆ",
        "ಕೊಲೆ", "ಅಪಹರಣ", "ಸೈಬರ್ ಅಪರಾಧ",
        "ಮೋಸ", "ಹಿಂಸೆ", "ಅತ್ಯಾಚಾರ",
        "ಉತ್ಪೀಡನೆ", "ದಾಳಿ",
        "ಜಗಳ", "ಅಪರಾಧ",
        "ಮೊಬೈಲ್ ಕಳ್ಳತನ", "ಕಾಣೆಯಾಗಿದೆ"

    ]):
        dept = "Police Department"

    # ==============================
    # 🌾 AGRICULTURE
    # ==============================

    elif any(word in text for word in [

        # English
        "farmer", "crop", "agriculture",
        "fertilizer", "pesticide",
        "farm", "crop damage",
        "irrigation", "tractor",

        # Hindi
        "किसान", "फसल", "कृषि",
        "उर्वरक", "कीटनाशक",
        "खेती", "सिंचाई", "ट्रैक्टर",

        # Kannada
        "ರೈತ", "ಬೆಳೆ", "ಕೃಷಿ",
        "ರಸಗೊಬ್ಬರ", "ಕೀಟನಾಶಕ",
        "ಕೃಷಿ ಭೂಮಿ", "ನೀರಾವರಿ",
        "ಟ್ರಾಕ್ಟರ್"

    ]):
        dept = "Agriculture Department"

    # ==============================
    # 🏫 EDUCATION
    # ==============================

    elif any(word in text for word in [

        # English
        "school", "college", "teacher",
        "student", "exam", "scholarship",
        "education", "classroom",

        # Hindi
        "स्कूल", "कॉलेज", "शिक्षक",
        "छात्र", "परीक्षा", "छात्रवृत्ति",
        "शिक्षा", "कक्षा",

        # Kannada
        "ಶಾಲೆ", "ಕಾಲೇಜು", "ಶಿಕ್ಷಕ",
        "ವಿದ್ಯಾರ್ಥಿ", "ಪರೀಕ್ಷೆ", "ವಿದ್ಯಾರ್ಥಿವೇತನ",
        "ಶಿಕ್ಷಣ", "ತರಗತಿ"

    ]):
        dept = "Education Department"

    # ==============================
    # 🌳 FOREST
    # ==============================

    elif any(word in text for word in [

        # English
        "forest", "tree", "wild animal",
        "deforestation", "animal attack",
        "forest fire",

        # Hindi
        "जंगल", "पेड़", "जंगली जानवर",
        "वन कटाई", "जानवर हमला",
        "जंगल में आग",

        # Kannada
        "ಕಾಡು", "ಮರ", "ಕಾಡು ಪ್ರಾಣಿ",
        "ಅರಣ್ಯ ನಾಶ", "ಪ್ರಾಣಿ ದಾಳಿ",
        "ಕಾಡ್ಗಿಚ್ಚು"

    ]):
        dept = "Forest Department"
    
    dept_map = {
        "en": dept,
        "hi": {
            "Electricity Department": "बिजली विभाग",
            "Municipal / Water Department": "जल / नगर निगम विभाग",
            "Roads & Buildings Department": "सड़क और भवन विभाग",
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

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ip_address = "Local User"

        location = "Karnataka"

        cursor.execute("""
        INSERT INTO complaints (
            complaint_id,
            complaint_text,
            language,
            department,
            case_type,
            ip_address,
            location,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            st.session_state.complaint_id,
            st.session_state.user_text,
            lang,
            dept,
            category,
            ip_address,
            location,
            timestamp

        ))

        conn.commit()

        # 🔥 NORMAL CASE AUDIO ONLY
        if category != "emergency":

            play_audio(confirm_text[lang]["success"], lang)

        # ==============================
        # 🚨 SMART EMERGENCY RESPONSE
        # ==============================

        emergency_response = ""
        emergency_tips = []
        emergency_number = ""

        # ❤️ HEART ATTACK
        if any(word in text for word in [

            "heart attack", "दिल का दौरा", "ಹೃದಯಾಘಾತ"

        ]):

            emergency_response = {
                "en": "Medical emergency detected. Ambulance support required immediately.",
                "hi": "चिकित्सा आपातकाल का पता चला। तुरंत एम्बुलेंस सहायता आवश्यक है।",
                "kn": "ವೈದ್ಯಕೀಯ ತುರ್ತು ಪರಿಸ್ಥಿತಿ ಪತ್ತೆಯಾಗಿದೆ. ತಕ್ಷಣ ಆಂಬ್ಯುಲೆನ್ಸ್ ಸಹಾಯ ಅಗತ್ಯವಿದೆ."
            }[lang]
            
            emergency_number = {
                "en": "108 Ambulance",
                "hi": "108 एम्बुलेंस",
                "kn": "108 ಆಂಬ್ಯುಲೆನ್ಸ್"
            }[lang]
            
            emergency_tips = {
                "en": [
                    "Keep the patient calm and seated.",
                    "Loosen tight clothes.",
                    "Call ambulance immediately.",
                    "If unconscious, check breathing."
                ],
            
                "hi": [
                    "रोगी को शांत रखें और बैठाएं।",
                    "तंग कपड़े ढीले करें।",
                    "तुरंत एम्बुलेंस बुलाएं।",
                    "यदि बेहोश है तो सांस जांचें।"
                ],
            
                "kn": [
                    "ರೋಗಿಯನ್ನು ಶಾಂತವಾಗಿರಿಸಿ ಕುಳ್ಳಿರಿಸಿ.",
                    "ಬಿಗಿಯಾದ ಬಟ್ಟೆಗಳನ್ನು ಸಡಿಲಗೊಳಿಸಿ.",
                    "ತಕ್ಷಣ ಆಂಬ್ಯುಲೆನ್ಸ್ ಕರೆಮಾಡಿ.",
                    "ಅಚೇತನವಾಗಿದ್ದರೆ ಉಸಿರಾಟ ಪರಿಶೀಲಿಸಿ."
                ]
            }[lang]

        # 🔥 FIRE
        elif any(word in text for word in [

            "fire", "आग", "ಬೆಂಕಿ"

        ]):

            emergency_response = {
                "en": "Fire emergency detected.",
                "hi": "आग की आपात स्थिति का पता चला।",
                "kn": "ಬೆಂಕಿ ತುರ್ತು ಪರಿಸ್ಥಿತಿ ಪತ್ತೆಯಾಗಿದೆ."
            }[lang]

            emergency_number = {
                "en": "101 Fire Emergency",
                "hi": "101 अग्निशमन सेवा",
                "kn": "101 ಅಗ್ನಿಶಾಮಕ ಸೇವೆ"
            }[lang]

            emergency_tips = {
                "en": [
                    "Move away from smoke.",
                    "Turn off gas if safe.",
                    "Use stairs instead of lift."
                ],

                "hi": [
                    "धुएं से दूर जाएं।",
                    "यदि सुरक्षित हो तो गैस बंद करें।",
                    "लिफ्ट के बजाय सीढ़ियों का उपयोग करें।"
                ],

                "kn": [
                    "ಹೊಗೆಯಿಂದ ದೂರ ಸರಿಯಿರಿ.",
                    "ಸುರಕ್ಷಿತವಾಗಿದ್ದರೆ ಗ್ಯಾಸ್ ಆಫ್ ಮಾಡಿ.",
                    "ಲಿಫ್ಟ್ ಬದಲು ಮೆಟ್ಟಿಲುಗಳನ್ನು ಬಳಸಿ."
                ]
            }[lang]

        # ⛽ GAS LEAK
        elif any(word in text for word in [

            "gas leak", "गैस रिसाव", "ಗ್ಯಾಸ್ ಸೋರಿಕೆ"

        ]):

            emergency_response = {
                "en": "Gas leakage detected.",
                "hi": "गैस रिसाव का पता चला।",
                "kn": "ಗ್ಯಾಸ್ ಸೋರಿಕೆ ಪತ್ತೆಯಾಗಿದೆ."
            }[lang]

            emergency_number = {
                "en": "101 Fire Emergency",
                "hi": "101 अग्निशमन सेवा",
                "kn": "101 ಅಗ್ನಿಶಾಮಕ ಸೇವೆ"
            }[lang]

            emergency_tips = {
                "en": [
                    "Do NOT switch on electrical appliances.",
                    "Open windows immediately.",
                    "Turn off gas regulator."
                ],

                "hi": [
                    "कोई विद्युत उपकरण चालू न करें।",
                    "तुरंत खिड़कियां खोलें।",
                    "गैस रेगुलेटर बंद करें।"
                ],

                "kn": [
                    "ವಿದ್ಯುತ್ ಸಾಧನಗಳನ್ನು ಆನ್ ಮಾಡಬೇಡಿ.",
                    "ತಕ್ಷಣ ಕಿಟಕಿಗಳನ್ನು ತೆರೆಯಿರಿ.",
                    "ಗ್ಯಾಸ್ ರೆಗ್ಯುಲೇಟರ್ ಆಫ್ ಮಾಡಿ."
                ]
            }[lang]

        # 🚨 SHOW EMERGENCY PANEL
        if category == "emergency" and emergency_response != "":
        
            emergency_ui = {
                "en": {
                    "detected": "🚨 Emergency Situation Detected",
                    "response": "⚠ Emergency Response",
                    "contact": "📞 Emergency Contact",
                    "tips": "🩺 Safety Instructions"
                },
            
                "hi": {
                    "detected": "🚨 आपातकालीन स्थिति का पता चला",
                    "response": "⚠ आपातकालीन प्रतिक्रिया",
                    "contact": "📞 आपातकालीन संपर्क",
                    "tips": "🩺 सुरक्षा निर्देश"
                },
            
                "kn": {
                    "detected": "🚨 ತುರ್ತು ಪರಿಸ್ಥಿತಿ ಪತ್ತೆಯಾಗಿದೆ",
                    "response": "⚠ ತುರ್ತು ಪ್ರತಿಕ್ರಿಯೆ",
                    "contact": "📞 ತುರ್ತು ಸಂಪರ್ಕ",
                    "tips": "🩺 ಸುರಕ್ಷತಾ ಸೂಚನೆಗಳು"
                }
            }

            st.error(emergency_ui[lang]["detected"])
            
            st.subheader(emergency_ui[lang]["response"])
            st.write(emergency_response)
            
            st.subheader(emergency_ui[lang]["contact"])
            st.success(emergency_number)
            
            st.subheader(emergency_ui[lang]["tips"])
        
            for tip in emergency_tips:
                st.write(f"✅ {tip}")
        
            # 🚨 PLAY ONLY ONE EMERGENCY AUDIO
            emergency_audio_map = {

                "en": f"""
                {emergency_response}
            
                Emergency contact number is {emergency_number}.
            
                Please follow the safety instructions carefully.
                """,
            
                "hi": f"""
                {emergency_response}
            
                आपातकालीन संपर्क नंबर {emergency_number} है।
            
                कृपया सुरक्षा निर्देशों का पालन करें।
                """,
            
                "kn": f"""
                {emergency_response}
            
                ತುರ್ತು ಸಂಪರ್ಕ ಸಂಖ್ಯೆ {emergency_number} ಆಗಿದೆ.
            
                ದಯವಿಟ್ಟು ಸುರಕ್ಷತಾ ಸೂಚನೆಗಳನ್ನು ಅನುಸರಿಸಿ.
                """
            }

            play_audio(emergency_audio_map[lang], lang)

    elif choice == confirm_text[lang]["no"]:
        st.warning(confirm_text[lang]["cancel"])
        play_audio(confirm_text[lang]["cancel"], lang)
