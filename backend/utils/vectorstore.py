# vectorstore.py
import chromadb
import uuid

# In-memory ChromaDB client for simplicity
# For persistence, you can specify a path: chromadb.PersistentClient(path="./chroma_db")
client = None
collection = None
COLLECTION_NAME = "pdf_rag_collection"

def get_vector_store_collection():
    """Initializes and returns the ChromaDB collection."""
    global client, collection
    if client is None:
        client = chromadb.Client() # In-memory client
        # Or for persistent storage:
        # client = chromadb.PersistentClient(path="./chroma_data") 
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Using existing collection: {COLLECTION_NAME}")
    except:
        print(f"Creating new collection: {COLLECTION_NAME}")
        # The embedding function is automatically handled by ChromaDB if embeddings are provided directly.
        # If you were to let Chroma handle embedding generation, you'd specify an embedding_function here.
        collection = client.create_collection(
            name=COLLECTION_NAME,
            # metadata={"hnsw:space": "cosine"} # Optional: specify distance metric if needed
        )
        print(f"Collection {COLLECTION_NAME} created.")
    return collection

def add_chunks_to_vector_store(pdf_id: str, chunks: list[str], embeddings: list[list[float]]):
    """Adds text chunks and their embeddings to the vector store, associated with a PDF ID."""
    vs_collection = get_vector_store_collection()
    
    documents_to_add = []
    embeddings_to_add = []
    ids_to_add = []
    metadatas_to_add = []

    for i, chunk_text in enumerate(chunks):
        # Create a unique ID for each chunk, perhaps combining pdf_id and chunk index
        chunk_id = f"{pdf_id}_chunk_{i}"
        documents_to_add.append(chunk_text)
        embeddings_to_add.append(embeddings[i])
        ids_to_add.append(chunk_id)
        metadatas_to_add.append({"pdf_id": pdf_id, "chunk_index": i}) # Store pdf_id for potential filtering

    if documents_to_add:
        vs_collection.add(
            embeddings=embeddings_to_add,
            documents=documents_to_add,
            ids=ids_to_add,
            metadatas=metadatas_to_add
        )
        print(f"Added {len(documents_to_add)} chunks from PDF {pdf_id} to vector store.")

def query_vector_store(query_embedding: list[float], pdf_id: str, top_k: int = 5) -> list[str]:
    """Queries the vector store for relevant chunks based on the query embedding and PDF ID."""
    vs_collection = get_vector_store_collection()
    
    results = vs_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        # ChromaDB's where filter syntax for metadata:
        where={"pdf_id": pdf_id} # Filter results to only include chunks from the specified PDF
    )
    
    # results['documents'] is a list of lists, one for each query embedding. We have one query.
    retrieved_chunks = results['documents'][0] if results['documents'] else []
    print(f"Retrieved {len(retrieved_chunks)} chunks for PDF {pdf_id} based on query.")
    return retrieved_chunks

# Example usage (optional, for testing - requires embedder.py)
# if __name__ == '__main__':
#     # This example assumes you have embedder.py in the same directory or accessible in PYTHONPATH
#     from embedder import generate_embeddings, generate_embedding_for_query

#     sample_pdf_id = "sample_pdf_001"
#     sample_chunks = [
#         "The weather is sunny today in California.",
#         "Machine learning models require a lot of data.",
#         "Paris is the capital of France and is known for the Eiffel Tower.",
#         "Chromadb is a vector database used for similarity search."
#     ]
    
#     print("Generating embeddings for sample chunks...")
#     sample_embeddings = generate_embeddings(sample_chunks)
    
#     print("Adding chunks to vector store...")
#     add_chunks_to_vector_store(pdf_id=sample_pdf_id, chunks=sample_chunks, embeddings=sample_embeddings)
    
#     # Test query
#     query_text = "What is the capital of France?"
#     print(f"\nGenerating embedding for query: '{query_text}'")
#     query_emb = generate_embedding_for_query(query_text)
    
#     print("Querying vector store...")
#     retrieved_docs = query_vector_store(query_embedding=query_emb, pdf_id=sample_pdf_id, top_k=2)
    
#     print(f"\nRetrieved documents for query '{query_text}':")
#     for doc in retrieved_docs:
#         print(f"- {doc}")

#     # Test query for a different PDF ID (should return nothing if store is fresh)
#     query_text_other_pdf = "Tell me about machine learning."
#     print(f"\nGenerating embedding for query: '{query_text_other_pdf}'")
#     query_emb_other_pdf = generate_embedding_for_query(query_text_other_pdf)
#     print("Querying vector store for a different PDF ID...")
#     retrieved_docs_other_pdf = query_vector_store(query_embedding=query_emb_other_pdf, pdf_id="other_pdf_002", top_k=2)
#     print(f"\nRetrieved documents for query '{query_text_other_pdf}' from PDF 'other_pdf_002':")
#     if not retrieved_docs_other_pdf:
#         print("(No documents found, as expected)")
#     for doc in retrieved_docs_other_pdf:
#         print(f"- {doc}")