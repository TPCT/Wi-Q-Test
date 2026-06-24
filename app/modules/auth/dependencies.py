from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.dependencies import DatabaseSessionDep
from app.modules.auth.repository import SqlAlchemyClientRepository
from app.modules.auth.service import AuthService


def get_client_repository(session: DatabaseSessionDep) -> SqlAlchemyClientRepository:
    return SqlAlchemyClientRepository(session=session)


def get_auth_service(
    client_repository: Annotated[SqlAlchemyClientRepository, Depends(get_client_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(client_repository=client_repository, settings=settings)


ClientRepositoryDep = Annotated[SqlAlchemyClientRepository, Depends(get_client_repository)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
