from fastapi import APIRouter, Depends
from starlette.requests import Request

from app.product.schemas.product import (
    ProductResponseSchema,
    ProductCreateRequestSchema,
    ProductCreateResponseSchema,
    ProductDeleteRequestSchema,
    ProductUpdateRequestSchema,
    BuyRequestSchema,
    BuyResponseSchema,
)
from app.product.services.product import ProductService
from core.fastapi.dependencies import PermissionDependency, IsAuthenticated, AllowAll

product_router = APIRouter()


@product_router.get(
    "/product/{product_id}",
    response_model=ProductResponseSchema,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_product(product_id: int):
    return await ProductService().get_product(product_id=product_id)


@product_router.post(
    "/product/create",
    response_model=ProductCreateResponseSchema,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def create_product(payload: ProductCreateRequestSchema, request: Request):
    return await ProductService().create_product(
        user_id=request.user.id, payload=payload
    )


@product_router.post(
    "/product/update",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_product(payload: ProductUpdateRequestSchema, request: Request):
    await ProductService().update_product(user_id=request.user.id, payload=payload)
    return {"message": f"Updated product successful"}


@product_router.delete(
    "/product", dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
async def delete_product(payload: ProductDeleteRequestSchema, request: Request):
    await ProductService().delete_product(
        user_id=request.user.id, product_id=payload.product_id
    )
    return {"message": "successful"}


@product_router.post(
    "/buy",
    response_model=BuyResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def buy_product(payload: BuyRequestSchema, request: Request):
    return await ProductService().buy(request.user.id, payload)
