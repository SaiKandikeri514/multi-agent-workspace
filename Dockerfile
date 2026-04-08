FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and pgvector
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# Expose both ports (FastAPI on 8080, Streamlit on 8501)
# For the hackathon, we can use a script to run both, but Cloud Run
# typically uses one port (PORT env var). So we can serve Streamlit
# on PORT and FastAPI on another, or vice versa. We'll run FastAPI as an API 
# and the Streamlit as the main frontend.
EXPOSE 8080

# A simple script to start the backend and frontend
CMD sh -c "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false"
