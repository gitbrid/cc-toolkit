"""Text chunking with overlap for RAG indexing.

Splits documents into overlapping chunks that respect paragraph boundaries,
preserving context across chunk boundaries for better retrieval.
"""

from dataclasses import dataclass


@dataclass
class Chunk:
    """A text chunk with its source metadata."""

    text: str
    metadata: dict  # source_file, page_number, chunk_index, project, etc.


def chunk_text(
    text: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 300,
    metadata: dict = None,
) -> list[Chunk]:
    """Split text into overlapping chunks, respecting paragraph boundaries.

    Args:
        text: The text to chunk
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        metadata: Base metadata to attach to each chunk

    Returns:
        List of Chunk objects with text and metadata
    """
    if not text or not text.strip():
        return []

    metadata = metadata or {}
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""
    chunk_index = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # If adding this paragraph exceeds chunk_size, save current and start new
        if current_chunk and len(current_chunk) + len(paragraph) + 2 > chunk_size:
            chunks.append(
                Chunk(
                    text=current_chunk.strip(),
                    metadata={**metadata, "chunk_index": chunk_index},
                )
            )
            chunk_index += 1

            # Keep overlap from end of current chunk for context continuity
            if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                current_chunk = current_chunk[-chunk_overlap:]
            else:
                current_chunk = ""

        current_chunk += ("\n\n" if current_chunk else "") + paragraph

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(
            Chunk(
                text=current_chunk.strip(),
                metadata={**metadata, "chunk_index": chunk_index},
            )
        )

    # Handle oversized chunks (single paragraph larger than chunk_size)
    return _split_oversized_chunks(chunks, chunk_size)


def _split_oversized_chunks(chunks: list[Chunk], chunk_size: int) -> list[Chunk]:
    """Force-split any chunks that are significantly larger than chunk_size."""
    final_chunks = []

    for chunk in chunks:
        if len(chunk.text) <= chunk_size * 1.5:
            final_chunks.append(chunk)
            continue

        # Force-split at sentence boundaries where possible
        text = chunk.text
        sub_idx = 0

        while text:
            split_at = min(chunk_size, len(text))

            # Try to split at a natural boundary
            if split_at < len(text):
                for separator in [". ", ".\n", "\n", "; ", ", ", " "]:
                    last_sep = text[:split_at].rfind(separator)
                    if last_sep > chunk_size * 0.5:
                        split_at = last_sep + len(separator)
                        break

            sub_text = text[:split_at].strip()
            if sub_text:
                final_chunks.append(
                    Chunk(
                        text=sub_text,
                        metadata={
                            **chunk.metadata,
                            "sub_index": sub_idx,
                        },
                    )
                )
                sub_idx += 1

            text = text[split_at:].strip()

    return final_chunks
