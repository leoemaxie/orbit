import logging
from typing import Any, Optional
import httpx
from orbit_mcp.config import get_mcp_settings

logger = logging.getLogger("orbit_mcp.client")


class OrbitBackendClient:
    """Async HTTP client to communicate with the Orbit backend server."""

    def __init__(self, base_url: Optional[str] = None):
        settings = get_mcp_settings()
        self.base_url = (base_url or settings.orbit_api_url).rstrip("/")
        self.timeout = settings.request_timeout

    async def health(self) -> dict[str, Any]:
        """Check Orbit backend health status."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/health")
            resp.raise_for_status()
            return resp.json()

    async def create_automation(self, goal: str) -> dict[str, Any]:
        """Interpret goal and create automation."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/v1/automations",
                json={"goal": goal},
            )
            resp.raise_for_status()
            return resp.json()

    async def list_automations(self) -> dict[str, Any]:
        """List all automations."""
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/automations")
            resp.raise_for_status()
            return resp.json()

    async def get_automation(self, automation_id: str) -> dict[str, Any]:
        """Get single automation details."""
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/automations/{automation_id}")
            resp.raise_for_status()
            return resp.json()

    async def delete_automation(self, automation_id: str) -> dict[str, Any]:
        """Delete an automation."""
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.delete(f"{self.base_url}/api/v1/automations/{automation_id}")
            resp.raise_for_status()
            return resp.json()

    async def run_automation(self, automation_id: str) -> dict[str, Any]:
        """Trigger an execution run for an automation."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/v1/automations/{automation_id}/run")
            resp.raise_for_status()
            return resp.json()

    async def get_run(self, run_id: str) -> dict[str, Any]:
        """Get details, audit trail, and results of a specific run."""
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/runs/{run_id}")
            resp.raise_for_status()
            return resp.json()

    async def list_automation_runs(self, automation_id: str) -> list[dict[str, Any]]:
        """List past runs for an automation."""
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/automations/{automation_id}/runs")
            resp.raise_for_status()
            return resp.json()
