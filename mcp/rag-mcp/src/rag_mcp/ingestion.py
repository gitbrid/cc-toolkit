"""
ingestion.py — Turn raw files into embedded chunks ready for the vector store.

This module owns the full pipeline:
  File on disk  →  raw text  →  chunks  →  embedded chunks

Three concepts to understand here:

1. READING
   Different file types need different parsers:
   - PDF  → pypdf extracts text page by page
   - Everything else (md, txt, py, js, …) → plain open() read

2. CHUNKING (sliding window)
   We can't embed an entire document as one vector — the model has a
   token limit and, more importantly, a whole-document vector loses
   fine-grained meaning.  We split the text into overlapping windows:

       |<------- chunk_size ------->|
       |---- overlap ----|          |
                         |<------- chunk_size ------->|

   The overlap means a sentence that falls near a boundary appears in
   both adjacent chunks, so we never lose context at the seams.

3. METADATA
   Every chunk carries metadata so we can later:
   - Filter by source file
   - Show the user where the answer came from (page number, filename)
   - Delete all chunks belonging to a document when re-indexing

Data flow for a single file:
  read_file(path)        → list[PageContent]   (text per page/file)
  chunk_pages(pages)     → list[Chunk]         (small overlapping windows)
  embed_chunks(chunks)   → list[EmbeddedChunk] (chunk + vector)
  ingest_file(path, ...) → orchestrates all three + calls vector_store
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from pypdf import PdfReader

if TYPE_CHECKING:
    # Avoid circular imports — only used for type hints
    from rag_mcp.ollama_client import OllamaClient
    from rag_mcp.vector_store import VectorStore


# --------------------------------------------------------------------------- #
# Data classes — simple containers that make the pipeline easy to follow       #
# --------------------------------------------------------------------------- #

@dataclass
class PageContent:
    """Raw text from a single page (PDF) or the whole file (plain text)."""
    text: str
    page_number: int   # 1-indexed; for non-PDF files this is always 1


@dataclass
class Chunk:
    """
    A slice of a document's text, small enough to embed meaningfully.

    Fields:
        text        — the actual text window
        source      — filename (without path), e.g. "design_doc.md"
        chunk_index — sequential number within this file (0-based)
        page_number — which page this chunk came from (for PDFs)
        file_type   — extension without dot, e.g. "pdf", "md", "py"
        ingested_at — ISO-8601 timestamp so we know when this was indexed
    """
    text: str
    source: str
    chunk_index: int
    page_number: int
    file_type: str
    ingested_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class EmbeddedChunk:
    """A Chunk that has been paired with its embedding vector."""
    chunk: Chunk
    embedding: list[float]


# --------------------------------------------------------------------------- #
# Supported file types                                                         #
# --------------------------------------------------------------------------- #

SUPPORTED_EXTENSIONS = {
    ".pdf", ".md", ".txt",
    ".py", ".js", ".ts",
    ".json", ".yaml", ".yml",
}


# --------------------------------------------------------------------------- #
# Step 1 — Reading                                                             #
# --------------------------------------------------------------------------- #

def read_file(path: Path) -> list[PageContent]:
    """
    Read a file and return its text as a list of PageContent objects.

    For PDFs each page becomes its own PageContent so we can preserve
    page numbers in chunk metadata.  For all other supported types the
    whole file is one PageContent with page_number=1.

    Raises:
        ValueError: if the file extension is not supported.
        FileNotFoundError: if the file doesn't exist.
    """
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if suffix == ".pdf":
        return _read_pdf(path)
    else:
        return _read_text(path)


def _read_pdf(path: Path) -> list[PageContent]:
    """Extract text from each page of a PDF using pypdf."""
    reader = PdfReader(str(path))
    pages: list[PageContent] = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        # Skip blank pages — they add nothing to the index.
        if text.strip():
            pages.append(PageContent(text=text, page_number=page_num))

    return pages


def _read_text(path: Path) -> list[PageContent]:
    """Read any plain-text file as a single PageContent."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return [PageContent(text=text, page_number=1)]


# --------------------------------------------------------------------------- #
# Step 2 — Chunking                                                            #
# --------------------------------------------------------------------------- #

def chunk_pages(
    pages: list[PageContent],
    source: str,
    file_type: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Chunk]:
    """
    Convert a list of PageContent objects into overlapping Chunk objects.

    The sliding window algorithm:
      - Start at position 0
      - Take `chunk_size` characters as one chunk
      - Advance by `chunk_size - chunk_overlap` (so the next chunk
        re-reads the last `chunk_overlap` characters of the previous one)
      - Repeat until the end of the text

    Args:
        pages:          Output from read_file()
        source:         Filename to embed in each chunk's metadata
        file_type:      Extension (without dot) for metadata
        chunk_size:     Max characters per chunk
        chunk_overlap:  Characters of overlap between adjacent chunks

    Returns:
        List of Chunk objects, ready for embedding.
    """
    chunks: list[Chunk] = []
    chunk_index = 0  # global counter across all pages in this file
    now = datetime.now(timezone.utc).isoformat()

    for page in pages:
        text = page.text.strip()
        if not text:
            continue

        start = 0
        step = chunk_size - chunk_overlap  # how far to advance each iteration

        while start < len(text):
            end = start + chunk_size
            window = text[start:end].strip()

            if window:  # ignore whitespace-only windows
                chunks.append(Chunk(
                    text=window,
                    source=source,
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    file_type=file_type,
                    ingested_at=now,
                ))
                chunk_index += 1

            start += step  # advance the window

    return chunks


# --------------------------------------------------------------------------- #
# Step 3 — Embedding                                                           #
# --------------------------------------------------------------------------- #

async def embed_chunks(
    chunks: list[Chunk],
    ollama: "OllamaClient",
) -> list[EmbeddedChunk]:
    """
    Embed each chunk's text using Ollama and return EmbeddedChunk objects.

    We embed chunks one at a time (sequential, not batched) because
    Ollama's /api/embeddings endpoint is single-text-per-request.
    For most knowledge bases this is fine — indexing happens once.

    Args:
        chunks: Output from chunk_pages()
        ollama: An OllamaClient instance (must be open/not closed)

    Returns:
        List of EmbeddedChunk, same order as input.
    """
    embedded: list[EmbeddedChunk] = []

    for chunk in chunks:
        vector = await ollama.get_embedding(chunk.text)
        embedded.append(EmbeddedChunk(chunk=chunk, embedding=vector))

    return embedded


# --------------------------------------------------------------------------- #
# Orchestrator — the public API for this module                               #
# --------------------------------------------------------------------------- #

async def ingest_file(
    path: str | Path,
    ollama: "OllamaClient",
    store: "VectorStore",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> dict:
    """
    Full pipeline: read a file, chunk it, embed it, store it.

    Before indexing, any previously indexed chunks from the same file
    are deleted — this makes re-indexing idempotent (safe to run twice).

    Args:
        path:          Absolute or relative path to the file to index.
        ollama:        Open OllamaClient.
        store:         Open VectorStore.
        chunk_size:    Characters per chunk (default 1000).
        chunk_overlap: Overlap between chunks (default 200).

    Returns:
        A summary dict, e.g.:
        {
            "source": "design_doc.pdf",
            "file_type": "pdf",
            "pages_read": 12,
            "chunks_created": 47,
            "status": "success"
        }

    Raises:
        ValueError: unsupported file type.
        FileNotFoundError: file doesn't exist.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    source = path.name                      # e.g. "design_doc.pdf"
    file_type = path.suffix.lstrip(".")     # e.g. "pdf"

    # --- Step 1: Read ---
    pages = read_file(path)

    # --- Step 2: Chunk ---
    chunks = chunk_pages(
        pages=pages,
        source=source,
        file_type=file_type,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        return {
            "source": source,
            "file_type": file_type,
            "pages_read": len(pages),
            "chunks_created": 0,
            "status": "skipped — no text extracted",
        }

    # --- Step 3: Embed ---
    embedded = await embed_chunks(chunks, ollama)

    # --- Step 4: Store (delete old chunks first for idempotency) ---
    await store.delete_document(source)   # no-op if not yet indexed
    await store.add_chunks(embedded)

    return {
        "source": source,
        "file_type": file_type,
        "pages_read": len(pages),
        "chunks_created": len(chunks),
        "status": "success",
    }
