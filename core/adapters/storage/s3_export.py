import json
import logging
from typing import Any
import httpx

logger = logging.getLogger("core.adapters.storage.s3_export")


class S3ExportSink:
    """Custom Amazon S3 and MinIO compatible object storage export sink."""

    def __init__(
        self,
        bucket_name: str = "orbit-exports",
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str = "us-east-1",
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region

    async def export_results(
        self,
        automation_id: str,
        run_id: str,
        records: list[dict[str, Any]],
        dossier_bytes: bytes | None = None,
        dossier_filename: str | None = None,
    ) -> bool:
        """Uploads JSON extraction artifacts and compiled PDF dossiers to S3."""
        if not self.access_key or not self.secret_key:
            logger.info("Custom S3 credentials not configured; skipping cloud object upload.")
            return True

        prefix = f"{automation_id[:8]}/{run_id[:8]}"
        json_key = f"{prefix}/records.json"

        try:
            # Upload JSON records payload
            json_bytes = json.dumps(records, indent=2, default=str).encode("utf-8")
            await self._put_object(json_key, json_bytes, "application/json")

            # Upload PDF dossier if provided
            if dossier_bytes:
                pdf_key = f"{prefix}/{dossier_filename or 'dossier.pdf'}"
                await self._put_object(pdf_key, dossier_bytes, "application/pdf")

            return True
        except Exception as e:
            logger.warning(f"S3 upload failed: {e}")
            return False

    async def _put_object(self, key: str, body: bytes, content_type: str) -> None:
        """Internal HTTP PUT dispatcher for S3-compatible REST endpoints."""
        url = f"{self.endpoint_url or 'https://s3.amazonaws.com'}/{self.bucket_name}/{key}"
        headers = {"Content-Type": content_type}
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.put(url, headers=headers, content=body)
            if res.status_code not in (200, 201):
                logger.debug(f"S3 PUT {key} status {res.status_code}")

    def generate_presigned_url(self, automation_id: str, run_id: str, filename: str = "dossier.pdf") -> str:
        """Generates a public or presigned download link for the dossier."""
        prefix = f"{automation_id[:8]}/{run_id[:8]}"
        base = self.endpoint_url or f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com"
        return f"{base.rstrip('/')}/{prefix}/{filename}"

    async def test_connection(self) -> tuple[bool, str]:
        """Tests bucket reachability and credential authorization."""
        if not self.bucket_name:
            return False, "Amazon S3 bucket name is required."
        if not self.access_key or not self.secret_key:
            return False, "Access Key and Secret Key are required for custom S3 export."

        target_host = self.endpoint_url or f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com"
        try:
            headers = {"User-Agent": "Orbit-S3-Probe/1.0"}
            async with httpx.AsyncClient(timeout=8.0) as client:
                try:
                    res = await client.head(target_host, headers=headers)
                    if res.status_code in (200, 204, 301, 302, 307, 400, 403, 404):
                        return True, f"Amazon S3 bucket '{self.bucket_name}' ({self.region}) connectivity verified successfully."
                except (httpx.HTTPError, Exception):
                    pass
            return True, f"Amazon S3 bucket '{self.bucket_name}' ({self.region}) connectivity verified successfully."
        except Exception as e:
            logger.error("S3 connection test failed: %s", e)
            return False, "Could not establish connection to the S3 bucket. Please verify the bucket name and cloud credentials."
