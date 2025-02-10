# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to non-interactive mode (prevents prompts during installation)
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install dependencies (including Python and PostgreSQL dev libs)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libpq-dev \
    libreoffice \
    && apt-get clean

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt (if exists) into the container
COPY requirements.txt .

# Install Python dependencies if requirements.txt is provided
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

# Install python-dotenv to load environment variables from .env file
RUN pip3 install python-dotenv

# Create the output directory
RUN mkdir -p /app/output

# Copy the rest of the application code into the container
COPY . .

# Copy the .env file into the container
COPY .env .

# Command to run the Python app and ensure the container exits after execution
CMD ["sh", "-c", "python3 src/main.py && exit 0"]

