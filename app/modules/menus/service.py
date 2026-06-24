from app.modules.menus.models import Menu
from app.modules.menus.repository import MenuRepository


class MenuNotFoundError(ValueError):
    def __init__(self, menu_name: str) -> None:
        super().__init__(f"Menu not found: {menu_name}")
        self.menu_name = menu_name


class MenuService:
    def __init__(self, menu_repository: MenuRepository) -> None:
        self._menu_repository = menu_repository

    async def list_menus(self) -> list[Menu]:
        return await self._menu_repository.list_menus()

    async def find_by_name(self, menu_name: str) -> Menu:
        menus = await self._menu_repository.list_menus()
        try:
            return next(menu for menu in menus if menu.name.casefold() == menu_name.casefold())
        except StopIteration as error:
            raise MenuNotFoundError(menu_name) from error
