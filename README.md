# AWS Lambda-Inspired Serverless Runtime

A lightweight serverless execution platform inspired by **AWS Lambda** that enables users to register and execute Python functions inside isolated Docker containers. The platform supports **cold execution**, **warm container reuse**, and **secure sandboxed execution using gVisor (`runsc`)**, while collecting runtime metrics such as execution time, CPU usage, and memory consumption.

---

# Features

* Register, retrieve, update, list, and delete serverless functions
* Execute Python functions using multiple runtime modes:

  * **Docker (`runc`)** – Creates a fresh container for every invocation (Cold Start)
  * **Docker Warm Pool** – Reuses pre-started containers to reduce startup latency
  * **gVisor (`runsc`)** – Executes functions inside a secure sandbox
* Automatic warm container initialization during server startup
* Collects runtime metrics:

  * Execution time
  * CPU usage
  * Memory usage
  * Error information
* SQLite-based metrics storage
* REST APIs built with FastAPI
* Interactive API documentation using Swagger UI

---

# Architecture

```text
                           +----------------------+
                           |       Client         |
                           |   REST API Request   |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           |   FastAPI Backend    |
                           |      (main.py)       |
                           +----------+-----------+
                                      |
                           +----------+-----------+
                           | Function Routes/API  |
                           | Register & Execute   |
                           +----------+-----------+
                                      |
                +---------------------+----------------------+
                |                     |                      |
                |                     |                      |
                v                     v                      v
        +---------------+     +---------------+     +----------------+
        | Docker (runc) |     | Warm Pool     |     | gVisor(runsc)  |
        | Cold Start    |     | Reuse         |     | Secure Sandbox |
        +-------+-------+     +-------+-------+     +-------+--------+
                \                   |                     /
                 \                  |                    /
                  +-----------------+-------------------+
                                    |
                                    v
                      +-------------------------------+
                      |     Execution Engine          |
                      | Executes User Function        |
                      +---------------+---------------+
                                      |
                         Collect Runtime Metrics
                   (Duration • CPU • Memory • Errors)
                                      |
                                      v
                        +----------------------------+
                        |     SQLite Database        |
                        |      (metrics.db)          |
                        +---------------+------------+
                                        |
                                        v
                              JSON Response
```

---

# Project Structure

```text
.
├── backend
│   ├── main.py
│   ├── models
│   │   ├── database.py
│   │   └── function_model.py
│   ├── routes
│   │   └── function_routes.py
│   ├── services
│   │   └── execution_engine.py
│   ├── tests
│   │   └── test_api.py
│   ├── utils
│   │   ├── container_pool.py
│   │   ├── execution_engine.py
│   │   ├── metrics.py
│   │   └── metrics_db.py
│   ├── requirements.txt
│   └── main.py
│
├── docker
│   └── python_runtime
│       ├── Dockerfile
│       └── function.py
│
├── frontend
│   └── app.py
│
├── tests
│   └── test_execution.py
│
├── metrics.db
├── .gitignore
└── README.md
```

---

# Tech Stack

| Component          | Technology       |
| ------------------ | ---------------- |
| Backend            | FastAPI          |
| Language           | Python           |
| Containerization   | Docker           |
| Secure Runtime     | gVisor (`runsc`) |
| Database           | SQLite           |
| Metrics Monitoring | psutil           |
| Validation         | Pydantic         |
| API Documentation  | Swagger UI       |

---

# API Endpoints

| Method | Endpoint                     | Description                     |
| ------ | ---------------------------- | ------------------------------- |
| GET    | `/`                          | Health Check                    |
| POST   | `/functions/register`        | Register a function             |
| POST   | `/functions/execute`         | Execute a function              |
| GET    | `/functions/get/{name}`      | Retrieve function metadata      |
| GET    | `/functions/list`            | List all registered functions   |
| PUT    | `/functions/update/{name}`   | Update function metadata        |
| DELETE | `/functions/delete/{name}`   | Delete a function               |
| GET    | `/functions/metrics/{name}`  | Retrieve metrics for a function |
| GET    | `/functions/runtime-metrics` | Retrieve runtime metrics        |

---

# Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Build the Docker runtime image

```bash
docker build -t python-lambda-runtime docker/python_runtime
```

### 5. (Optional) Configure gVisor

Ensure Docker recognizes the `runsc` runtime.

```bash
docker info
```

Expected output:

```text
Runtimes:
runc
runsc
```

### 6. Start Docker Desktop

Ensure Docker is running before starting the application.

### 7. Start the FastAPI server

```bash
cd backend
uvicorn main:app --reload
```

The application will be available at:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

---

# Execution Flow

1. The client sends a request to execute a function.
2. FastAPI validates the request and selects the requested runtime.
3. The execution engine executes the function using:

   * Docker (`runc`)
   * Warm Docker Container
   * gVisor (`runsc`)
4. Runtime metrics are collected.
5. Metrics are stored in SQLite.
6. The execution output and metrics are returned to the client.

---
---

# License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
