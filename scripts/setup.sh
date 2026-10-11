#!/usr/bin/env bash

set -e

echo "=== AegisCommerce Environment Initialization ==="

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Building and starting Docker container services..."
docker-compose -f docker/docker-compose.yml up --build -d

echo "AegisCommerce services launched successfully!"
echo "API Documentation: http://localhost:8000/docs"
