"""Authentication forms.

Defines form classes for authentication-related data input. Provides
structured form handling for login operations with proper field mapping.
"""

from fastapi import Form


class LoginForm:
    """User login form for credential-based authentication.

    Handles form data submission for user login operations with proper
    field mapping and validation. Uses alias mapping for compatibility
    with standard OAuth2 form fields.

    Attributes:     phone: User's phone number used as login identifier
    (aliased as 'username')     password: User's password for
    authentication
    """

    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
    ):
        """Initialize login form with user credentials.

        Args:
            username: Phone number serving as user identifier, mapped
                   from 'username' field for OAuth2 compatibility
            password: User password for authentication verification
        """
        self.username = username
        self.password = password
