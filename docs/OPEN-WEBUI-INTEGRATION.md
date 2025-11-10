# Open-WebUI Integration Guide

## Current Status
✅ Neo4j database running with vector indexes
✅ PDF ingested (dirac_ga.pdf - 7 pages, 7 chunks)
✅ FastAPI server working at http://localhost:8000/search
✅ All tests passing (3/3)

## Integration Steps

### 1. Start the API Server
```bash
cd /home/pjs/Documents/_dev/pjs-neo-rag
source .venv/bin/activate
python app.py
```
Server runs on: http://127.0.0.1:8000

### 2. Add HTTP Tool in Open-WebUI

Navigate to: **Settings → Tools → HTTP → Add Tool**

**Configuration:**
- **Name:** `graphrag.search`
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/search`
- **Headers/Auth:** (leave empty)

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": { 
      "type": "string",
      "description": "Search query for scientific documents"
    },
    "k": { 
      "type": "integer", 
      "default": 8, 
      "minimum": 1, 
      "maximum": 20,
      "description": "Number of results to return"
    },
    "mathy": { 
      "type": "boolean", 
      "default": false,
      "description": "Hint that query is math-heavy"
    }
  },
  "required": ["query"]
}
```

**Response Type:** `JSON`

Click **Save**

### 3. Model Settings

Navigate to: **Settings → Models**

- **Model:** `mistral:7b-instruct` (or your Ollama model)
- **Function/Tool Calling:** `ON (Native)` ⚠️ **CRITICAL**
- **Temperature:** `0.2–0.4` (optional, for focused answers)
- **Max Tokens:** `1024` (optional)

### 4. System Prompt (Recommended)

Navigate to: **Model Settings → System Prompt**

```
You are a local physics research assistant with access to scientific documents.

When the user asks about physics concepts, the Dirac equation, geometric algebra, 
or related topics, call the tool "graphrag.search" with a focused query.

Use ONLY the returned passages to answer. Do not invent facts.
Always cite the page numbers from the tool results in your answer.

Citation format: [p.2], [p.7], etc.
```

### 5. Test Queries

Open a new chat and try these:

**Query 1:**
```
Find passages about the Dirac equation and cite the pages.
```

**Query 2:**
```
What does the document say about geometric algebra? Include page references.
```

**Query 3:**
```
Explain how Clifford algebra relates to the content. Cite sources.
```

**Expected Behavior:**
1. Model calls `graphrag.search` tool with `{"query": "...", "k": 8}`
2. Tool returns JSON with scored passages
3. Model synthesizes answer with citations like [p.2], [p.7]

### 6. Troubleshooting

#### No tool call made
- ✅ Check: Function/Tool Calling = **ON (Native)**
- ✅ Check: Model has `-instruct` tag (e.g., `mistral:7b-instruct`)
- ✅ Try: Restart Open-WebUI after adding the tool

#### HTTP 500 errors
- ✅ Check: API server is running (`python app.py`)
- ✅ Check: Terminal shows uvicorn logs
- ✅ Check: Neo4j is running
- ✅ Run: `python tests/test_search.py` to verify API

#### Empty results returned
- ✅ Verify: PDFs are ingested
  ```bash
  python src/pjs_neo_rag/ingest_pdf.py path/to/your.pdf
  ```
- ✅ Check: Vector indexes exist in Neo4j
  ```bash
  python src/pjs_neo_rag/create_neo_indexes.py
  ```

#### Tool not appearing in chat
- ✅ Refresh Open-WebUI page
- ✅ Check tool is enabled in workspace settings
- ✅ Verify tool name is exactly `graphrag.search`

### 7. Enhanced Prompting Tips

To get better citations, add to your query:

```
When you answer, list bullet citations using page numbers from the tool results.
Format: [p.2], [p.7]. Include the score if confidence varies.
```

### 8. Testing the Complete Flow

**Before Open-WebUI integration:**
```bash
# Terminal 1: Start API
cd /home/pjs/Documents/_dev/pjs-neo-rag
source .venv/bin/activate
python app.py

# Terminal 2: Test API
source .venv/bin/activate
python tests/test_search.py
```

**After Open-WebUI integration:**
1. Open browser to http://localhost:8080 (Open-WebUI)
2. Start new chat with mistral:7b-instruct
3. Ask: "What does the document say about the Dirac equation?"
4. Watch tool call in action!

## Architecture Summary

```
User Question (Open-WebUI)
    ↓
Mistral LLM (Ollama) decides to call tool
    ↓
graphrag.search tool (HTTP POST)
    ↓
FastAPI /search endpoint
    ↓
dual_vector_search() function
    ↓
Neo4j (text + latex vectors)
    ↓
Scored passages returned
    ↓
Mistral synthesizes answer with citations
    ↓
User sees answer with [p.X] references
```

## Key Files

- **API Server:** `app.py` → `neo4j_retriever_api.py`
- **Search Logic:** `neo_search.py`
- **Embeddings:** `ollama.py`
- **Config:** `config.py` (uses .env)
- **Tests:** `tests/test_search.py` (API), `tests/test_cypher_direct.py` (direct)

## Next Steps

1. ✅ Complete Open-WebUI tool setup (Steps 2-4 above)
2. Test with sample queries (Step 5)
3. Ingest more PDFs from `SOURCE_DIR`
4. Adjust system prompt based on results
5. Tune temperature/k values for your use case

---

**System is fully functional and ready for integration! 🚀**
