from pydantic import BaseModel


class Client(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str
    scope: str


class AccessToken(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
