# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application code to container
COPY . /app/

# Install dependencies
RUN pip install -r requirements.txt

# Expose port for the app
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
