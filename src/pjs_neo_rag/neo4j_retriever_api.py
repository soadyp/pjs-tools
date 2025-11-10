from fastapi import FastAPI
from pydantic import BaseModel
from pjs_neo_rag.neo_search import dual_vector_search

app = FastAPI(title="GraphRAG Retriever", version="0.1")


# ---- request/response ----
class SearchReq(BaseModel):
    query: str
    k: int = 8
    mathy: bool = False  # allow UI to hint "math-heavy"


class Passage(BaseModel):
    chunk_id: str
    text: str
    latex: str | None = ""
    page_start: int
    page_end: int
    score: float


@app.post(
    "/search",
    operation_id="graphrag_search",
    response_model=list[Passage],
    tags=["graphrag"],
    summary="Search Neo4j knowledge graph",
    description="Dual-vector search across text and LaTeX embeddings",
)
def graphrag_search(req: SearchReq):
    return dual_vector_search(req.query, req.k)
