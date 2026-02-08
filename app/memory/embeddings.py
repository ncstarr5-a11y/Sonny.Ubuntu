"""
embeddings.py — Embedding generator for sonny

This module sends text to Ollama's embedding endpoint and returns
a vector representation. These vectors are used by ChromaDB to
store and retrieve memories based on similarity.
"""

import requests

# ---------------------------------------------------------
# Generate embeddings using Ollama
# ---------------------------------------------------------

def generate_embedding(text: str) -> list:
    """
    Generates an embedding vector for the given text using Ollama.

    Args:
        text (str): The text to embed.

    Returns:
        list: A list of floating-point numbers representing the embedding.

    Notes:
        - Uses the 'nomic-embed-text' model (small, fast, ideal for memory).
        - You can swap this for another embedding model later.
    """

    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "nomic-embed-text",
        "input": text
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        return data.get("embedding", [])

    except Exception as e:
        print(f"[Embedding Error] {e}")
        return []