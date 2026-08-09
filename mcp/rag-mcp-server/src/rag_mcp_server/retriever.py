"""Semantic search retriever — queries ChromaDB for relevant document chunks."""

import os
import logging

logger = logging.getLogger(__name__)


class Retriever:
    """Queries indexed documents using semantic similarity search."""

    def __init__(self, config):
        self.config = config
        self._model = None
        self._chroma_client = None

    @property
    def model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.embedding_model)
        return self._model

    @property
    def chroma_client(self):
        """Lazy-load ChromaDB persistent client."""
        if self._chroma_client is None:
            import chromadb

            db_path = os.path.join(self.config.data_dir, "chromadb")
            self._chroma_client = chromadb.PersistentClient(path=db_path)
        return self._chroma_client

    def query(
        self,
        query: str,
        project: str = None,
        top_k: int = None,
    ) -> list[dict]:
        """Query indexed documents for relevant chunks.

        Args:
            query: Natural language search query
            project: Optional project name to search in (all projects if None)
            top_k: Number of results to return

        Returns:
            List of result dicts with text, metadata, distance, relevance, project
        """
        top_k = top_k or self.config.top_k

        # Generate query embedding
        query_embedding = self.model.encode([query]).tolist()

        # Determine which collections to search
        if project:
            collection_names = [project]
        else:
            collection_names = [
                c.name for c in self.chroma_client.list_collections()
            ]

        results = []

        for col_name in collection_names:
            try:
                collection = self.chroma_client.get_collection(col_name)

                if collection.count() == 0:
                    continue

                query_results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=min(top_k, collection.count()),
                    include=["documents", "metadatas", "distances"],
                )

                for i in range(len(query_results["ids"][0])):
                    distance = query_results["distances"][0][i]
                    results.append({
                        "text": query_results["documents"][0][i],
                        "metadata": query_results["metadatas"][0][i],
                        "distance": distance,
                        "relevance": round(1 - distance, 4),
                        "project": col_name,
                    })
            except Exception as e:
                logger.warning(f"Error querying collection {col_name}: {e}")

        # Sort by relevance (highest first)
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return results[:top_k]

    def format_results(self, results: list[dict]) -> str:
        """Format query results into a readable string for the LLM.

        Includes source citations so the LLM can reference exact locations.
        """
        if not results:
            return "No relevant results found in indexed documents."

        formatted = []
        for i, r in enumerate(results, 1):
            meta = r["metadata"]
            source = meta.get("source_file", "unknown")
            page = meta.get("page_number")
            project = r.get("project", "unknown")
            relevance = f"{r['relevance']:.0%}"

            header = f"Result {i} [{relevance} relevance]"
            header += f"\n   Project: {project}"
            header += f"\n   Source: {source}"
            if page:
                header += f" (page {page})"
            if meta.get("ocr_applied"):
                header += " [OCR]"

            separator = "-" * 60
            formatted.append(f"{header}\n{separator}\n{r['text']}\n")

        return "\n".join(formatted)
