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
    
#---------------------------------------------------------
# Hybrid memory search (semantic + keyword)
#---------------------------------------------------------

def hybrid_memory_search(query: str, n_results: int = 3):
    collection = get_memory_collection()

    # --- Semantic search ---
    semantic = []
    try:
        semantic_results = collection.query(
            query_embeddings=[embed_text(query)],
            n_results=n_results
        )
        semantic = semantic_results.get("documents", [[]])[0]
    except Exception:
        semantic = []

    # --- Keyword search ---
    all_docs = collection.get().get("documents", [])
    flat_docs = [d for sub in all_docs for d in sub]  # flatten

    keywords = [
        "name", "prefer", "like", "love", "from", "live",
        "working on", "kids", "family", "raspberry", "linux",
        "project", "favourite", "favorite" ,"remember", "use", "have"
    ]

    keyword_hits = [
        doc for doc in flat_docs
        if any(k in doc.lower() for k in keywords)
    ]

    # Combine + dedupe + trim
    combined = semantic + keyword_hits
    seen = set()
    unique = []
    for m in combined:
        if m not in seen:
            unique.append(m)
            seen.add(m)

    return unique[:n_results]