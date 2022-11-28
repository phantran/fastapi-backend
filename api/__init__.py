from fastapi import APIRouter

from api.auth.auth import auth_router
from api.product.v1.product import product_router as product_v1_router
from api.user.v1.user import user_router as user_v1_router

router = APIRouter()
router.include_router(user_v1_router, prefix="/api/v1", tags=["User"])
router.include_router(product_v1_router, prefix="/api/v1", tags=["Product"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])


__all__ = ["router"]
