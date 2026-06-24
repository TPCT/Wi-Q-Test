from typing import Protocol

from sqlalchemy.orm import Session

from app.core.tables import ClientTable
from app.modules.auth.models import Client


class ClientRepository(Protocol):
    async def find_by_client_id(self, client_id: str) -> Client | None: ...


class SqlAlchemyClientRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    async def find_by_client_id(self, client_id: str) -> Client | None:
        client_row = self._session.get(ClientTable, client_id)
        if client_row is None:
            return None
        return Client.model_validate(client_row, from_attributes=True)
