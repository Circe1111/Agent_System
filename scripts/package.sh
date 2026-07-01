#!/bin/bash
set -e
echo "=== EduAgent Package Builder ==="
docker compose build
docker save eduagent-backend:latest eduagent-frontend:latest | gzip > eduagent-images.tar.gz
tar -czf eduagent-dist.tar.gz \
    docker-compose.yml docker/nginx.conf \
    .env.example .dockerignore .gitattributes \
    eduagent-images.tar.gz scripts/up.sh scripts/up.ps1
rm eduagent-images.tar.gz
echo "=== Package: eduagent-dist.tar.gz ==="
echo "Extract on target, edit .env, run scripts/up.sh or scripts/up.ps1"
