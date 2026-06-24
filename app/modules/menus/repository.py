from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.tables import MenuTable
from app.modules.menus.models import Menu


class MenuRepository(Protocol):
    async def list_menus(self) -> list[Menu]: ...


class SqlAlchemyMenuRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    async def list_menus(self) -> list[Menu]:
        menu_rows = self._session.scalars(select(MenuTable).order_by(MenuTable.id)).all()
        return [Menu.model_validate(menu_row) for menu_row in menu_rows]
