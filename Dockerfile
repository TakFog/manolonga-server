# Use an official Python runtime as the base image
FROM python:3.13-slim
LABEL org.opencontainers.image.source https://github.com/TakFog/manolonga-server

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY server.py .

# Command to run the Flask app
CMD ["python", "server.py"]
