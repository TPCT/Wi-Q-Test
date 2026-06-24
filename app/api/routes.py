from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.menus.router import router as menus_router
from app.modules.products.router import router as products_router

router = APIRouter()


@router.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


router.include_router(auth_router)
router.include_router(menus_router)
router.include_router(products_router)
