from fastapi import Form


class OAuth2PhoneRequestForm:
    def __init__(
        self,
        phone: str = Form(..., alias="username"),
        password: str = Form(...),
    ):
        self.phone = phone
        self.password = password
