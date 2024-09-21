# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install celery

# Copy the entire project to the working directory
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the port on which the app will run
EXPOSE 8000

# Run migrations and start the Django development server
CMD ["celery","-A","lms", "worker", "--loglevel=info","python", "manage.py", "runserver", "0.0.0.0:8000"]
