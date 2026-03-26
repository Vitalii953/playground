FROM python:3.13-slim-bookworm


WORKDIR /app

# Copy dependency manifests for layer caching.
COPY pyproject.toml poetry.lock* /app/

# Install dependencies via pip using pyproject metadata.
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install .

# Copy app code
COPY . /app

# Ensure CLI commands available.
ENV PATH="/usr/local/bin:$PATH"

# Default command (overridden by docker-compose)
CMD ["python"]