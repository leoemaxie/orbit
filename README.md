# Orbit

Goal → Interpret → Discover → Retrieve → Extract → Validate → Store → Verify → (Schedule)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in: OPENROUTER_API_KEY, BRIGHTDATA_API_KEY, BRIGHTDATA_ZONE, SERPAPI_API_KEY, DATABASE_URL
```

Postgres locally (or swap DATABASE_URL for a hosted instance):
```bash
docker run --name orbit-pg -e POSTGRES_USER=orbit -e POSTGRES_PASSWORD=orbit -e POSTGRES_DB=orbit -p 5432:5432 -d postgres:16
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

## Flow

1. `POST /api/automations` with `{"goal": "Every day at 8AM, find the cheapest PS5 Slim from Nigerian retailers and alert me if price drops below 400000 NGN"}`
   → returns the interpreted spec + automation id.
2. `POST /api/automations/{id}/run`
   → runs the full pipeline synchronously right now, returns the Run with results.
3. `GET /api/automations/{id}/runs`
   → execution history for that automation.
