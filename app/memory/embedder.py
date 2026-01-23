from app.memory.embeddings import generate_embedding

def embed_text(text: str) -> list:
    """
    Wrapper around the embedding generator.
    Ensures we always return a valid vector.
    """
    embedding = generate_embedding(text)

    # Fallback if Ollama fails
    if not embedding:
        return [0.0] * 768

    return embedding

