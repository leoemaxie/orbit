from typing import Any, Protocol


class DataSink(Protocol):
    """Protocol for exporting extracted records to external storage/databases."""

    async def export_results(
        self, automation_id: str, run_id: str, records: list[dict[str, Any]]
    ) -> bool:
        ...


class NotificationAdapter(Protocol):
    """Protocol for external communication platforms."""

    async def send_alert(
        self, title: str, message: str, payload: dict[str, Any] | None = None
    ) -> bool:
        ...
