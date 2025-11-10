# Troubleshooting Guide

Common issues and solutions for the Local AI RAG system.

## Neo4j Issues

### Connection Failed
```bash
# Check if Neo4j is running
systemctl status neo4j

# Check logs
sudo journalctl -u neo4j -f

# Verify port is open
netstat -tuln | grep 7687

# Test connection
cypher-shell -a bolt://localhost:7687 -u neo4j -p 'pjsneo!!' -d neo4j "RETURN 1"
```

### Password Authentication Failed
```bash
# Reset password
sudo neo4j-admin dbms set-initial-password pjsneo!!

# Restart service
sudo systemctl restart neo4j
```

### APOC Plugin Not Working
```bash
# Verify plugin is in plugins directory
ls -la /var/lib/neo4j/plugins/

# Check neo4j.conf has unrestricted setting
grep apoc /etc/neo4j/neo4j.conf

# Should show: dbms.security.procedures.unrestricted=apoc.*

# Restart after config change
sudo systemctl restart neo4j
```

## Ollama Issues

### Service Not Running
```bash
# Check status
systemctl status ollama

# Check logs
journalctl -u ollama -f

# Restart service
sudo systemctl restart ollama

# Manual start (if needed)
ollama serve
```

### Model Not Found
```bash
# List installed models
ollama list

# Pull missing model
ollama pull bge-m3
ollama pull mistral:7b

# Remove and re-pull if corrupted
ollama rm bge-m3
ollama pull bge-m3
```

### Slow Inference
```bash
# Check GPU usage (if you have NVIDIA GPU)
nvidia-smi

# Check if model is using GPU
watch -n 0.5 nvidia-smi
# Run a query and watch GPU memory/utilization
```

See [[NVIDIA Notes]] for GPU monitoring details.

### Port Already in Use
```bash
# Check what's using port 11434
sudo lsof -i :11434

# Kill the process if needed
sudo kill -9 <PID>

# Restart Ollama
sudo systemctl restart ollama
```

## Open-WebUI Issues

### Container Won't Start
```bash
# Check container status
podman ps -a

# View container logs
podman logs open-webui

# Remove and recreate container
podman stop open-webui
podman rm open-webui
podman run -d --network=host --name open-webui -v open-webui-data:/app/backend/data ghcr.io/open-webui/open-webui:main
```

### Can't Connect to Ollama
1. Verify container is using host networking: `podman inspect open-webui | grep NetworkMode`
2. Should show: `"NetworkMode": "host"`
3. Try connection URL: `http://localhost:11434` instead of `http://host.docker.internal:11434`
4. Check Ollama is accessible from host: `curl http://localhost:11434/api/tags`

### Models Not Appearing
1. Go to **Settings** → **Admin Panel** → **Connections**
2. Remove existing Ollama connection
3. Add new connection with URL: `http://localhost:11434`
4. Click "Verify" button
5. Refresh page

### LaTeX Not Rendering
1. Verify system prompt is set (see [[OPEN-WEBUI]])
2. Test with simple query: "What is the Pythagorean theorem?"
3. Response should use `$a^2 + b^2 = c^2$` format, not backticks

## Python RAG Project Issues

### Module Not Found
```bash
# Verify virtual environment is activated
which python
# Should show: /path/to/pjs-neo-rag/.venv/bin/python

# Activate if needed
source .venv/bin/activate

# Reinstall dependencies
uv sync
```

### Import Error: pjs_neo_rag
```bash
# Ensure you're in project root
cd /path/to/pjs-neo-rag

# Install in editable mode
uv pip install -e .
```

### Connection to Neo4j Failed
```bash
# Test connection script
python src/pjs_neo_rag/neo4j_connection_test.py

# Check .env file has correct credentials
cat .env | grep NEO4J
```

### Embedding Dimension Mismatch
```bash
# Error: "Got dim 1024 but expected 384"
# Fix: Update .env to match your model
# For bge-m3: EMBED_DIM=1024
# For bge-small-en-v1.5: EMBED_DIM=384

# Recreate indexes after changing
python src/pjs_neo_rag/create_neo_indexes.py
```

### No PDFs Found
```bash
# Verify SOURCE_DIR in .env
cat .env | grep SOURCE_DIR

# Check directory exists and has PDFs
ls -la /path/to/SOURCE_DIR/**/*.pdf

# Update .env with correct path
nano .env
```

## FastAPI Issues

### Port Already in Use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Change port in .env
echo "API_PORT=8001" >> .env

# Restart app
python app.py
```

### API Not Responding
```bash
# Check if running
curl http://localhost:8000/docs

# View logs when starting
python app.py
# Look for errors in output
```

### Vector Search Returns No Results
```bash
# Verify data is ingested
# Open Neo4j Browser: http://localhost:7474
# Run query: MATCH (c:Chunk) RETURN count(c)

# Verify indexes exist
# In Neo4j Browser: SHOW INDEXES

# Re-ingest if needed
python src/pjs_neo_rag/ingest_files.py
```

## General System Issues

### Out of Memory
```bash
# Check memory usage
free -h

# Check which process is using memory
top
# Press Shift+M to sort by memory

# Consider:
# - Use smaller model (qwen2.5:7b instead of larger)
# - Reduce batch size in ingestion
# - Add swap space
```

### Disk Space Full
```bash
# Check disk usage
df -h

# Clean Docker/Podman images
podman system prune -a

# Clean Ollama cache
rm -rf ~/.ollama/models/* 
ollama pull bge-m3  # Re-pull needed models
```

### Slow Performance
1. **Enable GPU**: See [[NVIDIA Notes]]
2. **Use smaller models**: Try `qwen2.5:7b` instead of larger models
3. **Reduce chunk size**: Lower `CHUNK_TOKENS` in `.env`
4. **Limit results**: Lower `K_PROSE` and `K_LATEX` values

## Getting Help

If you're still stuck:

1. Check logs systematically:
   - Neo4j: `sudo journalctl -u neo4j -n 100`
   - Ollama: `journalctl -u ollama -n 100`
   - Podman: `podman logs open-webui --tail 100`

2. Verify services are running:
   ```bash
   systemctl status neo4j
   systemctl status ollama
   podman ps
   ```

3. Test each component individually before testing the full system

4. Review the [[Installation Guide]] to ensure no steps were missed
