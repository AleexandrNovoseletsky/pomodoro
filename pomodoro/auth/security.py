"""Utilities for hashing passwords and creating JWT tokens.

The module provides functions for password verification and generation,
as well as for creating access tokens (JWT) using Argon2 for password
hashing and JOSE for JWT operations.
"""

from datetime import UTC, datetime

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt

from pomodoro.core.settings import Settings

# Global password hasher instance with optimized security parameters
password_hasher = PasswordHasher(
    time_cost=2, memory_cost=19 * 1024, parallelism=1
)
settings = Settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password using Argon2.

    Securely compares a plain text password with a stored hash to
    determine if they match without exposing timing attacks.

    Args:     plain_password: User-provided plain text password
    hashed_password: Previously hashed password from database

    Returns:     True if password matches the hash, False otherwise

    Raises:     argon2.exceptions.VerifyMismatchError: If password
    doesn't match hash     argon2.exceptions.VerificationError: If hash
    format is invalid

    Note:     Uses constant-time comparison to prevent timing attacks
    """
    try:
        return password_hasher.verify(
            hash=hashed_password, password=plain_password
        )
    except VerifyMismatchError:
        return False


def get_password_hash(password: str) -> str:
    """Generate secure password hash.

    Creates a cryptographically secure hash of the password suitable for
    long-term storage. Includes salt and security parameters.

    Args:     password: Plain text password to hash

    Returns:     Securely hashed password string for database storage
    """
    return password_hasher.hash(password=password)


def create_access_token(data: dict) -> str:
    """Generate JWT access token for user authentication.

    Creates a signed JWT token containing user identity and expiration
    for API authorization. Tokens are signed with application secret.

    Args:     data: Payload data to include in token (e.g., {"sub":
    user_id})

    Returns:     Encoded JWT token string for Bearer authentication

    Note:     Automatically adds expiration timestamp based on
    application settings.     Uses HS256 algorithm for signing with
    application secret key.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + settings.JWT_LIFE_SPAN
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt
