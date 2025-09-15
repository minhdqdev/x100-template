# Technical Guideline

## 1. Introduction
This document helps solutions architects and developers understand the system's design and make informed decisions during implementation. Unless there are reasons to deviate, the guidelines in this document should be followed.

## 2. Architecture Overview
- Prefer simple architectures (monolithic, SOA) rather than complex architectures (microservices, event-driven).


## Code base management
- Prefer Git submodules for multi-repo management:
    ```bash
    git submodule add <repository-url>
    git submodule update --init --recursive
    ```


## 3. Design Decisions
Backend:
- Prefer Python for backend than Node.js, Java, etc.
- Prefer Django than Flask, FastAPI, etc.
- Prefer uvicorn than other ASGI servers (e.g., Daphne, Hypercorn, etc.).
- Prefer `uv` for package management than `pip`.
- Prefer PostgreSQL than MySQL, SQLite, etc.
- Prefer Redis than Memcached, etc.

Frontend:
- Prefer Next.js than other React frameworks (e.g., Create React App, Gatsby, etc.).


Deployment:
- Prefer Docker for containerization than other solutions (e.g., Vagrant, manual setup, etc.).
- Prefer docker compose than other orchestration tools (e.g., Kubernetes, Swarm, etc.).


Example project structure:
```
.
├── backend/
│   ├── .git
│   ├── deploys/
│   │   ├── docker-compose.yml
│   │   └── Dockerfile
│   ├── app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── .git
│   ├── deploys/
│   │   ├── docker-compose.yml
│   │   └── Dockerfile
│   ├── src
│   ├── package.json
│   └── Dockerfile
```



## 4. API Design
- Prefer OpenAPI Specification (OAS) for API documentation.
- Use API versioning to manage changes.
- Include examples and descriptions for all endpoints.
- Prefer REST API principles (statelessness, resource-based URLs, etc.).
- Prefer HTTP error codes rather than custom error codes.

## 5. Database Design
- Prefer relational databases (PostgreSQL, MySQL) for structured data.
- Prefer NoSQL databases (MongoDB, DynamoDB) for unstructured data.


## 6. Security Considerations
- Prefer bearer token authentication for APIs.
- Prefer HTTPS for all communications between clients and servers.
- Prefer input validation and sanitization to prevent injection attacks.
- Prefer using established libraries and frameworks for security features.

## 7. Performance Considerations
- Prefer caching strategies (e.g., Redis, Memcached) to improve response times.
- Prefer asynchronous processing (e.g., Celery, RabbitMQ) for long-running tasks.

## 8. Deployment Strategy
- Prefer canary deployments for rolling out changes.
- Prefer deployment automation (e.g., GitHub Actions, GitLab CI/CD) for consistent and repeatable deployments.


