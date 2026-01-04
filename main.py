# moderation_service.py
from fastapi import FastAPI

import joblib
from fastapi.middleware.cors import CORSMiddleware
from schema.schemas import CommentRequest
# -----------------------
# CORS settings
# -----------------------
app = FastAPI(title="Hybrid Moderation API", version="1.0")

origins = [
    "http://localhost:3000",  # your frontend URL
    "http://127.0.0.1:3000",
    "*",  # optional: allow all origins (use carefully in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, etc
    allow_headers=["*"],  # allow custom headers
)
# -----------------------
# 1️⃣ FastAPI setup
# -----------------------

# -----------------------
# 2️⃣ Load trained ML artifacts
# -----------------------
MODEL_FILE = "moderation_model.joblib"
VECT_FILE = "vectorizer.joblib"

try:
    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECT_FILE)
    print("✅ Loaded trained model and vectorizer")
except FileNotFoundError:
    raise FileNotFoundError(
        f"Could not find '{MODEL_FILE}' or '{VECT_FILE}'. Train the model first!"
    )

# -----------------------
# 3️⃣ Request model
# -----------------------


# -----------------------
# 4️⃣ Optional rule-based flags
# -----------------------
PROFANE_WORDS = [
    "pussy", "cum", "dick", "sex", "porn", "bitch", "fuck",
    "asshole", "bastard", "damn", "crap", "slut", "whore",
    "douche", "shit", "cock", "fag", "twat", "jerk", "prick",
    "hell", "suck", "nigger", "nigga", "bollocks", "bugger",
    "cunt", "arse", "wanker", "motherfucker", "fucking", "shithead"
]

def check_flags(text: str):
    flags = []
    text_lower = text.lower()
    for word in PROFANE_WORDS:
        if word in text_lower:
            flags.append("sexual_language")
    return flags

# -----------------------
# 5️⃣ API endpoint
# -----------------------
@app.post("/moderate")
def moderate(comment: CommentRequest):
    # ML prediction
    X_vec = vectorizer.transform([comment.text])
    probs = model.predict_proba(X_vec)[0]
    label = model.classes_[probs.argmax()]

    # Rule-based flags
    flags = check_flags(comment.text)

    return {
        "text": comment.text,
        "label": label,
        "scores": dict(zip(model.classes_, probs)),
        "flags": flags
    }

