from app.memory.embeddings import generate_embedding

# Cache the fallback dimension after first successful embed
FALLBACK_DIM = 768

def embed_text(text: str) -> list:
    global FALLBACK_DIM

    embedding = generate_embedding(text)

    if embedding:
        FALLBACK_DIM = len(embedding)
        return embedding

    return [0.0] * FALLBACK_DIM