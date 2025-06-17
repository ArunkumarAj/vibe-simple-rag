# PDF RAG Application with Django, Groq, and LLaMA 3

This is a full-stack PDF-based Retrieval-Augmented Generation (RAG) application.
It allows users to upload PDF files and ask questions about their content.

## Features

- **PDF Upload**: Upload PDF files via a REST API.
- **Text Extraction**: Extracts text from PDFs using PyMuPDF.
- **Text Chunking**: Splits extracted text into manageable chunks.
- **Vector Embeddings**: Generates embeddings using `all-MiniLM-L6-v2`.
- **Vector Storage**: Stores chunks and embeddings in ChromaDB (in-memory by default).
- **Chat with PDF**: Ask questions about the uploaded PDF.
- **Contextual Answers**: Uses Groq API with LLaMA 3 (8B) to generate answers based *only* on the retrieved context from the PDF.
- **Frontend**: Basic Vanilla HTML, CSS, and JavaScript for interaction.

## Project Structure

```
rag-geni-pro/
├── backend/
│   ├── api/                 # Django app for API endpoints (upload, chat)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── chat.py          # Chat API logic
│   │   └── upload_pdf.py    # PDF upload API logic
│   ├── rag_project/         # Django project configuration
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── utils/               # Utility modules
│   │   ├── __init__.py
│   │   ├── embedder.py      # Embedding generation
│   │   ├── pdf_extractor.py # PDF text extraction and chunking
│   │   └── vectorstore.py   # Vector store interaction (ChromaDB)
│   └── manage.py            # Django's command-line utility
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── script.js            # Frontend JavaScript
│   └── style.css            # CSS styles
├── tmp/
│   └── pdf_uploads/         # Temporary storage for uploads (auto-created)
├── .env                     # Environment variables (GROQ_API_KEY, DJANGO_SECRET_KEY)
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Prerequisites

- Conda (Anaconda or Miniconda)
- Python 3.11 (the project is developed and tested with Python 3.11)

## Setup and Installation

1.  **Clone the repository (if applicable) or ensure you have the project files.**

2.  **Create and activate a Conda environment:**
    Replace `rag_env` with your preferred environment name.
    ```bash
    conda create -n rag_env python=3.11
    conda activate rag_env
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    Create a `.env` file in the project root directory (i.e., `rag-geni-pro/.env`). Copy the contents from `.env.example` (if provided) or add the following variables:

    ```env
    GROQ_API_KEY="your_groq_api_key_here"
    DJANGO_SECRET_KEY="your_django_secret_key_here" # Optional for local, but recommended
    ```

    *   `GROQ_API_KEY`: Your API key for Groq. You can get this from the [Groq Console](https://console.groq.com/keys).
    *   `DJANGO_SECRET_KEY`: A strong, unique secret key for your Django application. If not set (and not using Docker Compose with an env_file), a fallback development key is used (not suitable for production). You can generate one using Python: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

    **Note:** The `docker-compose.yml` is configured to use the `.env` file automatically.

    *   `GROQ_API_KEY`: Your API key for Groq. You can get this from the [Groq Console](https://console.groq.com/keys).
        ```bash


5.  **Apply Django Migrations:**
    (Although this project uses SQLite and doesn't have custom models requiring extensive migrations initially, it's good practice for Django projects.)
    Navigate to the `backend/` directory:
    ```bash
    cd backend
    python manage.py migrate
    ```

## Running the Application (Local Conda Environment)

1.  **Start the Django development server:**
    Make sure you are in the `backend/` directory where `manage.py` is located.
    ```bash
    python manage.py runserver
    ```
    The application will typically be available at `http://127.0.0.1:8000/` or `http://localhost:8000/`.

2.  **Open the application in your browser:**
    Navigate to `http://127.0.0.1:8000/`.

## How to Use

1.  **Upload a PDF**: Use the form on the page to select and upload a PDF file.
2.  **Ask Questions**: Once the PDF is processed (you'll see a success message with a PDF ID), type your question into the input box and click "Ask".
3.  **View Response**: The AI's answer, based on the content of your PDF, will appear in the chat history.

## Important Notes

-   **Groq API Key**: The application will not be able to answer questions without a valid `GROQ_API_KEY`.
-   **Embedding Model**: The `all-MiniLM-L6-v2` model will be downloaded automatically by the `sentence-transformers` library the first time it's needed. This might take a few moments.
-   *   **Vector Store**: ChromaDB is used in-memory by default. This means the vector store will be cleared each time the Django application restarts. For persistence, you can configure ChromaDB to use a persistent directory (see comments in `backend/utils/vectorstore.py`).
-   **Error Handling**: Basic error handling is in place. Check the console (both browser and Django server) for more detailed error messages if something goes wrong.
-   **Security**: The `ALLOWED_HOSTS = ['*']` and `CORS_ALLOW_ALL_ORIGINS = True` settings in `settings.py` are for development convenience. For production, these should be configured securely.
-   **Scalability**: For larger PDFs or higher traffic, consider:
    *   Asynchronous processing for PDF uploads (e.g., using Celery).
    *   A more robust, persistent vector database (the `docker-compose.yml` includes an example PostgreSQL setup, but the application currently uses SQLite).
    *   Optimizing chunking and embedding strategies.
-   **Docker & Gunicorn**: The provided `Dockerfile` uses Django's development server. For a more production-like setup with Docker, you would typically use a WSGI server like Gunicorn. The `docker-compose.yml` also uses the development server for simplicity but can be adapted for Gunicorn.

## Running the Application with Docker Compose

This is the recommended way to run the application as it handles dependencies and services consistently.

1.  **Ensure Docker and Docker Compose are installed.**

2.  **Create and configure the `.env` file:**
    Make sure you have a `.env` file in the project root with your `GROQ_API_KEY` and optionally `DJANGO_SECRET_KEY` as described in the "Set Environment Variables" section.

3.  **Build and run the services:**
    From the project root directory (where `docker-compose.yml` is located):
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker image for the `web` service (if it doesn't exist or if `Dockerfile` changed) and start all services defined in `docker-compose.yml` (web and db).

4.  **Access the application:**
    Once the containers are up and running, the application will be available at `http://localhost:8000/`.

5.  **Applying Migrations (First time or after model changes):**
    If you need to apply Django migrations (e.g., on the first run or after database model changes), you can run:
    ```bash
    docker-compose exec web python backend/manage.py migrate
    ```
    The `Dockerfile` already runs migrations during the image build, so this is typically only needed if models change after the initial build.

6.  **Stopping the application:**
    Press `Ctrl+C` in the terminal where `docker-compose up` is running. To stop and remove the containers:
    ```bash
    docker-compose down
    ```

7.  **Viewing logs:**
    ```bash
    docker-compose logs -f web  # To follow logs for the web service
    ```

## Future Enhancements (Potential)

-   User authentication to manage individual PDF collections.
-   Support for multiple PDFs in a single chat session.
-   More sophisticated chunking and context retrieval strategies.
-   Persistent storage for PDF metadata and vector data.
-   Improved UI/UX.