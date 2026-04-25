from fastapi import FastAPI
from transformers import pipeline
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
from fastapi.responses import FileResponse

app = FastAPI()

# ✅ CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load models
intent_model = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")
sentiment_model = pipeline("sentiment-analysis")

@app.get("/")
def home():
    return {"message": "Backend running"}

# ✅ AI ANALYSIS
@app.post("/analyze")
def analyze(data: dict):
    text = data.get("text", "")

    if text.strip() == "":
        return {"error": "Empty input"}

    labels = ["complaint", "emergency", "information request", "other"]

    intent_result = intent_model(text, labels)
    intent = intent_result["labels"][0]

    sentiment_result = sentiment_model(text)
    sentiment = sentiment_result[0]["label"]

    priority = "HIGH" if sentiment == "NEGATIVE" else "NORMAL"

    return {
        "intent": intent,
        "emotion": sentiment,
        "priority": priority
    }

# 🔊 MULTILINGUAL ERROR VOICE
@app.get("/speak-error")
def speak_error():
    text = """
    I did not understand. Please try again.
    मुझे समझ में नहीं आया। कृपया फिर से बोलें।
    ನನಗೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಹೇಳಿ.
    """

    tts = gTTS(text=text, lang='en')
    tts.save("error.mp3")

    return FileResponse("error.mp3", media_type="audio/mpeg")

# 🔊 MULTILINGUAL WELCOME VOICE
@app.get("/welcome")
def welcome():
    text = """
    Welcome to Helpline 1092. Please tell your problem.
    हेल्पलाइन 1092 में आपका स्वागत है।
    ಹೆಲ್ಪ್‌ಲೈನ್ 1092 ಗೆ ಸ್ವಾಗತ.
    """

    tts = gTTS(text=text, lang='en')
    tts.save("welcome.mp3")

    return FileResponse("welcome.mp3", media_type="audio/mpeg")

# ✅ RUN SERVER
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)