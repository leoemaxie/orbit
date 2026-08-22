import json
from pathlib import Path
from typing import Any


class LocalFileExportSink:
    """Exports validated records to JSON lines or CSV files on the local filesystem."""

    export_dir: Path

    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_results(
        self, automation_id: str, run_id: str, records: list[dict[str, Any]]
    ) -> bool:
        if not records:
            return True

        target_file = self.export_dir / f"{automation_id[:8]}_{run_id[:8]}.json"
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, default=str)
            return True
        except Exception:
            return False
