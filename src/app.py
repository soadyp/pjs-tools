"""Launch the FastAPI retriever server."""

import uvicorn
from pjs_neo_rag.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting server on port {settings.API_PORT}")
    uvicorn.run(
        "pjs_neo_rag.neo4j_retriever_api:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=False,
    )
