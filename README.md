<div align="center">

<img src="./images/logo.png" width="450" alt="fastapi-nosql logo">

# ⚡ FastAPI NoSQL Template
**The high-performance, minimalist backbone for NoSQL-native applications.**

[![Coverage](https://img.shields.io/badge/coverage-100%25-00D100?style=for-the-badge&logo=pytest)](https://github.com/th0truth/fastapi-nosql-template)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

[**Features**](#-features) • [**Speedrun**](#-speedrun) • [**The Stack**](#-the-stack) • [**GraphQL**](#-graphql-playground) • [**Contributing**](CONTRIBUTING.md)

</div>

---

## 🌪️ Philosophy
Most templates are bloated. **FastAPI-NoSQL** is built for developers who care about the metal. It’s focused, strictly type-safe, and asynchronous from the ground up. Zero ORM overhead, just raw NoSQL power and clean abstractions. 

> "If it's not async, it's not ready for the future."

---

## 🚀 Features

### **🔥 Core Engine**
*   **Fully Async**: Non-blocking I/O across FastAPI, Motor (MongoDB), and Redis.
*   **Pydantic v2**: Lightning-fast data validation and serialization.
*   **Versioned APIs**: Native support for `/v1` and `/v2` routing out of the box.
*   **Hybrid Power**: Simultaneous support for **REST** and **GraphQL (Strawberry)**.

### **🛡️ Security & Auth**
*   **Asymmetric JWT**: RS256 token signing with auto-generated RSA keypairs.
*   **Scoped RBAC**: Fine-grained permissions (Admin, Seller, Customer).
*   **Rate Limiting**: Dynamic, Redis-backed protection via SlowAPI.

### **💾 Data & Management**
*   **Atlas Ready**: Intelligent URI construction for local or MongoDB Atlas (SRV).
*   **Admin Dashboard**: Real-time analytics for users, products, and categories.
*   **Role Migration**: Native logic to migrate users between roles and collections.

### **🛠️ Ops & Observability**
*   **Prometheus Ready**: Built-in `/metrics` endpoint and structured JSON logging.
*   **100% Coverage**: Exhuastive test suite with full MongoDB and Redis mocking.
*   **Nginx Gateway**: Production-ready container orchestration.

---

## 🕹️ Speedrun

```bash
# 1. Clone the power
git clone https://github.com/th0truth/fastapi-nosql-template.git && cd fastapi-nosql-template

# 2. Inject environment
cp .env.example .env

# 3. Ignite
docker compose up --build
```

### ⌨️ Local Workflow
| Command | Action |
| :--- | :--- |
| `bash scripts/build.sh` | Build optimized Docker images |
| `bash scripts/run.sh` | Launch the full stack |
| `bash scripts/clean.sh` | Wipe containers, networks, and volumes |

---

## 🏗️ The Stack

| Layer | Technology |
| :--- | :--- |
| **Logic** | FastAPI + Python 3.11+ |
| **Persistence** | MongoDB + Motor (Async) |
| **Cache / Limit** | Redis + aioredis |
| **GraphQL** | Strawberry GraphQL |
| **Metrics** | Prometheus |
| **Gateway** | Nginx |

---

## 🧬 GraphQL Playground
Fetch users and products in a single high-speed request at `/graphql`.

```graphql
query {
  user(username: "admin") {
    username
    email
    role
  }
  products(category: "electronics") {
    title
    brand
    price
  }
}
```

---

## 📂 Architecture
```text
.
├── compose.yaml
├── Dockerfile
├── images
│   └── logo.png
├── LICENSE
├── nginx
│   └── default.conf
├── prometheus.yaml
├── pyproject.toml
├── pytest.ini
├── README.md
├── scripts
│   ├── build.sh
│   ├── clean.sh
│   └── run.sh
├── src
│   ├── app
│   │   ├── api
│   │   │   ├── api.py
│   │   │   ├── dependencies.py
│   │   │   ├── graphql
│   │   │   │   ├── graphql.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── resolvers.py
│   │   │   ├── __init__.py
│   │   │   ├── v1
│   │   │   │   ├── api_v1_router.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── routers
│   │   │   └── v2
│   │   │       ├── api_v2_router.py
│   │   │       ├── __init__.py
│   │   │       └── routers
│   │   ├── core
│   │   │   ├── config.py
│   │   │   ├── database
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mongo.py
│   │   │   │   └── redis.py
│   │   │   ├── errors
│   │   │   │   ├── __init__.py
│   │   │   │   └── limiter.py
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   ├── middleware
│   │   │   │   ├── __init__.py
│   │   │   │   └── limiter.py
│   │   │   ├── schemas
│   │   │   │   ├── admin.py
│   │   │   │   ├── customers.py
│   │   │   │   ├── graphql.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── products.py
│   │   │   │   ├── sellers.py
│   │   │   │   ├── student.py
│   │   │   │   ├── token.py
│   │   │   │   ├── user.py
│   │   │   │   └── utils.py
│   │   │   ├── security
│   │   │   │   ├── __init__.py
│   │   │   │   ├── jwt.py
│   │   │   │   └── utils.py
│   │   │   └── services
│   │   │       ├── __init__.py
│   │   │       └── oauth
│   │   ├── crud
│   │   │   ├── base_crud.py
│   │   │   ├── __init__.py
│   │   │   ├── product_crud.py
│   │   │   └── user_crud.py
│   │   ├── __init__.py
│   │   └── main.py
│   └── tests
│       ├── conftest.py
│       └── routes
│           ├── test_admin.py
│           ├── test_auth.py
│           ├── test_customers.py
│           ├── test_graphql.py
│           ├── test_health.py
│           ├── test_products.py
│           ├── test_sellers.py
│           ├── test_user.py
│           └── test_users.py
├── tests
└── uv.lock
```

---

<div align="center">

**Built for developers who ship fast.**  
⭐ **Star this repo if it helps your next project!**

</div>