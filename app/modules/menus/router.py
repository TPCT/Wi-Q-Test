from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.responses import DataResponse
from app.core.security import AuthDep
from app.modules.menus.dependencies import MenuServiceDep
from app.modules.menus.models import Menu

router = APIRouter(prefix="/menus", tags=["menus"])


@router.get("")
async def list_menus(
    _: AuthDep,
    menu_service: MenuServiceDep,
) -> DataResponse[list[Menu]]:
    try:
        menus = await menu_service.list_menus()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
    return DataResponse(data=menus)
