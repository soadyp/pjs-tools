#!/bin/bash
# Manage the full RAG stack with podman-compose
# Includes: Neo4j, Ollama, Open-WebUI, and RAG API

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ACTION="${1:-help}"
SERVICE="${2:-}"

show_help() {
    echo -e "${CYAN}=== RAG Stack Compose Manager ===${NC}"
    echo ""
    echo "Usage: ./compose.sh [command] [service]"
    echo ""
    echo "Commands:"
    echo "  up        Start all services (or specific service)"
    echo "  down      Stop all services"
    echo "  restart   Restart all services (or specific service)"
    echo "  status    Show status of all services"
    echo "  logs      Follow logs (all or specific service)"
    echo "  build     Build the rag-app image"
    echo "  pull      Pull latest images for all services"
    echo "  help      Show this help"
    echo ""
    echo "Services: neo4j, ollama, open-webui, rag-app"
    echo ""
    echo "Examples:"
    echo "  ./compose.sh up              # Start full stack"
    echo "  ./compose.sh up rag-app      # Start just RAG app"
    echo "  ./compose.sh logs neo4j      # Follow Neo4j logs"
    echo "  ./compose.sh restart         # Restart everything"
}

check_compose() {
    if ! command -v podman-compose &> /dev/null; then
        echo -e "${RED}podman-compose not found${NC}"
        echo "Install with: pip install podman-compose"
        exit 1
    fi
}

case "$ACTION" in
    up)
        check_compose
        echo -e "${GREEN}=== Starting RAG Stack ===${NC}"
        
        if [ -n "$SERVICE" ]; then
            echo "Starting service: $SERVICE"
            podman-compose up -d "$SERVICE"
        else
            echo "Starting all services..."
            podman-compose up -d
        fi
        
        echo ""
        echo -e "${GREEN}Services:${NC}"
        echo "  Neo4j Browser:  http://localhost:7474"
        echo "  Ollama API:     http://localhost:11434"
        echo "  Open-WebUI:     http://localhost:8080"
        echo "  RAG API:        http://localhost:8000"
        echo ""
        echo "Check status: ./compose.sh status"
        ;;
        
    down)
        check_compose
        echo "Stopping all services..."
        podman-compose down
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;
        
    restart)
        check_compose
        if [ -n "$SERVICE" ]; then
            echo "Restarting service: $SERVICE"
            podman-compose restart "$SERVICE"
        else
            echo "Restarting all services..."
            podman-compose restart
        fi
        ;;
        
    status)
        check_compose
        echo -e "${CYAN}=== Stack Status ===${NC}"
        podman-compose ps
        ;;
        
    logs)
        check_compose
        if [ -n "$SERVICE" ]; then
            podman-compose logs -f "$SERVICE"
        else
            podman-compose logs -f
        fi
        ;;
        
    build)
        check_compose
        echo "Building rag-app image..."
        podman-compose build rag-app
        echo -e "${GREEN}✅ Build complete${NC}"
        ;;
        
    pull)
        check_compose
        echo "Pulling latest images..."
        podman-compose pull
        echo -e "${GREEN}✅ Images updated${NC}"
        echo ""
        echo "Restart to use new images: ./compose.sh restart"
        ;;
        
    help|--help|-h|"")
        show_help
        ;;
        
    *)
        echo "Unknown command: $ACTION"
        show_help
        exit 1
        ;;
esac
