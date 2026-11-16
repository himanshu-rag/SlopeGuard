# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system deps for psycopg2 / geoalchemy / postgis client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY backend/requirements.txt ./backend/requirements.txt
COPY ml/requirements.txt ./ml/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt \
    && pip install --no-cache-dir -r ml/requirements.txt \
    && pip install --no-cache-dir onnxruntime joblib

# Copy source code
COPY backend ./backend
COPY ml ./ml
COPY .cache ./.cache

# Set Python path so `from api_ml import ...` works from backend/
ENV PYTHONPATH=/app/backend

# Default to SQLite so it runs out of the box; override DATABASE_URL for Postgres
ENV DATABASE_URL=sqlite:///./slopeguard.db
ENV PORT=8000

EXPOSE 8000

# Run with uvicorn (no --reload in production)
CMD ["sh", "-c", "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
