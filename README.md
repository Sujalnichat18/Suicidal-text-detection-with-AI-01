# Suicidal Text Detection with AI 🧠🛑

A Flask-based web application that detects suicidal intent in textual content extracted from uploaded images using Optical Character Recognition (OCR) and a trained Machine Learning model.

## 🧩 Features

- 🔍 **Text Extraction:** Uses Tesseract OCR to extract text from uploaded images.
- 🧠 **AI-Powered Detection:** Classifies extracted text as *suicidal* or *non-suicidal*.
- 📈 **Pre-trained Model:** Trained on labeled datasets to detect patterns of suicidal ideation.
- 🌐 **Web Interface:** Simple and intuitive UI built with HTML, CSS, and Flask.

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **OCR:** [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- **Machine Learning:** scikit-learn
- **Deployment Ready:** Code is structured for easy deployment on platforms like Render.

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.x
- Tesseract OCR (add to system path)
- pip (Python package installer)

### Clone the Repository

```bash
git clone https://github.com/Sujalnichat18/Suicidal-text-detection-with-AI-01.git
cd Suicidal-text-detection-with-AI-01

```
📷 How It Works
Upload an image containing text.

The app uses Tesseract to extract text from the image.

The extracted text is passed through a trained machine learning model.

The result is displayed: Suicidal or Non-Suicidal.

🧪 Model Info
Vectorizer: TF-IDF

Classifier: Logistic Regression (can be upgraded)

You can find the serialized model and vectorizer in the model directory.

📁 Project Structure
```bash
.
├── static/                 # CSS and other static assets
├── templates/              # HTML templates
├── model/                  # ML model and vectorizer
├── app.py                  # Main Flask application
├── requirements.txt        # Dependencies
└── README.md               # Project documentation

```

🌍 Deployment
To deploy on Render, follow these steps:

Push this code to a GitHub repo.

Create a new Web Service on Render.

Use app.py as the entry point.

Set the build command to install dependencies:

```bash

pip install -r requirements.txt

```

Add environment variables if needed (e.g., TESSDATA_PREFIX for Tesseract).

Done!

⚠️ Disclaimer
This application is intended for educational and research purposes only. It is not a substitute for professional mental health services.

If you or someone you know is struggling, please seek help from a qualified professional or call a suicide prevention hotline.

📬 Contact
Made with ❤️ by Sujal Nichat and Team.

