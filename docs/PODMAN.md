# Podman Setup for GPU-Accelerated Containers

Podman is the container runtime used for running Ollama and Open-WebUI with GPU acceleration.

## Prerequisites

- NVIDIA GPU with proper drivers installed
- Ubuntu/Debian-based system (instructions can be adapted for other distros)

## Installation Steps

### 1. Install Podman

```bash
# Install Podman
sudo apt-get update
sudo apt-get install -y podman

# Verify installation
podman --version
```

**Optional: Install Podman Desktop** (GUI for container management):
```bash
# Download from https://podman-desktop.io/
# Or install via package manager if available
```

Podman Desktop provides:
- Visual container management
- Image browsing and updates
- Volume and network inspection
- Easy container logs viewing

### 2. Install NVIDIA Container Toolkit

The NVIDIA Container Toolkit is **required** for GPU access in containers.

#### Add NVIDIA repository:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

#### Install the toolkit:

```bash
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

This automatically:
- Installs CDI (Container Device Interface) support
- Generates GPU device specifications at `/var/run/cdi/nvidia.yaml`
- Enables systemd services for automatic CDI spec refresh

### 3. Verify CDI Configuration

```bash
nvidia-ctk cdi list
```

You should see output like:
```
INFO[0000] Found 3 CDI devices
nvidia.com/gpu=0
nvidia.com/gpu=GPU-xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
nvidia.com/gpu=all
```

## Running Containers with GPU Access

### Ollama Container with GPU

To run Ollama with GPU access:

```bash
podman run -d \
  --name ollama-std \
  --device nvidia.com/gpu=all \
  --security-opt=label=disable \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  docker.io/ollama/ollama:latest
```

**Key parameters:**
- `--device nvidia.com/gpu=all` - Grants access to all GPUs via CDI
- `--security-opt=label=disable` - Required for GPU device access
- `-v ollama-data:/root/.ollama` - Persists models and config

### Verifying GPU Usage

#### Check container is running:
```bash
podman ps
```

#### Run a model and check GPU memory:
```bash
# In one terminal, run a model
podman exec ollama-std ollama run <model-name> "test query"

# In another terminal, check GPU usage
nvidia-smi
```

You should see:
- Increased GPU memory usage (e.g., 2-4GB depending on model)
- `/usr/bin/ollama` process listed in the GPU processes section

## Troubleshooting

### Container can't access GPU

**Symptom:** Models run on CPU, low GPU memory usage (< 10MB)

**Solution:** Ensure container was created with `--device nvidia.com/gpu=all`

```bash
# Check if GPU devices are configured
podman inspect <container-name> | grep -i device

# Should show: "Devices": [...] not "Devices": []
```

If empty, recreate the container with proper GPU access:
```bash
podman stop <container-name>
podman rm <container-name>
# Re-run with --device nvidia.com/gpu=all
```

### CDI devices not found

**Symptom:** Error: `unresolvable CDI devices nvidia.com/gpu=all`

**Solution:** Regenerate CDI specifications:

```bash
sudo systemctl restart nvidia-cdi-refresh.service
nvidia-ctk cdi list
```

### Models already downloaded but not showing after recreating container

**Symptom:** `ollama list` shows empty after container recreation

**Cause:** Models are stored in the volume, but need to be re-pulled if volume was not properly mounted

**Solution:** Ensure the volume name matches: `-v ollama-data:/root/.ollama`

## Managing Container Images

### Updating Containers

When new versions are available, update your containers:

```bash
# Update Neo4j
podman pull neo4j:5.26.0  # or :latest for newest
podman stop neo4j
podman rm neo4j
# Re-run with new image (data persists in volume)
podman run -d --name neo4j --network host \
  -e NEO4J_AUTH=neo4j/yourpassword \
  -v neo4j-data:/data neo4j:5.26.0

# Update Open-WebUI
podman pull ghcr.io/open-webui/open-webui:main
podman stop open-webui
podman rm open-webui
podman run -d --name open-webui --network host \
  -v open-webui-data:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Update Ollama (with GPU)
podman pull docker.io/ollama/ollama:latest
podman stop ollama-std
podman rm ollama-std
podman run -d --name ollama-std \
  --device nvidia.com/gpu=all \
  --security-opt=label=disable \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  docker.io/ollama/ollama:latest
```

**Important:** Data persists in named volumes (`-v volumename:/path`), so updates won't lose your:
- Neo4j database (neo4j-data)
- Open-WebUI settings (open-webui-data)
- Ollama models (ollama-data)

### List Installed Images

```bash
# Show all downloaded images
podman images

# Check for updates (manual process)
podman pull <image-name>  # Downloads if newer available
```

### Remove Old Images

```bash
# List images
podman images

# Remove specific image
podman rmi <image-id>

# Remove all unused images (cleanup)
podman image prune -a
```

### Check Container Status

```bash
# List running containers
podman ps

# List all containers (including stopped)
podman ps -a

# Check container logs
podman logs <container-name>

# Follow logs in real-time
podman logs -f <container-name>
```

## References

- [NVIDIA Container Toolkit Documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [CDI Support Documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html)
- [Podman GPU Support](https://github.com/containers/podman/discussions)
- [Podman Command Reference](https://docs.podman.io/en/latest/Commands.html)




