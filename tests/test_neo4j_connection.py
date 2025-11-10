"""Test Neo4j connection and credentials."""

import sys
from pjs_neo_rag.neo4j_connection import get_driver, URI, USR, PWD, DB


def test_connection():
    """Test the Neo4j connection with current credentials."""
    print("🔍 Testing Neo4j Connection...")
    print(f"   URI: {URI}")
    print(f"   Username: {USR}")
    print(f"   Password length: {len(PWD) if PWD else 0}")
    print(f"   Password repr: {repr(PWD)}")  # Show actual password for debugging
    print(f"   Database: {DB}")
    print()

    if not PWD:
        print("❌ ERROR: NEO4J_PASSWORD is not set in .env file")
        return False

    try:
        driver = get_driver()
        print("✅ Driver created successfully")

        # Test connection with a simple query
        with driver.session(database=DB) as session:
            result = session.run("RETURN 1 AS test")
            value = result.single()["test"]
            print(f"✅ Connection successful! Test query returned: {value}")

        # Get Neo4j version
        with driver.session(database=DB) as session:
            result = session.run(
                "CALL dbms.components() YIELD name, versions RETURN name, versions[0] AS version"
            )
            record = result.single()
            print(f"✅ Neo4j version: {record['version']}")

        driver.close()
        print("\n✅ All connection tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Connection failed: {type(e).__name__}")
        print(f"   {str(e)}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
