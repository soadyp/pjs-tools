## Start open webui
http://localhost:8080/      <<<<===== Browser connection once installed


## but first Install open webui


pull  ghcr.io/open-webui/open-webui:main

run as container inside podman
podman run -d --network=host --name open-webui -v open-webui-data:/app/backend/data ghcr.io/open-webui/open-webui:main

logon to OPEN WEBUI  


use admin panel  tool to connect to ollama !
goto settings connections to add 
http://host.docker.internal:11434

note this will ONLY work if you started the container with access to localhost
see --network=host  option above !


 ## System Prompt for LateX 
 you need to add this system prompt to force LaTeX output

**CRITICAL INSTRUCTION:** You MUST render all mathematical content using LaTeX.

- Use `$...$` for inline math.
    
- Use `$$...$$` for block equations.
    
- You MUST NOT use markdown backticks (`` `...` ``) to render math.


## Register Custom Tool in OpenWebUI for retrieving pdfs from Neo4j RAG
Model: mistral:instruct (example) 
Function/Tool Calling: ON (Native).
Add HTTP Tool:
Name: graphrag.search
Method: POST
URL: http://127.0.0.1:8000/graphrag/search          (api_port is defined in .env)

Input schema:
{
  "type": "object",
  "properties": {
    "query": { "type": "string" },
    "k":     { "type": "integer", "default": 8, "minimum": 1, "maximum": 20 },
    "mathy": { "type": "boolean", "default": false }
  },
  "required": ["query"]
}




