FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Create a dummy setup.py or requirements if needed, but we'll use pip directly for simplicity with pyproject.toml
# Or better, just copy a requirements.txt generated from pyproject.toml concepts
# For this generated repo, I will write a requirements.txt for stability.

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.main"]
