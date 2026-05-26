"""RAG package exports.

Avoid eager submodule imports here: importing ``src.rag.query_preprocessor``
must not also import the full retriever stack during agent startup.
"""

from __future__ import annotations

from importlib import import_module

__all__ = [
    "Document",
    "DocumentLoader",
    "TextPreprocessor",
    "Chunk",
    "TextChunker",
    "Embedder",
    "ChromaIndexer",
    "IndexingPipeline",
    "QueryPreprocessor",
    "CrossEncoderReranker",
    "HybridRetriever",
    "build_hybrid_retriever",
]

_EXPORT_MAP = {
    "Document": ("src.rag.document_loader", "Document"),
    "DocumentLoader": ("src.rag.document_loader", "DocumentLoader"),
    "TextPreprocessor": ("src.rag.text_preprocessor", "TextPreprocessor"),
    "Chunk": ("src.rag.chunker", "Chunk"),
    "TextChunker": ("src.rag.chunker", "TextChunker"),
    "Embedder": ("src.rag.embedder", "Embedder"),
    "ChromaIndexer": ("src.rag.indexer", "ChromaIndexer"),
    "IndexingPipeline": ("src.rag.pipeline", "IndexingPipeline"),
    "QueryPreprocessor": ("src.rag.query_preprocessor", "QueryPreprocessor"),
    "CrossEncoderReranker": ("src.rag.reranker", "CrossEncoderReranker"),
    "HybridRetriever": ("src.rag.retriever", "HybridRetriever"),
    "build_hybrid_retriever": ("src.rag.retriever", "build_hybrid_retriever"),
}


def __getattr__(name: str):
    try:
        module_name, attr_name = _EXPORT_MAP[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
