"""
server.py — The MCP server for rag-mcp (personal knowledge base).

This is the entry point.  It wires together:
  - OllamaClient  (embeddings)
  - VectorStore   (ChromaDB)
  - ingestion     (file → chunks → embeddings)
  …and exposes everything to Claude via the MCP protocol.

MCP primitives used:
  Tools    — actions Claude can invoke (index, search, list, delete)
  Resource — URI-addressable data Claude can read (doc://<filename>)

Tools defined here:
  1. index_document     — ingest a file into the knowledge base
  2. search_docs        — semantic search across all indexed documents
  3. list_indexed_docs  — list every document currently in the index
  4. delete_document    — remove a document and all its chunks

Resource:
  doc://{filename}      — read all raw chunks for a specific document

Lifecycle:
  MCP servers using stdio transport are started by the host (Claude Desktop)
  as a subprocess.  The server reads JSON-RPC messages from stdin and writes
  responses to stdout.  We hook into the server's lifespan to open/close
  expensive resources (HTTP client, ChromaDB) exactly once.
"""

import os
import sys
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp import types as mcp_types

from rag_mcp.ollama_client import OllamaClient
from rag_mcp.vector_store import VectorStore
from rag_mcp.ingestion import ingest_file, SUPPORTED_EXTENSIONS

# --------------------------------------------------------------------------- #
# Configuration — loaded from .env (with sensible defaults)                   #
# --------------------------------------------------------------------------- #

# Load .env from the project root (two levels up from this file)
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path)

OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL",  "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
CHROMA_COLLECTION  = os.getenv("CHROMA_COLLECTION",  "rag_mcp_docs")
CHUNK_SIZE         = int(os.getenv("CHUNK_SIZE",    "1000"))
CHUNK_OVERLAP      = int(os.getenv("CHUNK_OVERLAP", "200"))
DOCUMENTS_DIR      = os.getenv("DOCUMENTS_DIR", "data/documents")


# --------------------------------------------------------------------------- #
# Shared state — holds open clients across tool calls                         #
# --------------------------------------------------------------------------- #

class AppState:
    """
    Container for the long-lived objects that every tool needs.

    We create this once at server startup and pass it to tools via
    FastMCP's lifespan / dependency injection pattern.
    """
    def __init__(self, ollama: OllamaClient, store: VectorStore):
        self.ollama = ollama
        self.store = store


# --------------------------------------------------------------------------- #
# Lifespan — open and close resources around the server's lifetime            #
# --------------------------------------------------------------------------- #

@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppState]:
    """
    Called once when the MCP server starts, yields, then cleans up on exit.

    This is the correct place to:
      - Open the HTTP client (OllamaClient)
      - Open the ChromaDB PersistentClient
      - Verify dependencies are reachable
      - Close everything gracefully on shutdown

    FastMCP passes the yielded value as `ctx.request_context.lifespan_context`
    which we access in each tool via `mcp.get_context()`.
    """
    ollama = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_EMBED_MODEL)
    store  = VectorStore(
        persist_dir=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION,
    )

    # Warn (don't crash) if Ollama isn't reachable — the server can still
    # serve list/delete operations even without embeddings.
    if not await ollama.health_check():
        print(
            f"[rag-mcp] WARNING: Ollama not reachable at {OLLAMA_BASE_URL}. "
            "index_document and search_docs will fail until Ollama is running.",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(f"[rag-mcp] Ollama OK ({OLLAMA_EMBED_MODEL})", file=sys.stderr, flush=True)

    print(
        f"[rag-mcp] ChromaDB ready — {store.count()} chunks in collection "
        f"'{CHROMA_COLLECTION}'",
        file=sys.stderr,
        flush=True,
    )

    state = AppState(ollama=ollama, store=store)

    try:
        yield state          # <-- server runs here, tools can use state
    finally:
        await ollama.close() # clean up the HTTP connection pool on shutdown
        print("[rag-mcp] Shutdown complete.", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# MCP server instance                                                          #
# --------------------------------------------------------------------------- #

mcp = FastMCP(
    name="rag-assistant",
    # lifespan receives the FastMCP instance and must yield our AppState
    lifespan=lifespan,
)


# --------------------------------------------------------------------------- #
# Helper: get AppState from inside a tool                                     #
# --------------------------------------------------------------------------- #

def _state() -> AppState:
    """
    Retrieve the AppState that was yielded by the lifespan context manager.

    FastMCP stores the lifespan context on a context-var that's accessible
    via mcp.get_context().request_context.lifespan_context.
    """
    ctx = mcp.get_context()
    return ctx.request_context.lifespan_context


# --------------------------------------------------------------------------- #
# Tool 1 — index_document                                                     #
# --------------------------------------------------------------------------- #

@mcp.tool()
async def index_document(file_path: str) -> str:
    """
    Index a document into the knowledge base so it can be searched.

    Reads the file at `file_path`, splits it into overlapping chunks,
    embeds each chunk using nomic-embed-text via Ollama, and stores the
    vectors in ChromaDB.  Re-indexing the same file is safe — old chunks
    are replaced automatically.

    Args:
        file_path: Absolute path to the file to index.
                   Supported types: .pdf .md .txt .py .js .ts .json .yaml .yml

    Returns:
        A summary string describing what was indexed.
    """
    state = _state()

    try:
        result = await ingest_file(
            path=file_path,
            ollama=state.ollama,
            store=state.store,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
    except FileNotFoundError:
        return f"Error: file not found at '{file_path}'"
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error during ingestion: {type(e).__name__}: {e}"

    if result["status"] == "success":
        return (
            f"Successfully indexed '{result['source']}'\n"
            f"  File type:  {result['file_type']}\n"
            f"  Pages read: {result['pages_read']}\n"
            f"  Chunks created: {result['chunks_created']}"
        )
    else:
        return f"Skipped '{result['source']}': {result['status']}"


# --------------------------------------------------------------------------- #
# Tool 2 — search_docs                                                        #
# --------------------------------------------------------------------------- #

@mcp.tool()
async def search_docs(
    query: str,
    n_results: int = 5,
    source_filter: str = "",
) -> str:
    """
    Semantically search the knowledge base for content related to `query`.

    The query is embedded using the same model used during indexing.
    ChromaDB finds the N most similar chunks using cosine similarity.
    Lower distance = more relevant.

    Args:
        query:         Natural-language question or keyword phrase.
        n_results:     How many results to return (default 5, max 20).
        source_filter: If non-empty, restrict search to chunks from this
                       specific document (exact filename, e.g. "notes.md").

    Returns:
        Formatted string with matching chunks, their sources, and distances.
        Returns a helpful message if the knowledge base is empty.
    """
    state = _state()

    if state.store.count() == 0:
        return (
            "The knowledge base is empty. "
            "Use index_document to add some files first."
        )

    n_results = max(1, min(n_results, 20))  # clamp to [1, 20]

    try:
        query_vector = await state.ollama.get_embedding(query)
    except Exception as e:
        return f"Error getting embedding from Ollama: {e}"

    results = await state.store.search(
        query_embedding=query_vector,
        n_results=n_results,
        source_filter=source_filter if source_filter else None,
    )

    if not results:
        msg = f"No results found for: '{query}'"
        if source_filter:
            msg += f" (filtered to '{source_filter}')"
        return msg

    # Format the results as a readable string for Claude to process
    lines = [f"Found {len(results)} result(s) for: '{query}'\n"]
    for i, r in enumerate(results, start=1):
        lines.append(
            f"--- Result {i} ---\n"
            f"Source:   {r['source']}  (page {r['page_number']}, "
            f"chunk {r['chunk_index']})\n"
            f"Distance: {r['distance']}  (lower = more relevant)\n"
            f"Text:\n{r['text']}\n"
        )

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Tool 3 — list_indexed_docs                                                  #
# --------------------------------------------------------------------------- #

@mcp.tool()
async def list_indexed_docs() -> str:
    """
    List all documents currently indexed in the knowledge base.

    Returns one entry per document with its filename, file type,
    number of chunks, and when it was last indexed.

    Returns:
        Formatted string listing all documents, or a message if empty.
    """
    state = _state()
    docs = await state.store.list_documents()

    if not docs:
        return (
            "No documents indexed yet. "
            "Use index_document(file_path=...) to add your first document."
        )

    lines = [f"Knowledge base contains {len(docs)} document(s):\n"]
    for doc in docs:
        lines.append(
            f"  {doc['source']}\n"
            f"    Type:       {doc['file_type']}\n"
            f"    Chunks:     {doc['chunk_count']}\n"
            f"    Indexed at: {doc['ingested_at']}\n"
        )

    total_chunks = sum(d["chunk_count"] for d in docs)
    lines.append(f"Total chunks: {total_chunks}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Tool 4 — delete_document                                                    #
# --------------------------------------------------------------------------- #

@mcp.tool()
async def delete_document(source: str) -> str:
    """
    Remove a document and all its chunks from the knowledge base.

    This is useful when a document has been updated (you'll delete then
    re-index it) or when you no longer need it to be searchable.

    Args:
        source: The filename of the document to remove, e.g. "design_doc.pdf".
                Use list_indexed_docs to see valid filenames.

    Returns:
        Confirmation message with the number of chunks deleted.
    """
    state = _state()

    try:
        count = await state.store.delete_document(source)
    except Exception as e:
        return f"Error deleting '{source}': {e}"

    if count == 0:
        return f"No document named '{source}' found in the knowledge base."
    return f"Deleted '{source}' ({count} chunk(s) removed from the index)."


# --------------------------------------------------------------------------- #
# Resource — doc://{filename}                                                  #
# --------------------------------------------------------------------------- #

@mcp.resource("doc://{filename}")
async def get_document_resource(filename: str) -> str:
    """
    Read all indexed chunks for a specific document as a structured resource.

    MCP Resources are URI-addressable data blobs — different from tools in
    that they're meant for reading structured content, not performing actions.

    URI format:  doc://design_doc.pdf
                 doc://README.md
                 doc://notes.txt

    Args:
        filename: The document's filename (from list_indexed_docs).

    Returns:
        JSON string with all chunks for the document, sorted by chunk_index.
        Returns a JSON error object if the document isn't indexed.
    """
    state = _state()
    chunks = await state.store.get_document_chunks(filename)

    if not chunks:
        return json.dumps({
            "error": f"No document named '{filename}' in the knowledge base.",
            "hint": "Use list_indexed_docs to see available documents.",
        }, indent=2)

    return json.dumps({
        "source": filename,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }, indent=2)


# --------------------------------------------------------------------------- #
# Entry point                                                                  #
# --------------------------------------------------------------------------- #

def main() -> None:
    """
    Start the MCP server.

    FastMCP uses stdio transport by default — reads JSON-RPC from stdin,
    writes to stdout.  This is exactly what Claude Desktop expects when it
    launches the server as a subprocess.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
