# syntax=docker/dockerfile:1.4
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Combined layer for FFmpeg (Media) + WeasyPrint (PDF) + Build Tools (C-compiler)
# REMOVED: libaccessor-dev (does not exist)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    pkg-config \
    python3-dev \
    # FFmpeg Dependencies + CLI tool (required by pydub for audio conversion)
    ffmpeg \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    # WeasyPrint Dependencies
    python3-pip \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libglib2.0-0 \
    libgirepository-1.0-1 \
    libcairo2 \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Pre-install core build tools
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install Cython av==12.3.0

# Define ARG before using it so the build command picks it up
ARG PAT_TOKEN

# Install g-agent-ai-core-backend
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "git+https://${PAT_TOKEN}@github.com/Ghaia-ai/g-agent-ai-core-backend.git@v2.3.18"

# Copy and install requirements BEFORE copying app code
# This creates a separate cached layer for dependencies
COPY ./requirements.txt /code/requirements.txt

# IMPORTANT: If 'av' is in your requirements.txt, this will skip it
# because it's already installed above.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /code/requirements.txt

# Copy application code LAST - this layer changes most frequently
# Now code changes won't invalidate the dependency cache layers above
COPY ./app /code/app

WORKDIR /code

EXPOSE 8000

CMD ["python", "-m", "app.main"]