# rag-mcp

A personal knowledge base MCP server for Claude Desktop.

Drop in files (PDF, Markdown, plain text, code), and ask Claude questions that span your entire document collection. Powered by local embeddings via [Ollama](https://ollama.com) and [ChromaDB](https://www.trychroma.com/) for persistent vector storage.

## Features

- **Index any document** — PDF, `.md`, `.txt`, `.py`, `.js`, `.ts`, `.json`, `.yaml`
- **Semantic search** — finds relevant content by meaning, not just keywords
- **Local & private** — all embeddings generated locally via Ollama (no data leaves your machine)
- **Persistent** — ChromaDB persists to disk; re-index only when documents change
- **Re-index safe** — indexing the same file twice replaces old chunks cleanly

## Tools exposed to Claude

| Tool | Description |
|------|-------------|
| `index_document` | Index a file into the knowledge base |
| `search_docs` | Semantic search across all indexed documents |
| `list_indexed_docs` | List every document currently in the index |
| `delete_document` | Remove a document and all its chunks |

**Resource:** `doc://{filename}` — read all raw chunks for a specific document

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com) running locally with `nomic-embed-text` pulled:
  ```bash
  ollama pull nomic-embed-text
  ```

## Setup

```bash
git clone https://github.com/Kamalesh-Kavin/rag-mcp
cd rag-mcp
cp .env.example .env
uv sync
```

## Claude Desktop configuration

Add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-assistant": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/rag-mcp",
        "run",
        "rag-mcp"
      ]
    }
  }
}
```

## Usage in Claude

```
Index a document:
  "Index the file /Users/me/notes/architecture.md"

Ask a question:
  "What does my architecture doc say about the database layer?"

List what's indexed:
  "What documents are in my knowledge base?"

Delete a document:
  "Remove architecture.md from the knowledge base"
```

## Architecture

```
File on disk
    │
    ▼
read_file()          ← pypdf (PDF) or open() (text/code)
    │
    ▼
chunk_pages()        ← sliding window: 1000 chars, 200 overlap
    │
    ▼
embed_chunks()       ← POST http://localhost:11434/api/embeddings
    │                   nomic-embed-text → 768-dim vector
    ▼
VectorStore.add()    ← ChromaDB PersistentClient, cosine similarity
    │
    ▼
search_docs()        ← embed query → cosine nearest-neighbour lookup
```

## Project structure

```
src/rag_mcp/
├── __init__.py
├── ollama_client.py   # async httpx wrapper for Ollama embeddings API
├── ingestion.py       # file readers, chunker, ingest pipeline
├── vector_store.py    # ChromaDB wrapper (add, search, list, delete)
└── server.py          # MCP server — 4 tools + 1 resource
data/documents/        # drop files here to index them
```

## License

MIT
