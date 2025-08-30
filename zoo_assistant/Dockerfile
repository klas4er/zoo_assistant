FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements_minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Create necessary directories
RUN mkdir -p core_engine/asr/models data/uploads

# Download Vosk model
RUN cd core_engine/asr/models && \
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip && \
    unzip -q vosk-model-small-ru-0.22.zip && \
    mv vosk-model-small-ru-0.22 vosk-model-ru && \
    rm vosk-model-small-ru-0.22.zip

# Copy application code
COPY . .

# Initialize the database
RUN python init_db.py

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "server.py"]