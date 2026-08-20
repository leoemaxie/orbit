import logging
import re
from typing import Any

logger = logging.getLogger("core.agent.condition")


class ConditionEvaluator:
    """Evaluates alert and filter conditions against extracted records."""

    def evaluate(
        self, condition_expr: str | None, records: list[dict[str, Any]]
    ) -> tuple[bool, str]:
        """
        Evaluates a condition string against extracted records.
        Returns: (condition_met: bool, message: str)
        """
        if not condition_expr or not condition_expr.strip():
            return False, "No condition specified"

        if not records:
            return False, "No extracted records to evaluate against condition"

        expr = condition_expr.strip()

        # 1. Check for aggregation functions: min(field), max(field), count()
        agg_match = re.match(
            r"^(min|max|avg|count)\(([a-zA-Z0-9_]*)\)\s*(<=|>=|<|>|==|!=)\s*([0-9.]+)",
            expr,
            re.IGNORECASE,
        )
        if agg_match:
            func, field_name, op, target_str = agg_match.groups()
            target_val = float(target_str)
            values = []
            for r in records:
                data = r.get("data", {})
                v = data.get(field_name)
                if v is not None:
                    try:
                        values.append(float(v))
                    except (ValueError, TypeError):
                        pass

            if not values and func.lower() != "count":
                return False, f"Could not extract numeric values for field '{field_name}'"

            actual_val = 0.0
            if func.lower() == "min":
                actual_val = min(values)
            elif func.lower() == "max":
                actual_val = max(values)
            elif func.lower() == "avg":
                actual_val = sum(values) / len(values)
            elif func.lower() == "count":
                actual_val = float(len(records))

            matched = self._compare(actual_val, op, target_val)
            msg = f"Aggregation {func}({field_name}) = {actual_val} vs target {op} {target_val} -> Matched: {matched}"
            return matched, msg

        # 2. Check for simple field comparison: field < value (matches if ANY record satisfies)
        simple_match = re.match(
            r"^([a-zA-Z0-9_]+)\s*(<=|>=|<|>|==|!=)\s*([0-9.]+)", expr
        )
        if simple_match:
            field_name, op, target_str = simple_match.groups()
            target_val = float(target_str)
            matching_records = []
            for r in records:
                data = r.get("data", {})
                v = data.get(field_name)
                if v is not None:
                    try:
                        num = float(v)
                        if self._compare(num, op, target_val):
                            matching_records.append((r.get("url"), num))
                    except (ValueError, TypeError):
                        pass

            if matching_records:
                sample_url, sample_val = matching_records[0]
                msg = f"Found {len(matching_records)} record(s) satisfying '{field_name} {op} {target_val}' (e.g. {sample_val} at {sample_url})"
                return True, msg
            else:
                return False, f"No records satisfied condition '{expr}'"

        # 3. Fallback: string presence / substring check
        return False, f"Unsupported condition format: '{expr}'"

    def _compare(self, actual: float, op: str, target: float) -> bool:
        if op == "<":
            return actual < target
        if op == "<=":
            return actual <= target
        if op == ">":
            return actual > target
        if op == ">=":
            return actual >= target
        if op == "==":
            return actual == target
        if op == "!=":
            return actual != target
        return False
