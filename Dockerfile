FROM python:3.12-slim-bookworm

# Install uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation for faster startups
ENV UV_COMPILE_BYTECODE=1
# Prevent uv from looking for a generic Python installation outside the container
ENV UV_LINK_MODE=copy

# Install dependencies first (for caching)
# We copy only the lock and toml files to avoid re-installing on code changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the rest of the application code
COPY . .

# Final sync to include the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Place the virtualenv on the PATH so we can run 'uvicorn', 'python', etc. directly
ENV PATH="/app/.venv/bin:$PATH"

# Default command (overridden by docker-compose)
CMD ["python"]