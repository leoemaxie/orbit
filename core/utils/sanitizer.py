def sanitize_error_message(error: str | None) -> str | None:
    """Sanitizes internal driver/database exceptions to avoid leaking SQL or internal parameters."""
    if not error:
        return None
    err_str = str(error)
    if "OperationalError" in err_str or "server closed the connection" in err_str or "connection refused" in err_str:
        return "Database connectivity error: the connection was closed or timed out. Please retry the run."
    if "SQLAlchemyError" in err_str or "[SQL:" in err_str or "psycopg2" in err_str:
        return "A database transaction error occurred during pipeline execution."
    if "IntegrityError" in err_str:
        return "Data integrity constraint violated during record storage."
    return err_str
