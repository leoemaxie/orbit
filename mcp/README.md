# Orbit MCP Server 🛰️

**Model Context Protocol (MCP) Server for Orbit Autonomous Web Data Operations**

The Orbit MCP server allows AI assistants (Claude Desktop, Cursor, Antigravity, VS Code) to directly control Orbit to formulate web-data goals, execute multi-stage scraping and extraction runs, inspect data records, and query schedules.

---

## 🛠️ Exposed MCP Capabilities

### 1. Tools

| Tool | Description |
|---|---|
| `create_automation(goal)` | Interprets a natural language goal into a domain-agnostic `ExecutionPlan` with a dynamic extraction schema. |
| `run_automation(automation_id)` | Triggers the complete agent loop on-demand (discovery → retrieval → extraction → validation → condition evaluation → verification). |
| `execute_goal(goal)` | One-shot execution: Interprets, executes, and returns structured extracted data in a single tool call. |
| `list_automations()` | Lists all registered automations and active schedules. |
| `get_automation(automation_id)` | Retrieves the dynamic extraction schema, objective, and schedule details for an automation. |
| `get_run_details(run_id)` | Returns execution audit logs, URLs discovered, pages retrieved, and reasoning decisions. |
| `query_extracted_data(run_id, valid_only)` | Queries extracted structured records with optional validation filtering. |
| `list_recurring_schedules()` | Lists all active recurring schedules and next execution timestamps. |

### 2. Resources

- `orbit://automations`: List of all registered automations.
- `orbit://automations/{automation_id}`: Single automation specification JSON.
- `orbit://runs/{run_id}`: Full run audit log and data payload.

### 3. Prompts

- `create-web-data-workflow`: Guided prompt for designing domain-agnostic web data operations.
- `audit-run-failure`: Diagnostic assistant prompt for inspecting and troubleshooting failed executions.

---

## 🚀 Installation & Configuration

### Option A: Run with `uvx` or `pip`

```bash
cd mcp
pip install -e .
```

### Option B: Configure in Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "orbit": {
      "command": "python",
      "args": ["-m", "orbit_mcp.server"],
      "cwd": "/path/to/orbit/mcp",
      "env": {
        "ORBIT_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Option C: Configure in Cursor / Antigravity

In `.cursor/mcp.json` or your MCP config file:

```json
{
  "mcpServers": {
    "orbit": {
      "command": "python",
      "args": ["-m", "orbit_mcp.server"],
      "cwd": "/path/to/orbit/mcp",
      "env": {
        "ORBIT_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

---

## 🧪 Testing

```bash
pytest mcp/tests/
```
