"""
memory_manager.py — High-level memory interface for sonny

This module provides simple functions for storing and retrieving
memories using ChromaDB. sonny will use this to remember facts,
conversations, user preferences, and long-term context.
"""
from app.memory.chroma_client import get_memory_collection
from app.memory.embedder import embed_text  # whatever you use to embed text
import uuid

# ---------------------------------------------------------
# Store a memory
# ---------------------------------------------------------

def store_memory(text: str, metadata: dict = None) -> str:
    """
    Stores a memory in ChromaDB.
    """

    collection = get_memory_collection()

    # Generate embedding
    embedding = embed_text(text)

    memory_id = str(uuid.uuid4())

    # Chroma 0.4.x requires metadata to be a NON-empty dict
    safe_metadata = metadata or {"source": "sonny"}

    collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[safe_metadata]
    )

    return memory_id






# ---------------------------------------------------------
# Search for similar memories
# ---------------------------------------------------------

def search_memory(query: str, n_results: int = 3):
    collection = get_memory_collection()

    # 1. Embed the query text
    query_embedding = embed_text(query)  # must return a list[float]

    # 2. Query Chroma using embeddings
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results




# ---------------------------------------------------------
# Retrieve all memories (debugging)
# ---------------------------------------------------------

def list_all_memories():
    """
    Returns all stored memories.
    Useful for debugging or inspecting sonny's long-term memory.

    Returns:
        dict: All memory entries.
    """

    collection = get_memory_collection()
    return collection.get()