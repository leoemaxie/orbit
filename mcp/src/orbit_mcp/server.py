import asyncio
import logging
from typing import Any
from mcp.server.fastmcp import FastMCP

from orbit_mcp.client import OrbitBackendClient
from orbit_mcp.prompts.templates import AUDIT_FAILURE_PROMPT, WORKFLOW_DESIGN_PROMPT
from orbit_mcp.resources.provider import OrbitResourceProvider
from orbit_mcp.tools.automations import (
    create_automation_tool,
    get_automation_tool,
    list_automations_tool,
)
from orbit_mcp.tools.execution import execute_goal_tool, run_automation_tool
from orbit_mcp.tools.inspection import (
    get_run_details_tool,
    list_recurring_schedules_tool,
    query_extracted_data_tool,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orbit_mcp.server")

# Initialize FastMCP Server
mcp = FastMCP("Orbit MCP Server")
client = OrbitBackendClient()
resource_provider = OrbitResourceProvider(client)


# ─────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────

@mcp.tool()
async def create_automation(goal: str) -> dict[str, Any]:
    """
    Creates an autonomous web data workflow from a natural language goal.
    The goal is interpreted into a domain-agnostic execution plan with a dynamic extraction schema.

    Args:
        goal: Plain English objective (e.g. 'Daily at 8AM, find cheapest PS5 in Nigeria and alert if < 400000 NGN',
              'Find remote Python developer jobs paying > $150k')
    """
    return await create_automation_tool(goal, client)


@mcp.tool()
async def run_automation(automation_id: str) -> dict[str, Any]:
    """
    Triggers an on-demand autonomous run for a registered automation.
    Executes the full agent loop: discovery -> retrieval -> extraction -> validation -> condition evaluation -> verification.

    Args:
        automation_id: The UUID of the automation to run.
    """
    return await run_automation_tool(automation_id, client)


@mcp.tool()
async def execute_goal(goal: str) -> dict[str, Any]:
    """
    One-shot execution: Interprets a natural language goal, creates an automation,
    immediately executes the full agent loop, and returns the extracted structured records.

    Args:
        goal: Natural language web data objective.
    """
    return await execute_goal_tool(goal, client)


@mcp.tool()
async def list_automations() -> dict[str, Any]:
    """
    Lists all registered Orbit web-data automations and their active schedules.
    """
    return await list_automations_tool(client)


@mcp.tool()
async def get_automation(automation_id: str) -> dict[str, Any]:
    """
    Gets details of a specific automation, including its dynamic extraction schema and schedule.

    Args:
        automation_id: The UUID of the automation.
    """
    return await get_automation_tool(automation_id, client)


@mcp.tool()
async def get_run_details(run_id: str) -> dict[str, Any]:
    """
    Retrieves full execution audit trail, provenance (sources discovered, pages retrieved),
    reasoning logs, and validation errors for a specific run.

    Args:
        run_id: The UUID of the run to inspect.
    """
    return await get_run_details_tool(run_id, client)


@mcp.tool()
async def query_extracted_data(run_id: str, valid_only: bool = True) -> dict[str, Any]:
    """
    Queries and filters extracted structured records for a specific run.

    Args:
        run_id: The UUID of the run.
        valid_only: If True, returns only records that passed dynamic schema validation.
    """
    return await query_extracted_data_tool(run_id, valid_only, client)


@mcp.tool()
async def list_recurring_schedules() -> dict[str, Any]:
    """
    Lists all active recurring scheduled automations and their next execution times.
    """
    return await list_recurring_schedules_tool(client)


# ─────────────────────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────────────────────

@mcp.resource("orbit://automations")
async def get_automations_resource() -> str:
    """Resource returning JSON list of all registered automations."""
    return await resource_provider.list_automations_resource()


@mcp.resource("orbit://automations/{automation_id}")
async def get_single_automation_resource(automation_id: str) -> str:
    """Resource returning JSON representation of an automation specification."""
    return await resource_provider.get_automation_resource(automation_id)


@mcp.resource("orbit://runs/{run_id}")
async def get_single_run_resource(run_id: str) -> str:
    """Resource returning JSON execution log and records for a run."""
    return await resource_provider.get_run_resource(run_id)


# ─────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────

@mcp.prompt()
def create_web_data_workflow() -> str:
    """Guided prompt for formulating an autonomous web data goal."""
    return WORKFLOW_DESIGN_PROMPT


@mcp.prompt()
def audit_run_failure(run_id: str) -> str:
    """Diagnostic prompt for investigating and explaining a failed run."""
    return AUDIT_FAILURE_PROMPT.format(run_id=run_id)


def main():
    """Main entrypoint for standard stdio MCP transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
