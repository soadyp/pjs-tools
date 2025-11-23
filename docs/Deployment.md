# Deployment Guide

This guide covers deploying the complete RAG stack using Podman containers.

## Prerequisites

1. **NVIDIA GPU with drivers installed**
2. **Podman installed**
3. **NVIDIA Container Toolkit** (see [PODMAN.md](./PODMAN.md))

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd pjs-neo-rag
```

### 2. Configure environment

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Important:** Update `SOURCE_DIR` to point to your document directory:
```bash
SOURCE_DIR=/mnt/ubuntustore/RAG-Docs
```

### 3. Update podman-compose.yml

Edit the `rag-app` service volume mount to match your document path:
```yaml
volumes:
  - /mnt/ubuntustore/RAG-Docs:/app/documents:ro
```

### 4. Start all services

```bash
podman-compose up -d
```

This starts:
- Neo4j database (ports 7474, 7687)
- Ollama with GPU (port 11434)
- Open-WebUI (port 3000)
- RAG API (port 8000)

### 5. Pull Ollama models

```bash
# Embedding model
podman exec ollama-std ollama pull bge-m3

# Chat model
podman exec ollama-std ollama pull mistral:7b
```

### 6. Create Neo4j indexes

```bash
podman exec pjs-neo-rag-app python src/pjs_neo_rag/create_neo_indexes.py
```

### 7. Ingest documents

```bash
podman exec pjs-neo-rag-app python src/pjs_neo_rag/ingest_files.py
```

## Manual Container Setup (Individual Services)

If you prefer manual control or don't use compose:

### 1. Start Neo4j

```bash
podman run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/yourpassword \
  -v neo4j-data:/data \
  docker.io/neo4j:latest
```

### 2. Start Ollama with GPU

```bash
podman run -d \
  --name ollama-std \
  --device nvidia.com/gpu=all \
  --security-opt=label=disable \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  docker.io/ollama/ollama:latest
```

### 3. Pull Ollama models

```bash
podman exec ollama-std ollama pull bge-m3
podman exec ollama-std ollama pull mistral:7b
```

### 4. Start Open-WebUI

```bash
podman run -d \
  --name open-webui \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://host.containers.internal:11434 \
  -v open-webui-data:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

### 5. Build and run RAG app

```bash
# Build the image
podman build -t pjs-neo-rag:latest .

# Run the app
podman run -d \
  --name pjs-neo-rag-app \
  -p 8000:8000 \
  -v /mnt/ubuntustore/RAG-Docs:/app/documents:ro \
  -e NEO4J_URI=bolt://host.containers.internal:7687 \
  -e NEO4J_PASSWORD=yourpassword \
  -e OLLAMA_URL=http://host.containers.internal:11434 \
  pjs-neo-rag:latest
```

## Deployment on Target Machine

When deploying to your main machine:

```bash
# 1. Clone repo
git clone <repo-url> pjs-neo-rag
cd pjs-neo-rag

# 2. Setup environment
cp .env.example .env
nano .env  # Configure for your machine

# 3. Update document path in podman-compose.yml
nano podman-compose.yml  # Edit volume mount

# 4. Start everything
podman-compose up -d

# 5. Pull production models
podman exec ollama-std ollama pull bge-m3
podman exec ollama-std ollama pull mistral:7b

# 6. Initialize database
podman exec pjs-neo-rag-app python src/pjs_neo_rag/create_neo_indexes.py

# 7. Ingest documents
podman exec pjs-neo-rag-app python src/pjs_neo_rag/ingest_files.py
```

## Verifying Deployment

### Check all containers are running:

```bash
podman ps
```

Expected output:
```
CONTAINER ID  IMAGE                    STATUS      PORTS
xxxxxxxxxxxx  neo4j:latest             Up          0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
xxxxxxxxxxxx  ollama/ollama:latest     Up          0.0.0.0:11434->11434/tcp
xxxxxxxxxxxx  open-webui:main          Up          0.0.0.0:3000->8080/tcp
xxxxxxxxxxxx  pjs-neo-rag:latest       Up          0.0.0.0:8000->8000/tcp
```

### Check GPU usage:

```bash
nvidia-smi
```

Should show Ollama process using GPU memory (2-4GB when model loaded).

### Test API:

```bash
curl http://localhost:8000/docs
```

### Access services:

- **Neo4j Browser:** http://localhost:7474
- **API Documentation:** http://localhost:8000/docs
- **Open-WebUI:** http://localhost:3000

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild container
podman build -t pjs-neo-rag:latest -f Containerfile .

# Restart app container
podman stop pjs-neo-rag-app
podman rm pjs-neo-rag-app
podman-compose up -d rag-app
```

## Troubleshooting

### Container can't connect to other services

**Issue:** "Connection refused" errors

**Solution:** Use `host.containers.internal` instead of `localhost` in connection strings when containers need to talk to each other.

### GPU not accessible in Ollama container

See [PODMAN.md Troubleshooting](./PODMAN.md#troubleshooting)

### Document directory not accessible

**Issue:** "No such file or directory" when ingesting

**Check:**
1. Path in podman-compose.yml matches your actual path
2. Path is absolute (starts with `/`)
3. Directory exists and has read permissions

```bash
ls -la /mnt/ubuntustore/RAG-Docs
```

### Models not persisting

**Issue:** Models disappear after container restart

**Solution:** Ensure volume is properly mounted:
```bash
podman volume inspect ollama-data
```

## Production Considerations

### Resource Limits

Add resource constraints in podman-compose.yml:

```yaml
rag-app:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
```

### Backup Volumes

```bash
# Backup Neo4j data
podman run --rm -v neo4j-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/neo4j-backup.tar.gz /data

# Backup Ollama models
podman run --rm -v ollama-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ollama-backup.tar.gz /data
```

### Monitoring

```bash
# View logs
podman logs -f pjs-neo-rag-app
podman logs -f ollama-std

# Check resource usage
podman stats
```

## References

- [PODMAN.md](./PODMAN.md) - Podman and GPU setup
- [OLLAMA.md](./OLLAMA.md) - Model selection and configuration
- [Neo4j.md](./Neo4j.md) - Database setup and queries
