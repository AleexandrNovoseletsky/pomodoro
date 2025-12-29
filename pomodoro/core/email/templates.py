"""Email templates."""

def password_recovery_email(code: int) -> str:
    """Generate password recovery email body."""
    return (
        "You have requested password recovery.\n\n"
        f"Recovery code: {code}\n\n"
        "If you did not request recovery — simply "
        "ignore this email.\n"
    )
