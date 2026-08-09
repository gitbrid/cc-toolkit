# RAG MCP Server

MCP Server that gives Claude Code semantic search over your PDFs, code, and documents. Index once, query instantly — with exact citations and zero hallucinations.

## Setup

### 1. Install

```bash
git clone https://github.com/Rubrum95/rag-mcp-server
cd rag-mcp-server
pip install .
```

For OCR support (scanned PDFs):
```bash
pip install ".[ocr]"

# macOS
brew install tesseract

# Windows — download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Linux
sudo apt install tesseract-ocr tesseract-ocr-spa
```

### 2. Connect to Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "rag": {
      "command": "rag-mcp-server"
    }
  }
}
```

## Usage

### Index a project
```
Ask Claude: "Index ~/projects/my-research"
→ Calls rag_index, processes all PDFs and code files
```

### Query documents
```
Ask Claude: "What does the paper say about ocean warming?"
→ Calls rag_query, returns exact text with page citations
```

### Update with new files
```
Ask Claude: "Update the my-research index"
→ Calls rag_update, only processes new/changed files
```

### List indexed projects
```
Ask Claude: "List my indexed projects"
→ Shows all projects with file/chunk counts
```

## Configuration

Copy `config.yaml` to `~/.rag-mcp-server/config.yaml` to customize:

- `embedding_model` — default: multilingual model (Spanish + English)
- `chunk_size` / `chunk_overlap` — text splitting parameters
- `top_k` — default number of search results
- `ocr_languages` — Tesseract languages for scanned PDFs
- `supported_extensions` — file types to index

## How It Works

```
Your files → Text extraction → Chunking → Embeddings → ChromaDB
                (+ OCR if needed)

Your question → Embedding → Cosine similarity search → Top chunks
                                                          ↓
                                            Claude reads exact text
                                            and responds with citations
```

## Requirements

- Python 3.10+
- ~500MB disk for embedding model (downloaded once)
- Tesseract (optional, for scanned PDFs)
