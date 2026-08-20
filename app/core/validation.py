def validate_record(record: dict) -> tuple[bool, list[str]]:
    """
    Validates a single extracted record. Returns (is_valid, list_of_errors).
    Kept intentionally simple for Phase 1 — required-field presence and basic type/sanity checks.
    """
    errors = []

    if not record.get("product"):
        errors.append("missing product name")

    price = record.get("price")
    if price is None:
        errors.append("missing price")
    else:
        try:
            price_val = float(price)
            if price_val <= 0:
                errors.append("price is not positive")
            if price_val > 100_000_000:
                errors.append("price implausibly large")
        except (TypeError, ValueError):
            errors.append("price is not numeric")

    if not record.get("currency"):
        errors.append("missing currency")

    if record.get("availability") not in ("in_stock", "out_of_stock", "unknown"):
        errors.append("invalid availability value")

    if not record.get("url"):
        errors.append("missing url")

    return (len(errors) == 0, errors)
