"""pjs-neo-rag: Graph RAG on Neo4j with LaTeX support."""

from pjs_neo_rag.config import settings
from pjs_neo_rag.neo4j_connection import get_driver, get_session
from pjs_neo_rag.ingest_pdf import ingest_pdf

__all__ = ["settings", "get_driver", "get_session", "ingest_pdf"]


def main() -> None:
    print("Hello from pjs-neo-rag!")
