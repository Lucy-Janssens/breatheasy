FROM python:3.11-slim

# System dependencies for GPIO, I2C, sensor libs, and Pillow
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    python3-dev \
    i2c-tools \
    libgpiod-dev \
    libjpeg-dev \
    zlib1g-dev \
    fonts-dejavu \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Create persistent data directory
RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
