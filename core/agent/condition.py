import logging
import re
from typing import Any

logger = logging.getLogger("core.agent.condition")


class ConditionEvaluator:
    """Evaluates alert, filter, and historical relative conditions against extracted records."""

    def evaluate(
        self,
        condition_expr: str | None,
        records: list[dict[str, Any]],
        previous_records: list[dict[str, Any]] | None = None,
    ) -> tuple[bool, str]:
        """
        Evaluates a condition string against extracted records, with support for historical comparisons.
        Returns: (condition_met: bool, message: str)
        """
        if not condition_expr or not condition_expr.strip():
            return False, "No condition specified"

        if not records:
            return False, "No extracted records to evaluate against condition"

        expr = condition_expr.strip()

        # 1. Historical Relative Percentage Drop Check: e.g. "price drops by 10%" or "price_drop >= 10"
        hist_match = re.search(
            r"(?:price[_\s]drop|drop[_\s]by|price[_\s]decrease)\s*(?:by|>=|>|<=|<)?\s*([0-9.]+)\s*%?",
            expr,
            re.IGNORECASE,
        )
        if hist_match:
            target_pct_drop = float(hist_match.group(1))
            if not previous_records:
                return False, f"First run: no historical baseline available to compute {target_pct_drop}% drop."

            curr_prices = self._extract_numeric_values(records, "price")
            prev_prices = self._extract_numeric_values(previous_records, "price")

            if not curr_prices or not prev_prices:
                return False, "Could not extract price series from current and previous runs to compare."

            prev_min = min(prev_prices)
            curr_min = min(curr_prices)

            if prev_min <= 0:
                return False, "Previous price was 0 or invalid."

            actual_pct_drop = ((prev_min - curr_min) / prev_min) * 100.0

            if actual_pct_drop >= target_pct_drop:
                return (
                    True,
                    f"Lowest price dropped by {actual_pct_drop:.1f}% (from {prev_min:.2f} to {curr_min:.2f}, target: >= {target_pct_drop}%)",
                )
            else:
                return (
                    False,
                    f"Price change: {actual_pct_drop:+.1f}% (current min: {curr_min:.2f} vs prev min: {prev_min:.2f}, target drop: >= {target_pct_drop}%)",
                )

        # 2. Aggregation functions: min(field), max(field), count()
        agg_match = re.match(
            r"^(min|max|avg|count)\(([a-zA-Z0-9_]*)\)\s*(<=|>=|<|>|==|!=)\s*([0-9.]+)",
            expr,
            re.IGNORECASE,
        )
        if agg_match:
            func, field_name, op, target_str = agg_match.groups()
            target_val = float(target_str)
            values = self._extract_numeric_values(records, field_name)

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

        # 3. Simple field comparison: field < value (matches if ANY record satisfies)
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

        return False, f"Unsupported condition format: '{expr}'"

    def _extract_numeric_values(self, records: list[dict[str, Any]], field: str) -> list[float]:
        values: list[float] = []
        for r in records:
            data = r.get("data", {})
            v = data.get(field)
            if v is not None:
                try:
                    values.append(float(v))
                except (ValueError, TypeError):
                    pass
        return values

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
