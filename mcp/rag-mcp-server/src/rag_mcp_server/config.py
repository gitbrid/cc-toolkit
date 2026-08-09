"""Configuration management for RAG MCP Server."""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field

DEFAULT_CONFIG = {
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
    "chunk_size": 1500,
    "chunk_overlap": 300,
    "top_k": 5,
    "ocr_languages": "spa+eng",
    "supported_extensions": [
        ".pdf", ".md", ".txt", ".py", ".js", ".ts", ".jsx", ".tsx",
        ".rs", ".toml", ".json", ".yaml", ".yml", ".html", ".css",
        ".sol", ".go", ".java", ".cpp", ".c", ".h",
    ],
    "data_dir": "~/.rag-mcp-server/data",
    "max_file_size_mb": 50,
}


@dataclass
class Config:
    """RAG MCP Server configuration."""

    embedding_model: str = DEFAULT_CONFIG["embedding_model"]
    chunk_size: int = DEFAULT_CONFIG["chunk_size"]
    chunk_overlap: int = DEFAULT_CONFIG["chunk_overlap"]
    top_k: int = DEFAULT_CONFIG["top_k"]
    ocr_languages: str = DEFAULT_CONFIG["ocr_languages"]
    supported_extensions: list = field(
        default_factory=lambda: DEFAULT_CONFIG["supported_extensions"].copy()
    )
    data_dir: str = DEFAULT_CONFIG["data_dir"]
    max_file_size_mb: int = DEFAULT_CONFIG["max_file_size_mb"]

    def __post_init__(self):
        self.data_dir = str(Path(self.data_dir).expanduser())
        os.makedirs(self.data_dir, exist_ok=True)

    @classmethod
    def load(cls, config_path: str = None) -> "Config":
        """Load config from YAML file, falling back to defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
            return cls(
                **{k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            )
        return cls()


def get_config(config_path: str = None) -> Config:
    """Get configuration, loading from file if provided."""
    return Config.load(config_path)
