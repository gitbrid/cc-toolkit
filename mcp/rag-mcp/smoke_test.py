"""
smoke_test.py — End-to-end test of the rag-mcp pipeline (no MCP server needed).

Run with:
    uv run python smoke_test.py

Tests:
  1. Ollama health check
  2. Get an embedding from nomic-embed-text
  3. Ingest the test document
  4. Search for relevant chunks
  5. List indexed documents
  6. Delete the document
  7. Confirm deletion
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

OLLAMA_BASE_URL    = os.getenv("OLLAMA_BASE_URL",    "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", ".chroma_smoke_test")
CHROMA_COLLECTION  = "smoke_test_collection"

TEST_DOC = Path(__file__).parent / "data" / "documents" / "test_rag_overview.md"


async def main() -> None:
    from rag_mcp.ollama_client import OllamaClient
    from rag_mcp.vector_store import VectorStore
    from rag_mcp.ingestion import ingest_file

    print("=" * 60)
    print("rag-mcp smoke test")
    print("=" * 60)

    async with OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_EMBED_MODEL) as ollama:
        store = VectorStore(persist_dir=CHROMA_PERSIST_DIR, collection_name=CHROMA_COLLECTION)

        # 1. Health check
        print("\n[1] Ollama health check...")
        ok = await ollama.health_check()
        assert ok, "FAIL: Ollama not reachable. Is `ollama serve` running?"
        print("    PASS: Ollama is reachable")

        # 2. Embedding
        print("\n[2] Get embedding for sample text...")
        vec = await ollama.get_embedding("What is retrieval augmented generation?")
        assert isinstance(vec, list) and len(vec) == 768, f"FAIL: Expected 768 floats, got {len(vec)}"
        print(f"    PASS: Got embedding vector of length {len(vec)}")

        # 3. Ingest document
        print(f"\n[3] Ingesting: {TEST_DOC.name}...")
        result = await ingest_file(TEST_DOC, ollama, store, chunk_size=1000, chunk_overlap=200)
        assert result["status"] == "success", f"FAIL: {result}"
        print(f"    PASS: {result['chunks_created']} chunks created from {result['pages_read']} page(s)")

        # 4. Search
        print("\n[4] Searching: 'how does vector search work with cosine similarity'...")
        query_vec = await ollama.get_embedding("how does vector search work with cosine similarity")
        results = await store.search(query_vec, n_results=3)
        assert len(results) > 0, "FAIL: No search results returned"
        print(f"    PASS: {len(results)} result(s) returned")
        for i, r in enumerate(results, 1):
            print(f"    [{i}] distance={r['distance']}  chunk={r['chunk_index']}  page={r['page_number']}")
            print(f"        {r['text'][:120].strip()}...")

        # 5. List documents
        print("\n[5] Listing indexed documents...")
        docs = await store.list_documents()
        assert len(docs) == 1, f"FAIL: Expected 1 doc, got {len(docs)}"
        doc = docs[0]
        print(f"    PASS: '{doc['source']}' ({doc['chunk_count']} chunks, type={doc['file_type']})")

        # 6. Delete document
        print(f"\n[6] Deleting '{TEST_DOC.name}'...")
        deleted = await store.delete_document(TEST_DOC.name)
        assert deleted > 0, "FAIL: delete returned 0"
        print(f"    PASS: {deleted} chunk(s) deleted")

        # 7. Confirm deletion
        print("\n[7] Confirming deletion...")
        docs_after = await store.list_documents()
        assert len(docs_after) == 0, f"FAIL: Expected 0 docs, got {len(docs_after)}"
        print("    PASS: Knowledge base is empty again")

    # Clean up the test chroma directory
    import shutil
    shutil.rmtree(CHROMA_PERSIST_DIR, ignore_errors=True)
    print(f"\n    (Cleaned up test ChromaDB at {CHROMA_PERSIST_DIR})")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
