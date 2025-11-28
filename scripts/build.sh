#!/bin/bash
# Build the pjs-neo-rag container image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

IMAGE_NAME="pjs-neo-rag"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Building pjs-neo-rag Container ===${NC}"

# Check for required files
if [ ! -f "Containerfile" ]; then
    echo -e "${YELLOW}Error: Containerfile not found${NC}"
    exit 1
fi

if [ ! -f "pyproject.toml" ]; then
    echo -e "${YELLOW}Error: pyproject.toml not found${NC}"
    exit 1
fi

# Build the image
echo "Building image: ${IMAGE_NAME}"
podman build -t "$IMAGE_NAME" -f Containerfile .

# Show result
echo ""
echo -e "${GREEN}✅ Build complete${NC}"
echo ""
podman images "$IMAGE_NAME"
echo ""
echo "Next steps:"
echo "  ./scripts/run.sh              # Run standalone (connects to host Neo4j/Ollama)"
echo "  ./scripts/compose.sh up       # Run full stack with compose"
