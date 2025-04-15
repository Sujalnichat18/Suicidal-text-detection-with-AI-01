#!/bin/bash

# Install system dependencies
echo "📥 Installing Tesseract OCR..."
apt-get update && apt-get install -y tesseract-ocr

# Verify Installation
echo "✅ Verifying Tesseract Installation..."
which tesseract
tesseract --version

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

