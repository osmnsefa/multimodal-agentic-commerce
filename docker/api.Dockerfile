# Optimized Python Dockerfile for AegisCommerce API

FROM python:3.11-slim

# Prevent python from writing bytecode and enable unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install build dependencies and clean up apt cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages with high timeout and retries
COPY services/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --default-timeout=100 --retries=10 -r /app/requirements.txt

# Copy source code
COPY services/backend /app

EXPOSE 8000

# Start server with uvicorn reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
