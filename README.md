# pjs-neo-rag

A complete local Retrieval-Augmented Generation (RAG) system built on Neo4j graph database with specialized support for scientific and mathematical documents containing LaTeX notation.

## Overview

This project provides a Python-based RAG pipeline that:

- **Extracts content** from PDF documents, separating prose text from LaTeX mathematical notation
- **Generates dual embeddings** using Ollama's bge-m3 model for both text and LaTeX content
- **Stores in Neo4j** with vector indexes for similarity search and graph relationships
- **Serves via FastAPI** for integration with chat interfaces like Open-WebUI
- **Optimized for technical documents** with proper LaTeX handling and rendering

## Key Features

- 🔍 **Dual-vector search**: Separate embeddings for prose and LaTeX content
- 📊 **Graph structure**: Documents → Sections → Chunks with relationships
- 🚀 **Local-first**: All processing runs on your hardware (no API costs)
- 🔒 **Privacy**: Your documents never leave your machine
- 📐 **LaTeX-aware**: Preserves mathematical notation for accurate retrieval
- 🔌 **REST API**: Easy integration with any chat interface

## Quick Start

**⭐ Recommended:** See **[Quick Start Guide](docs/QUICKSTART.md)** for complete step-by-step instructions to clone and deploy on a new machine.

### Local Development Setup (Recommended)

The app runs in development mode on the host machine, while Neo4j and Open-WebUI run in containers:

```bash
# 1. Clone and configure
git clone <repo-url>
cd pjs-neo-rag
cp .env.example .env
nano .env  # Edit: NEO4J_PASSWORD, SOURCE_DIR, model names/dimensions

# 2. Install and start services (containers)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull bge-m3  # or your chosen embedding model
ollama pull mistral:7b

podman run -d --name neo4j --network host \
  -e NEO4J_AUTH=neo4j/yourpassword \
  -v neo4j-data:/data neo4j:5.26.0

podman run -d --name open-webui --network host \
  -v open-webui-data:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# 3. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 4. Initialize database and ingest
python src/pjs_neo_rag/create_neo_indexes.py
python src/pjs_neo_rag/ingest_files.py

# 5. Start API (keep running)
python src/app.py
```

Access: 
- API: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- Open-WebUI: http://localhost:8080

### Fully Containerized (Optional)

For fully isolated deployment with all components containerized:

```bash
podman-compose up -d
podman exec ollama-std ollama pull bge-m3
podman exec ollama-std ollama pull mistral:7b
podman exec pjs-neo-rag-app python src/pjs_neo_rag/create_neo_indexes.py
podman exec pjs-neo-rag-app python src/pjs_neo_rag/ingest_files.py
```

See **[Deployment Guide](docs/Deployment.md)** for containerized setup details.

## Documentation

**⭐ Start Here:**
- **[Quick Start Guide](docs/QUICKSTART.md)** - Clone to production in 12 steps (recommended for first-time setup)

**Core Documentation:**
- **[Welcome to Local AI](docs/Welcome%20to%20Local%20AI%20with%20Neo4j%20DB%20RAG.md)** - System overview and architecture diagram
- **[Installation Guide](docs/Installation%20Guide.md)** - Detailed component installation
- **[Open-WebUI Integration](docs/OPEN-WEBUI-INTEGRATION.md)** - **How to add the RAG tool** ⚠️ Critical
- **[Troubleshooting](docs/Troubleshooting.md)** - Common issues and solutions

### Component Guides

- **[Deployment Guide](docs/Deployment.md)** - Container-based deployment (recommended)
- **[Neo4j Setup](docs/Neo4j.md)** - Database configuration and commands
- **[Ollama Setup](docs/OLLAMA.md)** - Embedding and LLM models
- **[Podman Setup](docs/PODMAN.md)** - Container runtime with GPU support
- **[Open-WebUI Setup](docs/OPEN-WEBUI.md)** - Chat interface configuration
- **[MCP Integration](docs/MCP.md)** - Model Context Protocol server
- **[NVIDIA GPU](docs/NVIDIA%20Notes.md)** - GPU acceleration

## Architecture

```
PDF Documents → Parser → Ollama (embeddings) → Neo4j (graph + vectors)
                                                      ↓
                                            FastAPI Retriever
                                                      ↓
                               Open-WebUI ← Ollama (LLM) → User
```

See [architecture diagram](docs/Welcome%20to%20Local%20AI%20with%20Neo4j%20DB%20RAG.md) for detailed flow.

## Requirements

### Local Development (Recommended)
- Python 3.13+
- Podman (for Neo4j and Open-WebUI containers)
- Ollama with embedding model (bge-m3 or bge-small-en-v1.5)
- Ollama with chat model (mistral:7b or qwen2.5:3b)
- 16GB+ RAM recommended
- NVIDIA GPU optional (for faster inference)

### Fully Containerized (Optional)
- Podman with Compose
- NVIDIA GPU with drivers + Container Toolkit
- 16GB+ RAM recommended

See the [Quick Start Guide](docs/QUICKSTART.md) for recommended setup or [Deployment Guide](docs/Deployment.md) for containerized options.

## Project Structure

```
src/pjs_neo_rag/
├── config.py              # Centralized configuration
├── neo4j_connection.py    # Database connection utilities
├── create_neo_indexes.py  # Vector and fulltext index creation
├── ingest_pdf.py          # PDF processing and embedding
├── ingest_files.py        # Batch document ingestion
└── neo4j_retriever_api.py # FastAPI retrieval service

app.py                     # API server entry point
docs/                      # Comprehensive documentation
```

## License

MIT

## Author

Phil Soady (phil.soady@gmail.com)
