# upload_pdf.py
import os
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from utils.pdf_extractor import extract_text_from_pdf, chunk_text
from utils.embedder import generate_embeddings
from utils.vectorstore import add_chunks_to_vector_store

# UPLOAD_TEMP_DIR is already defined in settings.py and created there
UPLOAD_TEMP_DIR = settings.UPLOAD_TEMP_DIR

class PDFUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return Response({"error": "No PDF file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not pdf_file.name.endswith('.pdf'):
            return Response({"error": "Invalid file type. Only PDF files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a unique ID for this PDF processing job/session
        # This ID will be used to associate chunks in the vector store
        pdf_id = str(uuid.uuid4())
        
        # Save the uploaded PDF temporarily
        temp_pdf_path = os.path.join(UPLOAD_TEMP_DIR, f"{pdf_id}_{pdf_file.name}")
        
        try:
            with open(temp_pdf_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)
            
            print(f"PDF temporarily saved to: {temp_pdf_path}")

            # 1. Extract text
            print(f"Extracting text from PDF: {pdf_id}")
            extracted_text = extract_text_from_pdf(temp_pdf_path)
            if not extracted_text.strip():
                return Response({"error": "Could not extract text from the PDF or PDF is empty."},
                                status=status.HTTP_400_BAD_REQUEST)

            # 2. Chunk text
            print(f"Chunking text for PDF: {pdf_id}")
            text_chunks = chunk_text(extracted_text)
            if not text_chunks:
                return Response({"error": "Failed to chunk the extracted text."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 3. Generate embeddings
            print(f"Generating embeddings for {len(text_chunks)} chunks of PDF: {pdf_id}")
            chunk_embeddings = generate_embeddings(text_chunks)

            # 4. Store chunks and embeddings
            print(f"Adding chunks and embeddings to vector store for PDF: {pdf_id}")
            add_chunks_to_vector_store(pdf_id=pdf_id, chunks=text_chunks, embeddings=chunk_embeddings)

            return Response({
                "message": "PDF processed successfully.", 
                "pdf_id": pdf_id, # Return the unique ID for this PDF
                "num_chunks": len(text_chunks)
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error processing PDF {pdf_id}: {e}")
            # Clean up the temporary file in case of error
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            return Response({"error": f"An error occurred during PDF processing: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up the temporary file after processing, regardless of success or failure
            if os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                    print(f"Temporary PDF file {temp_pdf_path} deleted.")
                except Exception as e_del:
                    print(f"Error deleting temporary PDF file {temp_pdf_path}: {e_del}")

# Note: For a real application, consider:
# - Asynchronous processing for large PDFs (e.g., using Celery).
# - More robust error handling and logging.
# - Storing PDF metadata (filename, upload date, user association) in a relational DB.
# - The `pdf_id` should be managed carefully, perhaps stored alongside user data if auth is added.