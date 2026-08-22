# Orbit Core Engine

The backend execution engine, agentic reasoning pipeline, scheduler daemon, and REST API for **Orbit — Autonomous Goal-Driven Web Data Operations**.

---

## ⚡ Overview

Orbit Core is responsible for:
- **Goal Interpretation & Planning**: Translating natural-language requests into typed schemas, search queries, schedules, and condition triggers via LLMs.
- **Autonomous Discovery & Retrieval**: Utilizing multi-source discovery (SerpApi, web hints) and robust retrieval proxies (Bright Data Web Unlocker) to fetch web pages.
- **Dynamic Extraction & Validation**: Extracting structured records matching dynamic JSON schemas and validating fields, types, and anomalies.
- **Agentic Self-Correction & Reasoning**: Diagnosing discovery and extraction failures and dynamically refining strategies.
- **Condition Alerts & Event Bus**: Evaluating aggregate and scalar condition rules (`min(price) < 400000`) and dispatching events/webhooks.
- **Persistent Scheduling Daemon**: Running cron-like recurring jobs via APScheduler with full audit trails stored in PostgreSQL.

---

## 🏗️ Architecture & Module Structure

```text
core/
├── adapters/         # Pluggable outputs & notification sinks (Slack, Local Files, etc.)
├── agent/            # Goal Interpreter, Condition Evaluator, Reasoner, Orchestrator
├── api/              # FastAPI v1 router & endpoints (automations, runs, health)
├── config/           # Pydantic Settings & environment configuration
├── db/               # SQLAlchemy ORM models & session lifecycle management
├── events/           # Async in-process Event Bus & event definitions
├── llm/              # LLM client abstractions (OpenRouter) & prompt templates
├── models/           # Domain schemas, DynamicExtractionSchema, ExecutionPlan
├── notifications/    # Alerting service (Webhooks & Structured Logs)
├── pipeline/         # Discovery, Retrieval, Extraction, and Validation stages
│   ├── discovery/    # SerpApi & composite URL search
│   ├── extraction/   # LLM structured data extractor
│   ├── retrieval/    # Bright Data proxy client & link extraction
│   └── validation/   # JSONSchema validation & anomaly detection
├── scheduler/        # APScheduler recurring execution engine & cron helpers
└── app.py            # FastAPI application factory
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- PostgreSQL (local or Docker)
- API Keys:
  - [OpenRouter](https://openrouter.ai/) (LLM reasoning & extraction)
  - [Bright Data](https://brightdata.com/) (Web Unlocker proxy)
  - [SerpApi](https://serpapi.com/) (Google search discovery)

### 2. Installation

From the project root:

```bash
# Navigate to core or create a virtual environment
python -m venv core/venv

# Activate virtual environment
# Windows (PowerShell):
.\core\venv\Scripts\Activate.ps1
# macOS/Linux:
source core/venv/bin/activate

# Install core package and dependencies
pip install -e ".[dev]"
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```ini
# LLM
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Web Data & Discovery
BRIGHTDATA_API_KEY=...
BRIGHTDATA_ZONE=your_unlocker_zone
SERPAPI_API_KEY=...

# Database
DATABASE_URL=postgresql+psycopg2://orbit:orbit@localhost:5432/orbit

# Scheduler & Alerts
ENABLE_SCHEDULER=true
DEFAULT_WEBHOOK_URL=https://webhook.site/...
```

### 4. Database Setup

Start PostgreSQL via Docker:

```bash
docker run --name orbit-pg -e POSTGRES_USER=orbit -e POSTGRES_PASSWORD=orbit -e POSTGRES_DB=orbit -p 5432:5432 -d postgres:16
```

### 5. Run the Server

```bash
uvicorn core.app:app --reload --port 8000
```

- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Health Probe**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 📡 REST API Reference

### 1. Create an Automation

Submit a natural-language goal to be parsed into an autonomous execution plan:

`POST /api/v1/automations`

```json
{
  "goal": "Every day at 8 AM, find the cheapest PlayStation 5 Slim from Nigerian retailers and alert me if price drops below 400000 NGN"
}
```

**Response:**
```json
{
  "id": "7b8c9d01-e234-4567-89ab-cdef01234567",
  "raw_goal": "Every day at 8 AM, find the cheapest PlayStation 5 Slim from Nigerian retailers and alert me if price drops below 400000 NGN",
  "plan": {
    "objective": "Find cheapest PS5 Slim prices in Nigeria daily and alert if < 400,000 NGN",
    "domain": "ecommerce",
    "search_query": "PlayStation 5 Slim price buy Nigeria",
    "source_hints": ["jumia.com.ng", "konga.com", "slot.ng"],
    "geography": "Nigeria",
    "country_code": "ng",
    "extraction_schema": {
      "entity_name": "product",
      "fields": [
        {"name": "product", "type": "string", "required": true},
        {"name": "price", "type": "number", "required": true},
        {"name": "currency", "type": "string", "required": true},
        {"name": "availability", "type": "string", "enum_values": ["in_stock", "out_of_stock"]},
        {"name": "seller", "type": "string", "required": false}
      ]
    },
    "frequency": "daily",
    "schedule_time": "08:00",
    "timezone": "Africa/Lagos",
    "condition": "min(price) < 400000"
  },
  "active": true,
  "created_at": "2026-08-20T23:00:00Z"
}
```

### 2. Trigger an Immediate Run

`POST /api/v1/automations/{automation_id}/run`

**Response:**
```json
{
  "id": "run-456",
  "status": "verified",
  "sources_found": ["https://konga.com/p/ps5-slim", "https://jumia.com.ng/ps5"],
  "pages_retrieved": ["https://konga.com/p/ps5-slim", "https://jumia.com.ng/ps5"],
  "extracted_count": 2,
  "validated_count": 2,
  "condition_matched": true,
  "condition_message": "Aggregation min(price) = 385000 vs target < 400000 -> Matched: True",
  "results": [
    {
      "url": "https://konga.com/p/ps5-slim",
      "data": {
        "product": "Sony PlayStation 5 Slim 1TB",
        "price": 385000,
        "currency": "NGN",
        "availability": "in_stock",
        "seller": "Official Sony Store"
      },
      "valid": true
    }
  ]
}
```

### 3. List Automations & Runs

- `GET /api/v1/automations` — List all registered automations.
- `GET /api/v1/automations/{id}` — Get single automation plan details.
- `GET /api/v1/automations/{id}/runs` — Get run history for an automation.
- `GET /api/v1/runs/{id}` — Get complete run details, results, and audit trails.
- `GET /api/v1/runs/{id}/results` — Export raw/filtered extracted records.

---

## 🧪 Testing

Run test suites using pytest:

```bash
# Run unit and integration tests
pytest

# Run with verbose output
pytest -v
```
