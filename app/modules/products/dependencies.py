from typing import Annotated

from fastapi import Depends

from app.core.dependencies import DatabaseSessionDep
from app.modules.products.repository import SqlAlchemyProductRepository
from app.modules.products.service import ProductService


def get_product_repository(session: DatabaseSessionDep) -> SqlAlchemyProductRepository:
    return SqlAlchemyProductRepository(session=session)


def get_product_service(
    product_repository: Annotated[SqlAlchemyProductRepository, Depends(get_product_repository)],
) -> ProductService:
    return ProductService(product_repository=product_repository)


ProductRepositoryDep = Annotated[SqlAlchemyProductRepository, Depends(get_product_repository)]
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
