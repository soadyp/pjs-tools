# Containerfile for pjs-neo-rag application (OCI-compatible)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directory for mounted documents
RUN mkdir -p /app/documents

# Expose API port
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "src/app.py"]
