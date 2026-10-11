# Dockerfile for AegisCommerce Background Workers & Agent Tasks

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --default-timeout=100 --retries=10 -r /app/requirements.txt

COPY services/backend /app

# Run Celery worker for task queues and multi-agent asynchronous workflows
CMD ["celery", "-A", "workers.celery_app.celery_app", "worker", "--loglevel=info"]
