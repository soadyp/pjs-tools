"""
Direct test of Neo4j Cypher queries for vector search.
Tests the search function directly without going through the HTTP API.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Now import after path is set
from pjs_neo_rag.neo_search import dual_vector_search  # noqa: E402


def test_vector_search():
    """Test dual_vector_search function directly"""

    print("\n" + "=" * 60)
    print("TESTING DUAL VECTOR SEARCH FUNCTION")
    print("=" * 60)

    test_queries = [
        "What is the Dirac equation?",
        "geometric algebra",
        "clifford algebra spinors",
    ]

    for test_query in test_queries:
        print(f"\n🔍 Query: '{test_query}'")
        print("-" * 60)

        try:
            results = dual_vector_search(test_query, k=5)

            print("✓ Search completed successfully")
            print(f"✓ Results: {len(results)} chunks")

            for i, row in enumerate(results, 1):
                print(
                    f"\n  [{i}] Score: {row['score']:.4f} | Page: {row['page_start']}"
                )
                text_preview = row["text"][:80] if row["text"] else ""
                print(f"      Text: {text_preview}...")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False

    print("\n" + "=" * 60)
    print("✓ ALL CYPHER TESTS PASSED")
    print("=" * 60 + "\n")

    return True


if __name__ == "__main__":
    success = test_vector_search()
    sys.exit(0 if success else 1)
