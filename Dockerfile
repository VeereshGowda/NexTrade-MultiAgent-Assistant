# NexTrade Multi-Agent Trading System - Docker Configuration
# Production-ready containerized deployment

# Use official Python runtime as base image
FROM python:3.12-slim

# Set metadata
LABEL description="NexTrade Multi-Agent Trading System"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./
COPY README.md ./

# Create virtual environment and install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e .

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY streamlit_app.py ./
COPY langgraph.json ./

# Create necessary directories
RUN mkdir -p data logs

# Expose ports
# 8000: FastAPI backend
# 8501: Streamlit UI
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create non-root user for security
RUN useradd -m -u 1000 nextrade && \
    chown -R nextrade:nextrade /app
USER nextrade

# Default command (can be overridden)
# Run both FastAPI backend and Streamlit UI
CMD ["/bin/bash", "-c", ". .venv/bin/activate && uvicorn src.api:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]

# Alternative commands for specific modes:
# FastAPI only: CMD [".venv/bin/uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
# Streamlit only: CMD [".venv/bin/streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
