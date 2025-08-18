# Dockerfile for a FastAPI application with a lightweight image

FROM python:3.11-slim-bookworm
WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends gcc python3-dev && \
  rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy Poetry configure files to the /app
COPY ./pyproject.toml /app/

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy application files
COPY src/app /app/     
COPY .env /app/

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--reload"]