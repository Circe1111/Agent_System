FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/
COPY data/ /app/data/

EXPOSE 8000

# Seed database, rebuild FAISS if needed, then start server
CMD python backend/scripts/seed_db.py && python backend/scripts/rebuild_faiss.py && uvicorn backend.main:app --host 0.0.0.0 --port 8000
