"""
vector_store.py — ChromaDB wrapper for storing and searching document chunks.

What is ChromaDB?
  ChromaDB is an open-source, embedded vector database.  "Embedded" means
  it runs *inside our process* — no separate server to spin up.
  "Vector database" means it stores vectors (lists of floats) and can
  answer the question: "give me the N vectors most similar to this query
  vector" extremely efficiently using approximate nearest-neighbour search.

Key concepts used here:

1. PersistentClient
   Instead of keeping everything in RAM (EphemeralClient), we use
   PersistentClient which writes the database to a directory on disk.
   This means indexed documents survive restarts — we don't have to
   re-index every time we start the MCP server.

2. Collection
   A collection is like a table — it holds vectors + metadata + raw text.
   We use a single collection ("rag_mcp_docs") for all documents.
   Each entry in the collection has:
     - id:        unique string (we use "source__chunk_index")
     - embedding: the 768-float vector
     - document:  the raw chunk text (ChromaDB stores this alongside the vector)
     - metadata:  dict of extra fields (source, page_number, file_type, …)

3. Similarity search (query)
   We embed the user's question → get its vector → ask ChromaDB for the
   N collection entries whose vectors are closest to it.
   "Closest" = smallest cosine distance = most semantically similar text.
   ChromaDB returns the matching documents + their metadata + distances.

4. Why distances matter
   A distance of 0.0 = identical meaning. A distance > 1.5 often means
   poor relevance.  We include distance in search results so the server
   can surface how confident each match is.
"""

from typing import Any, cast

import chromadb
from chromadb.config import Settings

from rag_mcp.ingestion import EmbeddedChunk


class VectorStore:
    """
    Thin wrapper around a ChromaDB PersistentClient + collection.

    Responsibilities:
      - Open / create the ChromaDB collection on startup
      - Add embedded chunks (with deduplication by source)
      - Run similarity searches
      - List all indexed documents
      - Delete all chunks for a given document
    """

    def __init__(self, persist_dir: str, collection_name: str):
        """
        Args:
            persist_dir:     Path to the directory where ChromaDB stores
                             its SQLite + HNSW index files, e.g. ".chroma"
            collection_name: Name of the collection to use/create,
                             e.g. "rag_mcp_docs"
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        # PersistentClient: data lives on disk, survives process restarts.
        # anonymized_telemetry=False: opt out of ChromaDB's usage analytics.
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )

        # get_or_create_collection: safe to call on every startup.
        # If the collection already exists, we get a handle to it.
        # If not, it's created fresh.
        #
        # embedding_function=None: we pass pre-computed embeddings ourselves
        # (from Ollama) rather than letting ChromaDB call an embedding model.
        # This is important — we must use the *same* model for indexing and
        # querying, and we want full control over that.
        # Store as Any to avoid Pylance fighting ChromaDB's incorrect stubs.
        # The stubs type embeddings/metadatas too narrowly; the actual runtime
        # API accepts list[list[float]] and list[dict] just fine.
        self._collection: Any = self._client.get_or_create_collection(
            name=collection_name,
            # cosine distance is standard for text similarity tasks
            metadata={"hnsw:space": "cosine"},
            embedding_function=None,   # we supply embeddings manually
        )

    # ---------------------------------------------------------------------- #
    # Write operations                                                        #
    # ---------------------------------------------------------------------- #

    async def add_chunks(self, embedded_chunks: list[EmbeddedChunk]) -> None:
        """
        Add a batch of embedded chunks to the collection.

        ChromaDB's add() is synchronous under the hood, but we mark this
        method async so callers (which are already in an async context) can
        call it uniformly with `await`.

        ID scheme: "<source>__<chunk_index>"
        Example:   "design_doc.pdf__0", "design_doc.pdf__1", …

        This makes IDs deterministic per file, so if we ever accidentally
        call add_chunks twice for the same file the second call will raise
        a duplicate-ID error (which is better than silent duplication).
        Use delete_document() before re-indexing to avoid this.
        """
        if not embedded_chunks:
            return

        ids: list[str] = []
        embeddings: list[list[float]] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for ec in embedded_chunks:
            chunk = ec.chunk

            # Unique ID for this chunk
            chunk_id = f"{chunk.source}__{chunk.chunk_index}"

            ids.append(chunk_id)
            embeddings.append(ec.embedding)
            documents.append(chunk.text)   # raw text stored alongside vector
            metadatas.append({
                "source":      chunk.source,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "file_type":   chunk.file_type,
                "ingested_at": chunk.ingested_at,
            })

        # upsert: insert new, overwrite existing with same ID
        # This is safer than add() because it won't error on duplicates.
        # We cast to Any to sidestep ChromaDB's incorrect stubs which don't
        # accept list[list[float]] even though that's exactly what works at runtime.
        _embeddings: Any = embeddings
        _metadatas: Any = metadatas
        self._collection.upsert(
            ids=ids,
            embeddings=_embeddings,
            documents=documents,
            metadatas=_metadatas,
        )

    async def delete_document(self, source: str) -> int:
        """
        Delete all chunks that came from `source` (the filename).

        Called before re-indexing a file to ensure we don't accumulate
        stale chunks from previous versions of the document.

        Args:
            source: The filename, e.g. "design_doc.pdf"

        Returns:
            Number of chunks deleted (0 if document wasn't indexed yet).
        """
        # First count how many chunks exist for this source.
        existing = self._collection.get(
            where={"source": source},
            include=[],  # we only need ids, not embeddings/documents
        )
        count = len(existing["ids"])

        if count > 0:
            self._collection.delete(where={"source": source})

        return count

    # ---------------------------------------------------------------------- #
    # Read operations                                                         #
    # ---------------------------------------------------------------------- #

    async def search(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        source_filter: str | None = None,
    ) -> list[dict]:
        """
        Find the `n_results` chunks most similar to `query_embedding`.

        Args:
            query_embedding: The embedding vector of the user's question.
            n_results:       How many results to return (default 5).
            source_filter:   If set, restrict results to chunks from this
                             document only (useful for targeted Q&A).

        Returns:
            List of result dicts, each containing:
            {
                "id":          str,    # chunk ID
                "text":        str,    # the chunk's raw text
                "source":      str,    # filename
                "page_number": int,
                "file_type":   str,
                "chunk_index": int,
                "ingested_at": str,
                "distance":    float,  # 0.0 = identical, higher = less similar
            }
            Sorted by distance ascending (best match first).
        """
        # Build the optional WHERE clause
        where = {"source": source_filter} if source_filter else None

        # Guard: ChromaDB raises if n_results > total items in collection
        total = self._collection.count()
        if total == 0:
            return []
        n_results = min(n_results, total)

        query_kwargs: dict = dict(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        if where:
            query_kwargs["where"] = where

        results: Any = self._collection.query(**query_kwargs)

        # ChromaDB returns parallel lists wrapped in an outer list (one entry
        # per query embedding — we always send exactly one).
        # The stubs type these fields as Optional but they're always present
        # when we include them explicitly — cast to silence the type checker.
        ids        = cast(list, results["ids"])[0]
        documents  = cast(list, results["documents"])[0]
        metadatas  = cast(list, results["metadatas"])[0]
        distances  = cast(list, results["distances"])[0]

        output = []
        for cid, doc, meta, dist in zip(ids, documents, metadatas, distances):
            output.append({
                "id":          cid,
                "text":        doc,
                "source":      meta.get("source", ""),
                "page_number": meta.get("page_number", 1),
                "file_type":   meta.get("file_type", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "ingested_at": meta.get("ingested_at", ""),
                "distance":    round(dist, 4),
            })

        return output

    async def list_documents(self) -> list[dict]:
        """
        Return a summary of all indexed documents.

        We fetch all chunk metadata and group by `source` to produce one
        summary entry per document.

        Returns:
            List of dicts, one per document:
            {
                "source":      str,  # filename
                "file_type":   str,
                "chunk_count": int,
                "ingested_at": str,  # timestamp of the *first* chunk indexed
            }
            Sorted alphabetically by source.
        """
        if self._collection.count() == 0:
            return []

        # Fetch all metadata (no embeddings/documents needed — keep it lean)
        # Use Any to escape ChromaDB's incorrect Optional stubs.
        all_meta: Any = self._collection.get(include=["metadatas"])
        metadatas: list[dict[str, Any]] = all_meta["metadatas"] or []

        # Group by source
        docs: dict[str, dict] = {}
        for meta in metadatas:
            src: str = str(meta.get("source", "unknown"))
            if src not in docs:
                docs[src] = {
                    "source":      src,
                    "file_type":   str(meta.get("file_type", "")),
                    "chunk_count": 0,
                    "ingested_at": str(meta.get("ingested_at", "")),
                }
            docs[src]["chunk_count"] += 1

        return sorted(docs.values(), key=lambda d: d["source"])

    async def get_document_chunks(self, source: str) -> list[dict]:
        """
        Retrieve all chunks for a specific document (used by the Resource).

        Args:
            source: The filename, e.g. "design_doc.pdf"

        Returns:
            List of chunk dicts sorted by chunk_index:
            {
                "chunk_index": int,
                "page_number": int,
                "text":        str,
                "ingested_at": str,
            }
        """
        result: Any = self._collection.get(
            where={"source": source},
            include=["documents", "metadatas"],
        )

        chunks = []
        for doc, meta in zip(result["documents"], result["metadatas"]):
            m: dict[str, Any] = meta
            chunks.append({
                "chunk_index": m.get("chunk_index", 0),
                "page_number": m.get("page_number", 1),
                "text":        doc,
                "ingested_at": m.get("ingested_at", ""),
            })

        return sorted(chunks, key=lambda c: c["chunk_index"])

    def count(self) -> int:
        """Return total number of chunks in the collection."""
        return self._collection.count()
