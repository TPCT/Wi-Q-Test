from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.responses import DataResponse
from app.core.security import AuthDep
from app.modules.products.dependencies import ProductServiceDep
from app.modules.products.models import Product, ProductRenameRequest

router = APIRouter(tags=["products"])

@router.get("/menu/{menu_id}/products")
async def list_products_for_menu(
    menu_id: int,
    _: AuthDep,
    product_service: ProductServiceDep,
) -> DataResponse[list[Product]]:
    try:
        products = await product_service.list_for_menu(menu_id)
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
    return DataResponse(data=products)


@router.put("/menu/{menu_id}/product/{product_id}")
async def rename_product(
    menu_id: int,
    product_id: int,
    request: ProductRenameRequest,
    _: AuthDep,
    product_service: ProductServiceDep,
) -> DataResponse[Product]:
    try:
        product = await product_service.rename_product(
            menu_id=menu_id,
            product_id=product_id,
            new_name=request.name,
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
    return DataResponse(data=product)
