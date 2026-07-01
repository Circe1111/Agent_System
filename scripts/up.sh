#!/bin/bash
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env with your API keys, then re-run: ./scripts/up.sh"
    exit 1
fi
docker load < eduagent-images.tar.gz 2>/dev/null || echo "No images.tar.gz, building..."
docker compose up -d
echo "================================================"
echo "  EduAgent running!"
echo "  Frontend: http://localhost"
echo "  Backend:  http://localhost:8000"
echo "  Login:    admin / admin123"
echo "================================================"
