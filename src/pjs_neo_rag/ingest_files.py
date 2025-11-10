"""Batch ingest all PDFs from SOURCE_DIR."""
import glob
import sys
from pjs_neo_rag.config import settings
from pjs_neo_rag.ingest_pdf import ingest_pdf

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
