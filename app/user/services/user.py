from fastapi import HTTPException
from passlib import context
from sqlalchemy import delete, select
from starlette.status import HTTP_400_BAD_REQUEST

from app.user.models import User
from app.user.schemas.user import DepositRequestSchema, LoginResponseSchema
from core.cache.redis import (
    add_to_active_sessions,
    get_active_sessions,
    revoke_other_active_sessions,
)
from core.consts import BUYER
from core.db import Transactional, db_session
from core.exceptions import (
    DuplicateUsernameException,
    InvalidCredentialsException,
    PasswordDoesNotMatchException,
    SellerDepositException,
    UserNotFoundException,
)
from core.utils.token_helper import TokenHelper

pwd_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


class UserService:
    def __init__(self):
        ...

    @staticmethod
    async def get_user(username: str, request_user_id: int) -> User:
        query = select(User).where(User.username == username)
        result = await db_session.execute(query)
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException
        res = user.__dict__
        if user.id != request_user_id and "deposit" in res:
            # remove deposit if user is not getting his data
            del res["deposit"]
        return user

    @Transactional()
    async def delete_user(
        self,
        user_id: str,
    ) -> User:
        query = delete(User).where(User.id == user_id)
        result = await db_session.execute(query)
        if not result or result.rowcount == 0:
            raise UserNotFoundException
        return result

    @Transactional()
    async def create_user(
        self, username: str, password1: str, password2: str, role: str, deposit: int
    ) -> None:
        if password1 != password2:
            raise PasswordDoesNotMatchException

        query = select(User).where((User.username == username))
        result = await db_session.execute(query)
        is_exist = result.scalars().first()
        if is_exist:
            raise DuplicateUsernameException
        if role == "seller" and deposit:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Only buyer can have deposit",
            )

        user = User(
            username=username,
            password=get_password_hash(password1),
            role=role,
            deposit=deposit,
        )
        db_session.add(user)

    @staticmethod
    async def login(username: str, password: str) -> LoginResponseSchema:
        result = await db_session.execute(
            select(User).where((User.username == username))
        )
        user = result.scalars().first()
        if not user:
            raise InvalidCredentialsException

        if not verify_password(password, user.password):
            raise InvalidCredentialsException

        message = None
        if await get_active_sessions(user.id):
            message = "There is already an active session using your account"
        access_token = TokenHelper.encode(payload={"user_id": user.id})
        await add_to_active_sessions(user.id, access_token)
        response = LoginResponseSchema(
            token=access_token,
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
            message=message,
        )
        return response

    @staticmethod
    async def logout_all(user_id: int, current_token: str) -> None:
        # logout all sessions
        await revoke_other_active_sessions(user_id, current_token)

    @staticmethod
    @Transactional()
    async def update_password(
        user_id, old_password: str, password1: str, password2: str
    ) -> bool:
        if password1 != password2:
            raise PasswordDoesNotMatchException

        result = await db_session.execute(select(User).where((User.id == user_id)))
        user = result.scalars().first()
        if not user or not verify_password(old_password, user.password):
            raise InvalidCredentialsException
        user.password = get_password_hash(password1)
        return True

    @staticmethod
    @Transactional()
    async def update_profile(user_id: str, payload: dict) -> bool:
        result = await db_session.execute(select(User).where((User.id == user_id)))
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        for key, value in payload.items():
            setattr(user, key, value)
        return True

    @staticmethod
    @Transactional()
    async def deposit(user_id: str, payload: DepositRequestSchema) -> dict:
        result = await db_session.execute(select(User).where((User.id == user_id)))
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        if user.role != BUYER:
            raise SellerDepositException

        user.deposit += payload.value
        return {
            "message": "successful",
            "balance": int(user.deposit),
            "added": payload.value,
        }

    @staticmethod
    @Transactional()
    async def reset_deposit(user_id: str) -> bool:
        result = await db_session.execute(select(User).where((User.id == user_id)))
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        if user.role != BUYER:
            raise SellerDepositException

        user.deposit = 0
        return True
