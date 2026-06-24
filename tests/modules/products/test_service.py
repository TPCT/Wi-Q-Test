from app.modules.products.models import Product
from app.modules.products.service import ProductService


class ProductRepositoryStub:
    def __init__(self) -> None:
        self.products_by_menu = {
            7: [Product(id=84, menu_id=7, name="Chpis")],
        }
        self.renamed_product_args: tuple[int, int, str] | None = None

    async def list_products_for_menu(self, menu_id: int) -> list[Product]:
        return self.products_by_menu.get(menu_id, [])

    async def rename_product(self, menu_id: int, product_id: int, new_name: str) -> Product:
        self.renamed_product_args = (menu_id, product_id, new_name)
        return Product(id=product_id, menu_id=menu_id, name=new_name)


async def test_lists_products_for_menu() -> None:
    service = ProductService(product_repository=ProductRepositoryStub())

    products = await service.list_for_menu(menu_id=7)

    assert products == [Product(id=84, menu_id=7, name="Chpis")]


async def test_renames_product_without_reading_existing_product() -> None:
    repository = ProductRepositoryStub()
    service = ProductService(product_repository=repository)

    product = await service.rename_product(menu_id=7, product_id=84, new_name="Chips")

    assert product == Product(id=84, menu_id=7, name="Chips")
    assert repository.renamed_product_args == (7, 84, "Chips")
    assert repository.products_by_menu[7][0] == Product(id=84, menu_id=7, name="Chpis")
