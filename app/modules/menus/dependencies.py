from typing import Annotated

from fastapi import Depends

from app.core.dependencies import DatabaseSessionDep
from app.modules.menus.repository import SqlAlchemyMenuRepository
from app.modules.menus.service import MenuService


def get_menu_repository(session: DatabaseSessionDep) -> SqlAlchemyMenuRepository:
    return SqlAlchemyMenuRepository(session=session)


def get_menu_service(
    menu_repository: Annotated[SqlAlchemyMenuRepository, Depends(get_menu_repository)],
) -> MenuService:
    return MenuService(menu_repository=menu_repository)


MenuRepositoryDep = Annotated[SqlAlchemyMenuRepository, Depends(get_menu_repository)]
MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]
