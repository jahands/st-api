# Multi-stage build for Railway.app deployment
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --compile-bytecode

# Production stage
FROM python:3.11-slim

# Install uv in production stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY model/ ./model/

# Make sure we use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Set environment variables for Railway
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose the port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:$PORT/health')" || exit 1

# Run the FastAPI application
CMD ["uvicorn", "src.railway_main:app", "--host", "0.0.0.0", "--port", "8000"]
