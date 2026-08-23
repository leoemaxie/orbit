# orbc MCP Server 🛰️

**Model Context Protocol (MCP) Server for Orbit Autonomous Web Data Operations**

The `orbc` MCP server allows AI coding assistants and LLM environments (Claude Desktop, Cursor, Antigravity, VS Code, Cline, Windsurf, Zed) to natively interact with Orbit to formulate goals, execute web scraping and extraction pipelines, query data records, and inspect execution audit trails.

---

## 🛠️ Exposed MCP Capabilities

### 1. Tools

| Tool | Parameters | Description |
|---|---|---|
| `create_automation` | `goal: str` | Interprets a natural language objective into a domain-agnostic `ExecutionPlan` with a dynamic schema. |
| `run_automation` | `automation_id: str` | Triggers the complete agent loop on-demand (discovery → retrieval → extraction → validation → condition evaluation → verification). |
| `execute_goal` | `goal: str` | **One-shot execution**: Interprets, creates, executes, and returns structured data in a single tool call. |
| `list_automations` | *none* | Lists all registered automations and active schedules. |
| `get_automation` | `automation_id: str` | Retrieves the dynamic extraction schema, objective, and schedule details for an automation. |
| `get_run_details` | `run_id: str` | Returns execution audit logs, URLs discovered, pages retrieved, and agent self-correction decisions. |
| `query_extracted_data` | `run_id: str`, `valid_only: bool = true` | Queries extracted structured records with optional validation filtering. |
| `list_recurring_schedules` | *none* | Lists all active recurring schedules and next execution timestamps. |

### 2. Resources (`orbc://`)

| URI Pattern | Description |
|---|---|
| `orbc://automations` | Live JSON index of all registered automations. |
| `orbc://automations/{automation_id}` | Automation specification JSON (objective, domain, extraction schema, schedule). |
| `orbc://runs/{run_id}` | Full run audit trail and validated extracted records JSON. |

### 3. Prompts

| Prompt | Description |
|---|---|
| `create_web_data_workflow` | Interactive prompt guiding the agent to formulate high-quality autonomous web data workflows. |
| `audit_run_failure` | Diagnostic prompt for auditing failed runs, reviewing the Agent Brain recovery log, and proposing remediation. |

---

## 🚀 How to Run the MCP Server

Ensure the Orbit backend is running on `http://127.0.0.1:8000`:
```bash
# Start backend from repo root:
core/venv/Scripts/python.exe -m uvicorn core.app:app --reload --port 8000
```

### 1. Run Directly via Command Line

Install the MCP package in editable mode:
```bash
cd mcp
pip install -e .
```

Run in stdio mode:
```bash
# Option A: Using python module
python -m orbit.server

# Option B: Using installed entrypoint
orbc-mcp
```

---

## ⚙️ Client Configurations

### Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "orbc": {
      "command": "python",
      "args": ["-m", "orbit.server"],
      "cwd": "/path/to/orbit/mcp",
      "env": {
        "ORBIT_API_URL": "http://127.0.0.1:8000",
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### Cursor / Antigravity
In `.cursor/mcp.json` or `.gemini/mcp.json`:
```json
{
  "mcpServers": {
    "orbc": {
      "command": "python",
      "args": ["-m", "orbit.server"],
      "cwd": "/path/to/orbit/mcp",
      "env": {
        "ORBIT_API_URL": "http://127.0.0.1:8000",
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### VS Code (Cline / Roo-Code / Continue)
Add to your MCP settings:
```json
{
  "mcpServers": {
    "orbc": {
      "command": "python",
      "args": ["-m", "orbit.server"],
      "cwd": "/path/to/orbit/mcp",
      "env": {
        "ORBIT_API_URL": "http://127.0.0.1:8000",
        "PYTHONPATH": "src"
      }
    }
  }
}
```

---

## 🧪 Testing

Run the MCP tool test suite:
```bash
pytest mcp/tests/
```
