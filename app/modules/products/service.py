from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository


class ProductService:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._product_repository = product_repository

    async def list_for_menu(self, menu_id: int) -> list[Product]:
        return await self._product_repository.list_products_for_menu(menu_id)

    async def rename_product(self, menu_id: int, product_id: int, new_name: str) -> Product:
        return await self._product_repository.rename_product(
            menu_id=menu_id,
            product_id=product_id,
            new_name=new_name,
        )
