### README

## Project Overview

This project generates a report based on a sample of 100 random items from a specified contract. The report includes various analyses and is saved as a PDF file.

## Prerequisites

- Docker
- Docker Compose

## Setup

1. **Build the Docker Image:**

   ```sh
   docker build -t gsads .
   ```

2. **Run the Docker Container:**

   ```sh
   docker run --rm -it -v $(pwd)/output:/app/output gsads
   ```

## Docker Commands

- **Build the Docker Image:**

  ```sh
  docker build -t gsads .
  ```

- **Run the Docker Container:**

  ```sh
  docker run --rm -it -v $(pwd)/output:/app/output gsads
  ```

## Project Structure

- `src/main.py`: Main script to run the report generation.
- `src/utils/report.py`: Contains the `SamplePriceComp` class for generating the report.
- `Dockerfile`: Docker configuration file.
- `requirements.txt`: Python dependencies.

## Usage

 **Run the Docker Container:**

   ```sh
   docker build -t gsads . && docker run --rm -it -v $(pwd)/output:/app/output gsads
   ```

The generated PDF report will be saved in the `output` directory.
