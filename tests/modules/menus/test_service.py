import pytest

from app.modules.menus.models import Menu
from app.modules.menus.service import MenuNotFoundError, MenuService


class MenuRepositoryStub:
    async def list_menus(self) -> list[Menu]:
        return [
            Menu(id=3, name="Takeaway"),
            Menu(id=7, name="Delivery"),
        ]


async def test_finds_menu_by_name_case_insensitively() -> None:
    service = MenuService(menu_repository=MenuRepositoryStub())

    menu = await service.find_by_name("takeaway")

    assert menu == Menu(id=3, name="Takeaway")


async def test_raises_clear_error_when_menu_is_missing() -> None:
    service = MenuService(menu_repository=MenuRepositoryStub())

    with pytest.raises(MenuNotFoundError, match="Menu not found: Breakfast"):
        await service.find_by_name("Breakfast")

