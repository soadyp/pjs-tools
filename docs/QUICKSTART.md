# Quick Start Guide - Clone to Production

This guide will help you reproduce the entire RAG system on a new machine from scratch.

**Deployment approach:** The Python application runs directly on the host (development mode) while Neo4j and Open-WebUI run in Podman containers. This provides the best balance of development flexibility and service isolation.

## Prerequisites

- Ubuntu/Debian Linux
- 16GB+ RAM
- Internet connection
- NVIDIA GPU with drivers (optional, for faster inference)

## Step 1: Install System Dependencies

```bash
sudo apt update
sudo apt install -y curl wget git python3 python3-pip python3-venv podman
```

## Step 2: Clone the Project

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/pjs-neo-rag.git
cd pjs-neo-rag
```

## Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Critical settings to update:**
- `NEO4J_PASSWORD`: Set a strong password
- `SOURCE_DIR`: Path to your PDF documents (e.g., `/home/username/Documents/pdfs`)
- `OLLAMA_EMBED_MODEL`: Confirm model name matches what you'll pull
- `OLLAMA_EMBED_DIM`: **Must match your embedding model's dimensions**
  - `bge-m3`: 1024
  - `bge-small-en-v1.5`: 384

## Step 4: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Pull embedding model
ollama pull bge-m3

# Pull chat model  
ollama pull mistral:7b

# Verify models
ollama list
```

**Expected output:**
```
NAME                    SIZE
bge-m3:latest          2.2 GB
mistral:7b:latest      4.1 GB
```

## Step 5: Install and Start Neo4j

```bash
# Create volumes
podman volume create neo4j-data
podman volume create neo4j-logs

# Start Neo4j (replace YOUR_PASSWORD with the one from .env)
podman run -d \
  --name neo4j \
  --network host \
  -e NEO4J_AUTH=neo4j/YOUR_PASSWORD \
  -v neo4j-data:/data \
  -v neo4j-logs:/logs \
  neo4j:5.26.0

# Verify Neo4j is running
podman ps | grep neo4j

# Test connection (use your password)
curl -u neo4j:YOUR_PASSWORD http://localhost:7474
```

Access Neo4j Browser at: http://localhost:7474

## Step 6: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -e .

# Verify installation
python -c "from pjs_neo_rag.config import settings; print('Config loaded successfully')"
```

## Step 7: Initialize Database

```bash
# Create vector indexes (with correct dimensions from .env)
python src/pjs_neo_rag/create_neo_indexes.py

# If you need to start fresh (wrong dimensions, etc.)
python src/pjs_neo_rag/create_neo_indexes.py --force
```

**Expected output:**
```
✅ Indexes ensured (DIM=1024) on database 'neo4j'.
```

## Step 8: Ingest Documents

```bash
# Place PDF files in your SOURCE_DIR first!
# Then run ingestion
python src/pjs_neo_rag/ingest_files.py
```

**Expected output:**
```
Step 1: Ensuring indexes...
✅ Indexes ensured (DIM=1024) on database 'neo4j'.

Step 2: Ingesting PDFs from /your/path...
✅ Ingested: document1.pdf  pages=10  chunks=12
✅ Ingested: document2.pdf  pages=25  chunks=28
```

## Step 9: Start the API Server

Open a **dedicated terminal** for the API server (keep it running):

```bash
# Activate environment
source .venv/bin/activate

# Start the API server
python src/app.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test the API (in a new terminal):**
```bash
# Test API is responding
curl http://localhost:8000/docs

# Test a search query
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "k": 3}'
```

Both should return valid responses (HTML for docs, JSON for search).

**Note:** Keep this terminal running. The API must be active for Open-WebUI to use it.

## Step 10: Install Open WebUI

```bash
# Create volume
podman volume create open-webui-data

# Start Open WebUI
podman run -d \
  --name open-webui \
  --network host \
  -v open-webui-data:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Verify it's running
podman ps | grep open-webui
```

Access Open WebUI at: http://localhost:8080

**First login:**
1. Create admin account (first user becomes admin)
2. Navigate to Settings → Connections
3. Add Ollama URL: `http://localhost:11434`
4. Click Test - should show ✅

## Step 11: Configure RAG Tool in Open WebUI

### 11.1 Create the Tool

1. Go to **Workspace → Tools** (or **Settings → Tools** depending on version)
2. Click **+ Create a Tool**
3. Select **HTTP Request Tool** or **Function**

### 11.2 Tool Configuration

**Name:** `graphrag_search` (or any name - will appear in UI)

**Description:** 
```
Search scientific documents in Neo4j knowledge graph using dual-vector embeddings
```

**Type:** `HTTP Request`

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/search`

**Headers:** (leave empty)

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": { 
      "type": "string",
      "description": "Search query for scientific documents"
    },
    "k": { 
      "type": "integer", 
      "default": 8, 
      "minimum": 1, 
      "maximum": 20,
      "description": "Number of results to return"
    },
    "mathy": { 
      "type": "boolean", 
      "default": false,
      "description": "Hint that query is math-heavy"
    }
  },
  "required": ["query"]
}
```

**Response Format:** `JSON`

Click **Save**

### 11.3 Enable Tool for Model

1. Go to **Workspace → Models** (or click on model dropdown)
2. Select your chat model (e.g., `mistral:7b`)
3. Click the **Settings/Edit** icon
4. Scroll to **Tools** section
5. Check the box next to your tool name (`graphrag_search`)
6. Scroll to **Capabilities**
7. Ensure **Function/Tool Calling** is **ON (Native)**

### 11.4 Set System Prompt (Optional but Recommended)

In the same model settings, find **System Prompt** and add:

```
You are a research assistant with access to scientific documents via the graphrag_search tool.

When users ask about topics in your knowledge base, call graphrag_search with relevant keywords.

Always cite page numbers from the results using format: [p.2], [p.7]

Be clear whether information comes from the documents or your general knowledge.
```

Click **Save & Update**

## Step 12: Test the Complete System

1. **Open a new chat** in Open WebUI
2. **Ask a question** about your documents:
   ```
   What does the document say about [YOUR TOPIC]? Please cite page numbers.
   ```

**Expected behavior:**
- You'll see the model "thinking" and calling the tool
- Tool call shows: `graphrag_search(query="...", k=8)`
- Response includes citations like [p.2], [p.5]

## Troubleshooting

### Tool doesn't appear in model settings
- Refresh the Open WebUI page
- Check you saved the tool properly
- Try logging out and back in

### Tool call fails with connection error
- Verify API is running: `curl http://localhost:8000/docs`
- Check URL in tool config is `http://127.0.0.1:8000/search` (not /graphrag/search)
- Ensure Open WebUI is using `--network host` mode

### Model doesn't call the tool
- Verify **Function/Tool Calling** is **ON (Native)**
- Check model has `-instruct` suffix (e.g., `mistral:7b-instruct`)
- Try more explicit prompts: "Use the graphrag_search tool to find..."

### Empty or error results
- Check documents were ingested: Query Neo4j Browser
  ```cypher
  MATCH (c:Chunk) RETURN count(c)
  ```
- Verify vector indexes exist:
  ```cypher
  SHOW INDEXES
  ```
- Check embedding dimensions match between .env and indexes

### Dimension mismatch errors
```
Index query vector has 384 dimensions, but indexed vectors have 1024
```

**Solution:**
```bash
# Drop everything and start fresh
python src/pjs_neo_rag/create_neo_indexes.py --force

# Re-ingest with correct dimensions
python src/pjs_neo_rag/ingest_files.py
```

## Verification Checklist

**Services Running:**
- [ ] Ollama: `ollama list` shows both embedding and chat models
- [ ] Neo4j container: `podman ps | grep neo4j` shows Up status
- [ ] Neo4j browser: http://localhost:7474 accessible with password from .env
- [ ] Open-WebUI container: `podman ps | grep open-webui` shows Up status
- [ ] Open-WebUI: http://localhost:8080 loads and you can log in
- [ ] API server: Terminal shows uvicorn running, http://localhost:8000/docs loads

**Database:**
- [ ] Documents ingested: Neo4j browser → `MATCH (c:Chunk) RETURN count(c)` returns > 0
- [ ] Indexes created: Neo4j browser → `SHOW INDEXES` shows vector indexes

**Open-WebUI Configuration:**
- [ ] Ollama connected: Settings → Connections shows http://localhost:11434 ✅
- [ ] Tool created: Workspace → Tools lists your tool
- [ ] Tool enabled: Model settings → Tools section has your tool checked
- [ ] Function calling ON: Model settings → Function/Tool Calling is ON (Native)

**End-to-End Test:**
- [ ] Chat query triggers tool call and returns citations like [p.2], [p.5]

## Updating the System

### Update Container Images

Check for and install updated versions of containerized services:

```bash
# Update Neo4j
podman pull neo4j:5.26.0
podman stop neo4j && podman rm neo4j
podman run -d --name neo4j --network host \
  -e NEO4J_AUTH=neo4j/yourpassword \
  -v neo4j-data:/data neo4j:5.26.0

# Update Open-WebUI
podman pull ghcr.io/open-webui/open-webui:main
podman stop open-webui && podman rm open-webui
podman run -d --name open-webui --network host \
  -v open-webui-data:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

**Note:** Your data (database, settings) persists in volumes and won't be lost.

### Update Python Application

```bash
# Pull latest code
cd ~/pjs-neo-rag
git pull

# Update dependencies
source .venv/bin/activate
pip install -e . --upgrade

# Restart API server
# Stop the running server (Ctrl+C in its terminal)
python src/app.py
```

### Update Ollama Models

```bash
# Update existing model
ollama pull bge-m3

# Or pull different model and update .env
ollama pull bge-large
nano .env  # Change OLLAMA_EMBED_MODEL=bge-large
```

## Next Steps

- **Add more documents**: Copy PDFs to SOURCE_DIR, run `ingest_files.py`
- **Tune retrieval**: Adjust `k`, `CHUNK_TOKENS`, weights in `.env`
- **Try different models**: `ollama pull` other models and update .env
- **Backup data**: See [PODMAN.md](./PODMAN.md) for volume backup

## Support

- **README.md** - Project overview
- **docs/PODMAN.md** - Container management and updates
- **docs/OPEN-WEBUI-INTEGRATION.md** - Tool configuration details
- **docs/Troubleshooting.md** - Common issues

For issues, check existing documentation or open a GitHub issue.
