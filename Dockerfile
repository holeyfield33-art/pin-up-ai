# ─────────────────────────────────────────────────────────────────────────────
# Pin-Up AI — Production Dockerfile
# Multi-stage: build frontend then serve via FastAPI backend
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Build frontend ─────────────────────────────────────────────────
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts
COPY frontend/ .
RUN npm run build

# ── Stage 2: Backend + serve ────────────────────────────────────────────────
FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/holeyfield33-art/pin-up-ai"

WORKDIR /app

# System deps (sqlite3 already in python-slim)
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Backend source
COPY backend/ .

# Frontend static assets (optional — for fullstack container)
COPY --from=frontend-build /build/dist /app/static

# Environment defaults
ENV ENVIRONMENT=production \
    DEBUG=false \
    LOG_LEVEL=WARNING \
    LOG_FORMAT=json \
    RATE_LIMIT_ENABLED=true \
    RATE_LIMIT_REQUESTS=100 \
    RATE_LIMIT_PERIOD=60

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Run with gunicorn + uvicorn workers
CMD ["gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "300", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
