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

# ✅ **Set Tesseract Path & Handle Missing Installation**
tesseract_path = shutil.which("tesseract") or "/usr/bin/tesseract"  # Default for Linux
if tesseract_path and os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✅ Tesseract found at: {tesseract_path}")
else:
    print("❌ Tesseract not found! OCR features will not work.")

# ✅ **Initialize Sentiment Analyzer**
sentiment_analyzer = SentimentIntensityAnalyzer()

# ✅ **Define Risk Phrases**
high_risk_phrases = ["i want to die", "i have no reason to live", "i will end my life"]
moderate_risk_phrases = ["i feel empty", "i don’t belong here", "i lost hope"]
suicidal_words = ["suicide", "die", "kill", "hopeless", "worthless"]

# ✅ **List of Safe Phrases (To Prevent False Alarms)**
safe_phrases = ["my name is", "hello", "hi", "good morning", "how are you", "i feel okay"]

# ✅ **Preprocess Image Function**
def preprocess_image(image):
    """Preprocess image for better OCR accuracy."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # High-contrast
    return Image.fromarray(thresh)

# ✅ **Risk Analysis Function**
def analyze_text(text):
    """Evaluate risk level of a given text based on predefined phrases and sentiment analysis."""
    text = text.lower().strip()

    # 🚫 Ignore harmless common phrases to prevent false alarms
    if any(text.startswith(phrase) for phrase in safe_phrases):
        print(f"🟢 Safe phrase detected: {text}")
        return {"text": text, "risk_percentage": 0, "risk_level": "🟢 Low Risk", "risk_color": "green"}

    # Count occurrences of high/moderate risk phrases
    high_count = sum(1 for phrase in high_risk_phrases if phrase in text)
    moderate_count = sum(1 for phrase in moderate_risk_phrases if phrase in text)
    word_count = sum(1 for word in suicidal_words if word in text)

    sentiment_score = sentiment_analyzer.polarity_scores(text)["compound"]
    print(f"🔍 Sentiment Score: {sentiment_score} for text: {text}")

    # **Fix 2**: Reduce the impact of neutral sentiment (Prevent overestimating risk)
    sentiment_weight = (1 - sentiment_score) * 20  # Reduced from 40 to 20

    # Calculate risk percentage
    risk_percentage = (high_count * 80) + (moderate_count * 50) + (word_count * 30) + sentiment_weight
    risk_percentage = max(0, min(100, risk_percentage))

    # Assign risk category
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

        # Ensure Tesseract is installed before running OCR
        if not os.path.exists(tesseract_path):
            return jsonify({"error": "Tesseract OCR is missing. Install it first."}), 500

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
    port = int(os.environ.get("PORT", 10000))  # Use Render's port if available, default to 10000
    serve(app, host="0.0.0.0", port=port)
