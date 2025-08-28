# Dockerfile for a FastAPI application with a lightweight image
FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends gcc python3-dev && \
  rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTE=1

ENV UV_LINK_MODE=copy

# Work directory
WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY ./pyproject.toml ./uv.lock /app/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
--mount=type=bind,source=uv.lock,target=uv.lock \
--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
uv sync --frozen --no-install-project --no-dev

# Copy the project into the image
COPY ./src/app /app/     
COPY .env /app/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]