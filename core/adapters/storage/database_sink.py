import json
import logging
import re
from typing import Any
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine, func, text
from sqlalchemy.dialects.postgresql import JSONB

from core.security.vault import SecretVault

logger = logging.getLogger("core.adapters.storage.database_sink")


class DatabaseExportSink:
    """Direct customer data warehouse export sink (PostgreSQL, MySQL, SQLite, Snowflake)."""

    def __init__(self, connection_uri: str | None = None, target_table: str | None = None):
        raw_uri = connection_uri or ""
        if "••••" in raw_uri or not raw_uri:
            from core.config.settings import get_settings
            raw_uri = get_settings().database_url or ""
        self.connection_uri = SecretVault.decrypt_secret(raw_uri) if raw_uri else ""
        self.target_table = target_table or "orbit_extracted_records"

    def _sanitize_ident(self, name: str) -> str:
        """Sanitizes identifiers to safe alphanumeric strings."""
        return re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()

    async def export_results(
        self,
        automation_id: str,
        run_id: str,
        records: list[dict[str, Any]],
        dossier_bytes: bytes | None = None,
        dossier_filename: str | None = None,
    ) -> bool:
        """Exports validated records directly into customer data warehouse tables."""
        if not self.connection_uri or not records:
            return True

        table_name = self._sanitize_ident(self.target_table)
        try:
            engine = create_engine(self.connection_uri, pool_pre_ping=True)
            metadata = MetaData()

            with engine.begin() as conn:
                # Ensure destination table exists with JSON payload support
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id SERIAL PRIMARY KEY,
                        automation_id VARCHAR(64) NOT NULL,
                        run_id VARCHAR(64) NOT NULL,
                        source_url TEXT,
                        data JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Batch insert records
                insert_stmt = text(f"""
                    INSERT INTO {table_name} (automation_id, run_id, source_url, data)
                    VALUES (:automation_id, :run_id, :source_url, :data)
                """)
                for rec in records:
                    rec_data = rec.get("data") if isinstance(rec, dict) and isinstance(rec.get("data"), dict) else (rec if isinstance(rec, dict) else {})
                    conn.execute(insert_stmt, {
                        "automation_id": automation_id,
                        "run_id": run_id,
                        "source_url": rec.get("url", "") if isinstance(rec, dict) else "",
                        "data": json.dumps(rec_data),
                    })
            return True
        except Exception as e:
            logger.warning(f"Data warehouse export failed: {e}")
            return False

    def test_connection(self) -> tuple[bool, str]:
        """Tests live reachability of the customer data warehouse connection URI."""
        if not self.connection_uri:
            return False, "Data warehouse connection URI is not configured."
        try:
            engine = create_engine(self.connection_uri, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True, "Data warehouse connection verified successfully."
        except Exception as e:
            logger.error("Data warehouse connection probe failed: %s", e)
            return False, "Could not connect to the database. Please verify your connection URI and server availability."
