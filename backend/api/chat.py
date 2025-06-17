# chat.py
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from groq import Groq

from utils.embedder import generate_embedding_for_query
from utils.vectorstore import query_vector_store

# --- Configuration for Groq API ---
# IMPORTANT: Store your Groq API key securely, e.g., in an environment variable
# DO NOT hardcode it directly in the source code.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY environment variable not set. Chat functionality will not work.")
    # raise ValueError("GROQ_API_KEY environment variable not set.")

LLAMA3_8B_MODEL = "llama3-8b-8192"
LLAMA3_70B_MODEL = "llama3-70b-8192"
# Choose the model you want to use:
SELECTED_LLM_MODEL = LLAMA3_8B_MODEL # or LLAMA3_70B_MODEL for potentially better (but slower/more expensive if not free tier) results

class ChatView(APIView):
    def post(self, request, *args, **kwargs):
        if not GROQ_API_KEY:
            return Response({"error": "Groq API key not configured on the server."}, 
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        question = request.data.get('question')
        pdf_id = request.data.get('pdf_id') # Get the PDF ID from the request

        if not question:
            return Response({"error": "No question provided."}, status=status.HTTP_400_BAD_REQUEST)
        if not pdf_id:
            return Response({"error": "No pdf_id provided. Please upload and select a PDF first."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Embed the question
            print(f"Generating embedding for question: '{question}' for PDF ID: {pdf_id}")
            query_embedding = generate_embedding_for_query(question)

            # 2. Query vector store for relevant chunks from the specific PDF
            print(f"Querying vector store for relevant chunks (PDF ID: {pdf_id})...")
            retrieved_chunks = query_vector_store(query_embedding, pdf_id=pdf_id, top_k=3) # Get top 3 chunks

            if not retrieved_chunks:
                # Fallback if no relevant chunks are found
                print(f"No relevant chunks found in PDF {pdf_id} for the question.")
                return Response({"answer": "I could not find relevant information in the provided document to answer your question.", "source": "fallback"},
                                status=status.HTTP_200_OK)

            # 3. Construct the prompt
            context_str = "\n\n".join(retrieved_chunks)
            
            system_prompt = (
                "You are a helpful AI assistant. Your task is to answer questions based ONLY on the provided context below. "
                "Do not use any external knowledge or information outside of this context. "
                "If the answer cannot be found within the provided context, you MUST respond with: "
                "'I cannot answer beyond the provided document.' "
                "Do not try to make up an answer or infer information not explicitly stated in the context."
            )
            
            user_prompt_template = (
                "Context from the document:\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Based ONLY on the context above, please answer the following question: {question}"
            )
            
            final_user_prompt = user_prompt_template.format(context_str=context_str, question=question)
            
            print(f"\nSystem Prompt:\n{system_prompt}")
            print(f"\nUser Prompt (with context):\n{final_user_prompt}\n")

            # 4. Call Groq API with LLaMA 3
            print(f"Sending request to Groq API with model: {SELECTED_LLM_MODEL}...")
            client = Groq(api_key=GROQ_API_KEY)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": final_user_prompt,
                    }
                ],
                model=SELECTED_LLM_MODEL,
                temperature=0.1, # Lower temperature for more factual, less creative responses
                max_tokens=300, # Adjust as needed
                # top_p=1, # Default
                # stop=None, # Default
                # stream=False # Default
            )

            llm_response = chat_completion.choices[0].message.content.strip()
            print(f"LLM Response: {llm_response}")

            # Basic guardrail: Check if the model tried to hallucinate despite the prompt
            # This is a very simple check; more sophisticated checks might be needed.
            if "I cannot answer beyond the provided document." not in llm_response and not any(chunk.lower() in llm_response.lower() for chunk in retrieved_chunks):
                 # A more robust check would involve semantic similarity or checking if the core entities of the answer are from the context.
                 # For now, if it doesn't say it can't answer AND doesn't seem to directly use context, we might be cautious.
                 # This is a placeholder for more advanced guardrailing.
                 pass # For now, we'll trust the strict prompt, but this is where more logic could go.

            return Response({"answer": llm_response, "source": "llm", "retrieved_context_length": len(retrieved_chunks)}, 
                            status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error during chat processing for PDF {pdf_id}: {e}")
            # Consider logging the full traceback for debugging
            # import traceback
            # print(traceback.format_exc())
            return Response({"error": f"An error occurred: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Note:
# - Ensure GROQ_API_KEY is set as an environment variable.
# - The prompt engineering is crucial for restricting the LLM.
# - Error handling can be made more granular.
# - Consider adding logging for requests and responses for monitoring and debugging.