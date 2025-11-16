"""
Core search logic for dual-vector RAG retrieval.
Separate from API layer for reusability and testing.
"""

from neo4j import GraphDatabase
from pjs_neo_rag.config import settings
from pjs_neo_rag.embeddings import embed_vector


# ---- database connection ----
driver = GraphDatabase.driver(
    settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
)


# ---- core search logic ----
def dual_vector_search(query: str, k: int = 8):
    """
    Perform dual vector search (text + latex embeddings) and merge results.

    Args:
        query: Search query string
        k: Number of results to return (max 20)

    Returns:
        List of result dicts with chunk_id, text, latex, page_start, page_end, score
    """
    v_text = embed_vector(query)
    v_latex = embed_vector(query)

    # Query text embeddings
    cypher_text = """
    CALL db.index.vector.queryNodes('chunk_vec_text', 40, $v_text)
      YIELD node AS n, score
    RETURN n.chunk_id AS chunk_id,
           n.text_norm AS text,
           n.latex_raw AS latex,
           n.page_start AS page_start,
           n.page_end AS page_end,
           score
    """

    # Query latex embeddings
    cypher_latex = """
    CALL db.index.vector.queryNodes('chunk_vec_latex', 40, $v_latex)
      YIELD node AS n, score
    RETURN n.chunk_id AS chunk_id,
           n.text_norm AS text,
           n.latex_raw AS latex,
           n.page_start AS page_start,
           n.page_end AS page_end,
           score
    """

    with driver.session(database=settings.NEO4J_DATABASE) as s:
        text_results = s.run(cypher_text, v_text=v_text).data()
        latex_results = s.run(cypher_latex, v_latex=v_latex).data()

    # Merge and deduplicate by chunk_id, keeping highest score
    merged = {}
    for result in text_results + latex_results:
        chunk_id = result["chunk_id"]
        if chunk_id not in merged or result["score"] > merged[chunk_id]["score"]:
            merged[chunk_id] = result

    # Sort by score and limit
    rows = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    return rows[: max(1, min(k, 20))]
