# --- Build/Dependencies Stage ---
FROM python:3.12-slim AS builder

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Minimal Final Runtime Stage ---
FROM python:3.12-slim AS runner

WORKDIR /app

# Inherit built packages securely
COPY --from=builder /root/.local /root/.local
COPY app/ /app/app/

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
