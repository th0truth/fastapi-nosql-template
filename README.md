![alt logo](./images/logo.png)

## **Features**

- High-performace Python web framework for building APIs with automatic OpenAPI & Swagger & ReDoc docs. 
- Fully async using async def path operation, enabling non-blocking oprations.
- Fast and robust data validation and serialization using Pydantic library. 
- Secure authentification using OAuth2.0 standard with username / password and access token (JWT).
- NoSQL databases:
    - Integrated with MongoDB using an async pymongo (related to 4.13 version) for efficient data access.
    - Supports Redis caching using async aioredis. 
- Seamless containerzation using Docker / Docker compose.
- Environment configuration.

# **Installation**

The current recommend way to install unify is from source.

## From source

```bash
git clone https://github.com/th0truth/fastapi-nosql-template.git
cd fastapi-nosql-template
```

## Requirements

- [Python +3.11](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-started/get-docker/)

# Configure

You must rename .env.example to .env and fill in your required secrets and configuration values.

## **Usage**

If you have installed `bash`.

```bash
bash scripts/build.sh

bash scripts/run.sh 
```

Alternative way:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

uv sync

docker compose up # --build
```

## **Docs**

    # Swagger UI:
    - http://localhost/docs

    # ReDoc UI:
    - http://localhost/redoc
