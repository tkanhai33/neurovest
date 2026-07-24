from backend.app.stacks.chat_public.rag.contracts import (
    KnowledgeChunk,
    RetrievalResult,
)
from backend.app.stacks.chat_public.rag.embedding_client import (
    DEFAULT_EMBEDDING_MODEL,
    EmbeddingBatch,
    EmbeddingError,
    OllamaEmbeddingClient,
)
from backend.app.stacks.chat_public.rag.local_index import (
    LocalKnowledgeIndex,
    chunk_text,
    discover_allowlisted_sources,
)

__all__ = [
    "DEFAULT_EMBEDDING_MODEL",
    "EmbeddingBatch",
    "EmbeddingError",
    "KnowledgeChunk",
    "LocalKnowledgeIndex",
    "OllamaEmbeddingClient",
    "RetrievalResult",
    "chunk_text",
    "discover_allowlisted_sources",
]
