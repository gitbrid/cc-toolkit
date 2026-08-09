"""Document indexer — discovers, extracts, chunks, embeds, and stores documents."""

import os
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Directories to always skip during file discovery
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".tox", "dist", "build", ".eggs", "target", ".next", ".nuxt",
    ".cache", ".pytest_cache", ".mypy_cache", "coverage", ".turbo",
}


class Indexer:
    """Indexes files into ChromaDB for semantic search."""

    def __init__(self, config):
        self.config = config
        self._model = None
        self._chroma_client = None

    @property
    def model(self):
        """Lazy-load the embedding model (heavy, only load when needed)."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self._model = SentenceTransformer(self.config.embedding_model)
        return self._model

    @property
    def chroma_client(self):
        """Lazy-load ChromaDB persistent client."""
        if self._chroma_client is None:
            import chromadb

            db_path = os.path.join(self.config.data_dir, "chromadb")
            os.makedirs(db_path, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(path=db_path)
        return self._chroma_client

    def _get_collection(self, project_name: str):
        """Get or create a ChromaDB collection for a project."""
        return self.chroma_client.get_or_create_collection(
            name=project_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _sanitize_project_name(self, name: str) -> str:
        """Sanitize project name for ChromaDB (alphanumeric, hyphens, underscores)."""
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        # ChromaDB requires collection names of at least 3 chars
        if len(safe) < 3:
            safe = safe + "_project"
        return safe

    # ── Manifest (tracks which files have been indexed) ──────────────

    def _get_manifest_path(self, project_name: str) -> str:
        path = os.path.join(self.config.data_dir, "manifests", f"{project_name}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def _load_manifest(self, project_name: str) -> dict:
        path = self._get_manifest_path(project_name)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {"files": {}, "indexed_at": None}

    def _save_manifest(self, project_name: str, manifest: dict):
        path = self._get_manifest_path(project_name)
        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)

    # ── File hashing (for change detection) ──────────────────────────

    def _file_hash(self, filepath: str) -> str:
        """MD5 hash of file contents for change detection."""
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(8192), b""):
                h.update(block)
        return h.hexdigest()

    # ── Main indexing logic ──────────────────────────────────────────

    def index_directory(
        self,
        directory: str,
        project_name: str = None,
        force: bool = False,
    ) -> dict:
        """Index all supported files in a directory.

        Args:
            directory: Path to the directory to index
            project_name: Name for this project (defaults to directory name)
            force: If True, re-index all files even if unchanged

        Returns:
            Dict with indexing statistics
        """
        directory = str(Path(directory).resolve())
        if not os.path.isdir(directory):
            return {"error": f"Directory not found: {directory}"}

        if project_name is None:
            project_name = Path(directory).name
        safe_name = self._sanitize_project_name(project_name)

        collection = self._get_collection(safe_name)
        manifest = self._load_manifest(safe_name)

        files = self._discover_files(directory)

        stats = {
            "project": safe_name,
            "directory": directory,
            "total_files": len(files),
            "indexed_files": 0,
            "skipped_files": 0,
            "total_chunks": 0,
            "ocr_applied": 0,
            "errors": [],
        }

        for filepath in files:
            rel_path = os.path.relpath(filepath, directory)
            file_hash = self._file_hash(filepath)

            # Skip unchanged files (unless forced)
            if not force and rel_path in manifest["files"]:
                if manifest["files"][rel_path]["hash"] == file_hash:
                    stats["skipped_files"] += 1
                    continue
                else:
                    # File changed — remove old chunks before re-indexing
                    self._remove_file_chunks(collection, rel_path)

            try:
                chunks = self._process_file(filepath, rel_path, safe_name)

                if chunks:
                    self._store_chunks(collection, chunks, safe_name, rel_path)

                    stats["indexed_files"] += 1
                    stats["total_chunks"] += len(chunks)
                    stats["ocr_applied"] += sum(
                        1 for c in chunks if c.metadata.get("ocr_applied")
                    )

                    manifest["files"][rel_path] = {
                        "hash": file_hash,
                        "chunks": len(chunks),
                        "indexed_at": datetime.now().isoformat(),
                    }

            except Exception as e:
                logger.error(f"Error processing {rel_path}: {e}")
                stats["errors"].append(f"{rel_path}: {str(e)}")

        manifest["indexed_at"] = datetime.now().isoformat()
        manifest["directory"] = directory
        self._save_manifest(safe_name, manifest)

        return stats

    def _store_chunks(self, collection, chunks, project_name, rel_path):
        """Generate embeddings and store chunks in ChromaDB."""
        texts = [c.text for c in chunks]
        embeddings = self.model.encode(texts).tolist()

        ids = [f"{project_name}::{rel_path}::{i}" for i in range(len(chunks))]
        metadatas = [c.metadata for c in chunks]

        # ChromaDB has a batch size limit, process in batches of 500
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            collection.add(
                ids=ids[i:end],
                embeddings=embeddings[i:end],
                documents=texts[i:end],
                metadatas=metadatas[i:end],
            )

    # ── File discovery ───────────────────────────────────────────────

    def _discover_files(self, directory: str) -> list[str]:
        """Find all supported files in directory, skipping build/hidden dirs."""
        files = []

        for root, dirs, filenames in os.walk(directory):
            # Prune directories we don't want to index
            dirs[:] = [
                d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
            ]

            for filename in filenames:
                filepath = os.path.join(root, filename)
                ext = Path(filename).suffix.lower()

                if ext not in self.config.supported_extensions:
                    continue

                # Skip files larger than max size
                try:
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    if size_mb > self.config.max_file_size_mb:
                        continue
                except OSError:
                    continue

                files.append(filepath)

        return sorted(files)

    # ── File processing ──────────────────────────────────────────────

    def _process_file(self, filepath: str, rel_path: str, project_name: str):
        """Extract text from a file and split into chunks."""
        from .pdf_extractor import extract_pdf
        from .chunker import chunk_text

        ext = Path(filepath).suffix.lower()
        all_chunks = []

        if ext == ".pdf":
            pages = extract_pdf(filepath, self.config.ocr_languages)
            for page in pages:
                chunks = chunk_text(
                    page.text,
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap,
                    metadata={
                        "source_file": rel_path,
                        "page_number": page.page_number,
                        "project": project_name,
                        "file_type": "pdf",
                        "ocr_applied": page.ocr_applied,
                    },
                )
                all_chunks.extend(chunks)
        else:
            # Text-based files (code, markdown, etc.)
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except Exception:
                return []

            if not text.strip():
                return []

            chunks = chunk_text(
                text,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                metadata={
                    "source_file": rel_path,
                    "project": project_name,
                    "file_type": ext.lstrip("."),
                },
            )
            all_chunks.extend(chunks)

        return all_chunks

    def _remove_file_chunks(self, collection, rel_path: str):
        """Remove all chunks for a specific file from the collection."""
        try:
            results = collection.get(where={"source_file": rel_path})
            if results["ids"]:
                collection.delete(ids=results["ids"])
        except Exception as e:
            logger.warning(f"Could not remove old chunks for {rel_path}: {e}")

    # ── Project management ───────────────────────────────────────────

    def list_projects(self) -> list[dict]:
        """List all indexed projects with their stats."""
        manifests_dir = os.path.join(self.config.data_dir, "manifests")
        if not os.path.exists(manifests_dir):
            return []

        projects = []
        for filename in sorted(os.listdir(manifests_dir)):
            if not filename.endswith(".json"):
                continue

            project_name = filename[:-5]
            manifest = self._load_manifest(project_name)

            projects.append({
                "name": project_name,
                "directory": manifest.get("directory", "unknown"),
                "files": len(manifest.get("files", {})),
                "total_chunks": sum(
                    f.get("chunks", 0) for f in manifest.get("files", {}).values()
                ),
                "indexed_at": manifest.get("indexed_at"),
            })

        return projects

    def delete_project(self, project_name: str) -> dict:
        """Delete a project's index and manifest."""
        try:
            self.chroma_client.delete_collection(project_name)
        except Exception:
            pass  # Collection might not exist

        manifest_path = self._get_manifest_path(project_name)
        if os.path.exists(manifest_path):
            os.remove(manifest_path)

        return {"deleted": project_name}
