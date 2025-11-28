#!/bin/bash
# Load/ingest files when running locally (not in container)
# Runs the Python ingestion script directly

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Loading Files (Local Mode) ===${NC}"

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${RED}Virtual environment not found. Run 'uv sync' first.${NC}"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check for .env
if [ ! -f ".env" ]; then
    echo -e "${RED}No .env file found. Copy .env.example and configure.${NC}"
    exit 1
fi

# Show SOURCE_DIR
SOURCE_DIR=$(grep "^SOURCE_DIR=" .env 2>/dev/null | cut -d'=' -f2)
echo "Document source: ${SOURCE_DIR:-not set}"
echo ""

# Run ingestion
python src/pjs_neo_rag/ingest_files.py

echo ""
echo -e "${GREEN}✅ File loading complete${NC}"
