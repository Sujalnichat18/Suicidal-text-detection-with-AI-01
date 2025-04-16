# Use a more secure Python base image (Debian Buster)
FROM python:3.10-buster AS builder

# Update and upgrade system packages, and minimize the number of layers
RUN apt-get update && apt-get install --only-upgrade libc6 libglib2.0-0 && apt-get clean


# Install only the essential system dependencies for building the application
RUN apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies in the build stage
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage (runtime)
FROM python:3.10-buster

# Copy only the installed packages and application files from the builder stage
COPY --from=builder /app /app

# Set the working directory to /app
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Expose the port your app runs on
EXPOSE 5000

# Command to run the app using Waitress
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]
