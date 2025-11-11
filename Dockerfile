# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Set the entry point to the MCP server
ENTRYPOINT ["python", "/app/src/tooner/server.py"]

# Metadata
LABEL maintainer="your-email@example.com"
LABEL description="Tooner MCP Server - Token compression using Toon format"
LABEL version="0.1.0"
