# Orbit 🛰️

**Autonomous Goal-Driven Web Data Operations**

> *"Set the goal. Walk away."*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Go Version](https://img.shields.io/badge/Go-1.23+-00ADD8?logo=go)](cli/)
[![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](core/)

Orbit is an autonomous, agentic web-data operations platform. Instead of hand-crafting brittle web scrapers, reverse-engineering dynamic page selectors, or constantly maintaining bespoke crawling pipelines, you simply specify what data you need in plain natural language. 

Orbit interprets your objective, derives structured extraction schemas, discovers relevant web sources, retrieves content via resilient proxy infrastructure, extracts typed records, performs anomaly and schema validation, evaluates condition triggers, and runs automatically on a recurring schedule with end-to-end provenance.

---

## 🌟 Core Capabilities

- 🗣️ **Natural-Language Goal Interpretation**: Provide goals like *"Every morning at 8 AM, find the cheapest flights from Lagos to London in December and alert me if under $800"*. Orbit synthesizes domain plans, extraction schemas, and search queries automatically.
- 🌐 **Universal & Domain Agnostic**: Operates across e-commerce, real estate, job listings, travel, financial data, and news without writing domain-specific scrapers.
- 🤖 **Agentic Self-Correction**: When discovery yields empty results or page structures change, an autonomous reasoner diagnoses the issue and refines search queries or retrieval strategies on the fly.
- 🛡️ **Verification & Anomaly Detection**: Every extracted dataset is validated against dynamically generated JSON schemas and inspected for anomalies, ensuring only clean, verified data reaches downstream systems.
- 🎯 **Condition Triggers & Alerts**: Evaluate expressions (e.g., `min(price) < 400000` or `salary >= 150000`) and dispatch instant notifications via webhooks or notification sinks.
- ⏰ **Daemonized Scheduling**: Set recurring intervals (`hourly`, `daily`, `weekly`, `monthly`) powered by a persistent background scheduler.
- 🔍 **Immutable Provenance Trail**: Complete audit trail for every run — including search queries, discovered URLs, raw HTML/markdown snapshots, validation errors, and LLM reasoning steps.

---

## 🔄 System Architecture

Orbit operates as a modular, distributed platform consisting of an autonomous execution daemon, a cross-platform command-line client, and extensible protocol adapters:

```mermaid
graph TD
    User["User / Developer"] -->|Goal via CLI or API| Core["Orbit Core Engine (Python)"]
    
    subgraph "Orbit Platform Ecosystem"
        CLI["CLI: orbc (Go)"] -->|REST / HTTP| API["FastAPI Gateway"]
        MCP["MCP Server"] -->|Tool Protocol| API
        
        subgraph Core ["Orbit Core Engine"]
            API --> Orchestrator["Agent Orchestrator"]
            Orchestrator --> LLM["Goal Interpreter & Reasoner"]
            Orchestrator --> Discovery["Multi-Source Discovery (SerpApi)"]
            Orchestrator --> Retrieval["Resilient Retrieval (Bright Data)"]
            Orchestrator --> Extraction["Schema Extractor & Validator"]
            Orchestrator --> Condition["Condition Evaluator"]
            Orchestrator --> DB[(PostgreSQL Store)]
            Scheduler["APScheduler Daemon"] --> Orchestrator
        end
    end

    Orchestrator -->|Alerts| Sinks["Notification Sinks (Slack / Webhooks)"]
    Orchestrator -->|Exports| DataStore["Local / Remote Data Sinks"]
```

---

## 📦 Repository Structure

The Orbit repository is structured as a monorepo containing:

| Component | Directory | Description | Documentation |
|-----------|-----------|-------------|---------------|
| **Core Engine** | [`core/`](./core) | Python backend daemon: Agent Orchestrator, LLM pipeline, APScheduler, PostgreSQL ORM, and FastAPI REST API. | [Core Docs](./core/README.md) |
| **CLI (`orbc`)** | [`cli/`](./cli) | High-performance Go CLI for interactive goal submission, manual runs, data exports, and daemon management. | [CLI Docs](./cli/README.md) |
| **MCP Integration** | [`mcp/`](./mcp) | Model Context Protocol adapters allowing AI agents (like Claude Desktop) to operate Orbit autonomously. | — |

---

## 🚀 Quickstart

### 1. Launch the Orbit Core Daemon

Follow the [Core Setup Guide](./core/README.md) to start the database and backend:

```bash
# 1. Start PostgreSQL
docker run --name orbit-pg -e POSTGRES_USER=orbit -e POSTGRES_PASSWORD=orbit -e POSTGRES_DB=orbit -p 5432:5432 -d postgres:16

# 2. Configure environment
cp core/.env.example .env
# Fill in OPENROUTER_API_KEY, BRIGHTDATA_API_KEY, SERPAPI_API_KEY, etc.

# 3. Launch Core server
python -m venv core/venv
source core/venv/bin/activate  # Windows: .\core\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn core.app:app --reload --port 8000
```

### 2. Install and Use the `orbc` CLI

The `orbc` CLI allows you to define automations, inspect runs, and export data directly from your terminal:

```bash
# Build the CLI
cd cli
make build
# Binary created at cli/bin/orbc

# Create an automation from a natural language goal
orbc goal "Every day at 8 AM, find the cheapest PlayStation 5 in Nigeria and alert if price < 400000 NGN"

# Run an automation immediately
orbc run <automation_id>

# View extracted results in aligned tables or export to CSV/JSON
orbc data <run_id> --format table
orbc data <run_id> --format csv > ps5_prices.csv

# Inspect full provenance and verification audit trail
orbc show <run_id>
```

---

## 💡 Example Goals

| Objective | Natural Language Goal |
|---|---|
| **E-Commerce & Arbitrage** | `"Daily at 9 AM, track prices for Sony WH-1000XM5 headphones across top retailers and alert me if price drops below $300"` |
| **Tech Hiring & Job Market** | `"Weekly on Monday, find remote Principal Go Engineer roles offering over $180,000 and export to CSV"` |
| **Travel & Flights** | `"Every 12 hours, find round-trip flights from New York to Tokyo under $900 for dates in November"` |
| **Real Estate Monitoring** | `"Every morning, find 2-bedroom apartments for rent in Lekki Phase 1 under 4,000,000 NGN/yr"` |
| **Regulatory & News Tracking**| `"Every 6 hours, monitor news mentions of 'open source AI regulations' across primary tech news portals"` |

---

## 🛡️ License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
