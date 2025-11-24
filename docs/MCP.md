# Model Context Protocol (MCP) Configuration

This configuration allows AI assistants (like Claude Desktop or other MCP clients) to connect directly to your local Neo4j database.

## Configuration File

Add the following configuration to your MCP client settings file:
- **Claude Desktop:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
- **Other Clients:** Refer to your client's documentation for MCP server configuration.

```json
{
       "mcpServers": {
         "neo4j-mcp": {
	           "type": "stdio",
	           "command": "neo4j-mcp",
	           "args": [],
	           "env": {
	             "NEO4J_URI": "bolt://localhost:7687",
	             "NEO4J_USERNAME": "neo4j",
	             "NEO4J_PASSWORD": "xxxxx",  // Replace with your Neo4j password
	             "NEO4J_DATABASE": "neo4j",
	             "NEO4J_READ_ONLY": "false"
	           }
	       }
       }
}


