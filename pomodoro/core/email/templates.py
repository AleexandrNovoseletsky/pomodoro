"""Email templates."""

def password_recovery_email(code: int) -> str:
    """Generate password recovery email body."""
    return (
        "Вы запросили восстановление пароля.\n\n"
        f"Код восстановления: {code}\n\n"
        "Если вы не запрашивали восстановление — просто "
        "проигнорируйте это письмо.\n"
    )
