import os
import re
import hashlib
import fitz  # PyMuPDF
from neo4j import GraphDatabase
from pjs_neo_rag.config import settings
from pjs_neo_rag.ollama import embed_ollama

# --- LaTeX splitter (keeps math verbatim) ---
LTX = re.compile(
    r"(\$\$.*?\$\$|\$.*?\$|\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|tikzpicture)\}.*?\\end\{\2\})",
    re.S,
)


def split_latex(text: str):
    parts = LTX.split(text)
    latex = [p for p in parts if LTX.fullmatch(p)]
    prose = "".join(" ⟨EQ⟩ " if LTX.fullmatch(p) else p for p in parts)
    return prose.strip(), "\n".join(latex).strip()


# --- Simple chunker (byte/char based; replace with token-aware later if you like) ---
def chunk_text(
    s: str,
    target_tokens: int = settings.CHUNK_TOKENS,
    overlap_tokens: int = settings.CHUNK_OVERLAP,
):
    # rough: ~4 chars per token
    step = max(200, target_tokens * 4)
    ovlp = overlap_tokens * 4
    i = 0
    n = len(s)
    while i < n:
        j = min(n, i + step)
        yield i, s[i:j]
        if j == n:
            break
        i = max(i + step - ovlp, 0)


# --- Upsert batch into Neo4j ---
UPSERT = """
UNWIND $rows AS r
MERGE (d:Document {doc_id:r.doc_id})
  ON CREATE SET d.title=r.title, d.path=r.path, d.page_count=r.page_count, d.added_at=timestamp()
  ON MATCH  SET d.path=r.path, d.page_count=r.page_count
MERGE (s:Section {sec_id:r.sec_id})
  ON CREATE SET s.title=r.section, s.page_start=r.page_start, s.page_end=r.page_end
  ON MATCH  SET s.page_start=r.page_start, s.page_end=r.page_end
MERGE (d)-[:CONTAINS]->(s)
MERGE (c:Chunk {chunk_id:r.chunk_id})
SET  c.text_norm=r.text_norm,
     c.latex_raw=r.latex_raw,
     c.vec_text=r.vec_text,
     c.vec_latex=r.vec_latex,
     c.page_start=r.page_start,
     c.page_end=r.page_end,
     c.source_hash=r.doc_id,
     c.source_type='pdf',
     c.added_at=coalesce(c.added_at, timestamp())
MERGE (s)-[:CONTAINS]->(c);
"""


def ingest_pdf(pdf_path: str):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    # Stable doc_id = SHA256(file bytes)
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
    doc_id = hashlib.sha256(file_bytes).hexdigest()

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = doc.page_count
    title = (doc.metadata.get("title") or os.path.basename(pdf_path)).strip()

    rows = []
    for p in range(page_count):
        page_num = p + 1
        text = doc.load_page(p).get_text("text")
        for off, chunk in chunk_text(text):
            text_norm, latex_raw = split_latex(chunk)
            vec_text = embed_ollama(text_norm)
            vec_latex = embed_ollama(latex_raw or " ")
            chunk_id = f"{doc_id}:p{page_num}:o{off}"
            sec_id = f"{doc_id}:p{page_num}"
            rows.append(
                {
                    "doc_id": doc_id,
                    "title": title,
                    "path": os.path.abspath(pdf_path),
                    "page_count": page_count,
                    "sec_id": sec_id,
                    "section": f"Page {page_num}",
                    "page_start": page_num,
                    "page_end": page_num,
                    "chunk_id": chunk_id,
                    "text_norm": text_norm,
                    "latex_raw": latex_raw,
                    "vec_text": vec_text,
                    "vec_latex": vec_latex,
                }
            )

    driver = GraphDatabase.driver(
        settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    with driver.session(database=settings.NEO4J_DATABASE) as s:
        # batch in chunks to avoid huge payloads
        BATCH = 200
        for i in range(0, len(rows), BATCH):
            s.run(UPSERT, rows=rows[i : i + BATCH])

    print(f"✅ Ingested: {pdf_path}  pages={page_count}  chunks={len(rows)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: uv run python src/grag/ingest/ingest_one_pdf.py /path/to/file.pdf"
        )
        sys.exit(1)
    ingest_pdf(sys.argv[1])
