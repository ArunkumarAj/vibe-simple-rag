# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend and frontend directories into the container at /app
COPY ./backend /app/backend
COPY ./frontend /app/frontend
# If you have other essential top-level directories that were inside rag_app, copy them too.
# For example, if tmp was versioned and essential at build time (usually not):
# COPY ./tmp /app/tmp

# Set the Django settings module environment variable
# Assumes manage.py is in /app/backend/ and rag_project is a subdir of backend
ENV DJANGO_SETTINGS_MODULE=rag_project.settings

# Expose port 8000 to the outside world
EXPOSE 8000

# Set the working directory to the backend app
WORKDIR /app/backend

# Run Django migrations
RUN python manage.py migrate

# Command to run the application
# For development, using Django's runserver. 
# For production, consider using Gunicorn or a similar WSGI server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]