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

# ✅ **Set Tesseract Path Explicitly**
tesseract_path = shutil.which("tesseract") or "/usr/bin/tesseract"  # Default path for Linux
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✅ Tesseract found at: {tesseract_path}")
else:
    print("❌ Tesseract not found! Make sure it's installed.")
    exit(1)  # Stop execution if Tesseract is missing

# ✅ **Initialize Sentiment Analyzer**
sentiment_analyzer = SentimentIntensityAnalyzer()

# ✅ **Define Risk Phrases**
high_risk_phrases = ["i want to die", "i have no reason to live", "i will end my life"]
moderate_risk_phrases = ["i feel empty", "i don’t belong here", "i lost hope"]
suicidal_words = ["suicide", "die", "kill", "hopeless", "worthless"]

# ✅ **Preprocess Image Function**
def preprocess_image(image):
    """Preprocess image to improve OCR accuracy."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # High-contrast
    return Image.fromarray(thresh)

# ✅ **Risk Analysis Function**
def analyze_text(text):
    """Analyze extracted text and calculate suicide risk percentage."""
    text = text.lower().strip()

    high_count = sum(1 for phrase in high_risk_phrases if phrase in text)
    moderate_count = sum(1 for phrase in moderate_risk_phrases if phrase in text)
    word_count = sum(1 for word in suicidal_words if word in text)

    sentiment_score = sentiment_analyzer.polarity_scores(text)["compound"]

    risk_percentage = (high_count * 80) + (moderate_count * 50) + (word_count * 30) + ((1 - sentiment_score) * 40)
    risk_percentage = max(0, min(100, risk_percentage))

    if risk_percentage >= 60:
        return {"text": text, "risk_percentage": risk_percentage, "risk_level": "🔴 High Risk", "risk_color": "red"}
    elif risk_percentage >= 25:
        return {"text": text, "risk_percentage": risk_percentage, "risk_level": "🟡 Moderate Risk", "risk_color": "yellow"}
    else:
        return {"text": text, "risk_percentage": risk_percentage, "risk_level": "🟢 Low Risk", "risk_color": "green"}

# ✅ **OCR and Risk Analysis for Images**
@app.route("/analyze_image", methods=["POST"])  
def analyze_image():
    """Extract text from an image and analyze it."""
    if "image" not in request.files or request.files["image"].filename == "":
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    try:
        image = Image.open(io.BytesIO(image_file.read()))

        # Convert image to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        print("✅ Image received. Processing...")

        preprocessed_image = preprocess_image(image)

        # Extract text using Tesseract OCR
        extracted_text = pytesseract.image_to_string(preprocessed_image)
        print(f"📝 Extracted Text: {repr(extracted_text)}")  # Debugging output

        if not extracted_text.strip():
            return jsonify({"error": "No text detected. Ensure image quality is good."}), 400

        return jsonify(analyze_text(extracted_text))

    except Exception as e:
        print(f"⚠️ OCR Processing Error: {str(e)}")  # Debugging
        return jsonify({"error": f"OCR Error: {str(e)}"}), 500

# ✅ **Manual Text Analysis**
@app.route("/analyze_text", methods=["POST"])
def analyze_manual_text():
    """Analyze manually entered text."""
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400
    return jsonify(analyze_text(text))

# ✅ **Serve Frontend**
@app.route("/")
def home():
    """Serve frontend HTML page."""
    return render_template("index.html")

# ✅ **Run App**
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get port from Render, default to 5000
    serve(app, host="0.0.0.0", port=port)