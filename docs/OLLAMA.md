
# Ollama Setup for Scientific Document RAG

Ollama provides the embedding and chat models for the RAG system.

## Installation

### Running Ollama in Podman (Recommended)

For GPU-accelerated Ollama in a container, follow the [PODMAN.md](./PODMAN.md) guide first to set up NVIDIA Container Toolkit.

**Start Ollama container:**

```bash
podman run -d \
  --name ollama-std \
  --device nvidia.com/gpu=all \
  --security-opt=label=disable \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  docker.io/ollama/ollama:latest
```

### Alternative: Native Installation

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Required Models

This RAG system requires **two types of models**:

### 1. Embedding Model (Required)

**For scientific papers with LaTeX:**

```bash
# Inside container
podman exec ollama-std ollama pull bge-m3

# Or if running natively
ollama pull bge-m3
```

**Model Details:**
- **Name:** bge-m3
- **Size:** ~2.2GB
- **Dimensions:** 1024
- **Purpose:** Generates embeddings for both prose text and LaTeX mathematical notation
- **Why:** Trained on scientific text, handles technical content well

**Alternative (for smaller GPU/testing):**
```bash
ollama pull nomic-embed-text  # 768 dims, ~150MB
ollama pull all-minilm        # 384 dims, ~25MB
```

### 2. Chat Model for Scientific/Math Content (Required)

**Production recommendation:**

```bash
podman exec ollama-std ollama pull mistral:7b
```

**Model Details:**
- **Name:** mistral:7b
- **Size:** ~4.1GB
- **Purpose:** Chat/instruction following for scientific queries
- **Why:** Good balance of performance and resource usage for technical content

**Alternative models to try:**

```bash
# General instruction models
ollama pull qwen2.5:7b-instruct   # Good at reasoning
ollama pull qwen2.5:14b-instruct  # Better quality, needs more VRAM

# Math specialists (if mistral doesn't perform well enough)
ollama pull qwen2.5:7b-math       # Specialized for mathematical reasoning
ollama pull deepseek-math:7b      # Another math-focused model

# Reasoning models (experimental)
ollama pull deepseek-r1:7b        # Chain-of-thought reasoning
```

**For testing on smaller GPUs:**
```bash
ollama pull qwen2.5:3b     # ~2GB, decent quality
ollama pull qwen2.5:1.5b   # ~1GB, minimal but functional
```

## Verifying Installation

### Check models are installed:

```bash
podman exec ollama-std ollama list
```

Expected output:
```
NAME          ID              SIZE      MODIFIED
bge-m3        abc123def456    2.2 GB    X minutes ago
mistral:7b    def789ghi012    4.1 GB    X minutes ago
```

### Test embedding model:

```bash
podman exec ollama-std ollama run bge-m3 "test embedding"
```

### Test chat model:

```bash
podman exec ollama-std ollama run mistral:7b "Explain the Schrödinger equation"
```

### Verify GPU usage:

```bash
nvidia-smi
```

You should see:
- GPU memory usage increased (2-4GB depending on model loaded)
- `/usr/bin/ollama` process in the GPU processes list

## Model Selection Guidelines

### For Production (Main Machine)

- **Embedding:** `bge-m3` - Best LaTeX/scientific text handling
- **Chat:** `mistral:7b` or `qwen2.5:7b-math` - Good balance of quality and speed

### For Development/Testing (Small GPU)

- **Embedding:** `nomic-embed-text` or `all-minilm` - Lighter weight
- **Chat:** `qwen2.5:3b` - Smallest viable model with decent quality

### Choosing Based on GPU Memory

| GPU VRAM | Embedding Model | Chat Model           | Total Usage |
|----------|----------------|----------------------|-------------|
| 4GB      | all-minilm     | qwen2.5:1.5b         | ~1.5GB      |
| 6GB      | nomic-embed    | qwen2.5:3b           | ~2.5GB      |
| 8GB      | bge-m3         | mistral:7b           | ~6GB        |
| 12GB+    | bge-m3         | qwen2.5:14b-instruct | ~9GB        |

## Configuration

The Python code reads model names from environment variables or `config.py`:

```python
OLLAMA_EMBED_MODEL = "bge-m3"
OLLAMA_CHAT_MODEL = "mistral:7b"
```

To use different models, update your `.env` file:

```bash
OLLAMA_EMBED_MODEL=bge-m3
OLLAMA_CHAT_MODEL=mistral:7b
```

## Troubleshooting

### Models running on CPU instead of GPU

See [PODMAN.md Troubleshooting](./PODMAN.md#troubleshooting) section.

### Out of memory errors

Switch to smaller models:
```bash
ollama pull qwen2.5:3b  # Instead of larger models
```

### Model download interrupted

Resume by running the same pull command again:
```bash
podman exec ollama-std ollama pull <model-name>
```

## References

- [Ollama Model Library](https://ollama.com/library)
- [BGE-M3 Paper](https://arxiv.org/abs/2402.03216)
- [Qwen2.5 Documentation](https://qwenlm.github.io/blog/qwen2.5/)
