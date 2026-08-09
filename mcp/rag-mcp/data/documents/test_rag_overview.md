# RAG MCP — Test Document

This is a test document for the rag-mcp personal knowledge base server.

## What is RAG?

RAG stands for Retrieval-Augmented Generation. It is a technique that combines
a retrieval system (vector search) with a language model to answer questions
grounded in specific documents.

The main steps in a RAG pipeline are:
1. **Ingestion** — Split documents into chunks, embed them, store in a vector DB.
2. **Retrieval** — Embed the user's query, find the closest chunks by cosine similarity.
3. **Generation** — Pass the retrieved chunks as context to the LLM to produce an answer.

## Why use a vector database?

Traditional keyword search looks for exact word matches. A vector database
stores the *semantic meaning* of text as a high-dimensional vector. This means
you can search for "how does retrieval augmented generation work" and find
documents that talk about "RAG pipelines" even if they don't contain the exact words.

## ChromaDB

ChromaDB is the vector database used in this project. It runs embedded inside
the Python process (no separate server needed), persists data to disk, and
supports cosine similarity search out of the box.

## Ollama

Ollama runs large language models locally. In this project we use it only for
its embedding endpoint — specifically the `nomic-embed-text` model, which
produces 768-dimensional vectors that capture semantic meaning extremely well
for document retrieval tasks.

## MCP (Model Context Protocol)

MCP is Anthropic's open protocol for connecting AI models to external tools and
data sources. An MCP server exposes Tools (actions) and Resources (data) that
Claude can call during a conversation. This project wraps the entire RAG pipeline
as an MCP server so Claude can index and search your personal documents.
