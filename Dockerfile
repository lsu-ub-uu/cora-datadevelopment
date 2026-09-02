FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

VOLUME ["/app/data", "/app/logs", "/app/reports"]
