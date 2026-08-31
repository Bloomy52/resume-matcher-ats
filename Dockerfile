# syntax=docker/dockerfile:1.7
FROM python:3.14-slim-trixie
LABEL "author"="Louie Bloomberg"

# Copy the uv binary directly from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy lock + project metadata first for better layer caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies from lockfile
RUN uv sync --frozen --no-install-project --no-cache

# Copy application source
COPY . .

# Resync Install
RUN uv sync --frozen --no-cache

# Ensure virtualenv binaries are on PATH
ENV PATH="/app/.venv/bin:${PATH}"

# Run the server with Gunicorn, binding to all interfaces on port 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]