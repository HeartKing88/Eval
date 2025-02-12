# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip to the latest version
RUN pip3 install -U pip

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -U -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Set the environment variable for Python to run in production mode
ENV PYTHONUNBUFFERED 1

# Make sure the start script is executable
RUN chmod +x start

# Expose the port that the app will run on (usually 5000 for Flask or Django)
EXPOSE 5000

# Run the start script using bash
CMD ["bash", "start"]
