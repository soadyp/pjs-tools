# Complete Installation Guide

This guide walks through setting up a complete local RAG system with Neo4j, Ollama, and Open-WebUI.

## Prerequisites

- Ubuntu/Debian Linux (or compatible)
- Python 3.13+
- 16GB+ RAM recommended
- GPU 

## 1. Install Flatpak (Optional)

```bash
sudo apt install flatpak
```

## 2. Install Neo4j Community Edition

### Download and Install
```bash
# Add Neo4j repository
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update

# Install Neo4j
sudo apt install neo4j

# Start Neo4j service
sudo systemctl enable neo4j
sudo systemctl start neo4j
```

### Configure Neo4j
```bash
# Set initial password
cypher-shell -a bolt://localhost:7687 -u neo4j -p neo4j
# You'll be prompted to change password - 
# Set the neo4j password in .env 


```

### Add APOC Plugin
```bash
# Download APOC plugin matching your Neo4j version
cd /var/lib/neo4j/plugins
sudo wget https://github.com/neo4j/apoc/releases/download/5.27.0/apoc-5.27.0-core.jar

# Enable APOC in config
sudo nano /etc/neo4j/neo4j.conf
# Add: dbms.security.procedures.unrestricted=apoc.*

# Restart Neo4j
sudo systemctl restart neo4j
```

### Verify Installation
```bash
systemctl status neo4j
cypher-shell -a bolt://localhost:7687 -u neo4j -p 'pjsneo!!' -d neo4j "RETURN 1"
```

Browser: http://localhost:7474/browser/

## 3. Install Neo4j MCP Server (Optional)

```bash
# Install globally
sudo npm install -g @neo4j-labs/neo4j-mcp

# Verify installation
which neo4j-mcp
# Should output: /usr/local/bin/neo4j-mcp
```

See [[MCP]] for configuration details.

## 4. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service (usually auto-starts)
systemctl status ollama
```

### Pull Required Models

```bash
# Embedding model for RAG (1024 dimensions)
ollama pull bge-m3

# Chat model for generation
ollama pull mistral:7b

# Verify models
ollama list
```

### Test Ollama
```bash
# Test embedding
curl http://localhost:11434/api/embeddings -d '{
  "model": "bge-m3",
  "prompt": "test"
}'

# Test chat
ollama run mistral:7b "Hello, world!"
```

## 5. Install Podman

```bash
# Install Podman
sudo apt update
sudo apt install podman

# Verify installation
podman --version

# Optional: Install Podman Desktop
# Download from https://podman-desktop.io/downloads
```

## 6. Install and Configure Open-WebUI

```bash
# Pull Open-WebUI image
podman pull ghcr.io/open-webui/open-webui:main

# Run container with host networking
podman run -d \
  --network=host \
  --name open-webui \
  -v open-webui-data:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Verify container is running
podman ps
```

### Configure Open-WebUI

1. Open browser: http://localhost:8080/
2. Create admin account on first login
3. Go to **Settings** → **Admin Panel** → **Connections**
4. Add Ollama connection:
   - URL: `http://host.docker.internal:11434`
   - (This works because of `--network=host` flag)
5. Verify models appear in model selector

### Add LaTeX System Prompt

In Open-WebUI, go to **Settings** → **Personalization** → **System Prompt**:

```
**CRITICAL INSTRUCTION:** You MUST render all mathematical content using LaTeX.

- Use `$...$` for inline math.
- Use `$$...$$` for block equations.
- You MUST NOT use markdown backticks to render math.
```

## 7. Install Python RAG Project

```bash
# Clone or create project directory
cd ~/Documents/_dev
mkdir -p pjs-neo-rag
cd pjs-neo-rag

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Create .env file
cp .env.example .env
nano .env
```

### Configure .env
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<redacted>
NEO4J_DATABASE=neo4j
EMBED_PROVIDER=ollama
CHAT_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
VLLM_URL=http://localhost:8001
OLLAMA_EMBED_MODEL=bge-m3
OLLAMA_EMBED_DIM=1024
OLLAMA_CHAT_MODEL=mistral:7b
VLLM_EMBED_MODEL=BAAI/bge-m3
VLLM_EMBED_DIM=1024
VLLM_CHAT_MODEL=mistralai/Mistral-7B-Instruct-v0.2

SOURCE_DIR=/path/to/your/pdf/documents
API_PORT=8000
```

Toggle providers by changing `EMBED_PROVIDER` and `CHAT_PROVIDER` between `ollama` and `vllm`. The corresponding `*_MODEL` and `*_EMBED_DIM` variables tell each service which model configuration to use.

### Initialize Database

```bash
# Activate virtual environment
source .venv/bin/activate

# Create indexes
python src/pjs_neo_rag/create_neo_indexes.py

# Ingest documents
python src/pjs_neo_rag/ingest_files.py
```

### Start RAG API Server

```bash
python app.py
```

API docs: http://localhost:8000/docs

## Verification Checklist

- [ ] Neo4j running: `systemctl status neo4j`
- [ ] Neo4j browser accessible: http://localhost:7474
- [ ] Ollama running: `systemctl status ollama`
- [ ] Ollama models pulled: `ollama list` shows bge-m3 and mistral:7b
- [ ] Open-WebUI running: `podman ps` shows container
- [ ] Open-WebUI accessible: http://localhost:8080
- [ ] RAG API running: http://localhost:8000/docs
- [ ] Documents ingested: Check Neo4j browser for nodes

## Need Help?

If you encounter issues during installation, see [[Troubleshooting]] for detailed solutions.

