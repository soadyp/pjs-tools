"""Batch ingest all PDFs from SOURCE_DIR."""

import glob
import sys
from pjs_neo_rag.config import settings
from pjs_neo_rag.ingest_pdf import ingest_pdf
from pjs_neo_rag.create_neo_indexes import run as create_indexes

# Step 1: Ensure indexes exist
print("Step 1: Ensuring indexes...")
create_indexes(force_recreate=False)

# Step 2: Ingest PDFs
print(f"\nStep 2: Ingesting PDFs from {settings.SOURCE_DIR}...")
SOURCE_DIR = settings.SOURCE_DIR
files = sorted(glob.glob(str(SOURCE_DIR / "**/*.pdf"), recursive=True))
if not files:
    print(f"No PDFs found under {SOURCE_DIR}")
    sys.exit(0)

for f in files:
    try:
        ingest_pdf(f)
    except Exception as e:
        print(f"[WARN] {f}: {e}")
