# Orbit 🛰️

**Autonomous Goal-Driven Web Data Operations**

> *"Set the goal. Walk away."*

Orbit is an agentic web-data automation platform. Instead of manually designing web scrapers, writing selectors, or configuring brittle scraping pipelines, you define what you want in plain English. Orbit autonomously interprets the goal, plans the execution, discovers sources across the web, extracts structured data, self-corrects on errors, evaluates conditions, and runs on a recurring schedule.

---

## ⚡ Key Highlights

- 🌐 **Domain Agnostic**: Works on any web entity (e-commerce, job boards, flights, news, financial data, real estate) via dynamic, LLM-generated extraction schemas.
- 🤖 **Agentic Self-Correction**: When discovery or retrieval fails, the agent diagnoses the issue and adjusts its query or strategy autonomously.
- ⏰ **Automated Scheduling**: Set recurring intervals (`hourly`, `daily`, `weekly`, `monthly`) and let the background daemon execute without manual intervention.
- 🎯 **Condition Alerts**: Evaluates expressions like `min(price) < 400000` or `salary >= 150000` and dispatches webhook/log notifications.
- 🔍 **Full Provenance & Verification**: Every run logs discovered URLs, retrieved pages, extracted records, schema validations, and agent decision trails.

---

## 🔄 How It Works

```mermaid
graph LR
    A["Natural Language Goal"] --> B["1. Interpret & Plan"]
    B --> C["2. Discover Sources"]
    C --> D["3. Retrieve Pages"]
    D --> E["4. Extract Schema"]
    E --> F["5. Validate Data"]
    F --> G["6. Evaluate Condition"]
    G --> H["7. Store & Verify"]
    H --> I["8. Schedule Next Run"]
```

---

## 🚀 Quickstart

### 1. Prerequisites

- Python 3.10+
- PostgreSQL (or Docker)
- API Keys:
  - [OpenRouter](https://openrouter.ai/) (LLM reasoning & extraction)
  - [Bright Data](https://brightdata.com/) (Web Unlocker proxy & markdown conversion)
  - [SerpApi](https://serpapi.com/) (Google search discovery)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/leoemaxie/orbit.git
cd orbit

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 3. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

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

### 4. Start PostgreSQL (Docker)

```bash
docker run --name orbit-pg -e POSTGRES_USER=orbit -e POSTGRES_PASSWORD=orbit -e POSTGRES_DB=orbit -p 5432:5432 -d postgres:16
```

### 5. Launch Orbit

```bash
uvicorn orbit.app:app --reload --port 8000
```

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 📡 API Usage & Examples

### 1. Create an Automation

Submit any natural-language goal:

```http
POST /api/v1/automations
Content-Type: application/json

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

```http
POST /api/v1/automations/{automation_id}/run
```

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

### 3. More Cross-Domain Examples

| Domain | Example Goal |
|--------|--------------|
| **Job Market** | `"Weekly, find remote Senior Python developer jobs paying over $150,000 and alert me"` |
| **Travel** | `"Daily, monitor round-trip flights from Lagos to London in December under $800"` |
| **News** | `"Every 6 hours, monitor news mentions of 'AI regulation' across top tech publications"` |
| **Real Estate** | `"Find 2-bedroom apartments for rent in Lekki Phase 1 under 4,000,000 NGN"` |

---

## 📁 Project Structure

```text
src/orbit/
├── agent/            # Goal Interpreter, Condition Evaluator, Reasoner, Orchestrator
├── api/              # FastAPI v1 routes (automations, runs, health)
├── config/           # Pydantic Settings
├── db/               # SQLAlchemy models & session factory
├── events/           # Asynchronous in-process Event Bus
├── llm/              # LLM client protocols, OpenRouter client, prompt templates
├── models/           # Domain schemas, DynamicExtractionSchema, ExecutionPlan
├── notifications/    # Alerting service (Webhooks & Structured Logs)
├── pipeline/         # Pluggable Discovery, Retrieval, Extraction, and Validation
├── scheduler/        # APScheduler recurring job engine
└── app.py            # FastAPI application factory
```

---

## 🧪 Testing

Run unit and integration tests:

```bash
pytest
```

---

## 📄 License

MIT License. See `LICENSE` for details.
