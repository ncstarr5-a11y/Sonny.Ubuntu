"""
chroma_client.py — Handles connection to ChromaDB

This module initializes a persistent ChromaDB client and exposes
a function to retrieve the memory collection used by Droide.

ChromaDB stores vector embeddings and metadata, allowing Droide
to remember past interactions, facts, and context.
"""
import chromadb
import os

CHROMA_PATH = "/home/droide/droide-system/data/chroma"

def get_chroma_client():
    os.makedirs(CHROMA_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client


# ---------------------------------------------------------
# Get or create the memory collection
# ---------------------------------------------------------

def get_memory_collection():
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name="droide_memory",
        metadata={"hnsw:space": "cosine"}
    )
    return collection
