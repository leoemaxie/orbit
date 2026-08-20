# Orbit

> **Autonomous Goal-Driven Web Data Operations**
>
> *Set the goal. Walk away.*

Orbit is an agentic web-data automation platform that transforms natural-language objectives into reliable, recurring, and verifiable web-data workflows across **any** web domain (e.g., e-commerce, job boards, flight tracking, news, real estate, financial metrics).

---

## 🚀 Key Capabilities

- **Domain Agnostic**: Dynamic LLM-driven schema generation adapts to any entity type on the web.
- **Agent Loop**: Self-correcting orchestrator with failure diagnosis and reasoning instead of a rigid linear pipeline.
- **Verification & Provenance**: Audit trail tracking sources discovered, pages fetched, dynamic records extracted, and schema validation.
- **Automated Scheduling**: Background scheduler (APScheduler) continuously executes recurring automations.
- **Condition Evaluation & Alerts**: Condition evaluator for alerts (e.g. `min(price) < 400000`, `salary_min >= 150000`) with webhook and log dispatch.

---

## 🛠️ Architecture

```
Goal → Interpret → Plan → Discover → Retrieve → Extract → Validate → Evaluate Condition → Store → Verify → (Schedule)
```

```text
src/orbit/
├── agent/            # Goal Interpreter, Condition Evaluator, Reasoner, Orchestrator
├── api/              # FastAPI v1 REST API & WebSocket endpoints
├── config/           # Pydantic Settings
├── db/               # SQLAlchemy ORM, Engine & Sessions
├── events/           # In-process asynchronous Event Bus
├── llm/              # OpenRouter & LLM client abstraction + Prompts
├── models/           # ExecutionPlan, DynamicExtractionSchema, Pydantic Schemas
├── notifications/    # Notification Service (Webhooks & Logs)
├── pipeline/         # Pluggable Discovery, Retrieval, Extraction & Validation stages
├── scheduler/        # Background scheduler daemon for automated executions
└── app.py            # FastAPI Application Factory
```

---

## 📦 Setup & Installation

```bash
# Clone & install dependencies
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY, BRIGHTDATA_API_KEY, BRIGHTDATA_ZONE, SERPAPI_API_KEY, DATABASE_URL
```

### Run Postgres (Docker)

```bash
docker run --name orbit-pg -e POSTGRES_USER=orbit -e POSTGRES_PASSWORD=orbit -e POSTGRES_DB=orbit -p 5432:5432 -d postgres:16
```

### Start Server & Background Scheduler

```bash
uvicorn orbit.app:app --reload --port 8000
```

Interactive Docs: `http://localhost:8000/docs`

---

## 💡 Example Goals (Cross-Domain)

### 🛒 E-Commerce
```json
POST /api/v1/automations
{
  "goal": "Every day at 8AM, find the cheapest PS5 Slim from Nigerian retailers and alert me if price drops below 400000 NGN"
}
```

### 💼 Tech Jobs
```json
POST /api/v1/automations
{
  "goal": "Weekly, find remote Python backend developer jobs paying over $140,000 and notify me"
}
```

### ✈️ Flight Monitoring
```json
POST /api/v1/automations
{
  "goal": "Daily, track round-trip flights from Lagos to London in December and alert me if price < $900"
}
```

### 📰 News Monitoring
```json
POST /api/v1/automations
{
  "goal": "Every 6 hours, monitor news mentions of AI regulations across tech sites"
}
```
