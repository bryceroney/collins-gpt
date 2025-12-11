# Multi-stage build for Collins-GPT Flask application
# Stage 1: Build frontend assets
FROM node:20-slim AS frontend-builder

# Install pnpm
RUN npm install -g pnpm

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install frontend dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend source files
COPY frontend/ ./

# Build frontend for production
RUN pnpm run build:prod

# Stage 2: Python application
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy Python dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/
COPY main.py ./

# Copy built frontend assets from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./app/static/dist/

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV FLASK_APP=app
ENV PYTHONUNBUFFERED=1

# Cloud Run sets the PORT environment variable
# Flask will listen on 0.0.0.0:$PORT
ENV PORT=8080

# Expose the port (documentation only, Cloud Run ignores this)
EXPOSE 8080

# Use Gunicorn for production WSGI server
# --bind 0.0.0.0:$PORT - Listen on all interfaces on the port Cloud Run provides
# --workers 1 - Single worker (Cloud Run handles horizontal scaling)
# --threads 8 - Multiple threads for concurrent requests
# --timeout 0 - Disable timeout (Cloud Run handles request timeouts)
# --access-logfile - - Log access to stdout
# --error-logfile - - Log errors to stdout
CMD exec uv run gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 --access-logfile - --error-logfile - "app:create_app()"
