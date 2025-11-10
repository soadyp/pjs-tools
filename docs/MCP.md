Connect to local neo4j DB

{
       "mcpServers": {
         "neo4j-mcp": {
	           "type": "stdio",
	           "command": "neo4j-mcp",
	           "args": [],
	           "env": {
	             "NEO4J_URI": "bolt://localhost:7687",
	             "NEO4J_USERNAME": "neo4j",
	             "NEO4J_PASSWORD": "pjsneo!!",
	             "NEO4J_DATABASE": "neo4j",
	             "NEO4J_READ_ONLY": "false"
	           }
	       }
       }
}


