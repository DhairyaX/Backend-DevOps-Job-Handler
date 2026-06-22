# Transaction Processing & Risk Analysis Platform

## Overview

This project is an asynchronous transaction processing system built using FastAPI, PostgreSQL, Redis, Celery, Docker, and Google Gemini.

The system accepts transaction CSV files, processes them asynchronously, performs data cleaning, detects anomalies, enriches uncategorized transactions using Gemini, generates transaction summaries, and stores all results in PostgreSQL.

The architecture is designed to separate API responsiveness from long-running processing tasks through background workers.

---

## Architecture

```text
                    +----------------+
                    |     Client     |
                    +--------+-------+
                             |
                             v
                    +----------------+
                    |    FastAPI     |
                    +--------+-------+
                             |
                             v
                    +----------------+
                    |   PostgreSQL   |
                    |      Jobs      |
                    +--------+-------+
                             |
                             v
                    +----------------+
                    |     Redis      |
                    +--------+-------+
                             |
                             v
                    +----------------+
                    | Celery Worker  |
                    +--------+-------+
                             |
          +------------------+------------------+
          |                                     |
          v                                     v
+----------------------+       +----------------------+
| CSV Processing       |       | Google Gemini        |
| Data Cleaning        |       | Classification       |
| Anomaly Detection    |       | Summary Generation   |
+----------------------+       +----------------------+
                             |
                             v
                    +----------------+
                    |   PostgreSQL   |
                    |  Transactions  |
                    +----------------+
```

---

## Features

### CSV Upload & Job Creation

* Upload transaction CSV files
* Create processing jobs
* Track job status
* Background task execution

### Asynchronous Processing

* Redis-based task queue
* Celery workers
* Non-blocking API responses

### Data Cleaning

* Duplicate removal
* Date normalization
* Amount normalization
* Status standardization
* Missing category handling

### Anomaly Detection

#### Rule 1: Statistical Outlier Detection

Transactions are flagged when:

```text
Amount > 3 × Account Median
```

#### Rule 2: Domestic Merchant Currency Validation

Transactions are flagged when:

```text
Merchant ∈ {Swiggy, Ola, IRCTC}
AND
Currency = USD
```

### Gemini Integration

* Categorization of uncategorized transactions
* Summary generation
* Retry handling
* Graceful fallback behavior

---

## Technology Stack

| Layer            | Technology    |
| ---------------- | ------------- |
| Backend API      | FastAPI       |
| Database         | PostgreSQL    |
| ORM              | SQLAlchemy    |
| Queue            | Redis         |
| Worker           | Celery        |
| Data Processing  | Pandas        |
| AI Integration   | Google Gemini |
| Containerization | Docker        |

---

## Processing Workflow

```text
Upload CSV
    |
    v
Create Job
    |
    v
Store Job Metadata
    |
    v
Queue Task in Redis
    |
    v
Celery Worker
    |
    v
Read CSV
    |
    v
Data Cleaning
    |
    v
Anomaly Detection
    |
    v
Gemini Classification
    |
    v
Summary Generation
    |
    v
Store Results
    |
    v
Job Completed
```

---

## Database Schema

### Jobs

Stores metadata for processing jobs.

| Field           | Description        |
| --------------- | ------------------ |
| id              | Job ID             |
| filename        | Uploaded file name |
| status          | Current job status |
| row_count_raw   | Original CSV rows  |
| row_count_clean | Cleaned CSV rows   |

### Transactions

Stores processed transaction data.

| Field          | Description              |
| -------------- | ------------------------ |
| txn_id         | Transaction ID           |
| merchant       | Merchant Name            |
| amount         | Transaction Amount       |
| currency       | Transaction Currency     |
| category       | Transaction Category     |
| account_id     | Account Identifier       |
| is_anomaly     | Anomaly Flag             |
| anomaly_reason | Anomaly Reason           |
| llm_category   | Gemini Category          |
| llm_failed     | Gemini Processing Status |

### Job Summaries

Stores generated summaries.

| Field         | Description         |
| ------------- | ------------------- |
| job_id        | Related Job         |
| risk_level    | Risk Classification |
| anomaly_count | Number of Anomalies |
| narrative     | Generated Summary   |

---

## API Endpoints

| Method | Endpoint             | Description     |
| ------ | -------------------- | --------------- |
| POST   | `/jobs/upload`       | Upload CSV      |
| GET    | `/jobs`              | List Jobs       |
| GET    | `/jobs/{id}/status`  | Get Job Status  |
| GET    | `/jobs/{id}/results` | Get Job Results |
| GET    | `/health`            | Health Check    |

---

## Example API Usage

### Upload CSV

```http
POST /jobs/upload
```

Response:

```json
{
  "job_id": 9,
  "status": "pending"
}
```

### Check Status

```http
GET /jobs/9/status
```

Response:

```json
{
  "job_id": 9,
  "status": "completed"
}
```

---

## Project Structure

```text
app/
├── core/
│   ├── config.py
│   └── celery_app.py
│
├── db/
│   └── database.py
│
├── models/
│   ├── job.py
│   ├── transaction.py
│   └── job_summary.py
│
├── routers/
│   └── jobs.py
│
├── schemas/
│   └── job.py
│
├── services/
│   ├── job_service.py
│   ├── anomaly_service.py
│   ├── llm_service.py
│   └── summary_service.py
│
├── tasks.py
└── main.py

uploads/
docker-compose.yml
Dockerfile
requirements.txt
.env
```

---

## Environment Variables

Create a `.env` file:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db
POSTGRES_SERVER=db

REDIS_HOST=redis
REDIS_PORT=6379

GEMINI_API_KEY=my_api_key
```

---

## Running the Project

### Build and Start Containers

```bash
docker compose up --build
```

### Stop Containers

```bash
docker compose down
```

---

## Accessing Services

| Service    | URL                        |
| ---------- | -------------------------- |
| FastAPI    | http://localhost:8000      |
| Swagger UI | http://localhost:8000/docs |
| PostgreSQL | localhost:5433             |
| Redis      | localhost:6380             |

---

## Error Handling

### CSV Processing

* Missing file validation
* Invalid data handling
* Job failure tracking

### Gemini Processing

* Retry mechanism
* Fallback categorization
* Failure tracking via `llm_failed`

### Database Operations

* Transaction rollback
* Session cleanup
* Failure recovery

---

## Design Decisions

### Why Celery?

CSV processing, anomaly detection, and AI enrichment are long-running tasks that should not block API responses.

### Why Redis?

Redis provides a lightweight and reliable message broker for asynchronous task execution.

### Why PostgreSQL?

PostgreSQL provides strong consistency and structured storage for jobs, transactions, and summaries.

### Why Gemini?

Gemini is used to enrich transaction data through category classification and summary generation.

---

## Known Limitations

* Gemini free-tier quota limits can affect large batches of classification requests.
* Anomaly detection currently uses rule-based logic.
* No authentication layer is implemented.

---

## Future Improvements

* Batch Gemini requests
* Authentication and authorization
* Job progress tracking
* Monitoring and observability
* Automated testing
* Cloud deployment
* Advanced anomaly detection models

---

## Submission Artifacts

This repository contains:

* Source Code
* Docker Configuration
* Database Schema
* REST API
* Redis Queue Integration
* Celery Worker Integration
* Anomaly Detection Engine
* Gemini Integration
* Technical Documentation
