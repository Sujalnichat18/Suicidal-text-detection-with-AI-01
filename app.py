from flask import Flask, request, jsonify, render_template
import io
from PIL import Image
import cv2
import numpy as np
import pytesseract
import shutil
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from waitress import serve

app = Flask(__name__)

# ✅ Tesseract Setup
tesseract_path = shutil.which("tesseract") or "/usr/bin/tesseract"
if tesseract_path and os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✅ Tesseract found at: {tesseract_path}")
else:
    print("❌ Tesseract not found!")

# ✅ Initialize Sentiment Analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

# ✅ Phrases
high_risk_phrases = ["i want to die", "i have no reason to live", "i will end my life"]
moderate_risk_phrases = ["i feel empty", "i don’t belong here", "i lost hope"]
suicidal_words = ["suicide", "die", "kill", "hopeless", "worthless"]
safe_phrases = ["my name is", "hello", "hi", "good morning", "how are you", "i feel okay"]

# ✅ Image Preprocessing
def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)

# ✅ Risk Analysis Function
def analyze_text(text):
    text = text.lower().strip()

    if any(text.startswith(phrase) for phrase in safe_phrases):
        print(f"🟢 Safe phrase detected: {text}")
        return {"text": text, "risk_percentage": 0, "risk_level": "🟢 Low Risk", "risk_color": "green"}

    high_count = sum(1 for phrase in high_risk_phrases if phrase in text)
    moderate_count = sum(1 for phrase in moderate_risk_phrases if phrase in text)
    word_count = sum(1 for word in suicidal_words if word in text)

    sentiment_score = sentiment_analyzer.polarity_scores(text)["compound"]
    print(f"🔍 Sentiment Score: {sentiment_score} for text: {text}")

    sentiment_weight = (1 - sentiment_score) * 20
    risk_percentage = (high_count * 80) + (moderate_count * 50) + (word_count * 30) + sentiment_weight
    risk_percentage = max(0, min(100, risk_percentage))

    if risk_percentage >= 60:
        level = "🔴 High Risk"
        color = "red"
    elif risk_percentage >= 25:
        level = "🟡 Moderate Risk"
        color = "yellow"
    else:
        level = "🟢 Low Risk"
        color = "green"

    return {
        "text": text,
        "risk_percentage": risk_percentage,
        "risk_level": level,
        "risk_color": color
    }

# ✅ Image Analysis Endpoint
@app.route("/analyze_image", methods=["POST"])
def analyze_image():
    if "image" not in request.files or request.files["image"].filename == "":
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]

    try:
        image = Image.open(io.BytesIO(image_file.read()))

        if image.mode != "RGB":
            image = image.convert("RGB")

        print("✅ Image received. Processing...")

        preprocessed_image = preprocess_image(image)

        if not os.path.exists(tesseract_path):
            return jsonify({"error": "Tesseract OCR is missing. Install it first."}), 500

        extracted_text = pytesseract.image_to_string(preprocessed_image)
        print(f"📝 Extracted Text: {repr(extracted_text)}")

        if not extracted_text.strip():
            return jsonify({"error": "No text detected. Ensure image quality is good."}), 400

        return jsonify(analyze_text(extracted_text))

    except Exception as e:
        print(f"⚠️ OCR Processing Error: {str(e)}")
        return jsonify({"error": f"OCR Error: {str(e)}"}), 500

# ✅ Manual Text Analysis Endpoint
@app.route("/analyze_text", methods=["POST"])
def analyze_manual_text():
    data = request.json
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided."}), 400

    return jsonify(analyze_text(text))

# ✅ Serve Frontend
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Run
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    serve(app, host="0.0.0.0", port=port)