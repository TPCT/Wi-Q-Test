from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.tables import MenuTable, ProductTable
from app.modules.products.models import Product


class ProductRepository(Protocol):
    async def list_products_for_menu(self, menu_id: int) -> list[Product]: ...

    async def rename_product(self, menu_id: int, product_id: int, new_name: str) -> Product: ...


class SqlAlchemyProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    async def list_products_for_menu(self, menu_id: int) -> list[Product]:
        product_rows = self._session.scalars(
            select(ProductTable)
            .where(ProductTable.menu_id == menu_id)
            .order_by(ProductTable.id)
        ).all()
        return [Product.model_validate(product_row) for product_row in product_rows]

    async def rename_product(self, menu_id: int, product_id: int, new_name: str) -> Product:
        menu_row = self._session.get(MenuTable, menu_id)
        if menu_row is None:
            menu_row = MenuTable(id=menu_id, name=f"Menu {menu_id}")
            self._session.add(menu_row)

        product_row = self._session.get(ProductTable, (product_id, menu_id))
        if product_row is None:
            product_row = ProductTable(
                id=product_id,
                menu=menu_row,
                name=new_name,
            )
            self._session.add(product_row)
        else:
            product_row.name = new_name

        self._session.commit()
        self._session.refresh(product_row)
        return Product.model_validate(product_row)
