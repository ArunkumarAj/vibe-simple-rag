# embedder.py
from sentence_transformers import SentenceTransformer

# Using a free, high-quality sentence transformer model
MODEL_NAME = 'all-MiniLM-L6-v2'
model = None

def get_embedding_model():
    """Loads and returns the sentence embedding model."""
    global model
    if model is None:
        print(f"Loading embedding model: {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
        print("Embedding model loaded.")
    return model

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a list of text chunks."""
    embedding_model = get_embedding_model()
    embeddings = embedding_model.encode(texts, convert_to_tensor=False) # Get numpy arrays
    return embeddings.tolist() # Convert to list of lists for easier JSON serialization/DB storage

def generate_embedding_for_query(text: str) -> list[float]:
    """Generates embedding for a single query string."""
    embedding_model = get_embedding_model()
    embedding = embedding_model.encode(text, convert_to_tensor=False)
    return embedding.tolist()

# Example usage (optional, for testing)
# if __name__ == '__main__':
#     sample_texts = [
#         "This is the first document.",
#         "This document is the second document.",
#         "And this is the third one.",
#         "Is this the first document?"
#     ]
#     embeddings = generate_embeddings(sample_texts)
#     print(f"Generated {len(embeddings)} embeddings.")
#     for i, emb in enumerate(embeddings):
#         print(f"Embedding for text {i+1} (first 5 dims): {emb[:5]}...")
    
#     query = "What is the first document?"
#     query_embedding = generate_embedding_for_query(query)
#     print(f"\nEmbedding for query '{query}' (first 5 dims): {query_embedding[:5]}...")