from flask import Flask, request, jsonify, render_template
import io
from PIL import Image
import cv2
import numpy as np
import pytesseract
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from waitress import serve

app = Flask(__name__)

# ✅ **Set Tesseract Path**
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ **Initialize Sentiment Analyzer**
sentiment_analyzer = SentimentIntensityAnalyzer()

# ✅ **Define Risk Phrases**
high_risk_phrases = ["i want to die", "i have no reason to live", "i will end my life"]
moderate_risk_phrases = ["i feel empty", "i don’t belong here", "i lost hope"]
suicidal_words = ["suicide", "die", "kill", "hopeless", "worthless"]

# ✅ **Preprocess Image Function**
def preprocess_image(image):
    """Preprocess the image for better OCR accuracy."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return Image.fromarray(thresh)

# ✅ **Risk Analysis Function**
def analyze_text(text):
    """Analyze the text and calculate suicide risk."""
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
    image = Image.open(io.BytesIO(image_file.read()))

    # Debugging: Check if image is read properly
    print("Image Mode:", image.mode)

    preprocessed_image = preprocess_image(image)
    extracted_text = pytesseract.image_to_string(preprocessed_image)

    # Debugging: Print extracted text
    print("Extracted Text:", extracted_text)

    if not extracted_text.strip():
        return jsonify({"error": "No text detected."}), 400

    return jsonify(analyze_text(extracted_text))

# ✅ **Manual Text Analysis**
@app.route("/analyze_text", methods=["POST"])
def analyze_manual_text():
    """Analyze text entered manually."""
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
    serve(app, host="0.0.0.0", port=5000)  # Use Waitress for deployment
