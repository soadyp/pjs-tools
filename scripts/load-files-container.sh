#!/bin/bash
# Load/ingest files when running in container mode
# Executes ingestion inside the running pjs-neo-rag container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

CONTAINER_NAME="pjs-neo-rag-app"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Loading Files (Container Mode) ===${NC}"

# Check if container is running
if ! podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}Container '${CONTAINER_NAME}' is not running.${NC}"
    echo ""
    echo "Start it first with: ./scripts/run.sh start"
    echo ""
    echo "Or run a one-time ingestion:"
    echo "  podman run --rm --network host --env-file .env.container \\"
    echo "    -v /path/to/docs:/app/documents:ro \\"
    echo "    pjs-neo-rag python src/pjs_neo_rag/ingest_files.py"
    exit 1
fi

# Show mounted documents path
echo "Container: ${CONTAINER_NAME}"
echo "Documents mounted at: /app/documents"
echo ""

# Run ingestion in container
podman exec "$CONTAINER_NAME" python src/pjs_neo_rag/ingest_files.py

echo ""
echo -e "${GREEN}✅ File loading complete${NC}"
