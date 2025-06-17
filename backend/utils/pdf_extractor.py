# pdf_extractor.py
import fitz  # PyMuPDF

MAX_CHUNK_TOKENS = 400 # Approximate, as we are splitting by words

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """Extracts text from a given PDF file."""
    doc = fitz.open(pdf_file_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    doc.close()
    return text

def chunk_text(text: str, chunk_size: int = MAX_CHUNK_TOKENS) -> list[str]:
    """Chunks text into manageable sections based on approximate token count."""
    words = text.split()
    chunks = []
    current_chunk_words = []
    current_length = 0

    for word in words:
        current_chunk_words.append(word)
        current_length += 1 # Approximating token count with word count
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk_words))
            current_chunk_words = []
            current_length = 0
    
    if current_chunk_words: # Add any remaining words as the last chunk
        chunks.append(" ".join(current_chunk_words))
        
    return chunks

# Example usage (optional, for testing)
# if __name__ == '__main__':
#     sample_pdf_path = 'path_to_your_sample.pdf' # Replace with a real PDF path for testing
#     try:
#         extracted_text = extract_text_from_pdf(sample_pdf_path)
#         print(f"Extracted Text (first 500 chars): {extracted_text[:500]}\n...")
#         text_chunks = chunk_text(extracted_text)
#         print(f"\nNumber of chunks: {len(text_chunks)}")
#         for i, chunk in enumerate(text_chunks[:3]): # Print first 3 chunks
#             print(f"Chunk {i+1}: {chunk[:100]}...")
#     except Exception as e:
#         print(f"Error during testing: {e}")