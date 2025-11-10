"""Common Neo4j connection utilities."""

from neo4j import GraphDatabase
from pjs_neo_rag.config import settings

URI = settings.NEO4J_URI
USR = settings.NEO4J_USERNAME
PWD = settings.NEO4J_PASSWORD
DB = settings.NEO4J_DATABASE


def get_driver():
    """Create and return a Neo4j driver instance."""
    if not PWD:
        raise ValueError("NEO4J_PASSWORD environment variable is not set")
    return GraphDatabase.driver(URI, auth=(USR, PWD))


def get_session(driver=None, database=None):
    """Create and return a Neo4j session.

    Args:
        driver: Optional driver instance. If None, creates a new one.
        database: Optional database name. Defaults to NEO4J_DATABASE env var.
    """
    if driver is None:
        driver = get_driver()
    db = database or DB
    return driver.session(database=db)
