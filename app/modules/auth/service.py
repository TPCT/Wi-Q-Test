from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import Settings
from app.modules.auth.models import AccessToken
from app.modules.auth.repository import ClientRepository

CLIENT_CREDENTIALS_GRANT_TYPE = "client_credentials"


class InvalidClientCredentialsError(ValueError):
    def __init__(self) -> None:
        super().__init__("Invalid client credentials")


class AuthService:
    def __init__(self, client_repository: ClientRepository, settings: Settings) -> None:
        self._client_repository = client_repository
        self._settings = settings

    async def create_access_token(
        self,
        client_id: str,
        client_secret: str,
        grant_type: str,
    ) -> AccessToken:
        client = await self._client_repository.find_by_client_id(client_id)
        if (
            client is None
            or client.client_secret != client_secret
            or grant_type != CLIENT_CREDENTIALS_GRANT_TYPE
        ):
            raise InvalidClientCredentialsError()

        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=self._settings.access_token_expires_seconds)
        token = jwt.encode(
            {
                "sub": client.client_id,
                "client_id": client.client_id,
                "grant_type": grant_type,
                "scope": client.scope,
                "iat": int(now.timestamp()),
                "exp": int(expires_at.timestamp()),
            },
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

        return AccessToken(
            access_token=token,
            expires_in=self._settings.access_token_expires_seconds,
            token_type="Bearer",
            scope=" ".join(client.scope),
        )
