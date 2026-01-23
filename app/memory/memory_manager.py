"""
memory_manager.py — High-level memory interface for sonny

This module provides simple functions for storing and retrieving
memories using ChromaDB. Sonny uses this to remember facts,
preferences, and long-term context.
"""

from app.memory.chroma_client import get_memory_collection
from app.memory.embedder import embed_text
import uuid


# ---------------------------------------------------------
# Store a memory
# ---------------------------------------------------------

def store_memory(text: str, metadata: dict = None) -> str:
    """
    Stores a memory in ChromaDB.
    """

    collection = get_memory_collection()

    embedding = embed_text(text)
    memory_id = str(uuid.uuid4())

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

    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


# ---------------------------------------------------------
# Normalize memory text
# ---------------------------------------------------------

def normalize_memory(text: str) -> str:
    t = text.lower()

    if "my name is" in t:
        name = text.split("my name is", 1)[1].strip()
        return f"the user's name is {name}"

    if "i prefer" in t:
        pref = text.split("i prefer", 1)[1].strip()
        return f"the user prefers {pref}"

    if "i like" in t:
        like = text.split("i like", 1)[1].strip()
        return f"the user likes {like}"

    if "i am working on" in t or "i'm working on" in t:
        proj = text.split("working on", 1)[1].strip()
        return f"the user is working on {proj}"

    return text


# ---------------------------------------------------------
# Decide whether a memory should be stored
# ---------------------------------------------------------

def should_store_memory(text: str) -> bool:
    keywords = [
        "my name is",
        "i prefer",
        "i like",
        "i don't like",
        "i am working on",
        "i'm working on",
        "i use",
        "i have",
        "remember that",
        "please remember",
    ]

    t = text.lower()
    return any(k in t for k in keywords)


# ---------------------------------------------------------
# Retrieve all memories (debugging)
# ---------------------------------------------------------

def list_all_memories():
    """
    Returns all stored memories.
    Useful for debugging or inspecting Sonny's long-term memory.
    """
    collection = get_memory_collection()
    return collection.get()