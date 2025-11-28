# Containerfile for pjs-neo-rag application (OCI-compatible)
# Build: podman build -t pjs-neo-rag -f Containerfile .
# Run:   podman run --rm --env-file .env.container -p 8000:8000 pjs-neo-rag

FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files for installation
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# ---- Runtime stage ----
FROM python:3.13-slim

LABEL maintainer="Phil Soady <phil.soady@gmail.com>"
LABEL description="Neo4j Graph RAG API Server"
LABEL version="0.1.0"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY src/ ./src/

# Create directories for documents and logs
RUN mkdir -p /app/documents /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment defaults (override via --env-file or -e)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    API_PORT=8000 \
    LOG_DIR=/app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

# Expose API port
EXPOSE 8000

# Default command
CMD ["python", "src/app.py"]
