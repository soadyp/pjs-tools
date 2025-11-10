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

```bash
# Create indexes
python src/pjs_neo_rag/create_neo_indexes.py

# Ingest documents
python src/pjs_neo_rag/ingest_files.py

# Start API server
python app.py
```

API available at: http://localhost:8000/docs

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Welcome to Local AI](docs/Welcome%20to%20Local%20AI%20with%20Neo4j%20DB%20RAG.md)** - System overview and architecture diagram
- **[Installation Guide](docs/Installation%20Guide.md)** - Complete setup instructions for all components
- **[Troubleshooting](docs/Troubleshooting.md)** - Common issues and solutions

### Component Guides

- **[Neo4j Setup](docs/Neo4j.md)** - Database configuration and commands
- **[Ollama Setup](docs/OLLAMA.md)** - Embedding and LLM models
- **[Open-WebUI Setup](docs/OPEN-WEBUI.md)** - Chat interface configuration
- **[Podman Setup](docs/PODMAN.md)** - Container runtime
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

- Python 3.13+
- Neo4j 5.x
- Ollama with bge-m3 and mistral:7b models
- 16GB+ RAM recommended

See the [Installation Guide](docs/Installation%20Guide.md) for complete setup instructions.

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
