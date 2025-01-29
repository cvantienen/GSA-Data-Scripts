# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to non-interactive mode (prevents prompts during installation)
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install dependencies (including Python)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && apt-get clean

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt (if exists) into the container
# If you have dependencies, add your requirements file to the same directory as the Dockerfile
COPY requirements.txt .

# Install Python dependencies if requirements.txt is provided
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

# Command to run the Python app (this example assumes an app.py file exists)
CMD ["python3", "main.py"]