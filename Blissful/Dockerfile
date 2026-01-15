# Blissful - Lidarr Music Downloader
# Multi-stage Docker build for production use

FROM python:3.11-slim as base

# Install FFmpeg and dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY Blissful.py .
COPY extend/ ./extend/
COPY templates/ ./templates/
COPY static/ ./static/
COPY docs/ ./docs/

# Create directories for downloads and config
RUN mkdir -p downloads/temp config

# Expose port
EXPOSE 7373

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7373/api/health', timeout=5)" || exit 1

# Set environment variables
ENV PORT=7373 \
    PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "Blissful.py"]
