#!/bin/bash
# Run the pjs-neo-rag container standalone
# Connects to Neo4j and Ollama running on the host

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

IMAGE_NAME="pjs-neo-rag"
CONTAINER_NAME="pjs-neo-rag-app"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Parse arguments
ACTION="${1:-start}"

show_help() {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start    Start the container (default)"
    echo "  stop     Stop the container"
    echo "  restart  Restart the container"
    echo "  logs     Follow container logs"
    echo "  status   Show container status"
    echo "  shell    Open shell in container"
    echo "  help     Show this help"
    echo ""
    echo "To ingest documents, use:"
    echo "  ./load-files-container.sh  (when running in container)"
    echo "  ./load-files.sh            (when running locally)"
}

case "$ACTION" in
    start)
        echo -e "${GREEN}=== Starting pjs-neo-rag Container ===${NC}"
        
        # Check if image exists
        if ! podman image exists "$IMAGE_NAME"; then
            echo -e "${YELLOW}Image not found. Building...${NC}"
            "$SCRIPT_DIR/build.sh"
        fi
        
        # Check for .env.container
        if [ ! -f ".env.container" ]; then
            if [ -f ".env" ]; then
                echo -e "${YELLOW}Creating .env.container from .env${NC}"
                cp .env .env.container
            else
                echo -e "${RED}No .env.container found. Copy .env.example and configure.${NC}"
                exit 1
            fi
        fi
        
        # Stop existing if running
        if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
            echo "Stopping existing container..."
            podman stop "$CONTAINER_NAME" 2>/dev/null || true
            podman rm "$CONTAINER_NAME" 2>/dev/null || true
        fi
        
        # Get SOURCE_DIR from .env.container (host path for documents)
        HOST_SOURCE_DIR=$(grep "^SOURCE_DIR=" .env.container 2>/dev/null | cut -d'=' -f2)
        if [ -z "$HOST_SOURCE_DIR" ]; then
            echo -e "${YELLOW}Warning: SOURCE_DIR not set in .env.container${NC}"
            HOST_SOURCE_DIR="./corpus"
        fi
        
        # Run with host networking (connects to localhost Neo4j/Ollama)
        echo "Starting container with host networking..."
        echo "Mounting documents from: $HOST_SOURCE_DIR"
        podman run -d \
            --name "$CONTAINER_NAME" \
            --network host \
            --env-file .env.container \
            -e SOURCE_DIR=/app/documents \
            -v "${HOST_SOURCE_DIR}:/app/documents:ro" \
            -v rag-logs:/app/logs \
            "$IMAGE_NAME"
        
        # Wait and check health
        echo "Waiting for startup..."
        sleep 3
        
        API_PORT=$(grep "^API_PORT=" .env.container 2>/dev/null | cut -d'=' -f2 || echo "8000")
        API_PORT=${API_PORT:-8000}
        
        if curl -s "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Container is running${NC}"
            echo ""
            echo "API: http://localhost:${API_PORT}"
            echo "Docs: http://localhost:${API_PORT}/docs"
        else
            echo -e "${YELLOW}⚠️  Container started but health check pending${NC}"
            echo "Check logs: ./run.sh logs"
        fi
        ;;
        
    stop)
        echo "Stopping container..."
        podman stop "$CONTAINER_NAME" 2>/dev/null || echo "Container not running"
        ;;
        
    restart)
        "$0" stop
        sleep 1
        "$0" start
        ;;
        
    logs)
        podman logs -f "$CONTAINER_NAME"
        ;;
        
    status)
        if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
            echo -e "${GREEN}● Running${NC}"
            podman ps --filter "name=${CONTAINER_NAME}"
        else
            echo -e "${YELLOW}○ Stopped${NC}"
        fi
        ;;
        
    shell)
        podman exec -it "$CONTAINER_NAME" /bin/bash
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        echo "Unknown command: $ACTION"
        show_help
        exit 1
        ;;
esac
