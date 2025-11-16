from typing import LiteralString

from pjs_neo_rag.config import settings
from pjs_neo_rag.neo4j_connection import get_driver, DB

DIM = settings.EMBED_DIM

BTREE: list[LiteralString] = [
    "CREATE INDEX doc_id   IF NOT EXISTS FOR (d:Document) ON (d.doc_id)",
    "CREATE INDEX sec_id   IF NOT EXISTS FOR (s:Section)  ON (s.sec_id)",
    "CREATE INDEX chunk_id IF NOT EXISTS FOR (c:Chunk)    ON (c.chunk_id)",
    "CREATE INDEX fact_id  IF NOT EXISTS FOR (f:Fact)     ON (f.fact_id)",
    "CREATE INDEX snap_id  IF NOT EXISTS FOR (s:Snapshot) ON (s.snapshot_id)",
]

VECTORS: list[LiteralString] = [
    # prose embeddings (vec_text)
    """
    CREATE VECTOR INDEX chunk_vec_text IF NOT EXISTS
    FOR (c:Chunk) ON (c.vec_text)
    OPTIONS {indexConfig: {`vector.dimensions`: $dim, `vector.similarity_function`: 'cosine'}}
    """,
    # LaTeX embeddings (vec_latex)
    """
    CREATE VECTOR INDEX chunk_vec_latex IF NOT EXISTS
    FOR (c:Chunk) ON (c.vec_latex)
    OPTIONS {indexConfig: {`vector.dimensions`: $dim, `vector.similarity_function`: 'cosine'}}
    """,
    # Facts vector index (optional but recommended if you’ll bias facts)
    """
    CREATE VECTOR INDEX fact_vec IF NOT EXISTS
    FOR (f:Fact) ON (f.embedding)
    OPTIONS {indexConfig: {`vector.dimensions`: $dim, `vector.similarity_function`: 'cosine'}}
    """,
]

FULLTEXT: list[LiteralString] = [
    # BM25/keyword search over raw LaTeX strings for exact symbol/macro hits
    "CREATE FULLTEXT INDEX latex_fulltext IF NOT EXISTS FOR (c:Chunk) ON EACH [c.latex_raw]",
]


def run():
    driver = get_driver()
    try:
        with driver.session(database=DB) as s:
            for q in BTREE:
                s.run(q)
            for q in VECTORS:
                s.run(q, dim=DIM)
            for q in FULLTEXT:
                s.run(q)
    finally:
        driver.close()

    print(f"✅ Indexes ensured (DIM={DIM}) on database '{DB}'.")


if __name__ == "__main__":
    run()
