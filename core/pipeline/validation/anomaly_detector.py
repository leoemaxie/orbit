import statistics
from typing import Any


class AnomalyDetector:
    """Detects statistical outliers and anomalies across extracted records in a run."""

    def filter_and_annotate_outliers(
        self, records: list[dict[str, Any]], numeric_fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        if numeric_fields is None:
            numeric_fields = ["price", "salary", "fare", "amount"]
        if len(records) < 3:
            return records

        for field_name in numeric_fields:
            values = []
            for r in records:
                data = r.get("data", {})
                v = data.get(field_name)
                if v is not None:
                    try:
                        values.append(float(v))
                    except (ValueError, TypeError):
                        pass

            if len(values) < 3:
                continue

            median = statistics.median(values)
            # Flag extreme outliers (e.g. 10x higher or 10x lower than median)
            for r in records:
                data = r.get("data", {})
                v = data.get(field_name)
                if v is not None:
                    try:
                        num = float(v)
                        if num < median * 0.1:
                            r.setdefault("anomalies", []).append(
                                f"Value {num} for '{field_name}' is suspiciously low compared to median {median:.2f}"
                            )
                        elif num > median * 10.0:
                            r.setdefault("anomalies", []).append(
                                f"Value {num} for '{field_name}' is suspiciously high compared to median {median:.2f}"
                            )
                    except (ValueError, TypeError):
                        pass

        return records
