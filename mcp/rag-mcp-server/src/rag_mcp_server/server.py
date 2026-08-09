"""MCP Server — exposes RAG tools to Claude Code.

Tools:
    rag_index      — Index a directory (PDFs, code, docs)
    rag_query      — Semantic search across indexed documents
    rag_update     — Update index with new/changed files only
    rag_list       — List all indexed projects
    rag_delete     — Delete a project's index
"""

import logging
from mcp.server.fastmcp import FastMCP

from .config import get_config
from .indexer import Indexer
from .retriever import Retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "rag-mcp-server",
    instructions="RAG server for indexing and querying PDFs, code, and documents",
)

# Lazy singletons — heavy dependencies loaded only when first tool is called
_config = None
_indexer = None
_retriever = None


def _get_config():
    global _config
    if _config is None:
        _config = get_config()
    return _config


def _get_indexer():
    global _indexer
    if _indexer is None:
        _indexer = Indexer(_get_config())
    return _indexer


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever(_get_config())
    return _retriever


# ── Tools ────────────────────────────────────────────────────────────


@mcp.tool()
def rag_index(
    directory: str,
    project_name: str | None = None,
    force: bool = False,
) -> str:
    """Index a directory of files (PDFs, code, markdown, etc.) for semantic search.

    Extracts text, splits into chunks, generates embeddings, and stores in
    a vector database. Automatically applies OCR to scanned PDFs.
    Only re-indexes files that have changed since last indexing.

    Args:
        directory: Absolute path to the directory to index
        project_name: Optional name for this project (defaults to directory name)
        force: If True, re-index all files even if unchanged
    """
    indexer = _get_indexer()
    stats = indexer.index_directory(directory, project_name, force)

    if "error" in stats:
        return f"Error: {stats['error']}"

    lines = [
        f"Project '{stats['project']}' indexed successfully!",
        f"   Directory: {stats['directory']}",
        f"   Files indexed: {stats['indexed_files']}",
        f"   Files skipped (unchanged): {stats['skipped_files']}",
        f"   Total chunks: {stats['total_chunks']}",
    ]

    if stats["ocr_applied"]:
        lines.append(f"   OCR applied to: {stats['ocr_applied']} chunks")

    if stats["errors"]:
        lines.append(f"   Errors: {len(stats['errors'])}")
        for err in stats["errors"][:5]:
            lines.append(f"      - {err}")

    return "\n".join(lines)


@mcp.tool()
def rag_query(
    query: str,
    project: str | None = None,
    top_k: int = 5,
) -> str:
    """Search indexed documents for information relevant to a query.

    Uses semantic similarity to find the most relevant document chunks.
    Returns exact text excerpts with source file and page citations.

    Args:
        query: Natural language question or keywords to search for
        project: Optional project name to limit search (searches all if omitted)
        top_k: Number of results to return (default: 5)
    """
    retriever = _get_retriever()
    results = retriever.query(query, project, top_k)
    return retriever.format_results(results)


@mcp.tool()
def rag_update(
    directory: str,
    project_name: str | None = None,
) -> str:
    """Update an existing project index — only processes new or modified files.

    Faster than full re-indexing. Detects changes via file hashes.

    Args:
        directory: Path to the project directory
        project_name: Optional project name
    """
    return rag_index(directory, project_name, force=False)


@mcp.tool()
def rag_list_projects() -> str:
    """List all indexed projects with their statistics."""
    indexer = _get_indexer()
    projects = indexer.list_projects()

    if not projects:
        return "No projects indexed yet. Use rag_index to index a directory."

    lines = ["Indexed Projects:\n"]
    for p in projects:
        lines.append(f"  {p['name']}")
        lines.append(f"     Directory: {p['directory']}")
        lines.append(f"     Files: {p['files']} | Chunks: {p['total_chunks']}")
        lines.append(f"     Last indexed: {p['indexed_at']}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def rag_delete_project(project_name: str) -> str:
    """Delete a project's index from the vector database.

    Args:
        project_name: Exact name of the project to delete (use rag_list_projects to see names)
    """
    indexer = _get_indexer()
    result = indexer.delete_project(project_name)
    return f"Project '{result['deleted']}' deleted."


def main():
    """Entry point — starts the MCP server (stdio transport)."""
    mcp.run()
