<p align="center">
  <img src="./images/logo.png" width="300" alt="fastapi-nosql">
</p>

<p align="center">
  <b>FastAPI-NoSQL</b>: The high-performance, minimalist backbone for NoSQL-native applications.
</p>

<p align="center">
  <a href="https://github.com/th0truth/fastapi-nosql-template/actions"><img src="https://img.shields.io/badge/coverage-100%25-brightgreen" alt="Coverage"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi" alt="FastAPI"></a>
  <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white" alt="MongoDB"></a>
  <a href="https://redis.io/"><img src="https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white" alt="Redis"></a>
  <a href="https://strawberry.rocks/"><img src="https://img.shields.io/badge/GraphQL-E10098?style=flat&logo=graphql&logoColor=white" alt="GraphQL"></a>
</p>

---

### **Philosophy**
Most templates are bloated. **FastAPI-NoSQL** is built for speed and horizontal scalability. Focused, type-safe, and asynchronous from the ground up. No ORM overhead, just raw power and clean abstractions.

---

### **Features**

#### **🚀 Core Engine**
*   **100% Asynchronous**: Leverages `async def` for non-blocking I/O across FastAPI, Motor (MongoDB), and Redis.
*   **High Performance**: Minimalist architecture designed for high throughput and low latency.
*   **Pydantic v2**: Lightning-fast data validation and serialization.
*   **API Versioning**: Built-in support for `/v1` and `/v2` routing.
*   **Hybrid API**: Native support for both **REST** and **GraphQL (Strawberry)**.

#### **🛡️ Security & Auth**
*   **OAuth2.0 Flow**: Secure authentication using username/password and Bearer tokens.
*   **JWT (RS256)**: Asymmetric token signing with auto-generated RSA keys.
*   **RBAC & Scopes**: Granular Role-Based Access Control (Admin, Seller, Customer) with permission scopes.
*   **Rate Limiting**: Dynamic, Redis-backed rate limiting (SlowAPI) to prevent abuse.

#### **💾 Data Layer**
*   **MongoDB (Motor)**: Async driver for MongoDB with optimized CRUD abstractions.
*   **Redis Caching**: Built-in caching layer to reduce database load and improve response times.
*   **Atlas Support**: Intelligent URI construction for both local and MongoDB Atlas (SRV) clusters.

#### **👑 Admin & Management**
*   **Admin Dashboard**: Real-time statistics for users, products, and categories.
*   **Role Migration**: Native tools to migrate users between roles and collections (e.g., Customer → Seller).
*   **Initial Setup**: Dedicated `/admin/setup` endpoint for secure bootstrap.

#### **🛠️ Ops & Observability**
*   **Observability**: Integrated Prometheus metrics (`/metrics`) and structured JSON logging.
*   **Containerization**: Production-ready Docker and Docker Compose setup with Nginx gateway.
*   **Documentation**: Automatic, interactive Swagger UI, ReDoc, and GraphQL Playground.
*   **Reliability**: 100% test coverage with comprehensive MongoDB and Redis mocking.

---

### **Quick Start**

```bash
# Clone the power
git clone https://github.com/th0truth/fastapi-nosql-template.git && cd fastapi-nosql-template

# Setup environment
cp .env.example .env

# Run with one command
docker compose up --build
```

### **Bash Scripts**
For faster local workflows, use the bundled scripts:
```bash
bash scripts/build.sh   # Build Docker images
bash scripts/run.sh     # Launch the stack
bash scripts/clean.sh   # Remove containers, networks, and volumes
```

### **The Stack**
| Component | Technology |
| :--- | :--- |
| **Framework** | FastAPI (Python 3.11+) |
| **Primary DB** | MongoDB (Motor / Async) |
| **Cache/Limit** | Redis (aioredis / SlowAPI) |
| **GraphQL** | Strawberry GraphQL |
| **Metrics** | Prometheus |
| **Testing** | Pytest (100% Mocked) |
| **Gateway** | Nginx |

### **Architecture**
```text
src/app/
├── api/             # REST (v1/v2) & GraphQL Routers
├── core/            # Config, Database, Security, Schemas
├── crud/            # Optimized NoSQL operations
└── tests/           # 100% coverage suite
```

### **Contributing**
Keep it tiny. Keep it fast.

---
<p align="center">
  Built for developers who care about the metal. ⭐ Star if you ship fast.
</p>