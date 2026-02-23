## Project Title: "The Infrastructure Sandbox"

**Objective:** A dual-service architecture designed to demonstrate mastery of Python's asynchronous ecosystem and distributed systems.

### 1. Architectural Overview

We will split this into two distinct microservices to justify the use of a message broker and distributed caching.

* **Service A (The Producer/Gateway):** Built with **FastAPI**. This handles incoming requests, writes to the primary DB via **SQLAlchemy (Async)**, and offloads heavy or background tasks to the broker.
* **Service B (The Worker/Consumer):** A dedicated worker service that listens to **RabbitMQ**. It processes data and updates a shared or dedicated state.
* **Admin Panel:** A separate **Django** instance. Since Django excels at ORM-based interfaces, it will sit on top of your existing Postgres/MySQL database solely for data visualization and management.

### 2. The Core Tech Stack & Integration

| Technology     | Role              | Implementation Detail                                              |
| -------------- | ----------------- | ------------------------------------------------------------------ |
| **FastAPI**    | API Layer         | Utilizing `AsyncSession` for non-blocking DB calls.                |
| **Django**     | Admin/Internal    | Using `inspectdb` or shared models to provide UI for FastAPI data. |
| **SQLAlchemy** | ORM               | Version 2.0+ syntax with `asyncio` engine.                         |
| **Alembic**    | Migrations        | Handles schema evolution for the SQLAlchemy models.                |
| **RabbitMQ**   | Message Broker    | Handles inter-service communication (e.g., Task Queues).           |
| **Redis**      | Caching/State     | Used for fast lookups or as a result backend.                      |
| **Docker**     | Containerization  | Multi-stage builds to keep images slim.                            |

---

### 3. AWS Integration Strategy (Thinking Ahead)

To avoid massive refactoring later, we should design with "Cloud Native" principles in mind. Here is how your local stack maps to AWS services:

* **Database:** Locally you'll use Postgres in Docker; in AWS, this becomes **RDS**. Stick to standard environment variables for connection strings.
* **Message Broker:** RabbitMQ can be swapped for **Amazon MQ** or **SQS**. Using an abstraction library (like `TaskIQ` or `Celery`) makes this swap painless.
* **Storage:** If you plan on handling files, use a standard S3-compatible interface (like **MinIO** locally) so the code never knows the difference.
* **Deployment:** Docker Compose is your local orchestrator, but we’ll structure the `Dockerfile` so it’s ready for **AWS ECS (Fargate)** or **EKS**.

---

### 4. Immediate Development Roadmap

1. **Phase 1: The Docker Foundation**
* Create a `docker-compose.yml` defining Postgres, Redis, and RabbitMQ.
* Set up the FastAPI boilerplate with a basic health check.


2. **Phase 2: Data Persistence**
* Initialize Alembic.
* Create a dummy "Event" model in SQLAlchemy and run your first migration.


3. **Phase 3: The Async Loop**
* Implement a POST endpoint in FastAPI that pushes a message to RabbitMQ.
* Build the second microservice to consume that message and update Redis.


4. **Phase 4: The Admin View**
* Spin up Django and point it at the Postgres DB created by SQLAlchemy to "see" your data.