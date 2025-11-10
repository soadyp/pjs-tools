"""Test the search endpoint directly."""

import requests

# Test configuration
API_URL = "http://localhost:8000/search"
TEST_QUERIES = [
    {"query": "Dirac equation", "k": 5, "mathy": True},
    {"query": "What is geometric algebra?", "k": 3, "mathy": False},
    {"query": "clifford algebra", "k": 5, "mathy": True},
]


def test_search(query: str, k: int = 8, mathy: bool = False):
    """Test a single search query."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"k={k}, mathy={mathy}")
    print(f"{'='*60}")

    try:
        response = requests.post(
            API_URL, json={"query": query, "k": k, "mathy": mathy}, timeout=30
        )
        response.raise_for_status()
        results = response.json()

        print(f"\n✅ Found {len(results)} results")

        for i, result in enumerate(results, 1):
            print(f"\n[Result {i}]")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  Page: {result.get('page_start', 'N/A')}")
            print(f"  Text: {result.get('text', '')[:150]}...")
            if result.get("latex"):
                print(f"  LaTeX: {result.get('latex', '')[:100]}...")
            print(f"  Chunk ID: {result.get('chunk_id', 'N/A')}")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is the server running?")
        print("   Start with: python app.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False


def main():
    print("Testing Neo4j RAG Search API")
    print(f"API URL: {API_URL}\n")

    success_count = 0
    for test in TEST_QUERIES:
        if test_search(**test):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Results: {success_count}/{len(TEST_QUERIES)} tests passed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
