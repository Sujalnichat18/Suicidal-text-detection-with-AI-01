from flask import Flask, request, jsonify, render_template
import io
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import cv2
import numpy as np
import pytesseract

app = Flask(__name__)

# Set Tesseract OCR Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize Sentiment Analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

# **Risk Phrases**
high_risk_phrases = [
    "i want to die", "i have no reason to live", "i will end my life", "i feel dead inside",
    "nobody would miss me", "i have no purpose", "i don’t want to exist", "i want to disappear"
]

moderate_risk_phrases = [
    "i feel empty", "i don’t belong here", "i lost hope", "nobody cares about me",
    "i hate my life", "i just want to disappear", "i don’t have interest in life",
    "i am tired of everything"
]

suicidal_words = ["suicide", "die", "kill", "hopeless", "worthless", "goodbye",
                  "alone", "pain", "useless", "pointless"]

# **Preprocessing Function**
def preprocess_image(image):
    """Preprocess the image to improve OCR accuracy."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    denoised = cv2.fastNlMeansDenoising(dilated, h=30)
    return Image.fromarray(denoised)

# **Risk Analysis Function**
def analyze_text(text):
    """Analyze the text and calculate risk level."""
    text = text.lower().strip()

    high_phrase_count = sum(1 for phrase in high_risk_phrases if phrase in text)
    moderate_phrase_count = sum(1 for phrase in moderate_risk_phrases if phrase in text)
    suicidal_word_count = sum(1 for word in suicidal_words if word in text)

    sentiment_score = sentiment_analyzer.polarity_scores(text)["compound"]

    risk_percentage = (
        high_phrase_count * 80 + 
        moderate_phrase_count * 50 + 
        suicidal_word_count * 30 + 
        (1 - sentiment_score) * 40
    )

    if suicidal_word_count >= 3:
        risk_percentage += 20

    risk_percentage = max(0, min(100, risk_percentage))

    if risk_percentage >= 60:
        risk_level = "🔴 High Risk"
        risk_color = "red"
    elif risk_percentage >= 25:
        risk_level = "🟡 Moderate Risk"
        risk_color = "yellow"
    else:
        risk_level = "🟢 Low Risk"
        risk_color = "green"

    return {
        "text": text,
        "risk_percentage": round(risk_percentage, 2),
        "risk_level": risk_level,
        "risk_color": risk_color,
    }

# **OCR and Risk Analysis for Images**
@app.route("/analyze_image", methods=["POST"])
def analyze_image():
    """Analyze text from an uploaded image."""
    if "image" not in request.files or request.files["image"].filename == "":
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    image = Image.open(io.BytesIO(image_file.read()))
    preprocessed_image = preprocess_image(image)
    extracted_text = pytesseract.image_to_string(preprocessed_image)

    if not extracted_text.strip():
        return jsonify({"error": "No text detected."}), 400

    return jsonify(analyze_text(extracted_text))

# **Manual Text Analysis**
@app.route("/analyze_text", methods=["POST"])
def analyze_manual_text():
    """Analyze text entered manually."""
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400
    return jsonify(analyze_text(text))

# **Home Route**
@app.route("/")
def home():
    """Serve the frontend HTML page."""
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
