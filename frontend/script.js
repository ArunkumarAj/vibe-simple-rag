document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const pdfFile = document.getElementById('pdf-file');
    const uploadStatus = document.getElementById('upload-status');

    const questionInput = document.getElementById('question-input');
    const askButton = document.getElementById('ask-button');
    const chatHistory = document.getElementById('chat-history');

    let currentPdfId = null; // To store the ID or reference of the uploaded PDF

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        uploadStatus.textContent = 'Uploading...';
        const formData = new FormData();
        formData.append('pdf_file', pdfFile.files[0]);

        try {
            const response = await fetch('/api/upload_pdf/', { // Adjust API endpoint as needed
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                currentPdfId = result.pdf_id; // Assuming the backend returns an identifier for the PDF
                uploadStatus.textContent = `Successfully uploaded: ${pdfFile.files[0].name} (ID: ${currentPdfId})`;
                pdfFile.value = ''; // Clear the file input
            } else {
                const errorData = await response.json();
                uploadStatus.textContent = `Upload failed: ${errorData.error || response.statusText}`;
            }
        } catch (error) {
            console.error('Upload error:', error);
            uploadStatus.textContent = 'Upload failed. See console for details.';
        }
    });

    askButton.addEventListener('click', async () => {
        const question = questionInput.value.trim();
        if (!question) {
            alert('Please enter a question.');
            return;
        }

        if (!currentPdfId) {
            alert('Please upload a PDF first.');
            return;
        }

        appendMessage(question, 'user-message');
        questionInput.value = ''; // Clear input

        try {
            const response = await fetch('/api/chat/', { // Adjust API endpoint as needed
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    question: question,
                    pdf_id: currentPdfId // Send PDF identifier if needed by backend for context
                }),
            });

            if (response.ok) {
                const result = await response.json();
                appendMessage(result.answer, 'bot-message');
            } else {
                const errorData = await response.json();
                appendMessage(`Error: ${errorData.error || response.statusText}`, 'bot-message');
            }
        } catch (error) {
            console.error('Chat error:', error);
            appendMessage('Failed to get answer. See console for details.', 'bot-message');
        }
    });

    function appendMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.textContent = text;
        messageDiv.className = className;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to the bottom
    }
});