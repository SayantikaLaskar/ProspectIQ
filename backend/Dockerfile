FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LLM_PROVIDER=huggingface \
    HF_MODEL=meta-llama/Llama-3.1-8B-Instruct

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Serve mode: loads precomputed_*.json (fast, low memory). $PORT is set by the host.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level warning"]
