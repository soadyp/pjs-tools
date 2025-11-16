# Installation Guide

This document covers the full setup required to develop and run the `pjs-neo-rag` project locally. Follow these steps in order, stopping once all services are installed and verified. Project execution (indexing, ingestion, API startup) is handled separately.

## 1. System Requirements

- Ubuntu/Debian Linux (22.04 LTS or newer recommended)
- Python 3.13 or newer
- 16 GB RAM (32 GB recommended for large corpora)
- 25 GB free disk space
- Optional GPU with recent NVIDIA drivers for accelerated Ollama inference

## 2. Prepare the Host

```bash
sudo apt update
sudo apt install -y curl wget git build-essential pkg-config python3 python3-venv
```

If you plan to use GPU acceleration, install the appropriate NVIDIA drivers before proceeding.

## 3. Install Podman (Recommended)

Podman provides the container runtime used for Neo4j and Open-WebUI.

```bash
sudo apt install -y podman
podman --version
```

For desktop tooling, optionally install [Podman Desktop](https://podman-desktop.io/downloads).

### Enable Rootless Mode (Optional)

```bash
sudo loginctl enable-linger "$USER"
systemctl --user start podman.socket
systemctl --user enable podman.socket
```

Log out/in so the user session picks up lingering services.

## 4. Deploy Neo4j

Choose **one** installation path. The Podman approach keeps Neo4j isolated and is the recommended default.

### 4.1 Podman Container (Recommended)

```bash
podman volume create neo4j-data
podman volume create neo4j-logs

podman run -d \
	--name neo4j \
	--network host \
	-e NEO4J_AUTH=neo4j/<STRONG_PASSWORD> \
	-e NEO4J_dbms_security_procedures_unrestricted=apoc.* \
	-v neo4j-data:/data \
	-v neo4j-logs:/logs \
	-v neo4j-plugins:/plugins \
	neo4j:5.26.0
```

Add the APOC plugin to the mounted plugins directory:

```bash
podman exec neo4j bash -c "cd /plugins && wget https://github.com/neo4j/apoc/releases/download/5.27.0/apoc-5.27.0-core.jar"
podman restart neo4j
```

### 4.2 Native Package Install (Alternative to podman image/container)

```bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/neo4j.gpg
echo "deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest" | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install -y neo4j
sudo systemctl enable --now neo4j
```

Install the matching APOC jar in `/var/lib/neo4j/plugins/` and add `dbms.security.procedures.unrestricted=apoc.*` to `/etc/neo4j/neo4j.conf`, then restart the service.

### 4.3 Verify Neo4j

```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p '<STRONG_PASSWORD>' -d neo4j "RETURN 1"
```

Neo4j Browser should now be reachable at `http://localhost:7474`.

## 5. Install Embedding Runtime

Choose the runtime that matches your hardware. vLLM is recommended for GPU-capable systems, while Ollama remains a good CPU-friendly fallback.

### 5.1 vLLM (Recommended)

```bash
python3 -m venv ~/vllm-server
source ~/vllm-server/bin/activate
python -m pip install --upgrade pip
python -m pip install "vllm[torch]"

# Download the embedding model on first run
python -m vllm.entrypoints.openai.api_server \
	--model BAAI/bge-m3 \
	--task embedding \
	--host 0.0.0.0 \
	--port 8001
```

Leave the server running in a dedicated terminal, or create a systemd/podman service once you confirm everything works. The OpenAI-compatible endpoint will be available at `http://localhost:8001/v1/`.

Verify the endpoint:

```bash
curl -X POST http://localhost:8001/v1/embeddings \
	-H "Content-Type: application/json" \
	-d '{"model":"BAAI/bge-m3","input":"vLLM test"}'
```

If you prefer GPU quantization or additional models, see the [vLLM documentation](https://docs.vllm.ai/en/latest/). The `--task embedding` flag reduces memory usage by disabling generation operators.

### 5.2 Ollama (Alternative)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

Ensure the service is running:

```bash
systemctl status ollama
```

Pull the required models (run individually; downloads may take several minutes):

```bash
ollama pull bge-m3
ollama pull mistral:7b
ollama list
```

## 6. Install Open-WebUI (Podman)

```bash
podman volume create open-webui-data

podman run -d \
	--name open-webui \
	--network host \
	-v open-webui-data:/app/backend/data \
	ghcr.io/open-webui/open-webui:main

podman ps
```

After the container starts, visit `http://localhost:8080`, create the admin user, and configure the Ollama connection (`http://localhost:11434`).

## 7. Fetch Project Source

```bash
cd ~/Documents/_dev
git clone https://github.com/soadyp/pjs-neo-rag.git
cd pjs-neo-rag
```

If the repository already exists, pull the latest changes instead of cloning.

## 8. Configure Python Environment

### 8.1 Using uv (Preferred)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

Activate the environment when needed:

```bash
source .venv/bin/activate
```

### 8.2 Using Standard venv (Alternative)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt  # generate via `pip install .` if needed
```

## 9. Configure Environment Variables

Copy the example file and adjust credentials to match your Neo4j and Ollama setup.

```bash
cp .env.example .env
nano .env
```

Key values:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<STRONG_PASSWORD>
NEO4J_DATABASE=neo4j
EMBED_PROVIDER=vllm
CHAT_PROVIDER=ollama
VLLM_URL=http://localhost:8001
OLLAMA_URL=http://localhost:11434
VLLM_EMBED_MODEL=BAAI/bge-m3
VLLM_EMBED_DIM=1024
OLLAMA_CHAT_MODEL=mistral:7b
OLLAMA_EMBED_MODEL=bge-m3
OLLAMA_EMBED_DIM=1024
VLLM_CHAT_MODEL=mistralai/Mistral-7B-Instruct-v0.2
API_PORT=8000
SOURCE_DIR=/absolute/path/to/your/documents
```

Switch providers at any time by editing `EMBED_PROVIDER` and `CHAT_PROVIDER` (valid values: `ollama`, `vllm`). The matching `*_MODEL` and `*_EMBED_DIM` entries determine which model each backend runs.

## 10. Verify Installations

Run these short checks before moving on to project execution:

- `podman ps` shows `neo4j` and `open-webui` containers in `Up` status (if you used Podman).
- `cypher-shell` authenticates successfully with the configured password.
- `curl http://localhost:8001/v1/models` lists the `BAAI/bge-m3` model (or `ollama list` shows `bge-m3`/`mistral:7b` if using Ollama).
- `.venv` exists and `python -m pip show fastapi` reports the installed dependency.

At this point all components are installed. Proceed to the project execution guide to create indexes, ingest content, and launch the API.

