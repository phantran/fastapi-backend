from fastapi import HTTPException
from passlib import context
from sqlalchemy import delete, select
from starlette.status import HTTP_200_OK

from app.product.models import Product
from app.product.schemas.product import (
    BuyRequestSchema,
    ProductCreateRequestSchema,
    ProductUpdateRequestSchema,
)
from app.user.models import User
from core.consts import BUYER, SELLER
from core.db import Transactional, db_session
from core.exceptions import (
    ProductChangeNotAllowedException,
    ProductNotFoundException,
    UserNotFoundException,
)
from core.exceptions.product import (
    BuyOwnProductException,
    InsufficientBalanceException,
    RoleNotAllowedException,
    SellerBuyException,
)
from core.utils.utils import get_change

pwd_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")


class ProductService:
    def __init__(self):
        ...

    @staticmethod
    async def get_product(
        product_id: int,
    ) -> Product:
        query = select(Product).where(Product.id == product_id)
        result = await db_session.execute(query)
        product = result.scalars().first()
        if not product:
            raise ProductNotFoundException
        return product.__dict__

    @Transactional()
    async def delete_product(
        self,
        user_id: int,
        product_id: int,
    ) -> None:
        # Only seller is allowed to change product
        await self._role_check(user_id, SELLER, RoleNotAllowedException)
        query = delete(Product).where(Product.id == product_id)
        result = await db_session.execute(query)
        if not result or result.rowcount == 0:
            raise ProductNotFoundException

    @Transactional()
    async def create_product(
        self, user_id: int, payload: ProductCreateRequestSchema
    ) -> dict:
        # Only seller is allowed to add product
        await self._role_check(user_id, SELLER, RoleNotAllowedException)
        product = Product(
            product_name=payload.product_name,
            amount_available=payload.amount_available,
            cost=payload.cost,
            seller_id=user_id,
        )
        db_session.add(product)
        return {
            "product_name": payload.product_name,
            "message": "Product created successfully",
        }

    @Transactional()
    async def update_product(
        self, user_id: int, payload: ProductUpdateRequestSchema
    ) -> None:
        result = await db_session.execute(
            select(Product).where((Product.id == payload.id))
        )
        product = result.scalars().first()
        if not product:
            raise ProductNotFoundException

        if product.seller_id != user_id:
            raise ProductChangeNotAllowedException

        # Buyer is not allowed to change product
        await self._role_check(user_id, SELLER, RoleNotAllowedException)

        payload = payload.__dict__
        del payload["id"]
        for key, value in payload.items():
            setattr(product, key, value)

    @Transactional()
    async def buy(self, user_id: int, payload: BuyRequestSchema) -> dict:
        """
        Perform buying a product request from a buyer
        """
        # Seller is not allowed to buy, check if user is a buyer
        user = await self._role_check(user_id, BUYER, SellerBuyException)

        result = await db_session.execute(
            select(Product).where((Product.id == payload.product_id))
        )
        product = result.scalars().first()
        if not product:
            raise ProductNotFoundException

        if product.seller_id == user_id:
            raise BuyOwnProductException

        if product.amount_available == 0 or product.amount_available < payload.amount:
            raise HTTPException(
                status_code=HTTP_200_OK,
                detail=f"Product {product.product_name} is out of stock",
            )

        total_spent = product.cost * payload.amount
        if total_spent > user.deposit:
            raise InsufficientBalanceException

        aggregated_change = get_change(user.deposit - total_spent)
        change = []
        for count, coin in aggregated_change:
            change.extend([coin] * count)
        res = {
            "total_spent": total_spent,
            "product_name": product.product_name,
            "product_id": product.id,
            "change": change if change else None,
        }
        user.deposit = 0
        product.amount_available -= payload.amount
        return res

    @staticmethod
    async def _role_check(user_id: int, role: str, exception) -> User:
        query = select(User).where((User.id == user_id))
        result = await db_session.execute(query)
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException
        if user.role != role:
            raise exception
        return user
