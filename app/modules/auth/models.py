from pydantic import BaseModel


class Client(BaseModel):
    client_id: str
    client_secret: str
    scope: list[str]


class AccessToken(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: list[str]
