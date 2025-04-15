# Use an official Python base image
FROM python:3.10-slim

# Install system dependencies (Tesseract OCR)
RUN apt-get update && apt-get install -y tesseract-ocr

# Set working directory
WORKDIR /app

# Copy everything into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Command to run the app
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]
